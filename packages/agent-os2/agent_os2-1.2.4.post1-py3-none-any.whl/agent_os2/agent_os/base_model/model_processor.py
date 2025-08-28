from typing import Any,AsyncGenerator
from .builtin_config import ModelConfig
from abc import ABC,abstractmethod
from enum import Enum

class ModelError(Exception):
    """模型调用相关异常，表示网络或服务器方的问题，包含状态码信息"""
    def __init__(self, message: str, code: int = 500, detail: str = None):
        super().__init__(message)
        self.code = code
        self.detail = detail or message
class StreamDataStatus(Enum):
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"
class DataPackage:
    def __init__(self,status:StreamDataStatus,data:Any,usage:dict[str,Any]|None=None):
        self._status = status
        if self._status == StreamDataStatus.GENERATING:
            self._data = {"data":data}
        elif self._status == StreamDataStatus.COMPLETED:
            self._data = {"full_data":data,"usage":usage}
        elif self._status == StreamDataStatus.ERROR:
            self._data = data

    def to_dict(self)->dict[str,Any]:
        return {
            "status":self._status.value,
            "data":self._data
        }
    def read_data(self) -> Any:
        if self._status == StreamDataStatus.GENERATING:
            return self._data.get("data")
        elif self._status == StreamDataStatus.COMPLETED:
            return self._data.get("full_data")
        return self._data
    def get_status(self)->StreamDataStatus:
        return self._status
    def get_usage(self)->dict[str,Any]:
        return self._data.get("usage") or {}
class BaseProcessor(ABC):
    async def interact(
        self,
        messages: Any,
        model_config: ModelConfig,
        proxy: str,
        api_key: str,
        base_url: str
    ) -> AsyncGenerator[DataPackage, None]:
        chunks: list[Any] = []
        try:
            last_chunk = None
            async for raw_item in self.async_generator(messages, model_config, proxy, api_key, base_url):
                last_chunk = raw_item
                processed_chunk = self.process_chunk(raw_item,model_config)
                chunks.append(raw_item)
                if model_config.is_stream() and processed_chunk is not None:
                    yield DataPackage(StreamDataStatus.GENERATING, data=processed_chunk)
        except ModelError as error:  # 只捕获网络/服务器相关错误用于重试
            error_payload = self.process_error(error, model_config)
            yield DataPackage(StreamDataStatus.ERROR, data=error_payload)
            return
        # 其他异常（逻辑错误等）直接抛出，不封装为ERROR Package

        final_output = self.process_complete(chunks,model_config)
        usage = self.get_usage(last_chunk or {}, messages, final_output, model_config)
        yield DataPackage(StreamDataStatus.COMPLETED, data=final_output, usage=usage)

    @abstractmethod
    async def async_generator(
        self,
        messages: Any,
        model_config: ModelConfig,
        proxy: str,
        api_key: str,
        base_url: str
    ) -> AsyncGenerator[Any, None]:
        ...

    @abstractmethod
    def get_usage(self, last_chunk_data: Any, messages: Any, final_output: Any, model_config: ModelConfig) -> dict[str,Any]:
        ...

    @abstractmethod
    def process_chunk(self, raw_chunk: Any,model_config:ModelConfig) -> Any:
        ...

    @abstractmethod
    def process_complete(self, chunks: list[Any],model_config:ModelConfig) -> Any:
        ...

    def process_error(self, error: ModelError, model_config: ModelConfig) -> dict[str, Any]:
        """处理ModelError，返回包含正确远方错误代码的payload"""
        return {"code": error.code, "message": str(error), "detail": error.detail}
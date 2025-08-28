from typing import Any
# ModelConfig
# 模型配置
class ModelConfig:
    """
    用于基座模型在调用时，向模型发送的配置信息，包括模型名称、流式模式、交互配置等。
    
    参数说明：
    - model_name: 模型名称
    - is_stream: 是否流式模式
    - **kwargs: 其他配置信息
    支持从字典中获取模型配置，并自动根据模型名称获取模型类型，如果模型名称不存在，则抛出异常，可用类方法get_model_config从字典中获取模型配置
    """
    # 自动注册表
    registry: dict[str, type] = {}
    
    def __init_subclass__(cls, **kwargs):
        """子类定义时自动注册"""
        super().__init_subclass__(**kwargs)   
        # 只注册非基类
        if not cls.__name__.endswith("Config"): #排除ModelConfig和ImageConfig等基配置类
            ModelConfig.registry[cls.__name__.upper()] = cls
    
    def __init__(self,model_name,*,is_stream:bool,**kwargs):
        # 延迟导入避免循环依赖
        from .base_api import get_available_models
        available_models = get_available_models()
        if model_name not in available_models:
            raise ValueError(f"模型 {model_name} 不存在")
        self._model_type = available_models[model_name]
        self._model_name = model_name
        self._is_stream = is_stream
        self._interact_config = {
            **kwargs
        }
    def get_model_name(self)->str:
        return self._model_name
    def get_interact_config(self)->dict[str,Any]:
        return self._interact_config.copy()
    def is_stream(self)->bool:
        return self._is_stream
    def get_model_type(self)->str:
        return self._model_type
    def __str__(self)->str:
        return f"model_name: {self._model_name}, is_stream: {self._is_stream}, interact_config: {self._interact_config}"
    @classmethod
    def get_model_config(cls, config: dict[str, str | dict]) -> "ModelConfig|None":
        if config.get("model_name"):
            best_matched = ModelConfig
            max_score = 0
            # 备份config避免修改原始数据
            config_copy = config.copy()
            model_name = config_copy.pop("model_name")
            is_stream = config_copy.pop("is_stream", True)
            # 1. 精确匹配
            config_name = model_name.replace("-","").replace(".","").replace(" ","").replace("_","").upper()
            if config_name in cls.registry:
                return cls.registry[config_name](model_name, is_stream=is_stream, **config_copy)
            # 2. 模糊匹配：按 - 或 _ 分词后匹配，带版号（数字）的匹配权重*2
            import re
            words = re.split(r'[-_]', model_name.upper())
            words = [w for w in words if w]  # 过滤空字符串
            for registry_key, config_class in cls.registry.items():
                score = 0
                for word in words:
                    if word in registry_key:
                        # 带版号（包含数字）的匹配权重*2，提高版本匹配准确性
                        if re.search(r'\d', word):
                            score += 2
                        else:
                            score += 1
                if score > max_score:
                    max_score = score
                    best_matched = config_class
        return best_matched(model_name, is_stream=is_stream, **config_copy)
class GPT45(ModelConfig):
    def __init__(self,model_name:str="gpt-4.5-preview",*,is_stream:bool=True,temperature:float=1,max_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)
class GPT5(ModelConfig):
    def __init__(self,model_name:str="gpt-5",*,is_stream:bool=True,max_completion_tokens:int=128000,reasoning_effort:str="high",**kwargs):
        # GPT5 只支持 temperature=1，不允许自定义
        kwargs.pop('temperature', None)  # 移除外部传入的temperature参数
        super().__init__(model_name,is_stream=is_stream,temperature=1,max_completion_tokens=max_completion_tokens,reasoning_effort=reasoning_effort,**kwargs)
class GPT5Mini(ModelConfig):
    def __init__(self,model_name:str="gpt-5-mini",*,is_stream:bool=True,max_completion_tokens:int=128000,reasoning_effort:str="high",**kwargs):
        # GPT5Mini 只支持 temperature=1，不允许自定义
        kwargs.pop('temperature', None)  # 移除外部传入的temperature参数
        super().__init__(model_name,is_stream=is_stream,temperature=1,max_completion_tokens=max_completion_tokens,reasoning_effort=reasoning_effort,**kwargs)
# ========== OpenAI GPT 4.1 系列 ==========
class GPT41(ModelConfig):
    def __init__(self,model_name:str="gpt-4.1",*,is_stream:bool=True,temperature:float=1,max_tokens:int=32000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class GPT41Mini(ModelConfig):
    def __init__(self,model_name:str="gpt-4.1-mini",*,is_stream:bool=True,temperature:float=1,max_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class GPT41Nano(ModelConfig):
    def __init__(self,model_name:str="gpt-4.1-nano",*,is_stream:bool=True,temperature:float=1,max_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)
# ========== OpenAI GPT 4o 系列 ==========
class GPT4o(ModelConfig):
    def __init__(self,model_name:str="gpt-4o",*,is_stream:bool=True,temperature:float=1,max_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

# ========== OpenAI O系列推理模型 ==========
class O4Mini(ModelConfig):
    def __init__(self,model_name:str="o4-mini",*,is_stream:bool=True,max_completion_tokens:int=100000,reasoning_effort:str="high",**kwargs):
        super().__init__(model_name,is_stream=is_stream,max_completion_tokens=max_completion_tokens,reasoning_effort=reasoning_effort,**kwargs)

class O3Pro(ModelConfig):
    def __init__(self,model_name:str="o3-pro-2025-06-10",*,is_stream:bool=False,max_completion_tokens:int=100000,reasoning_effort:str="high",**kwargs):
        super().__init__(model_name,is_stream=is_stream,max_completion_tokens=max_completion_tokens,reasoning_effort=reasoning_effort,**kwargs)

class O3(ModelConfig):
    def __init__(self,model_name:str="o3",*,is_stream:bool=True,max_completion_tokens:int=100000,reasoning_effort:str="high",**kwargs):
        super().__init__(model_name,is_stream=is_stream,max_completion_tokens=max_completion_tokens,reasoning_effort=reasoning_effort,**kwargs)

class O1(ModelConfig):
    def __init__(self,model_name:str="o1",*,is_stream:bool=True,max_completion_tokens:int=100000,reasoning_effort:str="high",**kwargs):
        super().__init__(model_name,is_stream=is_stream,max_completion_tokens=max_completion_tokens,reasoning_effort=reasoning_effort,**kwargs)

# ========== Anthropic Claude 系列 ==========
class ClaudeOpus4(ModelConfig):
    def __init__(self,model_name:str="claude-opus-4",*,is_stream:bool=True,temperature:float=0.5,max_tokens:int=32000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs) 

class ClaudeSonnet4(ModelConfig):
    def __init__(self,model_name:str="claude-sonnet-4",*,is_stream:bool=True,temperature:float=0.5,max_tokens:int=64000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class Claude37Sonnet(ModelConfig):
    def __init__(self,model_name:str="claude-3-7-sonnet",*,is_stream:bool=True,temperature:float=0.5,max_tokens:int=128000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class ClaudeOpus41(ModelConfig):
    def __init__(self,model_name:str="claude-opus-4-1",*,is_stream:bool=True,temperature:float=0.5,max_tokens:int=64000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

# ========== Alibaba Qwen 系列 ==========
class QwenTurbo(ModelConfig):
    def __init__(self,model_name:str="qwen-turbo-latest",*,is_stream:bool=True,temperature:float=1,max_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class QwenPlus(ModelConfig):
    def __init__(self,model_name:str="qwen-plus-latest",*,is_stream:bool=True,temperature:float=1,max_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class QwenMax(ModelConfig):
    def __init__(self,model_name:str="qwen-max",*,is_stream:bool=True,temperature:float=1,max_tokens:int=8000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class QwQ32B(ModelConfig):
    def __init__(self,model_name:str="qwq-32b",*,is_stream:bool=True,max_tokens:int=8000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,max_tokens=max_tokens,**kwargs)

class QwQPlus(ModelConfig):
    def __init__(self,model_name:str="qwq-plus",*,is_stream:bool=True,max_tokens:int=8000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,max_tokens=max_tokens,**kwargs)

# ========== DeepSeek 系列 ==========
class DeepSeekReasoner(ModelConfig):
    def __init__(self,model_name:str="deepseek-reasoner",*,is_stream:bool=True,max_tokens:int=64000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,max_tokens=max_tokens,**kwargs)

class DeepSeekChat(ModelConfig):
    def __init__(self,model_name:str="deepseek-chat",*,is_stream:bool=True,temperature:float=1,max_tokens:int=8000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

# ========== Google Gemini 系列 ==========
class Gemini25Pro(ModelConfig):
    def __init__(self,model_name:str="gemini-2.5-pro",*,is_stream:bool=True,temperature:float=1,max_output_tokens:int=65535,include_thoughts:bool=False,**kwargs): #需要看到思考内容就开启include_thoughts
        kwargs.pop("thinking_budget",None) # 2.5Pro无法关闭思考
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_output_tokens=max_output_tokens,include_thoughts=include_thoughts,thinking_budget=True,**kwargs)
class Gemini25Flash(ModelConfig):
    def __init__(self,model_name:str="gemini-2.5-flash",*,is_stream:bool=True,temperature:float=1,max_output_tokens:int=65535,include_thoughts:bool=False,thinking_budget:bool|None=True,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_output_tokens=max_output_tokens,include_thoughts=include_thoughts,thinking_budget=thinking_budget,**kwargs)
class Gemini25FlashLite(ModelConfig):
    def __init__(self,model_name:str="gemini-2.5-flash-lite",*,is_stream:bool=True,temperature:float=1,max_output_tokens:int=65535,**kwargs):
        kwargs.pop("thinking_budget",None) #flash-lite思考
        kwargs.pop("include_thoughts",None) #flash-lite思考
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_output_tokens=max_output_tokens,**kwargs)
class Gemini20Flash(ModelConfig):
    def __init__(self,model_name:str="gemini-2.0-flash",*,is_stream:bool=True,temperature:float=1,max_output_tokens:int=8000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_output_tokens=max_output_tokens,**kwargs)

# ========== xAI Grok 系列 ==========
class Grok4(ModelConfig):
    def __init__(self,model_name:str="grok-4-0709",*,is_stream:bool=True,temperature:float=1,max_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class Grok3(ModelConfig):
    def __init__(self,model_name:str="grok-3",*,is_stream:bool=True,temperature:float=1,max_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class Grok3Mini(ModelConfig):
    def __init__(self,model_name:str="grok-3-mini",*,is_stream:bool=True,temperature:float=1,max_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

# ========== 图像生成模型配置 ==========
class ImageConfig(ModelConfig):
    def __init__(self,model_name:str,*,is_stream:bool=False,save_folder:str|None=None,**kwargs):
        if not save_folder:
            import os
            save_folder = os.path.join(os.getcwd(),"memory","pic_lib")
        super().__init__(model_name,is_stream=is_stream,save_folder=save_folder,**kwargs)
class Gemini25FlashImagePreview(ImageConfig):
    def __init__(self,model_name:str="gemini-2.5-flash-image-preview",*,is_stream:bool=False,save_folder:str|None=None,temperature:float=1,max_output_tokens:int=65535,**kwargs):
        kwargs.pop("thinking_budget",None) # 2.5FlashImagePreview不支持思考
        kwargs.pop("include_thoughts",None) # 2.5FlashImagePreview不支持思考
        super().__init__(model_name,is_stream=is_stream,save_folder=save_folder,temperature=temperature,max_output_tokens=max_output_tokens,**kwargs)
class Flux(ImageConfig):
    def __init__(self,model_name: str = "flux-kontext-pro",*,save_folder:str|None=None,steps: int = 28,guidance: float = 3.5,aspect_ratio: str = "1:1",seed: int | None = None,output_format: str = "png", **kwargs):
        super().__init__(model_name,save_folder=save_folder,steps=steps,guidance=guidance,aspect_ratio=aspect_ratio,seed=seed,output_format=output_format,**kwargs)
class DallE2(ImageConfig):
    def __init__(self,model_name="dall-e-2",*,save_folder:str|None=None,size:str="1024x1024",n=1,**kwargs):
        kwargs.pop("quality",None) # quality只能等于standard
        super().__init__(model_name,save_folder=save_folder,size=size,response_format="b64_json",n=n,**kwargs) # 内置处理器希望response_format=b64_json
class DallE3(ImageConfig):
    def __init__(self,model_name="dall-e-3",*,save_folder:str|None=None,size:str="1024x1024",quality:str="standard",style:str="natural",**kwargs):
        kwargs.pop("n",None) # n只能等于1
        super().__init__(model_name,save_folder=save_folder,size=size,quality=quality,style=style,response_format="b64_json",**kwargs)
class GPTImage1(ImageConfig):
    def __init__(self,model_name:str="gpt-image-1",*,is_stream:bool=False,save_folder:str|None=None,size:str="1024x1024",quality:str="high",output_format:str="png",moderation:str="auto",background:str="auto",partial_images:int=0,**kwargs):
        kwargs.pop("response_format",None) # response_format只能等于b64_json，且不接受该参数
        kwargs.pop("n",None) # n只能等于1
        super().__init__(model_name,is_stream=is_stream,save_folder=save_folder,size=size,quality=quality,output_format=output_format,moderation=moderation,background=background,n=1,partial_images=partial_images,**kwargs) #1<=n<=10
class ImagenConfig(ImageConfig):
    """
    Google Imagen 图像生成模型配置基类
    """
    def __init__(self, model_name:str, *, is_stream:bool=False, save_folder:str|None=None, 
                 number_of_images:int=1, aspect_ratio:str="1:1", 
                 person_generation:str="allow_adult", output_format:str="png", **kwargs):
        """        
        Args:
            model_name: 模型名称，支持 imagen-4.0-generate-001 等
            is_stream: Imagen不支持流式输出，固定为False
            save_folder: 图像保存文件夹路径
            number_of_images: 生成图像数量，1-4之间
            aspect_ratio: 宽高比，支持"1:1","3:4","4:3","9:16","16:9"
            person_generation: 人物生成控制，"dont_allow"|"allow_adult"|"allow_all"
            output_format: 输出格式，默认"png"
        """
        # 验证参数
        number_of_images = min(max(number_of_images, 1), 4)
        if aspect_ratio not in ["1:1", "3:4", "4:3", "9:16", "16:9"]:
            aspect_ratio = "1:1"  
        if person_generation not in ["dont_allow", "allow_adult", "allow_all"]:
            person_generation = "allow_adult"
            
        # 注意：sample_image_size 不被 Google GenAI SDK 支持，但保留用于配置兼容性
        super().__init__(
            model_name, 
            is_stream=False,  # Imagen不支持流式输出
            save_folder=save_folder,
            number_of_images=number_of_images,
            aspect_ratio=aspect_ratio,
            person_generation=person_generation,
            output_format=output_format,
            **kwargs
        )
# 提供具体模型的便捷配置类
class Imagen4(ImagenConfig):
    def __init__(self,model_name="imagen-4.0-generate-001", **kwargs):
        super().__init__(model_name=model_name, **kwargs)
class Imagen4Ultra(ImagenConfig):
    def __init__(self,model_name="imagen-4.0-ultra-generate-001", **kwargs):
        super().__init__(model_name=model_name, **kwargs)
class Imagen4Fast(ImagenConfig):
    def __init__(self,model_name="imagen-4.0-fast-generate-001", **kwargs):
        # Fast 模型不支持 sample_image_size 参数，强制移除（SDK 本身也不支持此参数）
        kwargs.pop("sample_image_size", None)
        super().__init__(model_name=model_name, **kwargs)
class Imagen3(ImagenConfig):
    def __init__(self,model_name="imagen-3.0-generate-002" ,**kwargs):
        super().__init__(model_name=model_name, **kwargs)
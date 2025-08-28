from typing import Type,Any,AsyncGenerator
from .model_processor import BaseProcessor,ModelError
import aiohttp
import os
import time
import uuid
from google import genai
from google.genai import types as genai_types
from google.genai.errors import APIError as GoogleAPIError
from .utility import *
from .builtin_config import ModelConfig
# 模型注册表
PROCESSOR_TYPE_MAPPINGS: dict[str, Type[BaseProcessor]] = {}

def register(*processor_types: str):
    def decorator(cls: Type[BaseProcessor]):
        for processor_type in processor_types:
            if processor_type in PROCESSOR_TYPE_MAPPINGS:
                raise ValueError(f"模型类型 '{processor_type}' 已注册")
            PROCESSOR_TYPE_MAPPINGS[processor_type] = cls
        return cls
    return decorator

def save_image_from_bytes(image_bytes: bytes, memory_folder: str, extension: str = "png", model_name: str = ""):
    """保存图像并返回@[Image](路径)格式"""
    model_prefix = model_name.replace("-", "_").replace(".", "_") if model_name else "unknown"
    image_id = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
    filename = f"{model_prefix}_{image_id}.{extension}"
    save_path = os.path.join(memory_folder, filename)
    with open(save_path, "wb") as f:
        f.write(image_bytes)
    return "@[Image](" + save_path + ")"
@register("google-chat")
class GoogleChatProcessor(BaseProcessor):
    """
    真异步的 Google Gemini 处理器
    使用新版 google-genai SDK 的异步实现
    """
    async def async_generator(self, messages: Any, model_config: "ModelConfig", proxy: str, api_key: str, base_url: str):
        """真异步实现：使用新版 google-genai SDK"""
        
        # 强制使用 httpx 而不是 aiohttp 来避免 "Chunk too big" 错误
        # 通过设置 transport 参数强制 SDK 不使用 aiohttp
        import httpx
        
        http_options = genai_types.HttpOptions(
            async_client_args={
                'trust_env': True,
                # 设置 transport 参数强制使用 httpx，避免 aiohttp 的缓冲区限制
                'transport': httpx.AsyncHTTPTransport(
                    limits=httpx.Limits(
                        max_keepalive_connections=30,
                        max_connections=100,
                        keepalive_expiry=300
                    )
                ),
            }
        )
        if proxy:
            http_options.async_client_args['proxy'] = proxy
            
        client = genai.Client(
            api_key=api_key, 
            http_options=http_options
        )
        system_instruction, contents = process_messages_to_genai_format(messages)
        contents = await extract_modals_from_genai_messages(contents,client)
        config = model_config.get_interact_config()
        config.pop("save_folder",None) #实际交互不需要这个参数
        
        # 处理thinking相关配置
        if thinking_budget := config.pop("thinking_budget", None):
            config["thinking_config"] = genai_types.ThinkingConfig(
                include_thoughts=config.pop("include_thoughts", None),
                thinking_budget=-1 if thinking_budget else 0  # -1开启思考，0关闭思考
            )
        #不管是否开启思考都删除额外配置，防止传入导致错误
        config.pop("include_thoughts",None)
        # 如果有system_instruction，添加到请求参数中
        if system_instruction:
            config["system_instruction"] = system_instruction
        # 构建请求参数
        request_params = {
            "model": model_config.get_model_name(),
            "contents": contents,
            "config": genai_types.GenerateContentConfig(**config)
        }
        
        # 使用异步流式API，BaseProcessor会根据is_stream()决定输出模式
        try:
            async for chunk in await client.aio.models.generate_content_stream(**request_params):
                yield chunk
        except GoogleAPIError as e:
            raise ModelError(f"Google GenAI API错误: {e.message}", e.code)
                    
    def get_usage(self, last_chunk_data: genai_types.GenerateContentResponse, messages: Any, final_output: Any, model_config: "ModelConfig") -> dict[str,Any]:
        model_name = model_config.get_model_name()
        
        # 处理新版SDK的usage
        if hasattr(last_chunk_data, 'usage_metadata') and last_chunk_data.usage_metadata:
            prompt_tokens = last_chunk_data.usage_metadata.prompt_token_count or 0
            candidates_tokens = last_chunk_data.usage_metadata.candidates_token_count or 0
            thoughts_tokens = last_chunk_data.usage_metadata.thoughts_token_count or 0
            completion_tokens = candidates_tokens + thoughts_tokens
            total_tokens = last_chunk_data.usage_metadata.total_token_count or 0
            return {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "cost": get_model_cost(model_name, prompt_tokens, completion_tokens)
            }
        else:
            # 回退计算
            prompt_tokens = get_fallback_tokens(str(messages), model=model_name, initial_tokens=3)
            completion_tokens = get_fallback_tokens(str(final_output), model=model_name, initial_tokens=3)
            total_tokens = prompt_tokens + completion_tokens
            return {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "cost": get_model_cost(model_name, prompt_tokens, completion_tokens)
            }

    def process_chunk(self, raw_chunk: genai_types.GenerateContentResponse,model_config:ModelConfig) -> str | tuple[str,str]:
        """处理新版SDK的响应块"""
        thoughts = ""
        answer = ""
        
        if hasattr(raw_chunk, 'candidates') and raw_chunk.candidates:
            candidate = raw_chunk.candidates[0]
            if (hasattr(candidate, 'content') and candidate.content is not None and 
                hasattr(candidate.content, 'parts') and candidate.content.parts is not None):
                for part in candidate.content.parts:
                    if hasattr(part,'inline_data') and part.inline_data:
                        answer += save_image_from_bytes(part.inline_data.data,model_config.get_interact_config().get("save_folder",os.path.join(os.getcwd(),"memory","pic_lib")),extension="png",model_name=model_config.get_model_name())
                    elif hasattr(part, 'thought') and part.thought:
                        thoughts += part.text if part.text else ""
                    elif hasattr(part, 'text') and part.text:
                        answer += part.text
        return (thoughts, answer) if thoughts else answer

    def process_complete(self, raw_chunks: list[genai_types.GenerateContentResponse],model_config:ModelConfig) -> str:
        accumulated_thoughts = ""
        accumulated_answer = ""
        for raw_chunk in raw_chunks:
            processed_result = self.process_chunk(raw_chunk, model_config)
            if processed_result is None:
                continue
            if isinstance(processed_result, tuple):
                thoughts, answer = processed_result
                if thoughts:
                    accumulated_thoughts += thoughts
                if answer:
                    accumulated_answer += answer
            elif isinstance(processed_result, str):
                accumulated_answer += processed_result
        return "[思考总结]\n" + accumulated_thoughts + "\n[回答]\n" + accumulated_answer if accumulated_thoughts else accumulated_answer
@register("openai-chat")
class OpenAIChatProcessor(BaseProcessor):
    def transform_model_name(self, model_config: "ModelConfig") -> str:
        """
        转换模型名称，子类可以重写此方法来实现模型名称映射
        默认实现直接返回原始模型名称
        """
        return model_config.get_model_name()
    
    def get_usage(self, last_chunk_data: dict[str,Any], messages: Any, final_output: Any, model_config: "ModelConfig") -> dict[str,Any]:
        model_name = model_config.get_model_name()
        
        # 优先使用API返回的usage，如果没有则使用fallback计算
        if last_chunk_data.get("usage"):
            usage = last_chunk_data["usage"]
            prompt_tokens = usage.get("prompt_tokens", get_fallback_tokens(str(messages), model=model_name, initial_tokens=3))
            completion_tokens = usage.get("completion_tokens", get_fallback_tokens(str(final_output), model=model_name, initial_tokens=3))
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
        else:
            # 完全回退计算
            prompt_tokens = get_fallback_tokens(str(messages), model=model_name, initial_tokens=3)
            completion_tokens = get_fallback_tokens(str(final_output), model=model_name, initial_tokens=3)
            total_tokens = prompt_tokens + completion_tokens
            
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost": get_model_cost(model_name,prompt_tokens,completion_tokens)
        }
    async def async_generator(self, messages: str|list[dict[str,str]]|dict[str,str], model_config: "ModelConfig",proxy:str,api_key:str,base_url:str):
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        url = (base_url[:-1] if base_url.endswith("/") else base_url) + ("" if base_url.endswith("/chat/completions") else "/chat/completions")

        messages = process_messages_to_openai_style(messages)
        messages = await extract_modals_from_openai_style_messages(messages)
        
        payload = {"model": self.transform_model_name(model_config), "messages": messages, **model_config.get_interact_config(), "stream": True}
        session_kwargs = {}
        if proxy:
            session_kwargs["proxy"] = proxy

        if not base_url:
            raise ValueError("api_url 不能为空！请检查 llm_key.json 配置和模型名到平台的映射关系。")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json=payload, **session_kwargs) as response:
                    if response.status != 200:
                        error = await response.text()
                        raise ModelError(f"请求失败: {error}", response.status)
                    # 使用通用SSE解析器
                    async for chunk_data in parse_sse_stream(response.content):
                        yield chunk_data

            except aiohttp.ClientError as net_exc:
                raise ModelError(f"网络异常: {net_exc}", 503)


    def process_chunk(self, raw_chunk: dict[str, Any],model_config:ModelConfig) -> Any:
        delta = raw_chunk.get('choices', [{}])[0].get('delta', {}) if isinstance(raw_chunk, dict) else {}
        return delta.get('content') or None

    def process_complete(self, raw_chunks: list[dict[str, Any]],model_config:ModelConfig) -> Any:
        result = ""
        for raw_chunk in raw_chunks:
            processed_chunk = self.process_chunk(raw_chunk, model_config)
            if processed_chunk is not None and isinstance(processed_chunk, str):
                result += processed_chunk
        return result

# 图片模型保留自定义实现
@register("openai-image-generate")
class OpenAIImageProcessor(BaseProcessor):
    def get_usage(self, last_chunk_data: dict[str,Any], messages: Any, final_output: Any, model_config: "ModelConfig") -> dict[str,Any]:
        model_name = model_config.get_model_name()
        cost = 0
        prompt_tokens = 0
        total_tokens = 0
        
        # 优先使用API返回的usage，如果没有则使用fallback计算
        if last_chunk_data.get("usage"):
            usage = last_chunk_data["usage"]
            prompt_tokens = usage.get("prompt_tokens", get_fallback_tokens(str(messages), model=model_name))
            total_tokens = usage.get("total_tokens", prompt_tokens)
        else:
            # 完全回退计算
            prompt_tokens = get_fallback_tokens(str(messages), model=model_name)
            total_tokens = prompt_tokens
        with open(os.path.join(os.path.dirname(__file__), "models_price.json"), "r") as f:
            model_cost = json.load(f).get(model_name,{})
            if model_name == "gpt-image-1":
                n = model_config.get_interact_config().get("n",1)
                quality = model_config.get_interact_config().get("quality","high")
                cost = model_cost.get("output_price",{}).get(quality,0) * n + model_cost.get("input_price",0) * prompt_tokens / 1000
        if model_name == "dall-e-2":
            cost = 0.02
        elif model_name == "dall-e-3":
            cost = 0.12 if model_config.get_interact_config().get("quality","standard") == "hd" else 0.08
        return {
            "prompt_tokens": prompt_tokens,
            "total_tokens": total_tokens,
            "cost": cost
        }
    async def async_generator(self, messages:str, model_config: "ModelConfig",proxy:str,api_key:str,base_url:str):
        if not base_url:
            raise ValueError("api_url 不能为空！请检查 llm_key.json 配置和模型名到平台的映射关系。")
        
        session_kwargs = {"proxy": proxy} if proxy else {}
        # 设置更大的chunk限制来处理图片数据
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=300)  # 5分钟超时
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            payload={
                    "model": model_config.get_model_name(),
                    "prompt": str(messages),
                    **model_config.get_interact_config()
                }
            if model_config.is_stream():
                payload["stream"] = True
            payload.pop("save_folder")
            async with session.post(
                f"{base_url}/images/generations",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
                **session_kwargs
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise ModelError(f"图片生成失败: {error}", response.status)
                
                if model_config.is_stream():
                    # 使用通用SSE解析器
                    async for chunk_data in parse_sse_stream(response.content,8192):
                        yield chunk_data
                else:
                    # 处理非流式响应
                    yield await response.json()

    def process_chunk(self, raw_chunk: dict[str, Any],model_config:ModelConfig) -> Any:
        if raw_chunk.get("type") == "image_generation.partial_image":
            b64_data = raw_chunk.get("b64_json")
            return self.save_image_from_base64(b64_data,model_config.get_interact_config().get("save_folder",os.path.join(os.getcwd(),"memory","pic_lib")),extension=model_config.get_interact_config().get("output_format","png"),model_name=model_config.get_model_name())
        return None
    def process_complete(self, raw_chunks: list[dict[str, Any]],model_config:ModelConfig) -> Any:
        if not raw_chunks:
            return []
        
        folder = model_config.get_interact_config().get("save_folder",os.path.join(os.getcwd(),"memory","pic_lib"))
        os.makedirs(folder, exist_ok=True)
        final_images = []
        
        # 遍历所有原始chunks寻找最终完整图片（非partial_image）
        for raw_chunk in raw_chunks:
            if isinstance(raw_chunk, dict):
                # 检查原始chunk根级别的图片数据，用于gpt-image-1
                if (raw_chunk.get("b64_json") and 
                    raw_chunk.get("type") != "image_generation.partial_image"):
                    final_images.append(self.save_image_from_base64(raw_chunk["b64_json"], folder,extension=model_config.get_interact_config().get("output_format","png"),model_name=model_config.get_model_name()))
                # 同时检查data字段中的图片数据，用于dall-e系列
                elif raw_chunk.get("data") and isinstance(raw_chunk["data"], list):
                    for image_data in raw_chunk["data"]:
                        if image_data.get("b64_json"):
                            final_images.append(self.save_image_from_base64(image_data["b64_json"], folder,extension=model_config.get_interact_config().get("output_format","png"),model_name=model_config.get_model_name()))
        
        return final_images

    @staticmethod
    def save_image_from_base64(b64_data, memory_folder,extension:str="png",model_name:str=""):
        image_id = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
        filename = f"{model_name.replace("-","_").replace(".","_")}_{image_id}.{extension}"
        save_path = os.path.join(memory_folder, filename)
        image_bytes = base64.b64decode(b64_data)
        with open(save_path, "wb") as f:
            f.write(image_bytes)
        return "@[Image](" + save_path+")"
@register("google-imagen-image-generate")
class GoogleImageProcessor(BaseProcessor):
    """
    Google Imagen 图像生成处理器
    支持 imagen-4.0-generate-001, imagen-4.0-ultra-generate-001, 
    imagen-4.0-fast-generate-001, imagen-3.0-generate-002 模型
    """
    
    def get_usage(self, last_chunk_data: dict[str, Any], messages: Any, final_output: Any, model_config: "ModelConfig") -> dict[str, Any]:
        """Imagen模型使用固定成本计算"""
        model_name = model_config.get_model_name()
        config = model_config.get_interact_config()
        number_of_images = config.get("number_of_images", 1)
        
        # 根据模型和图像数量计算成本
        if "4" in model_name:
            if "ultra" in model_name:
                cost_per_image = 0.06  # Ultra模型成本更高
            elif "fast" in model_name:
                cost_per_image = 0.02  # Fast模型成本较低
            else:
                cost_per_image = 0.04  # 标准模型成本
        elif "3" in model_name:
            cost_per_image = 0.03  # 标准模型成本
            
        return {
            "cost": cost_per_image * number_of_images,
            "images_generated": number_of_images
        }
    
    async def async_generator(self, messages: str, model_config: "ModelConfig", proxy: str, api_key: str, base_url: str):
        """使用Google GenAI SDK生成图像"""
        # 创建异步客户端
        http_options = genai_types.HttpOptions(
            async_client_args={'trust_env': True}
        )
        if proxy:
            http_options.async_client_args['proxy'] = proxy
            
        client = genai.Client(
            api_key=api_key,
            http_options=http_options
        )
        
        # 简化处理：只支持字符串提示词
        prompt = str(messages)
        
        # 构建配置
        config = model_config.get_interact_config()
        generate_config_params = {}
        
        # 映射配置参数 (使用camelCase格式)
        if "number_of_images" in config:
            generate_config_params["numberOfImages"] = min(max(config["number_of_images"], 1), 4)
        else:
            generate_config_params["numberOfImages"] = 1
            
        # 注意：sampleImageSize 参数不被 Google GenAI SDK 接受，已完全移除
            
        if "aspect_ratio" in config:
            generate_config_params["aspectRatio"] = config["aspect_ratio"]
            
        if "person_generation" in config:
            generate_config_params["personGeneration"] = config["person_generation"]
        
        # 调用Imagen API
        try:
            response = await client.aio.models.generate_images(
                model=model_config.get_model_name(),
                prompt=prompt,
                config=genai_types.GenerateImagesConfig(**generate_config_params)
            )
        except GoogleAPIError as e:
            raise ModelError(f"Google GenAI API错误: {e.message}", e.code)
        
        # 检查响应是否为空或被拒绝
        if not response or not response.generated_images:
            raise ModelError("模型拒绝生成图像：可能由于内容安全策略、提示词不当或其他限制", 400)
        
        # 返回生成的图像数据
        images_data = []
        for generated_image in response.generated_images:
            # 检查生成的图像是否有效
            if not generated_image or not generated_image.image:
                raise ModelError("模型返回了无效的图像数据：生成内容可能被安全过滤器阻止", 400)
            
            # 获取Google GenAI图像对象
            genai_image = generated_image.image
            
            # 直接获取图像字节数据
            if hasattr(genai_image, 'image_bytes') and genai_image.image_bytes:
                image_bytes = genai_image.image_bytes
            else:
                raise ModelError("图像生成失败：模型返回了空的图像数据，可能由于内容违反安全政策", 400)
            
            # 获取输出格式
            output_format = config.get("output_format", "png").lower()
            
            images_data.append({
                "image_bytes": image_bytes,
                "format": output_format
            })
        
        yield {"images": images_data}
    
    def process_chunk(self, raw_chunk: dict[str, Any], model_config: "ModelConfig") -> Any:
        """Imagen不需要流式处理"""
        return None
    
    def process_complete(self, raw_chunks: list[dict[str, Any]], model_config: "ModelConfig") -> str:
        """处理完成后保存图像并返回@[Image](路径)格式"""
        if not raw_chunks or not raw_chunks[-1].get("images"):
            raise ModelError("图像生成被拒绝：模型未返回任何图像数据，可能由于提示词违反内容政策", 400)
            
        final_data = raw_chunks[-1]
        images_data = final_data["images"]
        
        # 检查是否有有效的图像数据
        if not images_data or len(images_data) == 0:
            raise ModelError("图像生成被拒绝：未获得任何有效图像，可能由于内容安全限制", 400)
        
        # 获取保存配置
        config = model_config.get_interact_config()
        save_folder = config.get("save_folder", os.path.join(os.getcwd(), "memory", "pic_lib"))
        os.makedirs(save_folder, exist_ok=True)
        
        # 保存所有图像并生成结果
        results = []
        for i, image_data in enumerate(images_data):
            # 检查单个图像数据是否有效
            if not image_data.get("image_bytes"):
                raise ModelError(f"第{i+1}张图像生成被拒绝：图像数据为空，可能违反了内容安全政策", 400)
                
            image_path = save_image_from_bytes(
                image_data["image_bytes"], 
                save_folder,
                extension=image_data.get("format", "png"),
                model_name=model_config.get_model_name()
            )
            results.append(image_path)
        
        # 返回结果
        return results
    
@register("lite-llm-chat")
class LiteLLMChatProcessor(OpenAIChatProcessor):
    def transform_model_name(self, model_config: "ModelConfig") -> str:
        """
        LiteLLM模型名称转换，将原始模型名称转换为带提供商前缀的格式
        """
        name = model_config.get_model_name()
        
        if "gpt" in name or "o1" in name or "o3" in name or "o4" in name or "omni" in name or "dall-e" in name or "text-moderation" in name or "text_embedding" in name:
            return f"openai/{name}"
        elif "gemini" in name or "google" in name:
            return f"gemini/{name}"
        elif "grok" in name:
            return f"xai/{name}"
        elif "claude" in name:
            return f"anthropic/{name}"
        elif "deepseek" in name:
            return f"deepseek/{name}"
        else:
            return f"groq/{name}"
    
    async def async_generator(self, messages: Any, model_config: "ModelConfig", proxy: str, api_key: str, base_url: str):
        # 对于gemini模型，需要特殊处理max_output_tokens参数
        name = model_config.get_model_name()
        config = model_config.get_interact_config()
        if 'reasoning_effort' in config:
            config['allowed_openai_params'] = ['reasoning_effort']
        if "gemini" in name or "google" in name:
            # 创建一个临时的配置副本来处理gemini特殊参数
            config.pop("include_thoughts",None)
            thinking_budget = config.pop("thinking_budget",None)
            config["reasoning_effort"] = "high" if thinking_budget == True else None
            config["allowed_openai_params"] = ['reasoning_effort']
            if tokens := config.pop("max_output_tokens", None):
                config["max_tokens"] = tokens
        async for chunk in super().async_generator(messages, ModelConfig(name,is_stream=model_config.is_stream(),**config), proxy, api_key, base_url):
            yield chunk
@register("flux-image-generate")
class FluxProcessor(BaseProcessor):
    def get_usage(self, last_chunk_data: dict[str,Any], messages: Any, final_output: Any, model_config: "ModelConfig") -> dict[str,Any]:
        # Flux模型固定成本，不需要token计算
        return {
            "cost": 0.02
        }
    async def async_generator(self, messages:str, model_config: "ModelConfig",proxy:str,api_key:str,base_url:str):
        headers = {'accept': 'application/json','x-key': api_key,'Content-Type': 'application/json'}
        async with aiohttp.ClientSession() as session:
            # 透传交互配置：steps/guidance/aspect_ratio/seed
            payload = {
                'prompt': messages,
                **model_config.get_interact_config()
            }

            # 与既有后端保持兼容的固定路由
            async with session.post(f"{base_url}/{model_config.get_model_name()}", headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ModelError(f"Flux 图片生成失败: {error_text}", response.status)
                
                response_data = await response.json()
                if not response_data or not response_data.get("polling_url"):
                    raise ModelError("未能获取有效的响应数据", 502)
                
                # 轮询获取图片
                while True:
                    await asyncio.sleep(0.5)
                    async with session.get(response_data["polling_url"], headers=headers, params={'id': response_data["id"]}) as polling_response:
                        if polling_response.status != 200:
                            error_text = await polling_response.text()
                            raise ModelError(f"轮询请求失败: {error_text}", polling_response.status)
                        
                        polling_data = await polling_response.json()
                        if polling_data["status"] == "Ready":
                            image_url = polling_data['result']['sample']
                            break
                        elif polling_data["status"] in ["Error", "Failed"]:
                            raise ModelError("轮询失败", 502)
                
                # 下载图片
                async with session.get(image_url) as image_response:
                    if image_response.status != 200:
                        error_text = await image_response.text()
                        raise ModelError(f"图片下载失败: {error_text}", image_response.status)
                    yield {"image_bytes": await image_response.read(), "url": image_url}

    def process_chunk(self, raw_chunk: dict[str, Any],model_config:ModelConfig) -> Any:
        return None # Flux不需要流式输出处理

    def process_complete(self, raw_chunks: list[dict[str, Any]],model_config:ModelConfig) -> Any:
        # Flux直接从最后的原始数据处理
        if not raw_chunks:
            return ""
        final_raw_data = raw_chunks[-1] if raw_chunks else {}
        if not final_raw_data.get("image_bytes"):
            return ""
        folder = model_config.get_interact_config().get("save_folder",os.path.join(os.getcwd(),"memory","pic_lib"))
        os.makedirs(folder, exist_ok=True)
        result = save_image_from_bytes(final_raw_data["image_bytes"], folder,extension=model_config.get_interact_config().get("output_format","png"),model_name=model_config.get_model_name())
        return result
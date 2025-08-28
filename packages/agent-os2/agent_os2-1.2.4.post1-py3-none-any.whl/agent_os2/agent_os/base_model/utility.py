from google import genai
from google.genai import types as genai_types
import json
import asyncio
import base64
from typing import Any
from enum import Enum
# 获取保守tokens统计
def get_fallback_tokens(*messages, model="gpt-4o", initial_tokens=0)->int:
    """
    根据messages获取保守的tokens统计，借助tiktoken进行基本统计
    针对字符串消息进行简化处理
    
    args:
        *messages: 字符串消息列表
        model: 用于编码的模型名称，默认为gpt-4o
        initial_tokens: 初始token开销，用于不同类型处理器的格式开销，默认为0
    returns:
        总token数的保守估计
    """
    import tiktoken
    
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # 如果模型不支持，回退到gpt-4o的编码器
        encoding = tiktoken.encoding_for_model("gpt-4o")
    
    num_tokens = initial_tokens  # 添加初始开销，替代硬编码的3
    for message in messages:
        if message:  # 只处理非空消息
            num_tokens += len(encoding.encode(str(message)))
    
    return num_tokens
    

# 获取模型成本
def get_model_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    """
    根据配置文件获取模型成本，文件中是每1000token的美元计价。
    匹配策略：先精确匹配；若无则使用“键包含于 model_name”的子串匹配（取最长匹配键）。
    """
    import json
    import os
    with open(os.path.join(os.path.dirname(__file__), "models_price.json"), "r") as f:
        model_cost: dict[str, dict[str, float]] = json.load(f)

    # 精确匹配
    entry = model_cost.get(model_name)

    # 子串匹配（最长匹配优先），大小写不敏感
    if not entry:
        lower_name = (model_name or "").lower()
        best_key = None
        best_len = 0
        for key in model_cost.keys():
            k = key.lower()
            if k in lower_name and len(k) > best_len:
                best_key = key
                best_len = len(k)
        entry = model_cost.get(best_key, {})

    return entry.get("input_price", 0) * prompt_tokens / 1000 + entry.get("output_price", 0) * completion_tokens / 1000

async def parse_sse_stream(response_content,each_chunk_size:int=4096):
    """
    通用的Server-Sent Events流解析器
    
    Args:
        response_content: aiohttp响应的content对象
        
    Yields:
        解析后的JSON数据对象
    """
    buffer = ""
    async for chunk in response_content.iter_chunked(each_chunk_size):
        try:
            buffer += chunk.decode("utf-8")
        except:
            continue
        
        # 按行处理
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            
            if line.startswith("data: "):
                data = line[6:].strip()  # 移除 "data: "
                if data == "[DONE]":
                    return
                if data:
                    try:
                        chunk_data = json.loads(data)
                        yield chunk_data
                    except json.JSONDecodeError:
                        # JSON 解析失败就跳过，不要过度处理
                        pass

class Modals(Enum):
    IMAGE = "Image"
    TEXT = "Text"
    AUDIO = "Audio"
    VIDEO = "Video"
    DOCS = "Docs"
def extract_valid_modal_patterns(text: str) -> list[tuple[str, str, str]]:
    """
    提取并验证文本中所有有效的 @[Modal类型](路径) 格式内容
    支持格式：
    - @[Image](path) - 传统格式
    - @[Image/JPEG](path) - 新格式，可指定具体文件格式
    - @[Video:fps=5](path) - 带参数格式
    - @[Video/mp4:fps=5,start_offset=10s,end_offset=1750s](path) - 完整格式（类型/格式:参数）
    
    Args:
        text: 待解析的文本
        
    Returns:
        list[tuple[str, str, str]]: 返回验证通过的匹配结果列表，每个元组包含 (完整匹配, Modal类型+格式+参数, 路径)
    """
    import re
    
    # 从枚举类动态获取支持的Modal类型
    valid_modal_names = [modal.name for modal in Modals]
    
    # 构建正则表达式，直接在表达式中限制有效的Modal类型（大小写不敏感）
    # 支持格式：Modal类型 | Modal类型/格式 | Modal类型:参数 | Modal类型/格式:参数
    modal_pattern = '|'.join(re.escape(modal) for modal in valid_modal_names)
    # 修改正则表达式，支持可选的格式部分和参数部分
    pattern = rf'@\[(({modal_pattern})(?:/[A-Za-z0-9]+)?(?::[^]]+)?)\]\(([^)]*(?:/[^)]*)*[^)]*)\)'
    
    results = []
    for match in re.finditer(pattern, text, re.IGNORECASE):
        full_match = match.group(0)
        modal_type = match.group(1)  # 完整的类型+格式+参数，如 VIDEO/mp4:fps=5
        path = match.group(3)  # 路径现在在第3个捕获组
        
        # 验证路径：网页地址、包含路径分隔符的路径、或包含文件扩展名的文件名
        is_url = path.startswith(('http://', 'https://', 'file://'))
        has_path_separator = '/' in path or '\\' in path
        has_file_extension = '.' in path and not path.endswith('.')
        
        if is_url or has_path_separator or has_file_extension:
            results.append((full_match, modal_type, path))
    
    return results
async def get_file_bytes_from_url(url: str) -> bytes:
    """通用的异步文件bytes获取函数，支持HTTP/HTTPS/file://协议和本地路径"""
    import pathlib
    import httpx
    if url.startswith("http"):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.content
    elif url.startswith("file://"):
        local_path = url[7:]  # 移除 "file://"
        return await asyncio.get_event_loop().run_in_executor(None, pathlib.Path(local_path).read_bytes)
    else:
        return await asyncio.get_event_loop().run_in_executor(None, pathlib.Path(url).read_bytes)
async def get_file_b64_from_url(url: str) -> str:
    """通用的文件base64编码获取函数，支持HTTP/HTTPS/file://协议和本地路径"""
    return base64.b64encode(await get_file_bytes_from_url(url)).decode("utf-8")
async def get_text_from_url(url: str) -> str:
    """从url异步获取文本内容"""
    import pathlib
    import httpx
    if url.startswith("http"):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.text
    else:
        return await asyncio.get_event_loop().run_in_executor(None, pathlib.Path(url).read_text)

def get_file_name(file_path: str) -> str:
    """从文件路径获取文件名，支持混合分隔符"""
    # 统一替换为正斜杠，然后提取最后一部分
    normalized = file_path.replace('\\', '/')
    filename = normalized.split('/')[-1]
    return filename if filename else file_path

def parse_modal_type_components(modal_type: str, file_path: str = "") -> tuple[str, str, dict[str, str]]:
    """
    解析modal_type字符串，提取类型、格式和参数，并自动标准化文件格式
    
    Args:
        modal_type: 模态类型字符串，如 "Video/mp4:fps=5,quality=high"
        file_path: 文件路径，用于从扩展名推测格式（如果modal_type中没有指定格式）
        
    Returns:
        tuple[str, str, dict[str, str]]: (基础类型, 标准化后的格式, 参数字典)
        例如: ("VIDEO", "jpeg", {"fps": 5, "start_offset": "10s", "end_offset": "1750s"}) - 注意jpg会被标准化为jpeg
    """
    # 分离参数部分
    if ':' in modal_type:
        type_format_part, params_part = modal_type.split(':', 1)
        # 解析参数
        params = {}
        for param in params_part.split(','):
            if '=' in param:
                key, value = param.split('=', 1)
                value = value.strip()
                if value.isdigit():
                    value = int(value)
                elif value.count(".") == 1 and value.replace(".","").isdigit() and not value.endswith(".") and not value.startswith("."):
                    value = float(value)
                params[key.strip()] = value
    else:
        type_format_part = modal_type
        params = {}
    
    # 分离类型和格式
    if '/' in type_format_part:
        base_type, file_format = type_format_part.split('/', 1)
        file_format = file_format.lower()
    else:
        base_type = type_format_part
        file_format = ""
    
    # 如果modal_type中没有格式信息，从文件路径推测
    if file_format == "" and file_path:
        file_format = file_path.split('.')[-1].lower() if '.' in file_path else ""
    
    # 标准化文件格式
    if file_format in ["jpg", "jpeg"]:
        file_format = "jpeg"
    elif file_format in ["wav", "wave"]:
        file_format = "wav"
    elif file_format in ["mp3", "mpeg"]:
        file_format = "mp3"
    
    return base_type.upper(), file_format, params

def get_file_size(file_bytes:bytes, return_formatted: bool = False) -> int | str:
    """
    获取文件字节数大小的辅助函数
    
    Args:
        file_path_or_bytes: 可以是文件路径字符串或bytes数据
        return_formatted: 是否返回格式化的字符串（如 "1.2 MB"）
        
    Returns:
        int: 字节数（如果return_formatted=False）
        str: 格式化的大小字符串（如果return_formatted=True）
    """
    size_bytes = len(file_bytes)
    
    if not return_formatted:
        return size_bytes
    
    # 格式化大小显示
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

async def extract_modals_from_openai_style_messages(messages:list[dict[str,str]]) -> list[list[dict[str,Any]]]:
    for message in messages:
        if message["role"] == "user":
            modals = extract_valid_modal_patterns(message["content"])
            multi_modal_content = [{"type":"text","text":message["content"]}]
            for modal in modals:
                splited_content = multi_modal_content.pop().get("text").split(modal[0],1)
                
                # 只有非空字符串才添加左半部分
                if splited_content[0]:
                    multi_modal_content.append({"type":"text","text":splited_content[0]})
                
                modal_type_upper,file_format,params = parse_modal_type_components(modal[1],modal[2])
                
                
                if modal_type_upper.startswith("TEXT"):
                    multi_modal_content.append({"type":"text","text":await get_text_from_url(modal[2])})
                elif modal_type_upper.startswith("IMAGE"):
                    multi_modal_content.append({"type":"image_url","image_url":{"url":f"data:image/{file_format};base64,{await get_file_b64_from_url(modal[2])}",**params}})
                elif modal_type_upper.startswith("AUDIO"):
                    # 使用OpenAI标准的input_audio格式
                    multi_modal_content.append({"type":"input_audio","input_audio":{"data":await get_file_b64_from_url(modal[2]),"format":file_format}})
                elif modal_type_upper.startswith("DOCS"):
                    multi_modal_content.append({"type":"file","file":{"file_data":await get_file_b64_from_url(modal[2]),"filename":get_file_name(modal[2])}})
                else:
                    multi_modal_content.append({"type":"text","text":f"{modal[0]}"})
                # 只有存在且非空的右半部分才添加
                if len(splited_content) > 1 and splited_content[1]:
                    multi_modal_content.append({"type":"text","text":splited_content[1]})
                    
            message["content"] = multi_modal_content
    return messages
async def upload_file_to_genai(file_path:str,genai_client:genai.Client)->genai_types.File:
    """
    异步上传文件到Gemini，支持智能等待处理
    
    Args:
        file_path: 文件路径
        genai_client: Gemini客户端
        auto_wait_for_processing: 是否自动等待视频文件处理完毕，默认True
    
    Returns:
        上传并处理完毕的文件对象
        
    Note:
        超时控制由上层BaseAgent的model_timeout机制统一管理
    """
    import functools
    # 使用functools.partial来正确传递关键字参数
    upload_func = functools.partial(genai_client.files.upload, file=file_path)
    # 在线程池中执行上传
    loop = asyncio.get_event_loop()
    uploaded_file = await loop.run_in_executor(None, upload_func)
    while uploaded_file.state.name == "PROCESSING":
        await asyncio.sleep(1.5)
        get_func = functools.partial(genai_client.files.get, name=uploaded_file.name)
        uploaded_file = await loop.run_in_executor(None, get_func)
    
    if uploaded_file.state.name == "FAILED":
        from .model_processor import ModelError
        error_code = 500
        error_message = f"文件处理失败: {file_path}"
        error_detail = f"文件状态: {uploaded_file.state.name}"
        if uploaded_file.error:
            if uploaded_file.error.code:
                error_code = uploaded_file.error.code
            if uploaded_file.error.message:
                error_message = f"文件处理失败: {uploaded_file.error.message}"
                error_detail = f"文件: {file_path}, 详情: {uploaded_file.error.message}"
                if uploaded_file.error.details:
                    error_detail += f", 额外信息: {uploaded_file.error.details}"
        raise ModelError(
            message=error_message,
            code=error_code,
            detail=error_detail
        )
    
    return uploaded_file
async def extract_modals_from_genai_messages(messages:list[genai_types.Content],genai_client:genai.Client)->list[list[dict[str,Any]]]:
    for message in messages:
        if message.role == "user":
            modals = extract_valid_modal_patterns(message.parts[0].text)
            multi_modal_content = [message.parts[0]]
            for modal in modals:
                splited_content = multi_modal_content.pop().text.split(modal[0],1)
                if splited_content[0]:
                    multi_modal_content.append(genai_types.Part(text=splited_content[0]))
                
                modal_type_upper,file_format,params = parse_modal_type_components(modal[1],modal[2])
                
                if modal_type_upper.startswith("TEXT"):
                    multi_modal_content.append(genai_types.Part(text=await get_text_from_url(modal[2])))
                elif modal_type_upper.startswith("VIDEO"):
                    custom_params = {}
                    if "https://www.youtube.com/watch?v=" in modal[2]: #走genai内置的youtube视频解析
                        multi_modal_content.append(genai_types.Part(file_data=genai_types.FileData(file_uri=modal[2]),video_metadata=genai_types.VideoMetadata(**params)))
                    else:
                        bytes_data = await get_file_bytes_from_url(modal[2])
                        if get_file_size(bytes_data) <= 1024 * 1024 * 15: #15MB
                            multi_modal_content.append(genai_types.Part(inline_data=genai_types.Blob(data=bytes_data,mime_type=f'video/{file_format}')))
                        else:
                            file = await upload_file_to_genai(modal[2], genai_client)
                            multi_modal_content.append(genai_types.Part(file_data=genai_types.FileData(file_uri=file.uri,mime_type=file.mime_type)))
                elif modal_type_upper.startswith("IMAGE") or modal_type_upper.startswith("AUDIO") or modal_type_upper.startswith("DOCS"):
                    mime_type_mappings = {
                        "IMAGE":"image",
                        "AUDIO":"audio",
                        "DOCS":"application",
                    }
                    bytes_data = await get_file_bytes_from_url(modal[2])
                    if get_file_size(bytes_data) <= 1024 * 1024 * 15: #15MB
                        multi_modal_content.append(genai_types.Part.from_bytes(data=bytes_data,mime_type=f'{mime_type_mappings[modal_type_upper]}/{file_format}'))
                    else:
                        file = await upload_file_to_genai(modal[2], genai_client)
                        multi_modal_content.append(genai_types.Part(file_data=genai_types.FileData(file_uri=file.uri,mime_type=file.mime_type)))
                else:
                    multi_modal_content.append(genai_types.Part(text=f"{modal[0]}"))
                if len(splited_content) > 1 and splited_content[1]:
                    multi_modal_content.append(genai_types.Part(text=splited_content[1]))
            message.parts = multi_modal_content
    return messages
def process_messages_to_openai_style(messages:str|dict[str,str])->list[dict[str, str]]:
    processed_messages = []
    has_any_effective_message = False
    if isinstance(messages, str):
        lines = messages.split("\n")
        for line in lines:
            if line.split(":")[0].strip().lstrip().lower() in ["system","developer"]:
                processed_messages.append({"role":"system","content":line.split(":",1)[1].strip().lstrip()})
            elif line.split(":")[0].strip().lstrip().lower() in ["user","user"]:
                processed_messages.append({"role":"user","content":line.split(":",1)[1].strip().lstrip()})
                has_any_effective_message = True
            elif line.split(":")[0].strip().lstrip().lower() in ["assistant","model"]:
                processed_messages.append({"role":"assistant","content":line.split(":",1)[1].strip().lstrip()})
                has_any_effective_message = True
            elif len(processed_messages) != 0:
                processed_messages[-1]["content"] += line.strip().lstrip()
            elif line.strip().lstrip():
                processed_messages.append({"role":"user","content":line.strip().lstrip()})
                has_any_effective_message = True
    elif isinstance(messages,dict):
        if "system" in messages:
            processed_messages.append({"role":"system","content":messages["system"]})
        if "user" in messages:
            processed_messages.append({"role":"user","content":messages["user"]})
            has_any_effective_message = True
    if not has_any_effective_message:
        processed_messages.append({"role":"user","content":"没有任何信息，请根据要求自主决策"})
    return processed_messages
def process_messages_to_genai_format(messages:str|dict[str,str])->tuple[str,list[genai_types.Content]]:
        processed_messages = process_messages_to_openai_style(messages)
        system_instruction = ""
        contents = []
        for message in processed_messages:
            if message['role'] == 'system':
                system_instruction += message['content']
            elif message['role'] == 'user':
                contents.append(genai_types.Content(
                    role="user",
                    parts=[genai_types.Part(text=message['content'])]
                ))
            elif message['role'] == 'assistant':
                contents.append(genai_types.Content(
                    role="model",
                    parts=[genai_types.Part(text=message['content'])]
                ))
        return system_instruction,contents
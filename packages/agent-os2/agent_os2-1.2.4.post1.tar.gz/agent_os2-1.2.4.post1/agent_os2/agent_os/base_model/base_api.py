import json
from typing import AsyncGenerator
import os

from .model_processor import BaseProcessor,DataPackage
from .processor_registry import PROCESSOR_TYPE_MAPPINGS
from .builtin_config import ModelConfig
# 获取平台配置
MODELS_SETTINGS_PATH = os.environ.get("AOS_MODEL_SETTINGS_PATH",os.path.join(os.getcwd(),"aos_config","model_settings.json"))
AVAILABLE_MODELS:dict[str,dict[str,str]] = {} #字典类型：{"processor_type":...,"proxy":...,"api_key":...,"api_url":...}
MODEL_INSTANCE:dict[str,BaseProcessor] = {}

def update_available_models(processor_type: str):
    """动态更新可用模型列表"""
    with open(MODELS_SETTINGS_PATH, "r") as f:
        settings = json.load(f)
    
    if processor_type not in settings:
        return
    
    model_config = settings[processor_type]
    config = {}
    
    for key,value in model_config.items():
        if key == "api_key":
            config["api_key"] = value
        elif key == "base_url":
            config["base_url"] = value
        elif key == "proxy":
            config["proxy"] = value
        elif key == "models":
            for t in value:
                if isinstance(t,str):
                    AVAILABLE_MODELS[t] = {**config,"processor_type":processor_type}
                elif isinstance(t,dict):
                    AVAILABLE_MODELS[t["model_name"]] = {"processor_type":processor_type,"proxy":t["proxy"],"api_key":t["api_key"],"base_url":t["base_url"]}
                else:
                    raise ValueError(f"不支持的配置类型，{value} 不是字符串或字典")

def get_available_models()->dict[str,dict[str,str]]:
    # 如果模型列表为空，尝试加载所有已注册的处理器的模型配置
    if not AVAILABLE_MODELS:
        for processor_type in PROCESSOR_TYPE_MAPPINGS:
            update_available_models(processor_type)
    return AVAILABLE_MODELS

def get_processor_instance(model_name:str)->tuple[BaseProcessor,str,str,str]:
    # 使用 get_available_models() 确保模型配置已加载
    available_models = get_available_models()
    
    config = available_models.get(model_name)
    if not config:
        raise ValueError(f"不支持的模型: {model_name}")
    
    processor_type = config["processor_type"]
    
    # 如果处理器实例不存在，则创建
    if processor_type not in MODEL_INSTANCE:
        if processor_type not in PROCESSOR_TYPE_MAPPINGS:
            raise ValueError(f"处理器类型 '{processor_type}' 未注册")
        MODEL_INSTANCE[processor_type] = PROCESSOR_TYPE_MAPPINGS[processor_type]()
    
    return (MODEL_INSTANCE[processor_type],config["proxy"],config["api_key"],config["base_url"])

async def interact_with_model(messages:dict[str,str]|list[dict[str,str]]|str,model_config:ModelConfig)->AsyncGenerator[DataPackage,None]:
    processor_instance,proxy,api_key,base_url = get_processor_instance(model_config.get_model_name())
    async for result in processor_instance.interact(messages,model_config,proxy,api_key,base_url):
        yield result
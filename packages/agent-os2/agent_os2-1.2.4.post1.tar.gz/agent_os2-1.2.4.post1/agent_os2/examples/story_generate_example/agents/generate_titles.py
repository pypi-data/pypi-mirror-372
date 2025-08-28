from agent_os2 import BaseAgent
from typing import Any
from random import randint

class GenerateTitlesAgent(BaseAgent):
    """生成标题Agent，根据用户输入生成多个故事标题"""
    
    def setup(self):
        self.user_info = f"## 智能体{self.alias}正在生成故事标题...\n"
        self.prompts = {
            "user": f"""
### Note:
1.根据以下用户输入，生成 {randint(5,10)} 个有趣的故事标题。
2.标题长度为 {randint(5,6)}~{randint(10,20)}字。你要一定要生成一个最长的与一个最短的，其它随意。
3.如果很短，你可以生成一个很短的语或充满哲学意义的词。
4.如果很长，你可以生成一个类似日本二次元轻小说那种很长的名字。

### Example:

Input:  帮我写个主题故事
Output:
{{{{
    "titles": [
    "时光之沙的秘密",
    "。。。",
    "。。。"
    ]
}}}}

### USER_INPUT
Input: {{src.user_input}}
Output:
""",
            "system": "你是一个创造性的标题生成器，负责根据用户输入生成有趣的故事标题。"
        }
        self.retry_count = 3
        self.batch_field = ""
        self.strict_mode = True  # 启用严格模式，自动解析JSON
    
    async def post_process(self, source_context:Any,llm_result: Any, shared_context: dict[str, Any],extra_contexts: dict[str, Any], observer: list[tuple[Any, BaseAgent]], batch_id: int | None = None) -> tuple[Any,dict[str,dict|list]]:
        """处理生成的标题结果"""
        # strict_mode已经帮我们解析成了字典
        if not isinstance(llm_result, dict):
            if self.is_debug:
                raise ValueError(f"生成标题Agent{self.alias}模型返回结果类型错误，输入参数：{source_context}，模型返回结果：{llm_result}")
            # 解析失败时返回默认标题
            return llm_result,{"actions":[{"cancel_next_steps":{}}]}
        
        titles = llm_result.get("titles", [])
        
        # 确保至少有一个标题
        if not titles:
            titles = ["未命名故事"]
        
        return {
            "titles": titles
        } ,{}
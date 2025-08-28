from agent_os2 import BaseAgent
from typing import Any

class WriteStoriesAgent(BaseAgent):
    """写故事Agent，支持批处理，根据标题生成故事内容"""
    def setup(self):
        self.batch_field = "src.titles"  # 设置批处理字段
        self.user_info = f"## 智能体{self.alias}正在写故事...\n"
        self.prompts = {
            "user": """
### Note:
1.根据故事标题撰写一个简短的故事。故事长度应为 {src.story_lengths[%batch_index%]} 字。
2.发挥你的想象力。要用写故事的方法论写，如起承转合，铺垫等。

### Example:

Input: 时光之沙的秘密
Output:
{{
  "story": "在一个遥远的沙漠小镇，住着一位名叫艾莎的老钟表匠......"
}}

### USER_INPUT
Input: {src.titles[%batch_index%]}
Output:
""",
            "system": "你是一个富有创造力的故事作家，负责根据给定的标题撰写故事。"
        }
        self.retry_count = 3
        self.strict_mode = True  # 启用严格模式，自动解析JSON
    
    async def post_process(self, source_context:Any,llm_result: Any, shared_context: dict[str, Any], extra_contexts: dict[str, Any], observer: list[tuple[Any, BaseAgent]], batch_id: int | None = None) -> tuple[Any,dict[str,dict|list]]:
        """处理写故事的结果"""
        # strict_mode已经帮我们解析成了字典
        if not isinstance(llm_result, dict):
            if self.is_debug:
                raise ValueError(f"写故事Agent{self.alias}模型返回结果类型错误，输入参数：{source_context}，模型返回结果：{llm_result}")
            return {},{"actions":[{"cancel_next_steps":{}}]}
        story = llm_result.get("story", "")
        return {
            "stories": [story]
        },{}
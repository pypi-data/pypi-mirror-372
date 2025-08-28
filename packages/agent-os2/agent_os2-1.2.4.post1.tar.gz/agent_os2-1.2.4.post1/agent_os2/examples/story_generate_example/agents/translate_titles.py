from agent_os2 import BaseAgent
from typing import Any

class TranslateTitlesAgent(BaseAgent):
    """翻译标题Agent，支持批处理，将标题翻译成多种语言"""
    
    def setup(self):
        self.batch_field = "src.titles"  # 设置批处理字段
        self.user_info = f"## 智能体{self.alias}正在翻译标题...\n"
        self.prompts = {
            "user": """
### Note:
1. 请将以下故事标题翻译成中文、英文和日语，并以JSON格式输出。

### Example:

Input: 时光之沙的秘密
Output:
{{
  "translations": {{
    "Chinese": "时光之沙的秘密",
    "English": "The Secret of Time's Sand",
    "Japanese": "時の砂の秘密"
  }}
}}

### USER_INPUT
Input: {src.titles[%batch_index%]}
Output:
""",
            "system": "你是一个专业的翻译专家，特别擅长文学作品标题的翻译，能够保持原作的意境和美感。你负责将故事标题翻译成中文、英文和日语。"
        }
        self.retry_count = 3
        self.strict_mode = True  # 启用严格模式，自动解析JSON
    
    async def post_process(self, source_context:Any,llm_result:Any,shared_context:dict[str,Any],extra_contexts:dict[str,Any],observer:list[tuple[Any,BaseAgent]],batch_id:int|None=None)->tuple[Any,dict[str,dict|list]]:
        """处理翻译结果"""
        if not isinstance(source_context, dict):
            if self.is_debug:
                raise ValueError(f"翻译标题Agent{self.alias}输入参数类型错误，输入参数：{source_context}")
            return {},{"actions":[{"cancel_next_steps":{}}]}
        translations = llm_result.get('translations', {})

        combined_translation = f"中文：{translations.get('Chinese', '')}\n" \
                               f"英文：{translations.get('English', '')}\n" \
                               f"日文：{translations.get('Japanese', '')}\n"
        return {
            "translated_story_titles": [combined_translation]
        },{}
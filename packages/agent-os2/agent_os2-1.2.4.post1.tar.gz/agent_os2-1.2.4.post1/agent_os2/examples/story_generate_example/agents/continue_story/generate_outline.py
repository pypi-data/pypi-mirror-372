from agent_os2 import BaseAgent
from typing import Any

class GenerateOutlineAgent(BaseAgent):
    """生成大纲Agent，根据章节总数生成每章的大纲"""
    
    def setup(self):
        self.user_info = f"## 智能体{self.alias}正在生成章节大纲...\n"
        self.prompts = {
            "user": """
请根据以下选定的故事标题生成一个详细的小说大纲：

【故事标题】
{ctx.best_story_title}

【翻译标题】
{ctx.best_story_title_translations}
【故事内容】
{ctx.best_story_content}

【大纲要求】
1. 总共{src.chapter_count}章的完整大纲
2. 每章要有明确的主题和情节发展
3. 整体故事要有起承转合的结构
4. 人物设定要清晰
5. 情节要有逻辑性和连贯性
6. 要有高潮和结局

请按以下格式生成大纲：

{{
  "character_settings": "【人物设定】\\n主角：...\\n配角：...",
  "story_background": "【故事背景】\\n...",
  "chapters": {{
    "1": {{"title": "第1章标题", "content": "第1章详细情节描述"}},
    "2": {{"title": "第2章标题", "content": "第2章详细情节描述"}},
    ...
    "{src.chapter_count}": {{"title": "第{src.chapter_count}章标题", "content": "第{src.chapter_count}章详细情节描述"}}
  }}
}}

请开始生成：
""",
            "system": "你是一个专业的小说策划师，负责根据选定的故事标题生成详细的小说大纲。"
        }
        self.retry_count = 3
        self.batch_field = ""
        self.strict_mode = True  # 启用严格模式，自动解析JSON
    
    async def parse_model_result(self,runtime_contexts:dict[str,Any],llm_result:Any,batch_id:int|None=None)->Any:
        """
        仅当self.strict_mode为True时有效
        将模型返回的字符串解析为json格式，并带有预处理机制和详细的错误提示
        子类可选择性重写。
        """
        parsed_result = await super().parse_model_result(runtime_contexts,llm_result,batch_id)
        if isinstance(parsed_result,dict):
            chapters = parsed_result.get("chapters",{})
            if len(chapters) != runtime_contexts.get("src",{}).get("chapter_count",1):
                raise ValueError(f"生成大纲Agent{self.alias}模型返回结果章节数与要求不符，要求：{runtime_contexts.get('src',{}).get('chapter_count',1)}章，实际：{len(chapters)}章")
        return parsed_result
    def adjust_prompt_after_failure(self, prompts: dict[str, str], error_text: str, hint: str) -> dict[str, str]:
        """
        仅当self.strict_mode为True时有效
        当模型输出错误或格式不符时，允许用户自定义提示词的调整逻辑。
        默认对 OpenAI 风格提示词进行最小调整：加入“请严格按照格式返回”提示。
        子类可以选择性重写。
        """
        return super().adjust_prompt_after_failure(prompts,error_text,hint = f"\n\n⚠️ 注意：你刚才的回答不符合格式要求，错误信息：\n{error_text}\n，请严格按照指定 JSON 格式和要求的章节数作答，避免返回无关内容导致解析失败。")
    async def post_process(self, source_context:Any,llm_result: dict[str, Any]|None, shared_context: dict[str, Any], extra_contexts: dict[str, Any], observer: list[tuple[Any, BaseAgent]], batch_id: int | None = None) -> tuple[Any,dict[str,dict|list]]:
        """处理生成的大纲，存入ctx"""
        # strict_mode已经帮我们解析成了字典
        if not isinstance(llm_result, dict) or not isinstance(source_context, dict):
            if self.is_debug:
                raise ValueError(f"生成大纲Agent{self.alias}模型返回结果类型错误，输入参数：{source_context}，模型返回结果：{llm_result}")
            return {},{"actions":[{"cancel_next_steps":{}}]}
        return {},{
                "memory_modify":{
                    "total_chapters":source_context.get("chapter_count",1),
                    "story_background":llm_result.get("story_background",""),
                    "character_settings":llm_result.get("character_settings",""),
                    "chapters":llm_result.get("chapters",{})
                }
        }
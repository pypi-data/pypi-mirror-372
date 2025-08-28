from agent_os2 import BaseAgent
from typing import Any

class SelectBestStoryAgent(BaseAgent):
    """选择最佳故事Agent，综合故事和翻译结果，选择最佳故事"""
    
    def setup(self):
        self.user_info = f"## 智能体{self.alias}正在评估和选择最佳故事...\n"
        self.prompts = {
            "user": """
            ### Note:
1.如下是多个故事，请选择其中最好的一个。（标题和翻译标题和故事一一对应）

### Example:
Input: 
    stories: [
        "故事内容1",
        "故事内容2",
        "故事内容3"
    ],
    translated_story_titles: [
        "故事标题1",
        "故事标题2",
        "故事标题3"
    ],
    titles: [
        "故事标题1",
        "故事标题2",
        "故事标题3"
    ]
Output:
{{

  "best_story_title": "云端城市的守护者",
  "best_story_title_translations": "中文：云端城市的守护者\n英文：The Guardian of the Cloud City\n日文：クラウドシティの守護者s",
  "reason": "..."
  "best_story_content":"故事内容详细升华版"
}}

### USER_INPUT
Input: stories: {src.stories},translated_story_titles: {src.translated_story_titles},titles: {ctx.titles}
Output: 
""",
            "system": "你是一个助手，负责从多个故事中选择最佳的一个。"
        }
        self.retry_count = 3
        self.batch_field = ""
        self.strict_mode = True  # 启用严格模式，自动解析JSON
    
    async def post_process(self, source_context:Any,llm_result:Any,shared_context:dict[str,Any],extra_contexts:dict[str,Any],observer:list[tuple[Any,BaseAgent]],batch_id:int|None=None)->tuple[Any,dict[str,dict|list]]:
        """处理选择结果"""
        # strict_mode已经帮我们解析成了字典
        if not isinstance(llm_result, dict):
            if self.is_debug:
                raise ValueError(f"选择最佳故事Agent{self.alias}模型返回结果类型错误，输入参数：{source_context}，模型返回结果：{llm_result}")
            return {
                "best_story_title": "未选择最佳故事",
                "best_story_title_translations": "中文：未选择最佳故事\n英文：No best story selected\n日文：最良の物語が選択されていません",
                "reason": "JSON解析失败",
                "best_story_content": "未选择最佳故事"
            }, {}
        
        best_story_title = llm_result.get("best_story_title", "")
        reason = llm_result.get("reason", "")
        best_story_content = llm_result.get("best_story_content", "")
        best_story_title_translations = llm_result.get("best_story_title_translations", "")
        return {
        },{
            "memory_modify": {
                "best_story_title": best_story_title,
                "best_story_title_translations": best_story_title_translations,
                "reason": reason,
                "best_story_content": best_story_content,
                "completed_chapters": []  # 初始化章节列表
            },
            "actions":[
                {
                    "add_branch":{
                        "name":"continue_story_flow"
                        # continue_story_flow 会自动继承需要的键
                    }
                }
            ]
        }
from agent_os2 import BaseAgent
from typing import Any

class WaitInputAgent(BaseAgent):
    """等待输入Agent，用于获取用户输入的章节总数"""
    
    def setup(self):
        self.user_info = f"## 智能体{self.alias}正在等待用户输入...\n"
        # 不设置prompts，因为不需要调用LLM
        self.prompts = {}
        self.retry_count = 0
        self.batch_field = ""
        self.strict_mode = False
    
    async def post_process(self, source_context:Any,llm_result:Any,shared_context:dict[str,Any],extra_contexts:dict[str,Any],observer:list[tuple[Any,BaseAgent]],batch_id:int|None=None)->tuple[Any,dict[str,dict|list]]:
        """获取用户输入的章节总数"""
        # 不调用模型时，result就是self.args
        # 使用stdin获取用户输入
        self.user_info = f"## 请输入您想要续写的章节总数：\n"
        
        # 调用stdin函数获取用户输入
        # stdin是在BaseAgent中定义的输入函数
        chapter_count_str = await self.get_input("请输入章节总数（例如：5）: ")
        chapter_count = int(chapter_count_str.strip())
        
        if chapter_count <= 0:
            chapter_count = 1
        return {
            "chapter_count": chapter_count
        },{}
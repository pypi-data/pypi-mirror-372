from agent_os2 import Flow
from agent_os2 import BaseAgent
from typing import Any
class ContinueStoryFlowAgent(Flow):
    """继续故事流程Agent，根据用户输入继续故事"""
    def __init__(self,name:str,parent:"BaseAgent|None"=None,**settings:dict[str,Any]):
        # 期望的上下文键 - 根据实际使用情况定义
        expected_shared_context_keys = {"best_story_title", "best_story_title_translations", "reason", 
                                       "best_story_content", "total_chapters", "completed_chapters"}
        super().__init__(name,parent,expected_shared_context_keys=expected_shared_context_keys,agents_key="continue_story_example",**settings)
        # 添加agent必须在构造函数中，setup之前。
        self.add_agent(
            #只有出现重复的agent时，才需要显式指定别名
            "wait_input"
        )
        self.add_agent(
            "generate_outline"
        )
        self.add_agent(
            "generate_chapter",
        )

        self.add_edge("wait_input","generate_outline")
        self.add_edge("generate_outline","generate_chapter")

if __name__ == "__main__":
    print(ContinueStoryFlowAgent("test"))
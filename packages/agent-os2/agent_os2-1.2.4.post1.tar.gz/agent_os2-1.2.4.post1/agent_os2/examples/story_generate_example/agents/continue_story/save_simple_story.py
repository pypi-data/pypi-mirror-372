from agent_os2 import BaseAgent
from typing import Any
class SaveSimpleStoryAgent(BaseAgent):
    """保存简单故事Agent，将故事保存为txt文件"""
    
    def setup(self):
        #不调用模型
        self.prompts = {}
    async def apply_command(self, agent_command: dict[str, Any], source_context: Any, shared_context: dict[str, Any], extra_contexts: dict[str, Any]):
        await super().apply_command(agent_command, source_context, shared_context, extra_contexts)
        if "save_story" in agent_command:
            with open(agent_command["save_story"]["save_path"],"w",encoding="utf-8") as f:
                f.write(agent_command["save_story"]["content"])
    async def post_process(self, source_context:Any,llm_result:Any,shared_context:dict[str,Any],extra_contexts:dict[str,Any],observer:list[tuple[Any,BaseAgent]],batch_id:int|None=None)->tuple[Any,dict[str,dict|list]]:
        content = ""
        content += f"# {shared_context.get('best_story_title','').replace(' ','_')}\n"
        content += f"## 翻译标题：\n{shared_context.get('best_story_title_translations','').replace(' ','_')}\n"
        content += f"## 选择该故事的理由：\n{shared_context.get('reason','').replace(' ','_')}\n"
        content += f"## 序幕：\n{shared_context.get('best_story_content','').replace(' ','_')}\n"
        totoal_chapters = shared_context.get("total_chapters",1)
        for i in range(1,totoal_chapters+1):
            chapter_content = shared_context.get(f"chapter_{i}","").strip()
            if chapter_content:
                content += f"### 第{i}章\n{chapter_content}\n"
        command = {"save_story":{"save_path":f"memory/{shared_context.get('best_story_title','').replace(' ','_')}.md","content":content}}
        return content,{}
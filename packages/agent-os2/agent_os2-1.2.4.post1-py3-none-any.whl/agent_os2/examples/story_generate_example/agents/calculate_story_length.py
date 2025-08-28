from agent_os2 import BaseAgent
from typing import Any

class CalculateStoryLengthAgent(BaseAgent):
    def setup(self):
        self.user_info = f"## 智能体{self.alias}正在计算故事长度...\n"
        self.prompts = {}
    def calculate_title_length_range(self,titles:list[str])->tuple[int,int]:
        lengths = [len(title) for title in titles]
        return min(lengths), max(lengths)

    def map_title_length_to_story_length(self, title_length, min_title_length, max_title_length, min_story_length, max_story_length):
        if min_title_length == max_title_length:
            return 300  
        else:
            story_length = max_story_length - (
                (title_length - min_title_length) / (max_title_length - min_title_length)
            ) * (max_story_length - min_story_length)
            return int(story_length)

    async def post_process(self,source_context:Any,llm_result:Any,shared_context:dict[str,Any],extra_contexts:dict[str,Any],observer:list[tuple[Any,BaseAgent]],batch_id:int|None=None)->tuple[Any,dict[str,dict|list]]:
        if not isinstance(source_context, dict):
            if self.is_debug:
                raise ValueError(f"计算故事长度Agent{self.alias}输入参数类型错误，输入参数：{source_context}")
            return {},{"actions":[{"cancel_next_steps":{}}]}
        titles = source_context.get("titles", [])
        min_title_length, max_title_length = self.calculate_title_length_range(titles)
        min_story_length = 100
        max_story_length = 500
        story_lengths = [self.map_title_length_to_story_length(len(title), min_title_length, max_title_length, min_story_length, max_story_length) for title in titles]
        return {
            "story_lengths": story_lengths,
            "titles":titles
        },{}

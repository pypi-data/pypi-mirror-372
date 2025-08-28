from asyncio.tasks import Task
from typing import Any
from agent_os2 import BaseAgent
class UserInputGetAgent(BaseAgent):
    def setup(self):
        self.user_info = "正在获取用户输入"
        self.prompts = ""
    async def post_process(self, source_context: Any, model_result: Any | None, shared_context: dict[str, Any], extra_contexts: dict[str, Any], observer: list[tuple[Task[tuple[Any, bool]], BaseAgent]], batch_id: int | None = None) -> tuple[Any, dict[str, dict | list]]:
        prompt = self.settings.get("user_input_prompt","")
        user_input = await self.get_input(f"{prompt}\n",batch_id)
        return {},{"memory_append":{"chat_history":"User:"+user_input+"\n"},"actions":[{"insert":{"name":"request_analysis"}}]}
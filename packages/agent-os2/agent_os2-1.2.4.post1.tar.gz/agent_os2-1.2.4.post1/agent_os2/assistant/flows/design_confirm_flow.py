__package__ = "agent_os2.assistant.flows"
from agent_os2 import Flow,BaseAgent,execute_with_visualization
from .orchestrator_flow import OrchestratorFlow
import asyncio
def custom_output_processor(agent_uid,batch_id,info,tag):
    if tag == "response":
        print(f"模型回答:\n{info}",end="")
    if tag == "launch_tips":
        print(info,end="")
class DesignConfirmFlow(Flow):
    shared_context_keys = {"user_request","design_thinking","agents_design","flows_design","key_features","context_orchestration_design","chat_history"}
    def __init__(self,name:str,parent:BaseAgent|None=None,**settings):
        super().__init__(name,parent,agents_key="assistant/design_confirm",expected_shared_context_keys=self.shared_context_keys,stdout=custom_output_processor,**settings)
        self.add_agent("request_analysis")
async def main():
    result = await execute_with_visualization(OrchestratorFlow(guider_agent_name="design_confirm_flow",agents_key="assistant"),shared_context={"events":{"confirm_design":["design_confirm_flow"]}})
    print(result)
if __name__ == "__main__":
    asyncio.run(main())
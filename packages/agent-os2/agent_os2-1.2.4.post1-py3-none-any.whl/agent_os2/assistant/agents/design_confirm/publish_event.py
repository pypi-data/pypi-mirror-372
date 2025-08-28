from agent_os2 import BaseAgent
class PublishEventAgent(BaseAgent):
    def setup(self):
        self.prompts = ""
        self.user_info = ""
    async def post_process(self,source_context,model_result,shared_context,extra_contexts,observer,batch_id=None):
        return {"publish":["extract_need_feature_details"],"request_analysis":{"user_request":shared_context.get("user_request",""),"agents_design":shared_context.get("agents_design",{}),"flows_design":shared_context.get("flows_design",{}),"key_features":shared_context.get("key_features",[]),"context_orchestration_design":shared_context.get("context_orchestration_design","")}},{}
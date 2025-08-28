__package__ = "agent_os2.assistant.agents.design_confirm"
from agent_os2 import BaseAgent,Gemini25Flash,record_user_info
from typing import Any
import asyncio
from ...prompts.roles import DESIGN_CONFIRM_PROMPT
class RequestAnalysisAgent(BaseAgent):
    def setup(self):
        self.prompts = DESIGN_CONFIRM_PROMPT
        self.user_info = "正在设计流程..."
        self.model_config = Gemini25Flash()
        self.strict_mode = True
    async def parse_model_result(self, runtime_contexts: dict[str, Any], model_result: Any, batch_id: int | None = None) -> Any:
        parsed = await super().parse_model_result(runtime_contexts, model_result, batch_id)
        if "response" not in parsed:
            raise ValueError("RequestAnalysisAgent的模型结果必须包含response字段")
        if "next_step" not in parsed and parsed["next_step"] not in ["input","done"]:
            raise ValueError("RequestAnalysisAgent的模型结果必须包含next_step字段，且值为input或done")
        if "agents_design" in parsed and not isinstance(parsed["agents_design"],dict):
            raise ValueError("RequestAnalysisAgent的模型结果中的agents_design字段必须为字典")
        if "flows_design" in parsed and not isinstance(parsed["flows_design"],dict):
            raise ValueError("RequestAnalysisAgent的模型结果中的flows_design字段必须为字典")
        if "key_features" in parsed and not isinstance(parsed["key_features"],list):
            raise ValueError("RequestAnalysisAgent的模型结果中的key_features字段必须为列表")
        return parsed
    async def post_process(self,source_context:Any,model_result:Any|None,shared_context:dict[str,Any],extra_contexts:dict[str,Any],observer:list[tuple[asyncio.Task[tuple[Any,bool]],"BaseAgent"]],batch_id:int|None=None)->tuple[Any,dict[str,dict|list]]:
        command = {}
        if not isinstance(model_result,dict):
            self.debug("RequestAnalysisAgent的模型结果类型错误",batch_id)
            return {},{}
        record_user_info(self,f"{model_result['response']}\n",batch_id,"response")
        command["memory_append"] = {"chat_history":"Model:"+model_result.pop("response")+"\n"} #添加模型回答到对话历史
        command["memory_modify"] = {}
        #根据模型结果决定下一步操作
        step = model_result["next_step"]
        actions = [{"insert":{"name":"publish_event"}}]
        if step == "input":
            actions = [{"insert":{"name":"user_input_get","settings":{"user_input_prompt":"请与模型确认当前方案:"}}}]
        command["actions"] = actions
        #可选参数更新
        #memory_modify能够借助None删除对应的字典键，post_process避免直接处理副作用
        if "delete_features" in model_result:
            command["memory_modify"]["key_features"] = [feature for feature in shared_context.get("key_features",[]) if feature not in model_result["delete_features"]]
        if "delete_agents" in model_result:
            command["memory_modify"]["agents_design"] = {agent:None for agent in model_result["delete_agents"]}
        if "delete_flows" in model_result:
            command["memory_modify"]["flows_design"] = {flow:None for flow in model_result["delete_flows"]}
        if "user_request" in model_result:
            command["memory_modify"]["user_request"] = model_result["user_request"]
        if "design_thinking" in model_result:
            command["memory_modify"]["design_thinking"] = model_result["design_thinking"]
        if "agents_design" in model_result:
            command["memory_modify"]["agents_design"] = model_result["agents_design"]
        if "flows_design" in model_result:
            command["memory_modify"]["flows_design"] = model_result["flows_design"]
        if "key_features" in model_result:
            command["memory_append"]["key_features"] = model_result["key_features"] #列表需要用**追加优先**模式
        if "context_orchestration_design" in model_result:
            command["memory_modify"]["context_orchestration_design"] = model_result["context_orchestration_design"]
        # #将直接的副作用放到post_process的最后处理，避免副作用影响
        # if "delete_features" in model_result:
        #     shared_context["key_features"] = [feature for feature in shared_context.get("key_features",[]) if feature not in model_result["delete_features"]]
        # if "delete_agents" in model_result:
        #     shared_context["agents_design"] = {agent:design for agent,design in shared_context.get("agents_design",{}).items() if agent not in model_result["delete_agents"]}
        # if "delete_flows" in model_result:
        #     shared_context["flows_design"] = {flow:design for flow,design in shared_context.get("flows_design",{}).items() if flow not in model_result["delete_flows"]}
        return {},command
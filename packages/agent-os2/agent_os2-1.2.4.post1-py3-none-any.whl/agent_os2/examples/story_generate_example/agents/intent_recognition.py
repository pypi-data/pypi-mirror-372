from agent_os2 import BaseAgent
from typing import Any

class IntentRecognitionAgent(BaseAgent):
    """意图识别Agent，特化用于判断用户输入是故事生成请求还是一般对话"""
    
    def setup(self):
        self.user_info = f"## 智能体{self.alias}正在分析用户意图...\n"
        self.prompts = {
            "user": """
### Note:
1.Analyze the following user input and determine which task it corresponds to. Only reply with the task name.
2.Available tasks: story, general_response

### Example:

Input: 帮我写个主题故事
Output: {{
    "intent": "story",
    "topic": ""
}}

Input: 今天天气怎么样？
Output: {{
    "intent":"general_response",
    "response":"The weather is sunny today."
}}

Input: 我想听一个关于冒险的故事
Output: {{
    "intent":"story",
    "topic":"adventure"
}}

Input: 你能帮我计算一下50乘以75是多少吗？
Output: {{
    "intent":"general_response",
    "response":"The result is 3750."
}}

### USER_INPUT
Input: {ctx.user_input}
Output: 
""",
            "system": "You are an artificial intelligence assistant tasked with analyzing user input to determine their intent. Your job is to map the user's request to one of our predefined tasks and output the appropriate task name."
        }
        self.retry_count = 3
        self.batch_field = ""
        self.strict_mode = True  # 启用严格模式，自动解析JSON
    
    async def post_process(self,source_context:Any,model_result:Any,shared_context:dict[str,Any],extra_contexts:dict[str,Any],observer:list[tuple[Any,"BaseAgent"]],batch_id:int|None=None)->tuple[Any,dict[str,dict|list]]:
        """处理意图识别结果，根据识别结果决定流程走向"""
        # strict_mode已经帮我们解析成了字典
        if not isinstance(model_result, dict):
            if self.is_debug:
                raise ValueError(f"意图识别Agent{self.alias}模型返回结果类型错误，输入参数：{source_context}，模型返回结果：{model_result}")
            # 如果不是字典，说明解析失败，返回一般对话
            return model_result, {"actions":[{"cancel_next_steps":{}}]}
        
        intent = model_result.get("intent", "general_response")
        
        # 根据识别结果设置不同的流程控制
        if intent == "story":
            # 故事生成流程 - 继续执行后续的write_stories_flow
            result_data = {"user_input": shared_context.get("user_input", "")}  # 传递给下游
            command_data = {
                "actions": [{"add_branch": {"dsl": 
f"""
story_generation_flow:
    agents:
        generate_titles:
            name: generate_titles

        calculate_story_length:
            name: calculate_story_length
        
        write_stories:
            name: write_stories
        
        translate_titles:
            name: translate_titles
        
        select_best_story:
            name: select_best_story
    
    edges:
        - generate_titles -> calculate_story_length
        - generate_titles -> translate_titles
        - calculate_story_length -> write_stories
        - write_stories -> select_best_story
        - translate_titles -> select_best_story
    entry_agent: generate_titles
"""
            }}]}
            return result_data, command_data
        else:
            # 一般对话流程 - 返回响应并取消后续步骤
            response = model_result.get("response", str(model_result))
            return response, {"actions":[{"cancel_next_steps":{}}]}
async def main():
    from agent_os2 import execute_with_visualization,Flow
    user_input = input("请问你需要什么帮助？")
    main_flow = Flow("main_flow",agents_key="story_generation_example",expected_shared_context_keys={"user_input"},is_debug=True)
    main_flow.add_agent("intent_recognition")
    result = await execute_with_visualization(main_flow, shared_context={"user_input": user_input})
    print(result)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
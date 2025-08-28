async def start_story_generate(user_input:str):
    from agent_os2 import execute_with_visualization,Flow
    main_flow = Flow("main_flow",agents_key="story_generation_example",expected_shared_context_keys={"user_input"},is_debug=True)
    main_flow.add_agent("intent_recognition")
    return await execute_with_visualization(main_flow, shared_context={"user_input": user_input})
from .flows.continue_story_flow import ContinueStoryFlowAgent
__all__ = ["start_story_generate","ContinueStoryFlowAgent"]
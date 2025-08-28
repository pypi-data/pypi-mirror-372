__package__ = "agent_os2.agent_os"
from .utility import modify_graph, update_shared_context, inherit_settings,record_user_info,get_context_value,merge_elements,parse_multi_string_context_embed,log_debug_info,parse_str_to_json_with_preprocess,format_debug_context,generate_log_dir,add_context_to_extra_contexts
from .base_model.builtin_config import ModelConfig
from uuid import uuid4 as random_uuid, UUID
from typing import Any,Callable
import asyncio
class BaseAgent:
    alias:str
    uuid:UUID
    settings:dict[str,Any]
    is_debug:bool
    debug_cache:dict[int,str]
    debug_context:bool
    usage:dict[str,Any]
    stdout:Callable[[str,int|None,Any,str|None],None]
    stdin:Callable[[str],Any]
    parent:"BaseAgent|None"
    start_count:int
    source_context_collector:Any
    previous:set["BaseAgent"]
    after:set["BaseAgent"]
    prompts:str|dict[str,str]|None #根据处理器不同，传不同的提示词模板
    model_config:ModelConfig
    strict_mode:bool
    retry_count:int
    batch_field:str
    user_info:str
    model_timeout:int
    def __init__(self,alias:str|None=None,parent:"BaseAgent|None"=None,**settings:dict[str,Any]):
        self.alias = alias or self.__class__.__name__[:-5]
        self.uuid = random_uuid()  # 先生成uuid，因为log_dir可能需要用到
        self.settings = settings
        if parent:
            inherit_settings(parent.settings,self.settings)
        self.settings["log_dir"] = generate_log_dir(self)
        self.is_debug = self.settings.get("is_debug",True)
        self.debug_cache = {}
        self.debug_context = self.settings.get("debug_context",False)
        self.usage = {}
        self.stdout = self.settings.get("stdout",lambda agent_uid,batch_id,info,tag:print(info,end=""))
        self.stdin = self.settings.get("stdin",input)
        self.start_count = 0
        self.parent = parent
        self.source_context_collector = None
        self.previous = set()
        self.after = set()
        self.prompts = {}
        self.model_config = ModelConfig.get_model_config(self.settings.get("model_config",{"model_name":"gemini-2.5-flash","is_stream":True}))
        self.strict_mode = False
        self.retry_count = 3
        self.batch_field = ""
        self.user_info = ""
        self.model_timeout = 60
    def __start__(self,*,src:"BaseAgent|None",source_context:Any,shared_context:dict[str,Any],
    current_queue:asyncio.Queue[tuple[asyncio.Task[tuple[Any,bool]],"BaseAgent"]]|None=None,observer:list[tuple[asyncio.Task[tuple[Any,bool]],"BaseAgent"]]|None=None,concurrent_limit:asyncio.Semaphore|None=None,**extra_contexts)->asyncio.Task[tuple[Any,bool]]|None:
        if observer is None:
            observer = []
        if current_queue is None:
            current_queue = asyncio.Queue()
        if self.start_count == -1:
            raise RuntimeError(f"Agent {self.alias} {self.uuid} 已经被执行过")
        self.source_context_collector = self.merge_source_context(source_context)
        self.start_count += 1
        if self.start_count >= len(self.previous):
            return asyncio.create_task(self._create_execution_task(shared_context,extra_contexts,current_queue,observer,concurrent_limit))
        return None
    async def _create_execution_task(self,shared_context:dict[str,Any],extra_contexts:dict[str,Any],current_queue:asyncio.Queue[tuple[asyncio.Task[tuple[Any,bool]],"BaseAgent"]],observer:list[tuple[asyncio.Task[tuple[Any,bool]],"BaseAgent"]],concurrent_limit:asyncio.Semaphore|None=None)->tuple[dict[str,Any],bool]:
        if concurrent_limit is None:
            return await self.__execute__(self.source_context_collector,shared_context,extra_contexts,current_queue,observer,concurrent_limit),len(self.after) == 0
        else:
            async with concurrent_limit:
                return await self.__execute__(self.source_context_collector,shared_context,extra_contexts,current_queue,observer,concurrent_limit),len(self.after) == 0
    async def _run_body_wrapper(self,source_context:Any,shared_context:dict[str,Any],extra_contexts:dict[str,Any],observer:list[tuple[asyncio.Task[tuple[Any,bool]],"BaseAgent"]],concurrent_limit:asyncio.Semaphore|None=None,batch_id:int|None=None)->Any:
        if concurrent_limit is None:
            return await self._run_agent_pipeline(source_context,shared_context,extra_contexts,observer,batch_id)
        else:
            async with concurrent_limit:
                return await self._run_agent_pipeline(source_context,shared_context,extra_contexts,observer,batch_id)
    async def __execute__(self,source_context:Any,shared_context:dict[str,Any],extra_contexts:dict[str,Any],current_queue:asyncio.Queue[tuple[asyncio.Task[tuple[Any,bool]],"BaseAgent"]],observer:list[tuple[asyncio.Task[tuple[Any,bool]],"BaseAgent"]],concurrent_limit:asyncio.Semaphore|None=None)->tuple[dict[str,Any],bool]:
        self.start_count = -1
        self.setup()
        result = None
        if self.batch_field:
            actual_batch_content = await self.get_context_value(self.batch_field,{**extra_contexts, "src": source_context, "ctx": shared_context})
            if isinstance(actual_batch_content,list):
                gather_tasks = []
                for batch_id in range(len(actual_batch_content)):
                    gather_tasks.append(self._run_body_wrapper(source_context,shared_context,extra_contexts,observer,concurrent_limit,batch_id))
                results = await asyncio.gather(*gather_tasks)
                for chunk in results:
                    result = merge_elements(result,chunk,append_priority=True)
            else:
                raise ValueError(f"批处理字段{self.batch_field}的值不是列表，而是{type(actual_batch_content)}")
        else:
            result = await self._run_agent_pipeline(source_context,shared_context,extra_contexts,observer)     
        for agent in self.after:
            if (
                task := agent.__start__(src=self,source_context=result,shared_context=shared_context,current_queue=current_queue,observer=observer,concurrent_limit=concurrent_limit,**extra_contexts)
            ) is not None:
                await current_queue.put((task,agent))
                observer.append((task,agent))
        return result
    async def _run_agent_pipeline(self,source_context:Any,shared_context:dict[str,Any],extra_contexts:dict[str,Any],observer:list[tuple[asyncio.Task[tuple[Any,bool]],"BaseAgent"]],batch_id:int|None = None)->Any:
        record_user_info(self,f"## 🚀 **{self.alias}** 启动\n",batch_id)
        record_user_info(self,f"{self.user_info}\n",batch_id,tag="launch_tips")
        
        if batch_id is not None:
            self.debug(f"\n## Agent {self.alias} {self.uuid} [批处理id:{batch_id}]调试信息：",batch_id)
        else:
            self.debug(f"\n## Agent {self.alias} {self.uuid} 调试信息：",batch_id)
            
        try:
            runtime_contexts = {**extra_contexts, "src": source_context, "ctx": shared_context}
            prompts = await parse_multi_string_context_embed(self.prompts, runtime_contexts, self.get_context_value, "", batch_id) if self.prompts else None
            from datetime import datetime
            self.debug(f"### 调用时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",batch_id)
            self.debug(format_debug_context(source_context, not self.debug_context, "获得的上游参数"),batch_id)
            self.debug(format_debug_context(shared_context, not self.debug_context, "共享内存中的上下文"),batch_id)
            self.debug(format_debug_context(extra_contexts, not self.debug_context, "额外上下文"),batch_id)
            llm_result = None
            if prompts:
                self.debug(f"### 该Agent调用模型，模型配置为：\n```\n{self.model_config}\n```",batch_id)
                self.debug(f"### 该Agent调用模型，模型初始提示词为：\n```\n{prompts}\n```",batch_id)
                record_user_info(self,f"⌛ 正在调用模型...\n",batch_id)
                llm_result, usage = await self._call_model(runtime_contexts,prompts,self.model_config,batch_id)
                self.usage = merge_elements(self.usage,usage,append_priority=True)
            else:
                self.debug(f"### 该Agent没有调用模型，没有llm_result。",batch_id)  
            final_result,agent_command = await self.post_process(source_context,llm_result,shared_context,extra_contexts,observer,batch_id)
            self.debug(f"### 该Agent向下游发送结果：\n```\n{final_result}\n```",batch_id)
            if agent_command:
                self.debug(f"### 该Agent返回了命令，将执行命令：\n```\n{agent_command}\n```",batch_id)
                await self.apply_command(agent_command,source_context,shared_context,extra_contexts)
            record_user_info(self,f"✅ **{self.alias}** 执行结束\n\n",batch_id)
            return final_result
        except Exception as e:
            # 简化后的错误提示
            record_user_info(self,f"❌ **{self.alias}** 执行失败\n\n",batch_id)
            self.debug(f"### 该Agent调用模型失败，错误信息：\n```\n{e}\n```",batch_id)
            raise e
        finally:
            if self.is_debug and "log_dir" in self.settings:
                log_debug_info(self.settings["log_dir"],self.debug_cache.get(batch_id or 0,""))
    async def _call_model(self,runtime_contexts:dict[str,Any],prompts:dict[str,str]|str,model_config:ModelConfig,batch_id:int|None=None)->tuple[Any,dict[str,Any]]:
        from .base_model.base_api import interact_with_model
        from .base_model.model_processor import StreamDataStatus
        
        result = None
        usage = {}
        retry_count = self.retry_count
        
        while retry_count > 0:
            logic_error = False
            error_data = None
            try:
                async with asyncio.timeout(self.model_timeout):
                    async for chunk in interact_with_model(prompts,model_config):
                        if chunk.get_status() == StreamDataStatus.GENERATING:
                            chunk_data = chunk.read_data()
                            # 简化后只显示：模型输出
                            record_user_info(self, str(chunk_data), batch_id,tag="model_stream")
                        elif chunk.get_status() == StreamDataStatus.COMPLETED:
                            result = chunk.read_data()
                            usage = merge_elements(usage,chunk.get_usage(),append_priority=True)
                            
                            # 格式化输出
                            record_user_info(self,"\n", batch_id,tag="model_stream")
                            
                            if self.strict_mode:
                                try:
                                    result = await self.parse_model_result(runtime_contexts,result,batch_id)
                                except Exception as e:
                                    logic_error = True
                                    error_data = {"error":str(e),"original_model_result":result}
                            
                            self.debug(f"### 该模型本次调用结果为：\n```\n{result}\n```",batch_id)
                            if usage:
                                self.debug(f"### 该模型本次调用消耗tokens：\n```\n{usage}\n```",batch_id)
                        elif chunk.get_status() == StreamDataStatus.ERROR:
                            error_data = chunk.read_data()
                            error_data = {"error":error_data}
            except asyncio.TimeoutError:
                error_data = {"error":f"模型调用超时，超时时间：{self.model_timeout}秒"}
            if error_data:
                retry_count -= 1
                if retry_count > 0:
                    if logic_error:
                        prompts = self.adjust_prompt_after_failure(prompts,error_text=error_data["error"],hint = f"⚠️ 注意：你刚才的回答不符合格式要求，错误信息：\n{error_data['error']}\n，请严格按照指定 JSON 格式作答，避免返回无关内容导致解析失败。")
                        self.debug(f"### 该Agent调用模型返回输出不符合要求，已调整提示词为：\n```\n{prompts}\n```\n错误信息：\n```\n{error_data}\n```\n，剩余重试次数：{retry_count}",batch_id)
                    else:
                        self.debug(f"### 该Agent调用模型返回输出不符合要求，剩余重试次数：{retry_count}，错误信息：\n```\n{error_data}\n```",batch_id)
                    await asyncio.sleep(1)  # 等待1秒后重试
                else:
                    self.debug(f"### 智能体{self.alias}调用模型失败，重试次数已用完。\n最后一次错误信息：\n{error_data}",batch_id)
                    if self.is_debug:
                        raise RuntimeError(f"debug_error:模型{self.alias} {self.uuid} 调用模型失败，error_data: {error_data}")
                    return None,usage
            else:
                break
        return result, usage
    async def get_input(self,prompt:str,batch_id:int|None=None)->str:
        """
        获取使用者输入，并记录到user_info中
        """
        record_user_info(self,prompt+"\n",batch_id,tag="input_prompt")
        return await asyncio.get_running_loop().run_in_executor(None, self.stdin, prompt)
    def debug(self,info:str,batch_id:int|None=None):
        self.debug_cache[batch_id or 0] = self.debug_cache.get(batch_id or 0,"") + info + "\n"
    async def parse_model_result(self,runtime_contexts:dict[str,Any],model_result:Any,batch_id:int|None=None)->Any:
        """
        仅当self.strict_mode为True时有效
        默认将模型返回的字符串解析为json格式，并带有预处理机制和详细的错误提示
        子类可选择性重写。
        """
        if not isinstance(model_result,str):
            return model_result
        return parse_str_to_json_with_preprocess(model_result)
    def adjust_prompt_after_failure(self, prompts: dict[str, str]|str, error_text: str, hint: str) -> dict[str, str]|str:
        """
        仅当self.strict_mode为True时有效
        当模型输出错误或格式不符时，允许用户自定义提示词的调整逻辑。
        默认对 OpenAI 风格提示词进行最小调整：加入“请严格按照格式返回”提示。
        子类可以选择性重写。
        """
        if isinstance(prompts,str):
            if prompts.startswith("system:"):
                prompts = prompts[:7] + hint + "\n" + prompts[7:]
            else:
                prompts = prompts + "\n" + hint
        elif isinstance(prompts,dict):
            prompts["system"] = hint + "\n" + prompts.get("system","")
        return prompts
    def merge_source_context(self,source_context:Any)->Any:
        """该agent面对多个上游agent输入时，合并参数的策略，子类可选择性重写"""
        return merge_elements(self.source_context_collector,source_context,append_priority=True)
    async def apply_command(self,agent_command:dict[str,Any],source_context:Any,shared_context:dict[str,Any],extra_contexts:dict[str,Any]):
        """
        执行agent_command中的命令，子类可重写扩展自定义命令处理
        默认实现：
        - update_shared_context(): 处理memory命令
        - modify_graph(): 处理actions命令
        """
        update_shared_context(agent_command.pop("memory",{}),shared_context) #向后兼容版本,警告⚠将在1.2.6版本之后删除
        update_shared_context(agent_command.pop("memory_modify",{}),shared_context)
        update_shared_context(agent_command.pop("memory_append",{}),shared_context,append_priority=True)
        if self.parent: #为了安全性必须在parent存在的前提下下动态修改图结构
            modify_graph(self,agent_command.pop("actions",[]),self.parent)
        add_context_to_extra_contexts(agent_command.pop("add_context",{}),extra_contexts)
    async def get_context_value(self,key:str,runtime_contexts:dict[str,Any],default:Any="")->Any:
        """
        根据key，获取ctx中的值,默认支持src和ctx两个上下文的获取
        子类可选择性重写
        """
        if key.startswith("src."):
            return get_context_value(runtime_contexts["src"],key[4:],default) #直接抛出KeyError是可以的，parse_smart_string_index发现source不存在会取消模板替换
        elif key.startswith("ctx."):
            return get_context_value(runtime_contexts["ctx"],key[4:],default)
    def __str__(self)->str:
        return f"{self.alias}"
    def setup(self):
        """
        Agent参数的初始化设置
        子类应该重写该方法，可以设置：
        - self.user_info: 用户可见的初始信息
        - self.is_debug: 是否启用调试模式
        - self.model_config: 模型配置(默认是Gemini25Flash的默认实现)
        - self.prompts: 模型提示词模板
        - self.retry_count: 重试次数
        - self.batch_field: 批处理字段
        - self.strict_mode: 是否启用严格模式
        - self.model_timeout: 模型调用超时时间，单位秒
        - self.context_debug: 是否启用上下文调试模式
        """
        self.prompts = {
        "user":"这是上游agent给你发送的消息:{src.message}，这是共享内存中对本次任务的介绍{ctx.intro}",
        "system":"你是一个在工作流中的智能体，请你根据提示要求，来严谨的完成任务。"
        }
        self.batch_field = "" #批处理开关，指向一个列表字段(如"src.items")。
        self.strict_mode = False #启用解析框架，联动自动重试
    async def post_process(self,source_context:Any,model_result:Any|None,shared_context:dict[str,Any],extra_contexts:dict[str,Any],observer:list[tuple[asyncio.Task[tuple[Any,bool]],"BaseAgent"]],batch_id:int|None=None)->tuple[Any,dict[str,dict|list]]:
        """
        对Agent的执行结果进行后续处理，子类应重写此方法以实现自定义业务逻辑。
        
        这是Agent中最重要的“副作用”出口，所有状态变更都应在此处集中处理。
        
        Returns:
            一个元组 (final_result, agent_command):
            - final_result (Any): 将传递给下游Agent的最终结果。
            - agent_command (dict): 发送给父Flow的命令，用于动态修改工作流。
                支持 `memory` (更新共享上下文) 和 `actions` (修改图结构) 和 `add_context` (注入新的接口对象) 等命令。
                详细用法请参阅 `DEVELOPING_GUIDE.md`。
        """
        return model_result,{}

if __name__ == "__main__":
    base_agent = BaseAgent(alias="test",parent=None)
    async def main():
        from .flow import execute
        print("\n\nresult:\n",await execute(base_agent,source_context={"message":"你好，我是张三。"},shared_context={"intro":"你的任务是要复述一遍你的任务和上游消息的内容。"}))
    asyncio.run(main())
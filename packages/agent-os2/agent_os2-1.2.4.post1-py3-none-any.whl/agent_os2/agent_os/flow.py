__package__ = "agent_os2.agent_os"
from .base_agent import BaseAgent
from typing import Any
import asyncio
from .utility import get_agents_classes,merge_elements
class Flow(BaseAgent):
    agents_key:str|None
    agents:dict[str,"BaseAgent"]
    entry_agent:"BaseAgent"
    agent_classes:dict[str,type["BaseAgent"]]
    expected_shared_context_keys:set[str]
    def __init__(self,name:str,parent:"BaseAgent|None"=None,*,agents_key:str|None=None,expected_shared_context_keys:set[str]=None,**settings:dict[str,Any]):
        super().__init__(name,parent,**settings)
        self.agents_key = agents_key if agents_key is not None else parent.agents_key if isinstance(parent,Flow) else None
        self.agents = {}
        self.entry_agent = None
        self.expected_shared_context_keys = expected_shared_context_keys or set()
        self.agent_classes = {}
    def merge_source_context(self, source_context: Any) -> Any:
        # 学习第一个agent合并source_context的策略
        return self.entry_agent.merge_source_context(source_context)
    def setup(self):
        self.user_info = f"工作流 **{self.alias}**"
        self.prompts = {}
    async def post_process(self,source_context:Any,llm_result:Any,shared_context:dict[str,Any],extra_contexts:dict[str,Any],observer:list[tuple[asyncio.Task[tuple[Any,bool]],"BaseAgent"]],batch_id:int|None=None)->tuple[Any,dict[str,dict|list]]:
        if self.entry_agent is None:
            raise ValueError("entry agent not found")
        flow_result = None
        task_queue:asyncio.Queue[tuple[asyncio.Task[tuple[dict[str,Any],bool]],"BaseAgent"]] = asyncio.Queue()
        internal_shared_context = {}
        for key in self.expected_shared_context_keys:
            if key in shared_context:
                internal_shared_context[key] = shared_context[key]
        task = self.entry_agent.__start__(
            src=None,source_context=source_context,shared_context=internal_shared_context,current_queue=task_queue,observer=observer,**extra_contexts
        )
        if task:
            observer.append((task,self.entry_agent))
            await task_queue.put((task,self.entry_agent))
        try:
            while not task_queue.empty():
                task,agent = await task_queue.get()
                ret,leaf = await task
                self.usage = merge_elements(self.usage,agent.usage,append_priority=True)
                for key,value in self.usage.items():
                    name = key[6:] if key.startswith("total_") else key
                    if self.settings.get(f"max_{name}_limit",None) is not None and value > self.settings.get(f"max_{name}_limit"):
                        raise RuntimeError(f"Flow {self.alias} 的{name}使用量超过限制，当前{name}使用量为{value}，限制为{self.settings.get(f'max_{name}_limit')}")
                if leaf and ret:
                    flow_result = ret
        finally:
            from .utility import log_flow_info
            log_flow_info(self,flow_result,internal_shared_context,self.usage)
        return flow_result,{}
    #绕过注册系统，直接添加agent
    def add_custom_agent_class(self,agent_type_name:str,agent_class:type["BaseAgent"]):
        self.agent_classes[agent_type_name] = agent_class #采用直接覆盖的方式
    #dsl部分
    def get_agent_class(self,agent_type_name:str)->type["BaseAgent"]:
        if agent_type_name not in self.agent_classes:
            self.agent_classes = merge_elements(self.agent_classes,get_agents_classes(self.agents_key))
        try:
            return self.agent_classes[agent_type_name]
        except KeyError:
            raise ValueError(f"Agent {agent_type_name} 未找到，请检查agent_settings.json是否正确将{agent_type_name}注册到{self.agents_key}中")
    def add_agent(self,agent_type_name:str,alias:str|None=None,**settings:dict[str,Any])->"BaseAgent":
        # 处理重复别名：dsl构建时，alias不能重复
        if alias is None:
            alias = agent_type_name
        if alias in self.agents:
                raise ValueError(f"Agent {alias} 别名重复，请换个别名")
        self.agents[alias] = self.get_agent_class(agent_type_name)(alias, parent=self, **settings)
        if self.entry_agent is None:
            self.entry_agent = self.agents[alias]
        return self.agents[alias]
    def add_edge(self,src_alias:str,*dest_aliases:str):
        src = self.agents[src_alias]
        for dest_alias in dest_aliases:
            dest = self.agents[dest_alias]
            src.after.add(dest)
            dest.previous.add(src)
    def remove_edge(self,src_alias:str,*dest_aliases:str):
        src = self.agents[src_alias]
        for dest_alias in dest_aliases:
            dest = self.agents[dest_alias]
            src.after.remove(dest)
            dest.previous.remove(src)
            if not dest.previous and dest.after:
                self.agents.pop(dest_alias)
        if not src.after and src.previous:
                self.agents.pop(src_alias)
    def entrance(self,agent_alias:str):
        agent = self.agents[agent_alias]
        if agent.previous:
            raise ValueError(f"Agent {agent_alias} 作为入口节点，不能有前置节点")
        self.entry_agent = agent
    @classmethod
    def construct_from_dsl(cls,dsl:str,parent:"BaseAgent|None"=None):
        """
        从dsl中构造flow
        """
        from .utility import parse_flow_dsl
        return parse_flow_dsl(cls,dsl,parent)
# 执行接口
# 统一的执行函数，支持一次性执行和持续追踪两种模式
async def execute(
    agent: "BaseAgent",
    *,
    source_context: Any | None = None,
    shared_context: dict[str,Any] | None = None,
    concurrent_limit: int | None = None,
    observer: list[tuple[asyncio.Task[tuple[Any,bool]],"BaseAgent"]] | None = None,
    **extra_ctxs #为RAG,KAG额外上下文等预留接口
) -> Any:
    if observer is not None:
        observer.append((agent.__start__(
            src=None,source_context=source_context or {},shared_context=shared_context or {},observer=observer,concurrent_limit= asyncio.Semaphore(concurrent_limit) if concurrent_limit else None,**extra_ctxs
        ),agent))  
        return observer
    else:
        rets, _ = await agent.__start__(
            src=None,source_context=source_context or {},shared_context=shared_context or {},observer=observer,concurrent_limit= asyncio.Semaphore(concurrent_limit) if concurrent_limit else None,**extra_ctxs
        )
        return rets
async def test():
    flow = Flow(name="test",expected_shared_context_keys={"intro"},is_debug=False)
    flow.add_agent("base",alias="a",is_debug=True)#单独对这个agent开启debug模式
    observer = []
    await execute(flow,source_context={"message":"我是张三"},concurrent_limit=1,observer=observer,shared_context={"intro":"这是一个测试"})
    while observer:
        for task,agent in observer:
            if task.done():
                observer.remove((task,agent))
                print(f"Agent {agent.alias} 执行完成，结果为：{(await task)[0]}")
            else:
                print(f"Agent {agent.alias} 执行中")
                await asyncio.sleep(1)
if __name__ == "__main__":
    asyncio.run(test())
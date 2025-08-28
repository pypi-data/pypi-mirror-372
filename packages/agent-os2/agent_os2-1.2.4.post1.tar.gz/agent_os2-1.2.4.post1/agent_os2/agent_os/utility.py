import os
import json
from typing import Any, Callable, TYPE_CHECKING, Awaitable
import re
if TYPE_CHECKING:
    from .base_agent import BaseAgent
    from .flow import Flow
# 日志记录
def generate_log_dir(agent:"BaseAgent")->str:
    """
    用于生成日志目录的函数，根据agent的uuid和parallel_id生成日志目录
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # 精确到秒
    return agent.settings.get("log_dir",os.path.join(os.getcwd(),"memory",
                                                     f"statistics_{timestamp}_{str(agent.uuid)[:4]}"))
def log_user_info(log_dir:str,agent_uid:str,info:str,tag:str|None=None):
    """
    用于记录用户信息的函数，将info添加到对应agent区块的末尾，并且处理默认特殊标记[model_stream]
    args:
        log_dir: 日志目录路径
        agent_uid: 当前agent的完整uid（包含uuid和parallel_id）
        info: 待添加的用户信息
    """
    file_path = os.path.join(log_dir,"user_info.md")
    os.makedirs(log_dir,exist_ok=True)
    # 读取现有内容
    content = ""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    
    # 查找对应的agent区块
    start_marker = f"<!--{agent_uid}-->"
    end_marker = f"<!--/{agent_uid}-->"
    
    start_pos = content.find(start_marker)
    if start_pos == -1:
        # 区块不存在，创建新区块
        content += f"\n{start_marker}\n{info}{end_marker}\n"
    else:
        # 区块存在，在结束标记前插入新内容
        end_pos = content.find(end_marker, start_pos)
        if end_pos != -1:
            content = content[:end_pos] + info + content[end_pos:]
        else:
            # 缺少结束标记，追加完整区块
            content += f"\n{start_marker}\n{info}{end_marker}\n"
    
    # 写回文件
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def log_debug_info(log_dir:str,info:str):
    """
    用于记录与agent相关的记录信息的函数
    args:
        log_dir: 日志目录路径
        info: 待添加记录的日志信息
    """
    file_path = os.path.join(log_dir,"debug_info.md")
    os.makedirs(log_dir,exist_ok=True)
    with open(file_path,"a+",encoding="utf-8") as f:
        f.write(info)
def log_flow_info(flow:"Flow",return_value:dict[str,Any],flow_context:dict[str,Any],usage:dict[str,Any]):
    """
    用于记录flow的执行结果的函数
    args:
        flow: 当前flow对象，用于确定日志文件的存储路径
        return_value: flow的返回值
        flow_context: flow的上下文字典
        usage: 使用量
    """
    if "log_dir" not in flow.settings:
        # 如果没有log_dir，说明这个flow没有正确初始化，跳过日志记录
        return
    flow_log_dir = os.path.join(flow.settings["log_dir"],"flow_result")
    os.makedirs(flow_log_dir,exist_ok=True)
    
    # 基于执行顺序的命名：直接统计现有文件数量+1
    try:
        existing_files = os.listdir(flow_log_dir)
        # 过滤出.json文件来统计
        counter = len([f for f in existing_files if f.endswith('.json')]) + 1
    except Exception:
        counter = 1
    file_path = os.path.join(flow_log_dir, f"{flow.alias}_{counter}.json")
    info = {
        "flow_name":flow.alias,
        "flow_uuid":str(flow.uuid),
        "return_value":return_value,
        "shared_context":flow_context,
        **usage
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=4, default=str)
# 合并settings
def inherit_settings(parent: dict[str,Any], child: dict[str,Any]) -> None:
    """
    用于合并settings的函数，如果parent和child的key相同，则child的value会覆盖parent的value
    """
    parent = parent
    child = child
    keys = child.keys()
    for key, val in parent.items():
        if key not in keys:
            child[key] = val
# 用户信息记录器
def record_user_info(agent:"BaseAgent",info:str,batch_id:int|None=None,tag:str|None=None):
    """
    用于记录用户信息的函数，直接输出信息而不累加
    args:
        agent: 当前agent对象
        info: 待输出的用户信息
        parallel_id: 并行任务的ID，如果不为None，会追加到agent_uid后面
    """
    # 从agent获取必要信息
    agent_uid = str(agent.uuid)
    out = agent.stdout
    
    # 构建完整的uid
    full_uid = agent_uid if batch_id is None else f"{agent_uid}_{batch_id}"
    
    out(agent_uid,batch_id,info,tag)
    
    # 只有在有log_dir设置时才记录日志
    if "log_dir" in agent.settings:
        log_user_info(agent.settings["log_dir"],full_uid,info,tag)
# 键值索引器
def get_context_value(source: dict[str,Any], path: str, default: Any = None) -> Any:
    """
    从嵌套数据结构中获取值，支持点号访问和列表索引
    
    args:
        source: 数据源
        path: 访问路径，如 "a.b.c" 或 "a[0].b" 或 "a.b[1].c"
        default: 默认值
    
    returns:
        获取到的值或默认值
    """
    current = source
    
    # 将匹配结果转换为访问步骤
    steps = []
    i = 0
    while i < len(path):
        if path[i] == '[':
            # 找到匹配的右括号
            j = i + 1
            while j < len(path) and path[j] != ']':
                j += 1
            if j < len(path):
                index_str = path[i+1:j]
                index = int(index_str)
                steps.append(('index', index))
                i = j + 1
            else:
                raise ValueError(f"未找到匹配的右括号: {path}")
        elif path[i] == '.':
            i += 1
        else:
            # 查找下一个点号或方括号
            j = i
            while j < len(path) and path[j] not in '.[]':
                j += 1
            if j > i:
                key = path[i:j]
                steps.append(('key', key))
                i = j
            else:
                i += 1
    
    # 逐步访问
    for step_type, step_value in steps:
        if step_type == 'key':
            if isinstance(current, dict):
                current = current.get(step_value, None)
                if current is None:
                    return default #不存在返回默认值
            else:
                return default
        elif step_type == 'index':
            if isinstance(current, (list, tuple)):
                try:
                    current = current[step_value]
                except IndexError:
                    return default #超出索引返回默认值
            else:
                return default
    return current
# 递归式字典/列表自动给合并更新策略
def merge_elements(
    element1: Any,
    element2: Any,
    max_depth: int = 10,
    append_priority: bool = False
) -> Any:
    """
    递归式元素合并更新策略，支持字典、列表和其他类型的合并。        
    参数:
        element1: 原始元素（被修改）
        element2: 用于合并的新元素
        max_depth: 最大递归深度
        append_priority: 是否开启"列表优先追加策略"

    返回:
        合并后的 element1
    """
    if max_depth < 0:
        return element1
    if element1 is None:
        return element2
    if element2 is None:
        return element1
    # 情况1：两个都是字典，递归合并
    if isinstance(element1, dict) and isinstance(element2, dict):
        for key, value in element2.items():
            if key in element1:
                if value is None:
                    element1.pop(key)
                    continue
                # 递归合并已存在的键
                element1[key] = merge_elements(
                    element1[key], value, max_depth-1, append_priority
                )
            else:
                # 直接添加新键
                element1[key] = value
        return element1
    
    # 情况2：非字典情况，根据append_priority处理
    elif append_priority:
        # 列表追加优先策略
        if isinstance(element1, list):
            if isinstance(element2, list):
                element1.extend(element2)
            else:
                element1.append(element2)
            return element1
        elif isinstance(element1, str) and isinstance(element2, str):
            return element1 + element2
        elif isinstance(element1, int) and isinstance(element2, int) or isinstance(element1, float) and isinstance(element2, float):
            return element1 + element2
        else:
            # 非 list，变成 list 再追加
            if isinstance(element2, list):
                return [element1] + element2
            else:
                return [element1, element2]
    else:
        # 默认策略：覆盖
        return element2
# 智能字符串索引解析
async def _parse_single_context_embed(text: str, contexts: dict[str,Any], value_getter: Callable[[str, dict[str,Any], Any], Awaitable[Any]], default: str = "", batch_id: int|None = None) -> str:
    import re
    
    # 处理并行索引占位符
    if batch_id is not None:
        text = text.replace("%batch_index%", str(batch_id))
    
    # 转义语法处理：使用列表拼接避免索引变化问题
    left_marker = "__LEFT_BRABCE__"
    right_marker = "__RIGHT_BRABCE__"
    
    result_chars = []
    only_one_brace_count = 0
    i = 0
    while i < len(text):
        if i < len(text) - 1:
            # 检查是否是转义序列 {{
            if text[i] == '{' and text[i + 1] == '{':
                result_chars.append(left_marker)
                i += 2  # 跳过两个字符
                continue
            # 检查是否是转义序列 }}
            elif text[i] == '}' and text[i + 1] == '}':
                if only_one_brace_count == 0:
                    result_chars.append(right_marker)
                    i += 2  # 跳过两个字符
                    continue
                else:
                    # 当有未配对的{时，}}作为两个独立的}处理
                    result_chars.append(text[i])
                    only_one_brace_count -= 1
                    i += 1
                    continue
            
        # 普通字符，直接添加
        result_chars.append(text[i])
        if text[i] == '{':
            only_one_brace_count += 1
        elif text[i] == '}':
            only_one_brace_count = max(0, only_one_brace_count - 1)  # 防止计数器变负
        i += 1
    
    result_string = ''.join(result_chars)
    
    # 惰性基于最小{}逐步往外替换的方案，实现嵌套替换
    depth = 100
    while True:
        if depth == 0:
            raise RecursionError(f"嵌套层数过多,请检查引用逻辑,排除可能存在的递归引用情况,最后的解析结果为\n{result_string}")
        depth -= 1
        # 查找所有最简无嵌套的{prefix.path}模式
        # 匹配: {word.path} 其中word是字母数字下划线组成，path不包含{或}
        pattern = r"\{([a-zA-Z_][a-zA-Z0-9_]*)\.([^{}]+)\}"
        matches = re.findall(pattern, result_string)
        
        if not matches:
            break  # 没有找到更多的匹配，退出循环
        
        # 记录替换前的字符串，用于检测是否发生变化
        before_replacement = result_string
        
        # 执行替换
        for prefix, path in matches:
            template = f"{{{prefix}.{path}}}"
            current_field = f"{prefix}.{path}"
            value = template
            # 使用提供的value_getter获取值，传入contexts
            try:
                original_value = await value_getter(current_field, contexts, default)
                if original_value is not None:
                    value = original_value
            except Exception:
                # 当因为source不存在，解析路径错误等原因导致value_getter抛出异常时，不进行替换
                value = template

            # 替换模板
            result_string = result_string.replace(template, str(value))
        
        # 检查是否发生了变化
        if result_string == before_replacement:
            break  # 没有发生变化，退出循环
    
    # 还原转义标记为实际的花括号
    result_string = result_string.replace(left_marker, "{")
    result_string = result_string.replace(right_marker, "}")
    
    return result_string




async def parse_multi_string_context_embed(string_with_context_embed: str|dict[str,str], contexts: dict[str,Any], value_getter: Callable[[str, dict[str,Any], Any], Awaitable[Any]], default: str = "", batch_id: int|None = None) -> str|dict:
    """
    智能字符串索引解析，递归处理字符串、字典的模板替换。
    将数据结构中的字符串模板进行变量替换，支持嵌套的复杂数据结构。
    
    args：
    - string_with_context_embed: 待解析的数据结构，支持str、dict[str,str]
    - contexts: 上下文字典集合 (如 {"src": {...}, "ctx": {...}, "rag": {...}})
    - value_getter: 异步值获取函数，函数签名: async (key, contexts, default) -> Any
    - default: 当key不存在时的默认值
    - batch_id: 批处理执行时的索引ID，配合%batch_index%使用
    returns:
    - 返回解析后的同类型数据结构
    
    支持的数据类型：
    1. str - 直接进行模板替换
    2. dict - 递归处理所有value（value必须是str、dict、list之一）
    3. list - 递归处理所有元素（元素必须是str、dict、list之一）
    
    模板语法（参见_parse_single_context_embed的文档）：
    1. {src.key} - 从contexts["src"]中获取key对应的值
    2. {ctx.key} - 从contexts["ctx"]中获取key对应的值
    3. {rag.query} - 从contexts["rag"]中获取query对应的值
    4. {prefix.a.b.c} - 支持嵌套访问
    5. {prefix.a[0].b} - 支持列表索引和混合访问
    6. {memory.{src.query}} - 支持嵌套模板，内层先解析，外层后解析
    7. %batch_index% - 批处理时的索引占位符，会被替换为实际的batch_id
    8. {{}} - 转义语法，{{src.key}}会被替换为{src.key}，不进行变量替换
    
    示例：
    >>> contexts = {
    ...     "src": {"name": "Alice", "items": ["apple", "banana"]},
    ...     "ctx": {"task": "process"},
    ...     "rag": {"knowledge": "some retrieved info"}
    ... }
    >>> def custom_getter(key, contexts, default):
    ...     # 自定义获取逻辑
    ...     return get_context_value(contexts["src"], contexts["ctx"], key, default)
    
    >>> # 字符串处理
    >>> await parse_smart_string_index("Hello {src.name}, task: {ctx.task}", contexts, custom_getter)
    'Hello Alice, task: process'
    
    >>> # 字典处理
    >>> template_dict = {
    ...     "greeting": "Hello {src.name}",
    ...     "info": {
    ...         "task": "Task: {ctx.task}",
    ...         "knowledge": "RAG: {rag.knowledge}"
    ...     }
    ... }
    >>> await parse_smart_string_index(template_dict, contexts, custom_getter)
    {'greeting': 'Hello Alice', 'info': {'task': 'Task: process', 'knowledge': 'RAG: some retrieved info'}}
    """
    if isinstance(string_with_context_embed, str):
        return await _parse_single_context_embed(string_with_context_embed, contexts, value_getter, default, batch_id)
    elif isinstance(string_with_context_embed, dict):
        result = {}
        for key, value in string_with_context_embed.items():
            if isinstance(value, str):
                result[key] = await _parse_single_context_embed(value, contexts, value_getter, default, batch_id)
            else:
                raise ValueError(f"字典中的值必须是str类型，当前键'{key}'的值类型: {type(value)}")
        return result
    else:
        raise ValueError(f"不支持的数据类型: {type(string_with_context_embed)}，支持的类型: str, dict")
#类名转义注册名
def _snake_to_camel(snake: str) -> str:
    """将 snake_case 文件名转换为驼峰 + Agent 后缀的类名。

    规则：
    1. 如果文件名以 "_agent" 结尾，则去掉 "_agent"（6 个字符）。
    2. 如果文件名以 "agent" 结尾（但没有下划线），也去掉 "agent"（5 个字符）。
    3. 其余保持不变。
    4. 将剩余的 snake_case 部分按下划线分词并首字母大写后拼接。
    5. 最后追加 "Agent" 后缀。
    """
    if snake.endswith("_agent"):
        snake = snake[:-6]  # 去掉 "_agent"
    elif snake.endswith("agent"):
        snake = snake[:-5]  # 去掉 "agent"
    # 去除可能残留的尾部下划线
    if snake.endswith("_"):
        snake = snake[:-1]
    return "".join(word.capitalize() for word in snake.split("_")) + "Agent"

def _snake_to_camel_without_agent(snake: str) -> str:
    """将 snake_case 文件名转换为驼峰式类名，不添加 Agent 后缀。

    规则：
    1. 将 snake_case 按下划线分词并首字母大写后拼接。
    2. 不添加任何后缀。
    """
    return "".join(word.capitalize() for word in snake.split("_")) 
# agent自动注册器
def _check_file_exist(path:str)->str|None:
    """检查文件是否存在"""
    if os.path.exists(path):
        return path
    return None
AGENT_SETTINGS_PATH = _check_file_exist(os.path.join(os.getcwd(),"aos_config","agent_settings.json")) or os.path.join(os.path.dirname(os.path.dirname(__file__)),"agent_settings.json")

def get_agents_classes(agents_key:str|None=None)->dict[str,type["BaseAgent"]]:
    """
    根据agent_settings.json中的配置，根据key递归的获取该key下所有的Agent类
    加载顺序：先从agent_os2内置目录，再从cwd项目目录，后者覆盖前者
    """
    from .base_agent import BaseAgent
    agent_classes = {"base":BaseAgent}
    
    # 获取agent_os2根目录 (utility.py所在目录的上层目录)
    agent_os2_root = os.path.dirname(os.path.dirname(__file__))
    cwd = os.getcwd()
    
    with open(AGENT_SETTINGS_PATH, "r", encoding="utf-8") as f:
        agent_settings = json.load(f)
    
    # 处理agents_key为None的情况：加载所有keys
    if agents_key is None:
        for agent_paths in agent_settings.values():
            for raw_path in agent_paths:
                _load_agent_path_with_priority(raw_path, agent_os2_root, cwd, agent_classes)
    else:
        for raw_path in agent_settings.get(agents_key, []):
            _load_agent_path_with_priority(raw_path, agent_os2_root, cwd, agent_classes)
    
    return agent_classes

def _load_agent_path_with_priority(raw_path: str, agent_os2_root: str, cwd: str, agent_classes: dict):
    """加载单个路径，按优先级处理同名冲突"""
    # 先从agent_os2内置目录查找
    agent_os2_path = os.path.join(agent_os2_root, raw_path.lstrip('./'))
    if os.path.exists(agent_os2_path):
        builtin_classes = _find_agent_classes(agent_os2_path, package_root=agent_os2_root)
        for key, value in builtin_classes.items():
            if key in agent_classes and f"{value.__module__}.{value.__qualname__}" != f"{agent_classes[key].__module__}.{agent_classes[key].__qualname__}":
                raise ValueError(f"agent_classes中存在多个注册名为{key}的agent")
            agent_classes[key] = value
    
    # 再从cwd查找，覆盖同名的
    cwd_path = raw_path if os.path.isabs(raw_path) else os.path.join(cwd, raw_path)
    if os.path.exists(cwd_path):
        user_classes = _find_agent_classes(cwd_path, package_root=cwd)
        for key, value in user_classes.items():
            agent_classes[key] = value  # 用户版本覆盖内置版本
def _find_agent_classes(agent_path: str, package_root: str|None = None) -> dict[str, type["BaseAgent"]]:
    import importlib.util
    import inspect
    import sys
    from .base_agent import BaseAgent
    agent_classes = {}
    
    # 如果没有指定包根目录，使用当前工作目录
    if package_root is None:
        package_root = os.getcwd()

    for root, _, files in os.walk(agent_path):
        for file in files:
            if not file.endswith(".py"):
                continue
                
            file_stem = file[:-3]
            full_path = os.path.join(root, file)
            
            # 检查文件中存在的候选类名
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            candidate_class_name = None
            for class_name in [_snake_to_camel(file_stem), _snake_to_camel_without_agent(file_stem)]:
                if f"class {class_name}" in content:
                    candidate_class_name = class_name
                    break
            
            if not candidate_class_name:
                continue
            
            # 检查是否已缓存
            norm_full_path = os.path.normcase(os.path.abspath(full_path))
            module = None
            for loaded_module in sys.modules.values():
                if getattr(loaded_module, "__file__", None):
                    if os.path.normcase(os.path.abspath(loaded_module.__file__)) == norm_full_path:
                        module = loaded_module
                        break
            
            # 加载新模块
            if not module:
                spec = importlib.util.spec_from_file_location(file_stem, full_path)
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                    # 支持用户自定义的包结构
                    user_package = getattr(module, '__package__', None)
                    if user_package:
                        module_name = f"{user_package}.{file_stem}"
                        # 确保父包链存在
                        package_parts = user_package.split('.')
                        for i in range(len(package_parts)):
                            parent_name = '.'.join(package_parts[:i+1])
                            if parent_name not in sys.modules:
                                sys.modules[parent_name] = importlib.util.module_from_spec(
                                    importlib.util.spec_from_loader(parent_name, loader=None))
                        sys.modules[module_name] = module
                except ModuleNotFoundError as e:
                    if "relative import" in str(e):
                        raise ModuleNotFoundError(
                            f"文件 {full_path} 使用了相对导入，请在文件开头添加: __package__ = \"your.package.name\""
                        ) from e
                    raise
            
            # 验证并添加Agent类
            cls = getattr(module, candidate_class_name)
            if inspect.isclass(cls) and issubclass(cls, BaseAgent) and cls is not BaseAgent:
                agent_classes[file_stem] = cls
                    
    return agent_classes
# 字符串解析为json并带有预处理机制，当解析失败时自动抛出错误。
import json, re

def _make_error_context(text: str, error_pos: int, window: int = 40) -> str:
    """
    生成错误位置的上下文信息，显示错误位置周围的文本
    
    args:
        text: 原始文本
        error_pos: 错误位置
        window: 上下文窗口大小
    returns:
        包含错误位置指示的上下文字符串
    """
    excerpt = text[max(0, error_pos - window): error_pos + window]
    pointer = " " * (min(window, error_pos)) + "▲"
    return excerpt + "\n" + pointer

class JSONPreprocessError(Exception):
    """JSON预处理错误异常类"""
    def __init__(self, message: str, context: str = None):
        super().__init__(message)
        self.context = context
        
    def __str__(self):
        msg = super().__str__()
        if self.context:
            msg += f"\n\n{self.context}"
        return msg

def _smart_escape_json_strings(text: str) -> str:
    """智能修复JSON字符串中的转义问题：未转义双引号和非法反斜杠转义"""
    import json
    
    # 快速路径：已是合法JSON直接返回
    try:
        json.loads(text)
        return text
    except:
        pass
    
    result, in_string, i = [], False, 0
    
    while i < len(text):
        ch = text[i]
        
        if in_string:
            if ch == '\\' and i + 1 < len(text):
                nxt = text[i + 1]
                # 检查是否为合法JSON转义
                if nxt in '"\\/bfnrt':
                    result.extend([ch, nxt])
                    i += 2
                elif nxt == 'u' and i + 5 < len(text) and all(c in '0123456789abcdefABCDEF' for c in text[i+2:i+6]):
                    result.extend([ch, nxt] + list(text[i+2:i+6]))
                    i += 6
                else:
                    # 非法转义，反斜杠加倍
                    result.append('\\\\')
                    i += 1
            elif ch == '"':
                # 检查是否为字符串结束：看下个非空白字符
                j = i + 1
                while j < len(text) and text[j].isspace():
                    j += 1
                if j >= len(text) or text[j] in ',}]:':
                    result.append(ch)
                    in_string = False
                else:
                    result.append('\\"')  # 转义内部双引号
                i += 1
            elif ch in '\n\r\t':
                result.append({'\n': '\\n', '\r': '\\r', '\t': '\\t'}[ch])
                i += 1
            else:
                result.append(ch)
                i += 1
        else:
            if ch == '"':
                in_string = True
            result.append(ch)
            i += 1
    
    return ''.join(result)

def parse_str_to_json_with_preprocess(text: str) -> dict:
    """
    尝试将字符串清洗为合法 JSON 并解析，支持处理常见格式错误。
    """
    text = text.strip()

    # 去掉 markdown 的 ```json 或 ``` 包裹
    if text.startswith("```"):
        text = re.sub(r"^```(?:\w+)?\n?", "", text, count=1)
    if text.endswith("```"):
        text = re.sub(r"\n?```$", "", text, count=1)

    # 仅保留从第一个 { 或 [ 开始的部分
    match = re.search(r"([{[])", text)
    if match:
        text = text[match.start():]

    # 删除尾逗号，如 {"a": 1,}
    text = re.sub(r",(?=\s*[}\]])", "", text)

    # 如果只有单引号，尝试替换为双引号（简单处理）
    if '"' not in text and "'" in text:
        text = re.sub(r"'", '"', text)

    # 智能处理JSON字符串内的转义问题
    text = _smart_escape_json_strings(text)

    # 尝试解析
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        error_context = _make_error_context(text, e.pos)
        raise JSONPreprocessError(e.msg, context=error_context)

    
# flow dsl 解析器
def parse_flow_dsl(flow_class:type["Flow"],dsl:str,parent:"BaseAgent|None"=None)->"Flow":
    """
    根据dsl解析flow，严格遵守以下格式：
    
    ```yaml
    flow_name:
        agents_key: <agents_key> #可选，指定从哪个注册表加载agent类
        flow_settings: #可选
            <flow_settings> #解析为字典
        expected_shared_context_keys: #可选
            - <key1> # 期望从父级上下文继承的键列表
            - <key2>
            ...
        agents:
            <agent_alias>:
                name: <agent_type_name>
                settings: #可选
                    <agent_settings> #解析为字典
        edges:
            - <src_alias> -> <dest_alias>
            ...
        entry_agent: <entry_agent_alias> #可选，默认使用agents字典的第一个agent作为入口节点
        exit_agent: <exit_agent_alias> #可选
    ```
    
    args:
        flow_class: Flow类
        dsl: flow dsl字符串
        parent: 父flow实例，用于继承agents_key等配置
    returns:
        Flow实例
    """
    import yaml

    # ---------- 预处理：去除 ```yaml / ``` 包裹 ----------
    dsl = dsl.strip()
    if dsl.startswith("```"):
        # 跳过第一行 ``` 或 ```yaml
        first_newline = dsl.find("\n")
        if first_newline != -1:
            dsl = dsl[first_newline + 1 :]
    # 去掉末尾 ``` 行
    if dsl.rstrip().endswith("```"):
        lines = dsl.splitlines()
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        dsl = "\n".join(lines)

    # ---------- YAML 解析 ----------
    try:
        parsed_dsl = yaml.safe_load(dsl)
    except yaml.YAMLError as err:
        raise ValueError(f"DSL YAML解析失败: {err}")
    
    # ---------- 格式验证 ----------
    if not isinstance(parsed_dsl, dict):
        raise ValueError("DSL格式错误：根对象必须是字典")
    
    if len(parsed_dsl) != 1:
        raise ValueError("DSL格式错误：根对象必须只包含一个flow定义")
    
    flow_name, flow_config = next(iter(parsed_dsl.items()))
    
    if not isinstance(flow_config, dict):
        raise ValueError("DSL格式错误：flow配置必须是字典")
    
    # 验证必要字段
    required_fields = ['agents']
    for field in required_fields:
        if field not in flow_config:
            raise ValueError(f"DSL格式错误：缺少必要字段 '{field}'")
    
    # ---------- 创建Flow实例 ----------
    agents_key = flow_config.get('agents_key', None)
    flow_settings = flow_config.get('flow_settings', {})
    expected_shared_context_keys = flow_config.get('expected_shared_context_keys', [])
    
    # 验证agents_key格式
    if agents_key is not None and not isinstance(agents_key, str):
        raise ValueError("DSL格式错误：agents_key必须是字符串")
        
    if flow_settings and not isinstance(flow_settings, dict):
        raise ValueError("DSL格式错误：flow_settings必须是字典")
    
    # 验证 expected_shared_context_keys 格式
    if expected_shared_context_keys:
        if not isinstance(expected_shared_context_keys, list):
            raise ValueError("DSL格式错误：expected_shared_context_keys必须是列表")
        # 转换为集合
        expected_shared_context_keys = set(expected_shared_context_keys)
    else:
        expected_shared_context_keys = None
    
    flow = flow_class(flow_name, parent=parent, agents_key=agents_key, expected_shared_context_keys=expected_shared_context_keys, **flow_settings)
    
    # ---------- 创建和配置 agents ----------
    agents_config = flow_config['agents']
    if not isinstance(agents_config, dict):
        raise ValueError("DSL格式错误：agents字段必须是字典")
    
    for agent_alias, agent_details in agents_config.items():
        if not isinstance(agent_details, dict):
            raise ValueError(f"DSL格式错误：agent '{agent_alias}' 的配置必须是字典")
        
        if 'name' not in agent_details:
            raise ValueError(f"DSL格式错误：agent '{agent_alias}' 缺少name字段")
        
        agent_type_name = agent_details['name']
        agent_settings = agent_details.get('settings', {})
        
        if not isinstance(agent_settings, dict):
            raise ValueError(f"DSL格式错误：agent '{agent_alias}' 的settings必须是字典")
        
        flow.add_agent(agent_type_name, alias=agent_alias, **agent_settings)
    
    # ---------- 构建依赖关系 ----------
    if 'edges' in flow_config:
        edges_config = flow_config['edges']
        
        if not isinstance(edges_config, list):
            raise ValueError("DSL格式错误：edges字段必须是列表")
        
        for edge in edges_config:
            if not isinstance(edge, str):
                raise ValueError("DSL格式错误：每个edge必须是字符串")
            
            if '->' not in edge:
                raise ValueError(f"DSL格式错误：edge格式错误 '{edge}'，应为 'src_alias -> dest_alias'")
            
            parts = edge.split('->')
            if len(parts) != 2:
                raise ValueError(f"DSL格式错误：edge格式错误 '{edge}'，应只包含一个 '->'")
            
            src_alias = parts[0].strip()
            dest_alias = parts[1].strip()
            
            if not src_alias or not dest_alias:
                raise ValueError(f"DSL格式错误：edge格式错误 '{edge}'，源或目标不能为空")
            
            if src_alias not in flow.agents:
                raise ValueError(f"DSL构造错误：源agent '{src_alias}' 不存在")
            if dest_alias not in flow.agents:
                raise ValueError(f"DSL构造错误：目标agent '{dest_alias}' 不存在")
            
            flow.add_edge(src_alias, dest_alias)
    
    # ---------- 设置entry_agent ----------
    if 'entry_agent' in flow_config:
        entry_agent_alias = flow_config['entry_agent']
        if not isinstance(entry_agent_alias, str):
            raise ValueError("DSL格式错误：entry_agent必须是字符串")
        
        if entry_agent_alias not in flow.agents:
            raise ValueError(f"DSL构造错误：entry_agent '{entry_agent_alias}' 不存在")
        
        flow.entry_agent = flow.agents[entry_agent_alias]
    
    # ---------- 验证Flow结构 ----------
    # 验证entry_agent没有前置节点
    if flow.entry_agent.previous:
        raise ValueError(f"DSL构造错误：entry_agent '{entry_agent_alias}' 不能有前置节点")
    
    return flow
# 命令执行器辅助函数
def _create_single_agent_or_flow(config: dict[str, Any], parent: "BaseAgent"):
    """
    创建单个agent或flow实例（统一处理name和dsl两种方式）
    args:
        config: agent/flow配置字典
        parent: 父flow
    returns:
        创建的agent/flow实例
    """
    from .flow import Flow
    
    if "dsl" in config:
        # DSL构造Flow
        return Flow.construct_from_dsl(config["dsl"], parent)
    elif "name" in config:
        # 通过注册系统创建（包括普通Agent和注册的Flow）
        agent_type_name = config["name"]
        settings = config.get("settings", {}).copy()
        
        # 获取agent类并创建实例
        agent_class = parent.get_agent_class(agent_type_name) if isinstance(parent, Flow) else get_agents_classes()[agent_type_name]
        return agent_class(agent_type_name, parent=parent, **settings)
    else:
        raise ValueError("DSL格式错误：配置必须包含'name'或'dsl'字段")

def _handle_unified_action(action_type: str, config: Any, src: "BaseAgent", parent: "BaseAgent"):
    """
    统一处理add_branch和insert命令的配置
    args:
        action_type: "add_branch" 或 "insert"
        config: 配置，可以是dict、list或任意格式
        src: 源agent
        parent: 父flow
    """
    # 统一包装为list格式处理
    if isinstance(config, dict):
        # 单个配置包装为list
        config_list = [config]
    elif isinstance(config, list):
        # 已经是list，直接使用
        config_list = config
    else:
        raise ValueError(f"DSL格式错误：{action_type}配置必须是字典或列表")
    
    # 使用统一的列表处理函数
    _handle_agent_list(config_list, src, parent, action_type)


def _handle_agent_list(config: list, src: "BaseAgent", parent: "Flow", action_type: str):
    """
    处理复杂的agent列表逻辑（支持链式/并行）
    args:
        config: agent的列表配置
        src: 源agent
        parent: 父flow
        action_type: "add_branch" 或 "insert"
    """
    from .flow import Flow
    
    # insert模式需要保存和清理原有连接
    original_after = list(src.after) if action_type == "insert" else []
    if action_type == "insert":
        src.after.clear()
    
    # 解析所有层级
    layers = []
    for item in config:
        if isinstance(item, dict):
            # 单个agent/flow形成一层
            agent = _create_single_agent_or_flow(item, parent)
            layers.append([agent])
        elif isinstance(item, list):
            # 并行agents形成一层
            parallel_agents = []
            for sub_item in item:
                if not isinstance(sub_item, dict):
                    if isinstance(sub_item, list):
                        raise ValueError("DSL格式错误：agent列表不支持超过2层的嵌套列表")
                    else:
                        raise ValueError("DSL格式错误：agent列表中嵌套列表的元素必须是字典")
                
                agent = _create_single_agent_or_flow(sub_item, parent)
                parallel_agents.append(agent)
            layers.append(parallel_agents)
        else:
            raise ValueError("DSL格式错误：agent列表中的元素必须是字典或列表")
    
    # 连接各层
    if layers:
        # 连接 src 到第一层
        for agent in layers[0]:
            agent.previous.add(src)
            src.after.add(agent)
        
        # 连接各层之间（链式连接，支持并行）
        for i in range(len(layers) - 1):
            current_layer = layers[i]
            next_layer = layers[i + 1]
            
            for current_agent in current_layer:
                for next_agent in next_layer:
                    current_agent.after.add(next_agent)
                    next_agent.previous.add(current_agent)
        
        # insert模式：连接最后一层到原来的after节点
        if action_type == "insert" and original_after:
            last_layer = layers[-1]
            for agent in last_layer:
                for dest in original_after:
                    agent.after.add(dest)
                    dest.previous.discard(src)
                    dest.previous.add(agent)

# 默认命令执行器
def update_shared_context(merge_dict: dict[str, Any], shared_context: dict[str, Any],append_priority:bool=False):
    """
    更新共享上下文
    """
    merge_elements(shared_context, merge_dict if isinstance(merge_dict,dict) else {},append_priority=append_priority)

def modify_graph(src: "BaseAgent", actions: list[dict[str, Any]], parent: "BaseAgent"):
    """
    根据actions，动态修改flow的结构
    args:
        src: 当前agent
        actions: 当前agent的返回结果
        parent: 父flow
    """
    for action in actions:
        if "add_branch" in action:
            config = action["add_branch"]
            _handle_unified_action("add_branch", config, src, parent)
            
        elif "insert" in action:
            config = action["insert"]
            _handle_unified_action("insert", config, src, parent)
            
        elif "cancel_next_steps" in action:
            src.after.clear()
            
        # 保持向后兼容性的旧命令支持，警告⚠将在1.25版本之后移除
        elif "add_agent_branch" in action:
            config = action["add_agent_branch"]
            _handle_unified_action("add_branch", config, src, parent)
            
        elif "add_flow_branch" in action:
            config = action["add_flow_branch"]
            _handle_unified_action("add_branch", config, src, parent)
            
        elif "insert_agent" in action:
            config = action["insert_agent"]
            _handle_unified_action("insert", config, src, parent)
                
        elif "insert_flow" in action:
            config = action["insert_flow"]
            _handle_unified_action("insert", config, src, parent)
def add_context_to_extra_contexts(objs:dict[str,Any],extra_contexts:dict[str,Any]):
    """
    向extra_contexts中注入新的接口对象
    """
    extra_contexts.update(objs)
# 调试上下文格式化
def format_debug_context(context: Any, summary_mode: bool = True, context_name: str = "context") -> str:
    """
    格式化调试上下文信息，支持完整输出和摘要输出两种模式
    
    args:
        context: 要格式化的上下文数据
        summary_mode: 是否使用摘要模式（默认True）
        context_name: 上下文的名称，用于生成标题
    
    returns:
        格式化后的字符串，可直接添加到debug_info中
    """
    if not summary_mode:
        return f"### {context_name}：\n```\n{context}\n```"
    
    # 摘要模式处理
    def summarize(data):
        if isinstance(data, dict):
            result = {}
            for k, v in data.items():
                if isinstance(v, dict):
                    result[k] = f"<dict:{len(v)}>"
                elif isinstance(v, list):
                    result[k] = f"<list:{len(v)}>"
                elif isinstance(v, str) and len(v) > 100:
                    result[k] = f"<str:{len(v)}>"
                else:
                    result[k] = v if len(str(v)) < 50 else f"<{type(v).__name__}>"
            return json.dumps(result, ensure_ascii=False, indent=2, default=str)
        elif isinstance(data, list):
            types = {}
            for item in data[:10]:
                t = type(item).__name__
                types[t] = types.get(t, 0) + 1
            type_str = ",".join(f"{t}({n}{'+'if n==10 else ''})" for t,n in types.items())
            return f"<list:{len(data)} [{type_str}]>"
        elif isinstance(data, str) and len(data) > 200:
            return f"<str:{len(data)} '{data[:50]}...'>"
        return str(data)[:100]
    
    return f"### {context_name}（摘要）：\n```\n{summarize(context)}\n```"
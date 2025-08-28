__package__ = "agent_os2.assistant.prompts"
import os
from ..utility.tools import list_dir
def get_available_prompt(path:str|None=None) -> dict[str,str]:
    prompts_dict = {}
    path = path or os.path.dirname(__file__)
    for file in list_dir(path):
        if file.endswith(".txt"):
            prompts_dict[file[:-4]] = os.path.join(path, file)
        elif file.endswith("/"):
            prompts_dict.update(get_available_prompt(os.path.join(path, file)))
    return prompts_dict
def full_name(prompt_name:str,available_prompts:dict[str,str]) -> str|None:
    with open(available_prompts[prompt_name],"r",encoding="utf-8") as f:
        return f.readline().strip().split("[")[0][1:]
def get_prompt_content(prompt_name:str,available_prompts:dict[str,str]) -> str|None:
    with open(available_prompts[prompt_name],"r",encoding="utf-8") as f:
        lines = f.readlines()
        lines[0] = lines[0].strip().split("[")[0]+"\n"
        return "".join(lines)
def get_index(prompt_name:str,available_prompts:dict[str,str]) -> list[str]:
    with open(available_prompts[prompt_name],"r",encoding="utf-8") as f:
        title = f.readline().strip()
        return title.split("[")[1][:-1].split(",") if "[" in title else []
def analyze_prompt_references(selected_prompts: list[str], available_prompts: dict[str, str]) -> dict[int, list[str]]:
    """
    分析prompt文件的引用关系并计算每个文件的引用分数
    
    计分规则：
    1. 累加计分：不同引用路径会累加分数，体现基类重要性
    2. 递减机制：每条引用路径都有递减效应（10→6→2→1→1）  
    3. 避免重复解析：同一个文件的index只解析一次
    
    Args:
        selected_prompts: 选中的prompt文件名列表，如果为空则默认选择所有可用的prompts
        available_prompts: 可用prompt文件字典 {文件名: 文件路径}
    
    Returns:
        dict[int, list[str]]: 引用分数到文件名列表的映射
    
    Raises:
        KeyError: 当引用的文件不存在时
    """
    # 如果selected_prompts为空，默认选择所有可用的prompts（全选）
    if not selected_prompts:
        selected_prompts = list(available_prompts.keys())
    
    reference_scores = {}  # 存储每个文件的累加引用分数 {文件名: 总分数}
    parsed_indexes = set()  # 已经解析过index的文件，避免重复解析同一个文件的引用
    
    def add_reference_score(prompt_name: str, score: int) -> None:
        """给文件累加分数"""
        reference_scores[prompt_name] = reference_scores.get(prompt_name, 0) + score
    
    def parse_file_references(prompt_name: str, current_score: int) -> None:
        """
        解析文件的引用关系（index），每个文件的index只解析一次
        但每次调用此函数时，会为当前路径的被引用文件累加分数
        
        current_score: 当前引用路径的分数，用于计算其引用文件的分数
        """
        # 检查文件是否存在
        if prompt_name not in available_prompts:
            raise KeyError(f"引用的文件 '{prompt_name}' 不存在于 available_prompts 中")
        
        # 如果已经解析过该文件的index，则不再解析，但分数已经在调用前累加了
        if prompt_name in parsed_indexes:
            return
            
        # 标记为已解析
        parsed_indexes.add(prompt_name)
        
        # 获取该文件的索引（引用列表）
        referenced_files = get_index(prompt_name, available_prompts)
        
        # 没有索引的文件是独立文件，不引用其他文件，这是完全正常的情况
        
        # 计算引用文件的分数（递减4分，最小为1）
        next_score = max(current_score - 4, 1)
        
        # 处理引用的文件
        for referenced_file in referenced_files:
            referenced_file = referenced_file.strip()  # 去除可能的空格
            if referenced_file:  # 确保不是空字符串
                # 给被引用的文件累加分数
                add_reference_score(referenced_file, next_score)
                # 递归解析被引用文件的index
                parse_file_references(referenced_file, next_score)
    
    # 处理所有选中的文件
    for selected_prompt in selected_prompts:
        if selected_prompt not in available_prompts:
            raise KeyError(f"选中的文件 '{selected_prompt}' 不存在于 available_prompts 中")
        
        # 给选中的文件设置初始分数10分
        add_reference_score(selected_prompt, 10)
        # 解析选中文件的引用关系，传递当前分数10
        parse_file_references(selected_prompt, 10)
    
    # 转换输出格式：从 {文件名: 分数} 转为 {分数: [文件名列表]}
    score_to_files = {}
    for file_name, score in reference_scores.items():
        if score not in score_to_files:
            score_to_files[score] = []
        score_to_files[score].append(file_name)
    
    return score_to_files

def generate_sorted_prompts_content(selected_prompts: list[str], score_to_files: dict[int, list[str]], available_prompts: dict[str, str]) -> str:
    """
    根据打分结果按分数从高到低排列显示提示词内容
    
    Args:
        selected_prompts: 要显示的prompt文件名列表，如果为空则显示score_to_files中的所有文件
        score_to_files: analyze_prompt_references分析出来的结果 {分数: [文件名列表]}
        available_prompts: 可用prompt文件字典 {文件名: 文件路径}
    
    Returns:
        str: 按分数从高到低排序的提示词内容合集
    """
    # 创建文件名到分数的映射
    file_to_score = {}
    for score, files in score_to_files.items():
        for file_name in files:
            file_to_score[file_name] = score
    
    # 确定要显示的文件列表
    if selected_prompts:
        # 只显示指定的文件
        files_to_display = [f for f in selected_prompts if f in available_prompts]
    else:
        # 显示所有分析结果中的文件
        files_to_display = list(file_to_score.keys())
    
    # 按分数从高到低排序
    files_to_display.sort(key=lambda f: file_to_score.get(f, 0), reverse=True)
    
    # 生成内容 - 只要纯净的文章内容
    content_parts = []
    
    for file_name in files_to_display:
        file_content = get_prompt_content(file_name, available_prompts)
        content_parts.append(file_content.strip())
    
    return "\n".join(content_parts)

# 测试函数（可选）
if __name__ == "__main__":
    available = get_available_prompt()
    score_result = analyze_prompt_references([], available)
    with open("prompt_spec.txt","w",encoding="utf-8") as f:
        role_and_core_directives = """<Role>
你是一位精通 AgentOS2 架构的流程设计师
你能根据用户自然语言任务,设计语义清晰、结构规范的自动化流程,并且基于AgentOS2架构提供实现
<Core-Directives>
文本重要性说明:!!xxx!!>**xxx**>"xxx">一般文本
自主阅读通用守则
以下所有列出的文件都在agent_os2目录下
1.在任何与AgentOS2相关的任务开始前,你都应该阅读agent_os/base_agent.py和agent_os/flow.py来掌握项目核心架构,同时阅读agents/examples下的一个案例辅助分析
2.如果你需要用到一些辅助函数而不清楚具体的传参和结果,你可以阅读agent_os/utility.py
4.如果用户的询问涉及API调用拓展,你需要阅读agent_os/base_model/model_processor.py和agent_os/base_model/processor_registry.py学会如何继承BaseProcessor实现自定义模型处理器
5.如果用户的询问涉及模型配置选择,你需要阅读agent_os/base_model/builtin_config.py查看模型可选参数,并且主动查找用户指出的model_settings.json,查看用户配置的可用配置
6.如果涉及配置文件,你应该查看当前执行目录/aos_config下去查看agent_settings.json与model_settings.json,必要可以查看agent_settings_example.json和model_settings_example.json
7.如果用户的询问包含一些特别点,你需要自主去罗列agent_os下的所有文件,查询可能存在的拓展点
核心约束
1.与AgentOS2相关的编程任务,总是应该寻找AgentOS2的原生特性来完成目标,而非使用一些自己重复造轮子的代码
2.拒绝所有硬编码设计,充分利用大语言模型语义判断的能力
3.拒绝过度设计,算法设计之前应仔细考量更简单的算法实现,减少代码量
4.总是查看根目录下是否存在env目录,有则激活conda activate ./env,否则请求用户创建并安装./agent_os2
默认行为CoT(总是要遵守的行为流程规范)
1. 明确与理解用户语义 → 判断任务难度,如果很负责则拆解出一个简单的流程并当下专注于该流程
2. 结构确认：构建流程图：考虑嵌套、动态节点等特性,形成脑内或 mermaid 流程图,并向用户展示方案,确认无异议
3. 查阅实现：阅读相关 Agent、Processor 等代码,确定可复用组件与扩展点(根据阅读通用守则)
4. 方案定稿：整理实现计划(涉及文件、接口、设置等)并再次征求用户确认
5. 编码实现：在用户确认后,仅在扩展层编写/修改代码,执行必要且非安装性质和非程序运行性质的命令行操作
6. 调试迭代：当出现无法定位的错误,优先检查 cwd/memory/statistics_* 中的最新日志查看debug_info以找出问题根源
<Architecture-Guide>
"""
        full_content = role_and_core_directives+generate_sorted_prompts_content([], score_result, available)
        f.write(full_content)
def read_file_with_line_range(file_path: str,start_line:int=1,end_line:int|None=None) -> str:
    with open(file_path, 'r') as file:
        lines = file.readlines()
        end_line = min(len(lines) if not end_line else end_line,len(lines))
        if start_line > end_line:
            return ""
        return "".join(str(i+1)+":"+lines[i] for i in range(start_line-1,end_line))
def read_file_with_char_range(file_path: str,start_index:int=0,end_index:int|None=None) -> str:
    with open(file_path, 'r') as file:
        content = file.read()
        end_index = min(len(content) if not end_index else end_index,len(content))
        if start_index > end_index:
            return ""
        return content[start_index:end_index]
def modify_file(file_path: str,line_modify_command:str) -> None:
    change_list = line_modify_command.split("\n")
    modify_commands = [(line.split(":")[0],line[line.find(":")+1:]) for line in change_list]
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for command in modify_commands:
            if command[0][-1] == "-" and command[0][:-1].isdigit():
                lines.pop(int(command[0][:-1])-1)
            elif command[0][-1] == "+" and command[0][:-1].isdigit():
                lines.insert(int(command[0][:-1])-1,command[1]+"\n")
            else:
                raise ValueError("Invalid command: "+command)

    with open(file_path, 'w') as file:
        file.write("".join(lines))
def replace_file_content(file_path: str,content_to_change:str,start_line:int,end_line:int) -> None:
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i in range(start_line-1,end_line):
            lines.pop(start_line-1)
        change_list = content_to_change.split("\n")
        for i in range(len(change_list)):
            lines.insert(start_line-1+i,change_list[i]+"\n")
    with open(file_path, 'w') as file:
        file.write("".join(lines))
def search_file_lines_with_keyword(file_path: str, keyword: str, ambiguous_rate: float = 0) -> list[dict]:
    """
    关键字匹配拥有该关键字的行，并返回符合语义搜索范式的结果格式，支持处理模糊搜索，排序按照相似度优先排序
    args:
        file_path: 文件路径
        keyword: 关键字
        ambiguous_rate: 模糊搜索相似度，0为关键词匹配，大于0为模糊搜索，默认关键词搜索，不区分大小写，-与_等价
    return:
        list[dict]: 包含confidence、line_range、char_range、text等信息的字典列表，与语义搜索返回格式一致
    """
    import difflib
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            lines = content.splitlines(keepends=True)  # 保持换行符用于计算字符位置
    except FileNotFoundError:
        return []
    
    results = []
    keyword_lower = keyword.lower()
    char_pos = 0  # 追踪当前字符位置
    
    for line_num, line in enumerate(lines, 1):
        line_content = line.rstrip('\n')  # 去掉换行符用于显示
        line_normalized = line_content.lower()
        line_normalized = line_normalized.replace("-","_")
        
        similarity = 0
        if ambiguous_rate == 0:
            # 关键词匹配：查找所有包含关键字的行
            if keyword_lower in line_normalized:
                # 根据关键字在行中的匹配程度计算相似度
                length_ratio = len(keyword_lower) / len(line_normalized) if len(line_normalized) > 0 else 0
                similarity = 0.8 + length_ratio * 0.2  # 基础分数 + 长度比例
        else:
            # 模糊搜索：处理拼写错误、字符错乱等情况
            # 首先检查直接包含（最高优先级）
            if keyword_lower in line_normalized:
                length_ratio = len(keyword_lower) / len(line_normalized) if len(line_normalized) > 0 else 0
                similarity = 0.9 + length_ratio * 0.1
            else:
                # 使用序列相似度处理拼写错误、字符错乱
                # 对整行进行模糊匹配
                line_similarity = difflib.SequenceMatcher(None, keyword_lower, line_normalized).ratio()
                
                # 对行中的每个单词和子串进行模糊匹配
                words = line_normalized.split()
                max_word_similarity = 0
                
                # 处理空格分隔的单词（适用于拉丁字母）
                for word in words:
                    word_similarity = difflib.SequenceMatcher(None, keyword_lower, word).ratio()
                    max_word_similarity = max(max_word_similarity, word_similarity)
                
                # 处理连续字符的滑动窗口（适用于象形文字）
                keyword_len = len(keyword_lower)
                if keyword_len > 1:  # 只对多字符关键字进行滑动窗口
                    for pos in range(len(line_normalized) - keyword_len + 1):
                        substring = line_normalized[pos:pos + keyword_len]
                        substr_similarity = difflib.SequenceMatcher(None, keyword_lower, substring).ratio()
                        max_word_similarity = max(max_word_similarity, substr_similarity)
                        
                        # 也尝试稍长一点的子串（关键字长度+1）
                        if pos <= len(line_normalized) - keyword_len - 1:
                            longer_substr = line_normalized[pos:pos + keyword_len + 1]
                            longer_similarity = difflib.SequenceMatcher(None, keyword_lower, longer_substr).ratio()
                            max_word_similarity = max(max_word_similarity, longer_similarity)
                
                # 取整行相似度和最佳单词相似度的较大值
                similarity = max(line_similarity, max_word_similarity)
                
                # 根据 ambiguous_rate 设置相似度阈值
                threshold = 1 - ambiguous_rate
                
                if similarity < threshold:
                    similarity = 0  # 不满足阈值，设为0
        
        # 如果找到匹配，构造符合语义搜索范式的结果
        if similarity > 0:
            # 处理长文本截取
            display_text = line_content
            if len(line_content) > 200:
                # 超过200字符则截取：前100字符 + "..." + 后100字符
                display_text = line_content[:100] + "..." + line_content[-100:]
            
            # 计算字符范围
            line_start_char = char_pos
            line_end_char = char_pos + len(line)
            
            # 转换相似度为10分制的置信度
            confidence = round(similarity * 10, 1)
            
            result_item = {
                "line_range": (line_num, line_num),  # 单行匹配
                "char_range": (line_start_char, line_end_char),
                "confidence": confidence,
                "text": display_text
            }
            
            results.append((similarity, result_item))
        
        # 更新字符位置
        char_pos += len(line)
    
    # 按相似度降序排序，相似度高的排在前面
    results.sort(key=lambda x: x[0], reverse=True)
    
    # 返回符合语义搜索范式的字典列表
    return [result_item for _, result_item in results]
async def search_file_content_with_semantics(file_path:str,query:str,result_count:int=3,max_chunks=15,model_name:str="gpt-4o-mini") -> list[dict]:
    """
    借助语言大模型根据语义搜索文件内容
    args:
        file_path: 文件路径
        query: 查询内容
        result_count: 返回结果数量，默认3
        max_chunks: 最大分段数，默认15
        model_name: 模型名称，默认gpt-4o-mini
    return:
        list[dict]: 包含confidence、line_range、char_range、text等信息的字典列表
    """
    try:
        # 导入语义搜索流程
        from ..flows.tools.semantic_search_flow import SemanticSearchFlow
        from agent_os2 import execute
        
        # 创建语义搜索流程实例
        search_flow = SemanticSearchFlow(
            name="semantic_search", 
            default_model=model_name
        )
        
        # 准备输入参数
        search_args = {
            "file_path": file_path,
            "query": query,
            "max_chunks": max_chunks
        }
        
        # 执行语义搜索流程
        results = await execute(search_flow, source_context=search_args)
        
        # 确保返回的是正确格式的结果
        if isinstance(results, list):
            return results[:result_count]
        else:
            return []
            
    except Exception as e:
        # 如果出现错误，返回空列表
        print(f"语义搜索过程中出现错误: {e}")
        return []
def list_dir(dir_path: str) -> list[str]:
    """
    列出目录下的所有文件
    args:
        dir_path: 目录路径
    return:
        list[str]: 文件列表和目录列表，目录列表带/
    """
    import os
    return [f+"/" if os.path.isdir(os.path.join(dir_path, f)) else f for f in os.listdir(dir_path)]
def delete_file(file_path: str) -> None:
    """
    删除文件
    args:
        file_path: 文件路径
    """
    import os
    os.remove(file_path)
def create_file(file_path: str,content:str="") -> None:
    """
    创建文件
    args:
        file_path: 文件路径
    """
    import os
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(content)
def create_dir(dir_path: str) -> None:
    """
    创建目录
    args:
        dir_path: 目录路径
    """
    import os
    os.makedirs(dir_path, exist_ok=True)
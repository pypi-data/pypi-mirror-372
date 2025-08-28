#不走注册系统的一个Flow程序
from agent_os2 import Flow,BaseAgent
from typing import Any
import os
import re

class ReadFileContentBootstrapAgent(BaseAgent):
    """读取文件内容并初始化搜索上下文"""
    
    def setup(self):
        self.user_info = f"## 📖 正在读取文件内容...\n"
        self.prompts = {}  # 不调用模型
        self.strict_mode = False
        
    async def post_process(self, source_context: Any, llm_result: Any, shared_context: dict[str, Any], 
                          extra_contexts: dict[str, Any], observer: list[tuple[Any, BaseAgent]], 
                          batch_id: int | None = None) -> tuple[Any, dict[str, dict | list]]:
        
        # 简化错误处理：直接抛异常让框架处理
        if not isinstance(source_context, dict):
            raise ValueError(f"期待字典输入，得到: {type(source_context)}")
            
        file_path = source_context.get("file_path")
        query = source_context.get("query")
        max_chunks = source_context.get("max_chunks", 10)
        
        if not file_path or not query:
            raise ValueError("file_path和query参数必需")
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return {
            "file_path": file_path,
            "query": query,
            "content": content,
            "max_chunks": max_chunks
        }, {
            "memory_modify": {
                "file_path": file_path,
                "query": query,
                "content_length": len(content)
            }
        }
class CalculateChunkSizeAgent(BaseAgent):
    """根据文件长度和max_chunks计算合适的分块大小"""
    
    def setup(self):
        self.user_info = f"## 🧮 正在计算分块大小...\n"
        self.prompts = {}  # 不调用模型
        self.strict_mode = False
        
    async def post_process(self, source_context: Any, llm_result: Any, shared_context: dict[str, Any], 
                          extra_contexts: dict[str, Any], observer: list[tuple[Any, BaseAgent]], 
                          batch_id: int | None = None) -> tuple[Any, dict[str, dict | list]]:
        
        content = source_context.get("content", "")
        max_chunks = source_context.get("max_chunks", 10)
        
        if not content:
            raise ValueError("content参数必需")
        
        # 简化分块大小计算
        if len(content) <= 1000:
            size, chunks = len(content), 1
        else:
            size = max(500, min(5000, len(content) // max_chunks))
            chunks = min(max_chunks, (len(content) // size) + 1)
        
        self.debug(f"文件长度: {len(content)}, 分块大小: {size}, 预计分块数: {chunks}")
        
        return {
            **source_context,
            "chunk_size": size,
            "estimated_chunks": chunks
        }, {
            "memory_modify": {"chunk_size": size, "estimated_chunks": chunks}
        }
class SplitChunkAgent(BaseAgent):
    """基于字符数按语义边界智能分块文本内容"""
    
    def setup(self):
        self.user_info = f"## ✂️ 正在智能分块文本内容...\n"
        self.prompts = {}  # 不调用模型
        self.strict_mode = False
        
    def split_text_by_semantic_boundaries(self, content: str, chunk_size: int, max_chunks: int) -> list[dict[str, Any]]:
        """基于字符数按语义边界智能分块"""
        if not content:
            return []
        
        # 小文件不分块
        if len(content) <= chunk_size:
            return [{
                "content": content,
                "start_line": 1,
                "end_line": content.count('\n') + 1,
                "chunk_id": 0
            }]
        
        # 简化计算
        chunks = min(max_chunks, (len(content) + chunk_size - 1) // chunk_size)
        size = len(content) // chunks
        
        # 多层次边界字符定义（优先级递减）
        # 第一层：换行符（最高优先级）
        newline_chars = '\n'
        # 第二层：句子结束符（中优先级）
        sentence_chars = '。！？｡!?¡¿‼⁇⁈⁉︕︖︙'  # 包含中日韩句号、问号、感叹号
        # 第三层：子句分隔符（低优先级）
        clause_chars = ';；:：,，、｀｡･ﾟ'  # 包含中日韩逗号、分号、冒号
        
        result = []
        pos = 0
        
        for i in range(chunks):
            start = pos
            if i == chunks - 1:  # 最后一块
                end = len(content)
            else:
                # 分层边界查找：优先找换行符，再找句子符，最后找子句符
                target = pos + size
                end = target
                search_range = min(target + 200, len(content))
                
                # 第一层：在较大范围内优先查找换行符
                for j in range(target, search_range):
                    if content[j] in newline_chars:
                        end = j + 1
                        break
                else:
                    # 第二层：查找句子结束符
                    for j in range(target, search_range):
                        if content[j] in sentence_chars:
                            end = j + 1
                            break
                    else:
                        # 第三层：在较小范围内查找子句分隔符
                        small_range = min(target + 50, len(content))
                        for j in range(target, small_range):
                            if content[j] in clause_chars:
                                end = j + 1
                                break
                        
            text = content[pos:end]
            if text.strip():
                start_line = content[:pos].count('\n') + 1
                result.append({
                    "content": text,
                    "start_line": start_line,
                    "end_line": start_line + text.count('\n'),
                    "chunk_id": len(result),
                    "start_char": pos,
                    "end_char": end
                })
            pos = end
            if pos >= len(content):
                break
        
        return result
        
    async def post_process(self, source_context: Any, llm_result: Any, shared_context: dict[str, Any], 
                          extra_contexts: dict[str, Any], observer: list[tuple[Any, BaseAgent]], 
                          batch_id: int | None = None) -> tuple[Any, dict[str, dict | list]]:
        
        content = source_context.get("content", "")
        if not content:
            raise ValueError("content参数必需")
            
        chunks = self.split_text_by_semantic_boundaries(
            content, 
            source_context.get("chunk_size", 1000), 
            source_context.get("max_chunks", 10)
        )
        
        sizes = [len(c['content']) for c in chunks]
        avg = sum(sizes) // len(sizes) if sizes else 0
        self.debug(f"分块完成: {len(chunks)}个, 平均{avg}字符, 范围{min(sizes) if sizes else 0}-{max(sizes) if sizes else 0}")
        
        return {
            **source_context,
            "chunks": chunks,
            "actual_chunk_count": len(chunks)
        }, {
            "memory_modify": {
                "actual_chunk_count": len(chunks),
                "chunks_info": [{"start_line": c["start_line"], "end_line": c["end_line"]} for c in chunks]
            }
        }
class ExtractRelatedContentAgent(BaseAgent):
    """使用AI进行语义搜索并提取相关内容"""
    
    def setup(self):
        self.user_info = f"## 🔍 正在进行语义搜索...\n"
        self.batch_field = "src.chunks"  # 批处理chunks
        self.strict_mode = True
        self.retry_count = 2
        # model_config会自动从父级Flow继承，无需手动设置
        
        self.prompts = {
            "system": """你是一个专业的文档语义搜索助手。你的任务是在给定的文本片段中寻找与查询相关的一个或多个连续片段。

⚠️ 严格规则：
1. 只能从当前给定的文本块中提取片段，绝对不能基于推测或常识添加不存在的内容
2. start_snippet和end_snippet必须都能在当前文本中找到，一字不差
3. 如果找不到完整的相关片段，宁可返回空列表也不要编造
4. 每个片段必须是连续的文本，不能跨越不相邻的行

技术要求：
1. 仅在与查询有明确语义相关性时才返回片段
2. 锚点要求：简短、准确且在当前文本中唯一可定位
3. 必须与当前文本逐字一致，包括大小写、标点符号等
4. 为每个片段打分（relevance_score: 0-10）
5. 同一块最多返回3个片段，按相关性排序

返回JSON格式：
{
  "segments": [
    {
      "relevance_score": <0-10的数字>,
      "start_snippet": "<在当前文本中存在的开头片段>",
      "end_snippet": "<在当前文本中存在的结尾片段>",
      "reasoning": "<简短说明>"
    }
  ]
}

🚨 JSON格式要求：
1. 字符串中如有双引号(")，必须转义为(\\")
2. 字符串中如有反斜杠(\\)，必须转义为(\\\\)
3. 严格遵循JSON语法，确保可正确解析
⚠️ 再次强调：绝对不能返回当前文本块中不存在的内容！""",
            "user": """查询内容：{src.query}

当前文本片段（第{src.chunks[%batch_index%].chunk_id}块，行号{src.chunks[%batch_index%].start_line}-{src.chunks[%batch_index%].end_line}）：
```
{src.chunks[%batch_index%].content}
```

请在该片段中选择与查询最相关的连续文本，返回不超过3个片段，严格按指定JSON返回。若无相关，返回 {\"segments\": []}。"""
        }
    
    async def parse_model_result(self, runtime_contexts: dict[str, Any], model_result: Any, batch_id: int | None = None) -> Any:
        """检查模型返回的片段是否在原文中存在且顺序正确"""
        parsed = await super().parse_model_result(runtime_contexts, model_result, batch_id)
            
        chunks = runtime_contexts.get("src", {}).get("chunks", [])
        if batch_id is None or batch_id >= len(chunks):
            raise ValueError("无效批处理ID")
        
        # 只在当前chunk中验证，不是全文
        chunk_content = chunks[batch_id].get("content", "")
        
        # 调试信息
        self.debug(f"batch_id: {batch_id}, chunks数量: {len(chunks)}")
        self.debug(f"chunk_content长度: {len(chunk_content)}")
        self.debug(f"chunk_content前100字符: {chunk_content[:100]}")
        
        valid = []
        
        for seg in parsed.get("segments", []):
            if not isinstance(seg, dict):
                continue
                
            start = str(seg.get("start_snippet", "")).strip()
            end = str(seg.get("end_snippet", "")).strip()
            score = float(seg.get("relevance_score", 0))
            
            if not start or not end or score < 3:
                continue
                
            # 大小写不敏感的片段检查
            start_lower = start.lower()
            end_lower = end.lower()
            content_lower = chunk_content.lower()
            
            if start_lower not in content_lower:
                raise ValueError(f"开头片段在当前chunk中不存在: '{start}'")
            if end_lower not in content_lower:
                raise ValueError(f"结尾片段在当前chunk中不存在: '{end}'")
                
            # 使用原文进行精确定位
            start_idx = chunk_content.lower().find(start_lower)
            end_idx = chunk_content.lower().find(end_lower) + len(end)

            if start_idx > end_idx:
                raise ValueError(f"开头片段位置({start_idx})不能在结尾片段位置({end_idx})之后")
            
            valid.append({
                "relevance_score": score,
                "start_snippet": start,
                "end_snippet": end,
                "start_idx": start_idx,
                "end_idx": end_idx + len(end),
                "reasoning": str(seg.get("reasoning", ""))
            })
        
        return {"segments": valid[:3]}
    
    def adjust_prompt_after_failure(self, prompts, error_text, hint):
        """失败后调整提示词，告诉模型具体的失败原因"""
        failure_hint = f"""

🚨 上次提取失败：{error_text}

请严格检查：
1. 你返回的 start_snippet 和 end_snippet 是否都能在当前给定的文本块中找到
2. 不要基于编程常识或推测添加任何不存在的代码行
3. 如果当前文本块中没有完整的相关片段，请返回空列表 {{"segments": []}}
4. 仔细核对每个字符，包括大小写、标点符号、空格

⚠️ 只提取当前文本块中实际存在的内容！"""
        
        return super().adjust_prompt_after_failure(prompts, error_text, failure_hint)
    
    async def post_process(self, source_context: Any, llm_result: Any, shared_context: dict[str, Any], 
                          extra_contexts: dict[str, Any], observer: list[tuple[Any, BaseAgent]], 
                          batch_id: int | None = None) -> tuple[Any, dict[str, dict | list]]:
        
        if batch_id is None or batch_id >= len(source_context.get("chunks", [])):
            return [], {}
        
        chunk = source_context["chunks"][batch_id]
        content = source_context.get("content", "")
        start_char = chunk.get("start_char", 0)
        
        segments = []
        for seg in llm_result.get("segments", []):
            start, end = seg["start_idx"], seg["end_idx"]
            global_start, global_end = start_char + start, start_char + end
            
            segments.append({
                "line_range": (content[:global_start].count('\n') + 1, content[:global_end].count('\n') + 1),
                "char_range": (global_start, global_end),
                "confidence": seg["relevance_score"],
                "text": chunk["content"][start:end],
            })
        
        return segments, {}
class MergeContentAgent(BaseAgent):
    """合并和排序语义搜索结果"""
    
    def setup(self):
        self.user_info = f"## 📝 正在合并搜索结果...\n"
        self.prompts = {}  # 不调用模型
        self.strict_mode = False
        
    async def post_process(self, source_context: Any, llm_result: Any, shared_context: dict[str, Any], 
                          extra_contexts: dict[str, Any], observer: list[tuple[Any, BaseAgent]], 
                          batch_id: int | None = None) -> tuple[Any, dict[str, dict | list]]:
        
        if not isinstance(source_context, list):
            return [], {}
            
        # 简化过滤和排序
        valid = [
            r for r in source_context 
            if isinstance(r, dict) and r.get("text") and r.get("confidence", 0) >= 3
            and isinstance(r.get("line_range"), tuple) and isinstance(r.get("char_range"), tuple)
        ]
        
        valid.sort(key=lambda x: (x["confidence"], -x["char_range"][0]), reverse=True)
        
        self.debug(f"搜索完成：{len(valid)}个相关片段")
        
        return valid, {
            "memory_modify": {
                "search_results_count": len(valid),
                "total_processed_chunks": len(source_context),
                "valid_chunks": len(valid)
            }
        }
class SemanticSearchFlow(Flow):
    """语义搜索完整流程"""
    
    def __init__(self, name: str = "semantic_search", parent: "BaseAgent|None" = None, default_model: str = "gpt-4o-mini", **settings):
        # 设置模型配置 - 在settings中放入配置字典，而不是ModelConfig对象
        if "model_config" not in settings:
            settings["model_config"] = {
                "model_name": default_model,
                "is_stream": True
            }
        
        # 不需要特定的shared context keys，因为我们主要通过args传递数据
        super().__init__(name, parent, expected_shared_context_keys=set(), **settings)
        
        # 添加自定义Agent类到Flow中（不走注册系统）
        self.add_custom_agent_class("read_file_bootstrap", ReadFileContentBootstrapAgent)
        self.add_custom_agent_class("calculate_chunk", CalculateChunkSizeAgent)
        self.add_custom_agent_class("split_chunk", SplitChunkAgent)
        self.add_custom_agent_class("extract_content", ExtractRelatedContentAgent)
        self.add_custom_agent_class("merge_content", MergeContentAgent)
        
        # 构建流程图
        self.add_agent("read_file_bootstrap", alias="bootstrap")
        self.add_agent("calculate_chunk", alias="calculate")
        self.add_agent("split_chunk", alias="split")
        self.add_agent("extract_content", alias="extract")  # 不再需要传递default_model
        self.add_agent("merge_content", alias="merge")
        
        # 构建流程边
        self.add_edge("bootstrap", "calculate")
        self.add_edge("calculate", "split") 
        self.add_edge("split", "extract")
        self.add_edge("extract", "merge")
        
        # 设置入口节点
        self.entrance("bootstrap")
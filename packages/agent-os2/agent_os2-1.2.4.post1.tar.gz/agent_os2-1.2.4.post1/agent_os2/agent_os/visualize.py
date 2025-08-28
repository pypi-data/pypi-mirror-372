__package__ = "agent_os2.agent_os"
from typing import Any
import asyncio
from .base_agent import BaseAgent
from .flow import Flow, execute
import json
import os
from datetime import datetime


def serialize_agent_info(agent: BaseAgent) -> dict[str, Any]:
    """
    序列化 Agent 信息，处理不可 JSON 序列化的对象
    """
    info = {}
    for key, value in agent.__dict__.items():
        if key.startswith("_"):
            continue
        info[key] = value
    
    # 添加额外的有用信息
    info['_type'] = agent.__class__.__name__
    info['_is_flow'] = isinstance(agent, Flow)
    
    return info


def generate_visjs_html(flow: Flow, path: list[BaseAgent], output_file: str, flow_result: dict[str, Any] | None = None, node_outputs: dict[str, Any] | None = None, error_info: Exception | None = None):
    """
    生成 vis.js 可视化 HTML 文件
    
    Args:
        flow: 要可视化的 Flow 对象
        path: 该 Flow 下的 Agent 执行路径列表（子Flow在这里表现为一个Agent）
        output_file: 输出 HTML 文件路径
        flow_result: 该 Flow 的执行结果和上下文信息
        node_outputs: 节点的输出数据字典
        error_info: Flow执行时的错误信息（如果有）
    """
    nodes = []
    edges = []
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 检查是否有parent flow
    parent_flow_html = None
    if flow.parent and isinstance(flow.parent, Flow):
        parent_flow_html = f"{flow.parent.alias}_{str(flow.parent.uuid)[:8]}.html"
    
    # 如果没有提供node_outputs，初始化为空字典
    if node_outputs is None:
        node_outputs = {}
    
    # 生成节点数据
    for i, node in enumerate(path):
        node_data = {
            "id": str(node.uuid),
            "label": node.alias,
            "info": serialize_agent_info(node),
            "color": "#97C2FC"  # 默认颜色（普通节点 - 浅蓝色）
        }
        
        # 根据节点特性设置不同的颜色
        # 1. Flow节点 - 橙色
        if isinstance(node, Flow):
            node_data["color"] = "#FFA500"  # 橙色
            if hasattr(node, 'after') and len(node.after) == 0:
                node_data["color"] = "#F44336"  # 红色
            node_data["shape"] = "box"
            # 添加子Flow的HTML文件名
            node_data["info"]["subflow_html"] = f"{node.alias}_{str(node.uuid)[:8]}.html"
        # 2. 入口节点（没有previous） - 绿色
        elif hasattr(node, 'previous') and len(node.previous) == 0:
            node_data["color"] = "#4CAF50"  # 绿色
            node_data["borderWidth"] = 3  # 加粗边框
        # 3. 出口节点（没有after） - 红色
        elif hasattr(node, 'after') and len(node.after) == 0:
            node_data["color"] = "#F44336"  # 红色
            node_data["borderWidth"] = 3  # 加粗边框
        # 4. 批处理节点（batch_field不为空） - 紫色
        elif hasattr(node, 'batch_field') and node.batch_field:
            node_data["color"] = "#9C27B0"  # 紫色
            node_data["shape"] = "diamond"  # 菱形表示批处理
        
        nodes.append(node_data)
    
    # 基于执行路径中节点的真实依赖关系生成边
    # 创建path中节点的uuid到节点的映射
    path_nodes = {str(node.uuid): node for node in path}
    path_uuids = set(path_nodes.keys())
    
    # 遍历执行路径中的每个节点，基于其after属性构建边
    edge_id = 0
    seen_edges = set()  # 避免重复边
    
    for node in path:
        if hasattr(node, 'after'):
            # 对于每个后继节点
            for next_node in node.after:
                # 确保后继节点也在执行路径中
                if str(next_node.uuid) in path_uuids:
                    edge_key = (str(node.uuid), str(next_node.uuid))
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        
                        edge_data = {
                            "from": str(node.uuid),
                            "to": str(next_node.uuid),
                            "arrows": "to",
                            "id": f"edge_{edge_id}"
                        }
                        
                        # 如果有上游节点的输出数据，添加到边的属性中
                        if str(node.uuid) in node_outputs:
                            edge_data["output_data"] = node_outputs[str(node.uuid)]
                        
                        edges.append(edge_data)
                        edge_id += 1
    
    # 生成当前Flow的标题信息，如果有错误则显示错误信息
    if error_info:
        flow_title = f"{flow.alias} ({str(flow.uuid)[:8]}) - ❌ 错误: {str(error_info)}"
        title_color = "#FF4444"  # 红色
    else:
        flow_title = f"{flow.alias} ({str(flow.uuid)[:8]})"
        title_color = "#FF6B00"  # 橙色
    
    # 准备Flow结果信息，包含错误信息
    if error_info and flow_result:
        flow_result["__error__"] = str(error_info)
    flow_result_json = json.dumps(flow_result, default=str, indent=2, ensure_ascii=False) if flow_result else "{}"
    
    # 生成 HTML
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>FlowMind Execution Visualization - {flow.alias}</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            height: 100vh;
        }}
        #mynetwork {{
            flex: 1;
            border: 1px solid #ddd;
        }}
        #info-panel {{
            width: 400px;
            padding: 20px;
            background: #f5f5f5;
            overflow-y: auto;
            border-left: 1px solid #ddd;
        }}
        #info-panel h2 {{
            margin-top: 0;
            color: #333;
        }}
        #info-box {{
            background: white;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .subflow-link {{
            display: inline-block;
            margin-top: 10px;
            padding: 8px 16px;
            background: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }}
        .subflow-link:hover {{
            background: #45a049;
        }}
        .header {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(255,255,255,0.9);
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            z-index: 1000;
        }}
        .flow-breadcrumb {{
            font-size: 16px;
            font-weight: bold;
            color: {title_color};
            margin-bottom: 10px;
        }}
        .flow-result-header {{
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 10px;
        }}
        pre {{
            overflow-x: auto;
            overflow-y: auto;
            max-height: 400px;
            word-wrap: break-word;
            white-space: pre-wrap;
        }}
        .back-button {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            background: #2196F3;
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            transition: all 0.3s;
            z-index: 1000;
        }}
        .back-button:hover {{
            background: #1976D2;
            transform: scale(1.1);
        }}
    </style>
</head>
<body>
    <div id="mynetwork"></div>
    <div id="info-panel">
        <h2>Flow执行结果</h2>
        <div id="info-box">
            <!-- 初始内容将由JavaScript生成 -->
        </div>
    </div>
    <div class="header">
        <div class="flow-breadcrumb">📍 当前Flow: {flow_title}</div>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>节点数: {len(nodes)} | 执行步骤: {len(edges)}</p>
    </div>
    
    {'<button class="back-button" onclick="window.location.href=\'' + parent_flow_html + '\'" title="返回父Flow">↑</button>' if parent_flow_html else ''}

    <script type="text/javascript">
        // 节点数据
        var nodes = new vis.DataSet({json.dumps(nodes, default=str)});
        
        // 边数据
        var edges = new vis.DataSet({json.dumps(edges, default=str)});
        
        // 保存Flow结果
        var flowResult = {flow_result_json};

        // 创建网络
        var container = document.getElementById('mynetwork');
        var data = {{
            nodes: nodes,
            edges: edges
        }};
        
        // 先使用hierarchical布局获取初始位置
        var tempOptions = {{
            layout: {{
                hierarchical: {{
                    direction: 'LR',
                    sortMethod: 'directed',
                    levelSeparation: 200,
                    nodeSpacing: 150
                }}
            }},
            physics: {{
                enabled: false
            }}
        }};
        
        // 创建临时网络以获取hierarchical布局的位置
        var tempNetwork = new vis.Network(container, data, tempOptions);
        
        // 获取所有节点的位置
        var positions = tempNetwork.getPositions();
        
        // 更新节点位置
        Object.keys(positions).forEach(function(nodeId) {{
            nodes.update({{
                id: nodeId,
                x: positions[nodeId].x,
                y: positions[nodeId].y
            }});
        }});
        
        // 销毁临时网络
        tempNetwork.destroy();
        
        // 使用非hierarchical布局重新创建网络
        var options = {{
            layout: {{
                hierarchical: false  // 禁用hierarchical布局
            }},
            physics: {{
                enabled: false,  // 禁用物理引擎，保持节点位置
                stabilization: false
            }},
            nodes: {{
                shape: 'dot',
                size: 30,
                font: {{
                    size: 14,
                    color: '#333'
                }},
                borderWidth: 2
            }},
            edges: {{
                width: 2,
                color: {{
                    color: '#848484',
                    highlight: '#2B7CE9'
                }},
                smooth: {{
                    type: 'cubicBezier',
                    forceDirection: 'horizontal',
                    roundness: 0.4
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200,
                dragNodes: true,  // 允许拖动节点
                dragView: true,   // 允许拖动视图
                zoomView: true    // 允许缩放
            }}
        }};
        
        var network = new vis.Network(container, data, options);

        // HTML转义函数 - 移到这里让所有函数都能使用
        function escapeHtml(text) {{
            var map = {{
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            }};
            return text.replace(/[&<>"']/g, function(m) {{ return map[m]; }});
        }}

        // 初始化显示Flow结果的函数
        function displayFlowResult() {{
            var resultHtml = '<div class="flow-result-header">📊 Flow: {flow.alias}</div>';
            
            // 如果有错误，优先显示错误信息
            if (flowResult.__error__) {{
                resultHtml += '<div style="margin-top: 10px; background: #ffebee; padding: 15px; border-radius: 4px; border-left: 4px solid #f44336;">';
                resultHtml += '<strong style="color: #d32f2f;">❌ 错误信息:</strong>';
                resultHtml += '<pre style="background: transparent; color: #b71c1c; margin-top: 5px; padding: 0;">';
                resultHtml += escapeHtml(flowResult.__error__);
                resultHtml += '</pre></div>';
            }}
            
            // 显示返回值
            resultHtml += '<div style="margin-top: 10px;">';
            resultHtml += '<strong>🔹 返回值:</strong>';
            var returnValue = flowResult.__flow_return_value__ || flowResult;
            resultHtml += '<pre style="background: #f0f8ff; padding: 10px; border-radius: 4px; margin-top: 5px;">';
            resultHtml += escapeHtml(JSON.stringify(returnValue, null, 2));
            resultHtml += '</pre></div>';
            
            // 显示Flow信息
            if (flowResult.__flow_info__) {{
                resultHtml += '<div style="margin-top: 15px;">';
                resultHtml += '<strong>🔹 Flow信息:</strong>';
                resultHtml += '<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; margin-top: 5px;">';
                resultHtml += escapeHtml(JSON.stringify(flowResult.__flow_info__, null, 2));
                resultHtml += '</pre></div>';
            }}
            
            document.getElementById('info-box').innerHTML = resultHtml;
        }}
        
        // 页面加载时显示Flow结果
        displayFlowResult();

        // 点击事件处理
        network.on("click", function (params) {{
            if (params.nodes.length > 0) {{
                // 点击节点
                var nodeId = params.nodes[0];
                var node = nodes.get(nodeId);
                
                var infoHtml = '<h3>节点信息: ' + node.label + '</h3>';
                // 对JSON字符串进行HTML转义
                var jsonStr = JSON.stringify(node.info, null, 2);
                infoHtml += '<pre>' + escapeHtml(jsonStr) + '</pre>';
                
                // 如果有子Flow链接
                if (node.info.subflow_html) {{
                    infoHtml += '<a href="' + node.info.subflow_html + '" class="subflow-link">查看子Flow详情</a>';
                }}
                
                document.getElementById('info-box').innerHTML = infoHtml;
                document.querySelector('#info-panel h2').textContent = '节点信息';
            }} else if (params.edges.length > 0) {{
                // 点击边 - 新增功能
                var edgeId = params.edges[0];
                var edge = edges.get(edgeId);
                
                var infoHtml = '<h3>边信息: 数据传递</h3>';
                
                // 显示从哪个节点到哪个节点
                var fromNode = nodes.get(edge.from);
                var toNode = nodes.get(edge.to);
                infoHtml += '<p><strong>从:</strong> ' + fromNode.label + ' → <strong>到:</strong> ' + toNode.label + '</p>';
                
                // 显示传递的数据
                if (edge.output_data !== undefined) {{
                    infoHtml += '<div style="margin-top: 10px;">';
                    infoHtml += '<strong>🔄 传递的数据:</strong>';
                    infoHtml += '<pre style="background: #e8f5e9; padding: 10px; border-radius: 4px; margin-top: 5px;">';
                    infoHtml += escapeHtml(JSON.stringify(edge.output_data, null, 2));
                    infoHtml += '</pre></div>';
                }} else {{
                    infoHtml += '<p style="color: #666; margin-top: 10px;">⚠️ 没有记录到传递的数据（可能是Flow的出口节点）</p>';
                }}
                
                document.getElementById('info-box').innerHTML = infoHtml;
                document.querySelector('#info-panel h2').textContent = '数据传递信息';
            }} else {{
                // 点击空白处时显示Flow结果
                document.querySelector('#info-panel h2').textContent = 'Flow执行结果';
                displayFlowResult();
            }}
        }});

        // 双击节点聚焦
        network.on("doubleClick", function (params) {{
            if (params.nodes.length > 0) {{
                network.focus(params.nodes[0], {{
                    scale: 1.5,
                    animation: true
                }});
            }}
        }});
    </script>
</body>
</html>'''
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


async def execute_with_visualization(
    flow: "BaseAgent",
    *,
    source_context: Any | None = None,
    shared_context: dict[str, Any] | None = None,
    concurrent_limit: int|None = None,
    **extra_ctxs
) -> Any:
    """
    执行 Flow 并生成可视化
    
    每个Flow完成后会立即生成对应的HTML文件
    
    Returns:
        执行结果
    """
    # 从flow的settings中获取log_dir，如果没有则使用默认值
    base_log_dir = flow.settings.get("log_dir", os.path.join(os.getcwd(), "memory", "default"))
    log_dir = os.path.join(base_log_dir, "visualization")
    os.makedirs(log_dir, exist_ok=True)
    
    observer: list[tuple[asyncio.Task[tuple[Any,bool]], BaseAgent]] = []
    
    # 使用字典来追踪每个Flow的执行路径
    flow_paths: dict[str, list[BaseAgent]] = {} 
    
    # 记录每个节点的输出数据
    node_outputs: dict[tuple[str, str], Any] = {}
    
    # 记录每个Flow的结果和错误信息
    flow_results: dict[str, Any] = {}
    flow_errors: dict[str, Exception] = {}
    flows: dict[str, Flow] = {}
    
    # 记录最终结果（按完成顺序记录的最后一个叶子节点结果）
    final_result = None
    
    # 执行 Flow
    await execute(flow, source_context=source_context, shared_context=shared_context, concurrent_limit=concurrent_limit, observer=observer, **extra_ctxs)
    
    # 参考 flow.py 的 task_queue 方式，简化处理逻辑
    try:
        while observer:
            # 只检查队列的第一个元素是否完成，避免阻塞
            if observer[0][0].done():
                # 第一个任务已完成，移除并处理
                task, agent = observer.pop(0)
                
                # 记录所属的Flow
                if isinstance(agent.parent, Flow):
                    flow_uuid = str(agent.parent.uuid)
                    if flow_uuid not in flows:
                        flows[flow_uuid] = agent.parent
                    if flow_uuid not in flow_paths:
                        flow_paths[flow_uuid] = []
                    flow_paths[flow_uuid].append(agent)
                
                if isinstance(agent, Flow):
                    flow_uuid = str(agent.uuid)
                    flows[flow_uuid] = agent
                
                # 获取任务结果（只有在确认完成后才await）
                try:
                    ret, leaf = await task
                    
                    # 记录节点输出（非叶子节点）
                    if isinstance(agent.parent, Flow) and not leaf:
                        flow_uuid = str(agent.parent.uuid)
                        node_outputs[(flow_uuid, str(agent.uuid))] = ret
                    
                    # 记录Flow的结果
                    if isinstance(agent, Flow):
                        flow_results[str(agent.uuid)] = ret
                    
                    # 如果是叶子节点，更新最终结果（保证是最后完成的）
                    if leaf:
                        final_result = ret
                        
                except Exception as e:
                    # 记录错误
                    if isinstance(agent.parent, Flow):
                        flow_errors[str(agent.parent.uuid)] = e
                    if isinstance(agent, Flow):
                        flow_errors[str(agent.uuid)] = e
                    raise e
            else:
                # 第一个任务还未完成，等待一小段时间
                await asyncio.sleep(0.01)
    finally:
        # 生成可视化文件
        for flow_uuid, flow_obj in flows.items():
            output_file = os.path.join(
                log_dir,
                f"{flow_obj.alias}_{flow_uuid[:8]}.html"
            )
            
            flow_execution_path = flow_paths.get(flow_uuid, [])
            flow_result_data = flow_results.get(flow_uuid, {})
            
            flow_result_data = {
                "__flow_return_value__": flow_result_data or "未记录",
                "__flow_info__": serialize_agent_info(flow_obj)
            }
            
            # 传递节点输出数据
            flow_node_outputs = {
                agent_uuid: node_outputs.get((flow_uuid, agent_uuid))
                for agent_uuid in [str(agent.uuid) for agent in flow_execution_path]
                if (flow_uuid, agent_uuid) in node_outputs
            }
            
            # 获取该Flow的错误信息（如果有）
            error_info = flow_errors.get(flow_uuid)
            
            generate_visjs_html(flow_obj, flow_execution_path, output_file, flow_result_data, flow_node_outputs, error_info)
    
    # 返回最终结果：优先返回顶层Flow的结果，否则返回最后完成的叶子节点结果
    top_flow_result = flow_results.get(str(flow.uuid))
    if top_flow_result is not None:
        return top_flow_result
    return final_result


# 测试函数
async def test_visualization():
    """测试可视化功能"""
    from .flow import Flow
    
    # 创建测试 Flow
    flow = Flow("test_flow", expected_shared_context_keys={"task"})
    flow.add_agent("base", alias="start", is_debug=True)
    flow.add_agent("base", alias="process")
    flow.add_agent("base", alias="end")
    
    # 添加边
    flow.add_edge("start", "process")
    flow.add_edge("process", "end")
    
    # 执行并可视化
    result = await execute_with_visualization(
        flow,
        source_context={"message": "Hello, FlowMind!"},
        shared_context={"task": "visualization test"},
        concurrent_limit=1
    )
    
    print(f"\n执行结果: {result}")


if __name__ == "__main__":
    asyncio.run(test_visualization())
# AgentOS2 项目脚手架
> LLM驱动的智能工作流系统，支持图结构编排、流程嵌套、双层并发架构

## 📌 项目结构
```
agent_os2/
├── agent_os/              # 核心框架
│   ├── base_agent.py      # Agent抽象
│   ├── flow.py            # DAG调度器  
│   ├── base_model/        # 模型接口
│   ├── utility.py         # 工具函数
│   └── visualize.py       # 可视化
├── agents/examples/       # 示例
├── agent_settings.json    # Agent配置
├── model_settings.json    # 模型配置
└── DEVELOPING_GUIDE.md    # 开发指南
```

## 🚀 核心特性

### 一、BaseAgent

#### 1.1 生命周期
✅ **已完成**: 标准流程(`激活→批处理→执行→下发`) | 三阶段(`setup`/`pipeline`/`post_process`) | 纯函数特性

#### 1.2 上下文系统  
✅ **已完成**: Settings(构建时继承) | Args/SharedContext/ExtraContexts(运行时) | 模板系统(`{src.*}`/`{ctx.*}`) | 深度合并  
⏳ **未完成**: 上下文压缩 | RAG/KAG集成

#### 1.3 批处理
✅ **已完成**: `batch_field` | 批处理索引 | 双层并发架构

#### 1.4 模型交互
✅ **已完成**: 统一接口 | 智能重试 | 超时控制 | 严格模式 | JSON校验 | 模型配置优先级加载 | 为自动模型选择提供接口

#### 1.5 日志系统
✅ **已完成**: user_info | debug_info | 批处理标识 | 即时输出

#### 1.6 agent_command
✅ **已完成**: memory(替换更新Shared Context) | memory_append(追加更新Shared Context) | actions(修改图结构) | add_context(注入接口对象) | 可扩展

### 二、Flow

#### 2.1 图结构调度
✅ **已完成**: 有向图依赖 | 拓扑并发 | 动态修改 | 循环/条件分支  
⏳ **未完成**: 分布式调度 | 远程执行

#### 2.2 Flow功能
✅ **已完成**: Agent/Flow一体化 | YAML DSL | 入口管理 | 别名机制 | 热重载 | Agent类对象注入机制 | 注册系统

#### 2.3 上下文隔离  
✅ **已完成**: 父子隔离 | 按需继承(`expected_shared_context_keys`) | 动态更新 | 优化传递

#### 2.4 执行统计
✅ **已完成**: 资源限制(`max_*_limit`) | 性能指标 | 执行可视化 | flow_results

### 三、辅助系统

#### 3.1 模型系统
✅ **已完成**: Processor注册 | ModelConfig | 内置多模型配置 | 流式输出 | 多模态输入解析 | 多轮对话 | 多模态输出

#### 3.2 工具函数
✅ **已完成**: DSL解析 | Agent发现 | JSON解析 | 字典合并 | 模板解析  
⏳ **未完成**: Token压缩 | RAG/KAG工具

#### 3.3 执行接口
✅ **已完成**: execute() | 可视化执行 | 单Agent测试 | 双模式 | 并发限制 | observer  
⏳ **未完成**: 分布式执行 | MCP插件

## 📖 最新更新
- **上下文传递优化**: 只传递存在的键，改进get()行为

## 🔗 相关文档
- [DEVELOPING_GUIDE.md](DEVELOPING_GUIDE.md) - 详细开发指南
- [examples/](examples/) - 示例工作流

## 🚀 快速体验 (Quick Start)

跟随以下步骤，快速体验 AgentOS2 的强大功能。

### 1. 配置模型

首先，您需要在项目根目录下创建一个文件夹 `aos_config`，并在其中创建一个 `model_settings.json` 文件。这是AgentOS2寻找模型配置的地方。

**`./aos_config/model_settings.json` 内容示例:**
```json
{
    "google-chat":{
        "api_key":"YOUR_GEMINI_API_KEY",
        "base_url":"",
        "proxy":"",
        "models":[
            "gemini-2.5-flash"
        ]
    }
}
```
> **提示**: 请将 `"YOUR_GEMINI_API_KEY"` 替换为您自己的API密钥。AgentOS2的内置示例默认使用`gemini-2.5-flash`模型，您也可以根据需要配置其他模型，例如 `lite-llm-chat` 或 `openai-chat`。

### 2. 运行内置示例

项目自带了一个“故事生成”的示例，让您无需编写代码即可感受AgentOS2的流程编排能力。

创建一个Python文件（例如 `run_example.py`）并添加以下代码：

```python
import asyncio
from agent_os2.examples.story_generate_example import start_story_generate

async def main():
    # 故事生成示例的入口函数
    # 你可以修改 user_input 来尝试不同的故事主题
    user_input = "我想听一个关于一只勇敢的小猫去外太空探险的故事"
    result = await start_story_generate(user_input)
    print("流程执行完毕，最终结果:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. 查看可视化结果

运行 `run_example.py` 后，程序会自动在执行目录下的 `memory/` 文件夹中生成一个带时间戳的子目录，例如 `memory/statistics_20240730-103000`。

进入该目录，找到并用浏览器打开 `visualization.html` 文件。您将看到一个交互式流程图，清晰地展示了“故事生成”工作流中每个Agent的执行顺序、输入输出和最终结果。
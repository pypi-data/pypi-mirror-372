# 1.2.4 2025.8.28
    1. 新增命令支持：memory_append，用于向shared_context中追加数据，追加优先级为True
    2. 当不存在对应的前缀时，内部会保留该解析块原样，而不是解析为str(None)
    3. 删除当前prompts用不上的格式list[dict[str,str]]，因为这根本无法基于目前的结构构建历史记录，dict[str,str]格式足以。
    4. 支持新的以str为标准的连续对话格式标准
    5. 优化了merge_elements策略，str会自动拼接，int/float会自动相加
    6. 为self.user_info添加了tag="launch_tips"，用于在启动时输出提示信息
    7. 优化了json解析失败的错误提示，不再显示完整的错误原文
    8. 将错误hint调整为system_prompt，并且至于顶层
    9. 将get_input改为非阻塞事件循环的异步函数
    10. 修复了内置processor的process_chunk默认行为，现在会自动返回原始数据，否则process_complete无法获取积累的数据
    11. 实测GPTImage1的流式模式，并且完善GPTImage1模型配置的默认可选参数
    12. 为BaseProcessor的process_chunk和process_complete添加了model_config参数，用于在处理chunk和complete时获取模型配置
    13. BaseProcessor的process_complete现在收到的是原始的chunks而不是处理后的chunks
    14. 内置支持对dall-e-2和dall-e-3的cost计算
    15. 增强内置OpenAIChatProcessor和GoogleChatProcessor，支持多模态输入解析
    16. 添加对Google-Imagen类型的模型内置支持
    17. 将ProcessorError改名为ModelError，明确远端服务器发来的错误才会触发重试，一般代码的逻辑错误直接抛出异常
    18. 将memory命令重命名为语义更加明确的memory_modify，用于向shared_context**替换优先**的更新数据
    19. merge_elements处理字典时会自动删除值为None的键，实现了CRUD中的删除功能
    20. 重构examples flow的文件夹编排方式，初步内置assistantAPI
    21. 重构utility的_find_agent_class，明确了Agent存在相对路径导入会失败的要点，明确动态注册的agent需要填写__package__
    22. 支持fallback加载agent_os2/agent_settings.json为默认加载的agents_key，更加用户友好的使用内置example
    23. 支持通过环境变量AOS_MODEL_SETTINGS_PATH指定model_settings.json的路径，默认加载执行目录/aos_config/model_settings.json
    24. 将args，input_args规范名称未source_context,与src对应，中文名为源上下文
    25. 因为parse_model_result会可能会get一些异步的额外上下文，改为异步函数
    26. 支持gemini-2.5-flash-image-preview生图模型
# 1.2.3 2025.8.15
    1. 减少了一句因尝试加载Agent失败而产生的print
    2. 更加明确shared_context与extra_contexts的差异和职责。shared_context是flow内所有agent的共享上下文，并且是一个可序列化字典，而extra_contexts是一个会自动向下传递接口对象字典，子Flow的extra_contexts是父Flow的extra_contexts的浅拷贝
    3. 修改对是否是同一个"类对象"的判断方式，放松判断条件。
    4. 修复visualize对执行完毕的元素顺序判断错乱的问题（依赖条件触发）
    5. 增加命令：add_context，用于向extra_contexts注入新的接口对象
    6. 优化了utility中get_context_value的实现，现在这个工具函数变得更加通用了
    7. 优化了DEVELOPING_GUIDE.md，添加了更多关于shared_context与extra_contexts的说明
    8. 减少actions中的命令，将add_*_branch命令合并为add_branch命令，将insert_*命名合并为insert命令，保留dsl键作为构建flow的特工
    9. 将command_to_flow命令重命名为agent_command，明确语义
    10. 优化自动注册机制，防止重复的模块加载
    11. 优化了model_processor内部的逻辑，提高复用性和规范性
    12. 重置了ModelConfig，穷举了常见的模型配置，并为其适配可选默认参数，删除了宽泛的LLMConfig
    13. 为ModelConfig添加基于__init_subclass__的自动注册机制和基于分词的智能匹配功能，支持通过模型名称(如claude-opus-4-20250514)自动匹配到对应的配置类，同时新增GPT4、ClaudeOpus4等模型配置类
# 1.2.2 2025.8.6
    1. 为stdout添加tag参数，用于区分不同类型的输出
    2. 优化报错信息，提示更加具体指明问题原因
    3. 优化agent_settings.json的注册机制，支持多种命名映射方式
# 1.2.1 2025.8.5
    1. 添加settings属性中对model_config配置的支持，并且明确优先级：Agent内setup设置的ModelConfig>settings中的model_config>LLMConfig的构造默认值
# 1.2.0 
    项目正式发布版本，全部流程基本稳定
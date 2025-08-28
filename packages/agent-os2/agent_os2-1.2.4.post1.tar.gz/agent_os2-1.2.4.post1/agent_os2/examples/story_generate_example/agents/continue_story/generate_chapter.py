from agent_os2 import BaseAgent
from typing import Any
import os

class GenerateChapterAgent(BaseAgent):
    """续写故事：配置提示词，模型返回纯文本章节内容，并自动迭代至下一章"""
    
    def setup(self):
        current_chapter = self.settings.get("current_chapter", 1)
        
        # 构建正确的prompt模板
        prompt = f"""
请根据以下信息续写小说第{current_chapter}章：

【选定题目】
{{ctx.best_story_title}}

【故事背景】
{{ctx.story_background}}

【人物设定】
{{ctx.character_settings}}

【当前章节】第{current_chapter}章

【章节大纲】
标题：{{ctx.chapters.{current_chapter}.title}}
内容要求：{{ctx.chapters.{current_chapter}.content}}

【前面章节内容参考】
{{ctx.completed_chapters}}

【续写要求】
1. 请写出完整的第{current_chapter}章内容
2. 章节要有明确的开头、发展和结尾
3. 字数控制在3000-5000字
4. 严格按照大纲要求发展情节
5. 保持与前面章节的连贯性
6. 语言要生动有趣
7. 请直接开始写内容，不要加额外描述

开头格式：
--- 
## {{ctx.chapters.{current_chapter}.title}}
---

请开始续写：
"""
        
        self.prompts = {
            "system": "你是一个专业的作家，负责根据大纲续写小说章节。",
            "user": prompt
        }
        self.strict_mode = False
        self.user_info = f"## 正在续写第{current_chapter}章...\n"
        self.retry_count = 2
        self.batch_field = ""

    async def post_process(self,
                            source_context:Any,
                            llm_result: Any,
                            shared_context: dict[str, Any],
                            extra_contexts: dict[str, Any],
                            observer: list[tuple[Any, BaseAgent]],
                            batch_id: int | None = None
                          ) -> tuple[Any,dict[str,dict|list]]:
        from agent_os2 import record_user_info
        
        # 获取当前章节号
        current_chapter = self.settings.get("current_chapter", 1)
        total_chapters = shared_context.get("total_chapters", 0)
        
        # 记录进度
        record_user_info(self, 
                        f"✅ 第{current_chapter}章已完成！\n📖 进度：{current_chapter}/{total_chapters}\n\n", None)
        
        # 保存当前章节到上下文
        agent_command = {
            "memory_modify": {
                f"chapter_{current_chapter}": llm_result
            }
        }
        
        # 检查是否还有下一章需要续写
        if current_chapter < total_chapters:
            # 插入下一章的续写agent
            next_chapter = current_chapter + 1
            record_user_info(self, 
                            f"🔄 准备续写第{next_chapter}章...\n\n", None)
            # 获取已完成章节列表
            completed_chapters = shared_context.get("completed_chapters", [])
            agent_command["memory_modify"] = {
                "completed_chapters": completed_chapters + [llm_result]
            }
            agent_command["actions"] = [{
                "insert": {
                    "name": "generate_chapter",
                    "settings": {
                        "current_chapter": next_chapter
                    }
                }
            }]
        else:
            # 所有章节完成，插入简单保存agent
            record_user_info(self, 
                            f"🎉 所有章节已完成！准备保存故事...\n\n", None)
            
            agent_command["actions"] = [{
                "add_branch":{
                    "name":"save_simple_story"
                }
            }]
        
        return {},agent_command


        
import openai
import base64
import json
import re
import asyncio
import logging
from openai import NotFoundError, BadRequestError
from datetime import datetime
from src.mcp.client import get_mcp_manager
from src.models.user import db

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = None
        self.api_url = None
        self.api_key = None
        self.model = None

    def test_connection(self):
        """测试与AI服务的连通性"""
        # 重新加载配置
        self._load_config()
        if not self.client:
            return False, "AI服务未配置"
        try:
            # 调用一个轻量级接口验证连接
            self.client.models.list()
            return True, "连接成功"
        except Exception as e:
            return False, f"连接异常: {str(e)}"
    
    def _load_config(self):
        """加载AI配置。

        当配置不完整或缺少API密钥时，主动清除已有的客户端实例，防止沿用过期配置。
        """
        try:
            from src.models.diary import Config

            api_url_config = Config.query.filter_by(key='ai_api_url').first()
            api_key_config = Config.query.filter_by(key='ai_api_key').first()
            model_config = Config.query.filter_by(key='ai_model').first()

            # 判断配置是否完整且包含有效的API密钥
            if api_url_config and api_key_config and model_config and api_key_config.value:
                self.api_url = api_url_config.value
                self.api_key = api_key_config.value
                self.model = model_config.value

                # 初始化OpenAI客户端
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.api_url
                )
            else:
                # 配置不完整或缺少密钥，清除已有实例并打印警告
                if any([self.client, self.api_url, self.api_key, self.model]):
                    logger.warning("AI配置不完整或缺失，已清除旧的AI客户端配置")
                self.client = None
                self.api_url = None
                self.api_key = None
                self.model = None
        except Exception as e:
            # 如果加载配置失败，也要清除配置，避免复用旧实例
            self.client = None
            self.api_url = None
            self.api_key = None
            self.model = None
            logger.error(f"加载AI配置失败: {e}")
    
    def _encode_image(self, image_path):
        """将图片编码为base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"图片编码失败: {e}")
            return None

    def _extract_text_from_message(self, message):
        """从AI返回的消息中提取纯文本内容，兼容思考类型模型"""
        if not message:
            return ""

        content = getattr(message, "content", "")

        # 传统模型直接返回字符串
        if isinstance(content, str):
            return content.strip()

        # 思考类型模型可能返回内容列表
        if isinstance(content, list):
            text_parts = []
            for part in content:
                part_type = getattr(part, "type", None)
                if isinstance(part, dict):
                    part_type = part.get("type", part_type)
                # 跳过纯思考过程，只保留最终文本
                if part_type and part_type not in ("thinking", "reasoning"):
                    text = getattr(part, "text", None)
                    if isinstance(part, dict):
                        text = part.get("text", text)
                    if text:
                        text_parts.append(text)
            return "".join(text_parts).strip()

        return ""

    def _call_ai_api(self, messages, max_tokens, temperature):
        """调用底层AI接口，兼容Chat Completions和Responses API"""
        # 优先尝试 Chat Completions 接口
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return self._extract_text_from_message(response.choices[0].message)
        except (NotFoundError, BadRequestError, AttributeError):
            # 若接口不存在或不支持，尝试新的 Responses API
            response = self.client.responses.create(
                model=self.model,
                input=messages,
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
            # Responses API 提供 output_text 字段作为最终文本
            if getattr(response, "output_text", None):
                return response.output_text.strip()
            # 兼容旧结构，提取第一个输出消息
            output = getattr(response, "output", None)
            if output:
                return self._extract_text_from_message(output[0])
            return ""
    
    def analyze_entry(self, text_content=None, image_path=None, user_id=None):
        """分析日记条目（增强版，支持用户上下文）"""
        # 重新加载配置
        self._load_config()
        
        if not self.client:
            return "AI服务未配置"
        
        try:
            from src.models.diary import Config
            
            # 获取提示词模板
            prompt_config = Config.query.filter_by(key='ai_prompt_template').first()
            base_prompt = prompt_config.value if prompt_config else "请分析这个用户的日记内容，猜测用户在做什么。"
            
            # 获取用户上下文（如果提供了用户ID）
            user_context = ""
            if user_id:
                context_data = self._get_user_context_sync(user_id, text_content or "")
                if context_data and context_data.get('memories'):
                    memories = context_data['memories'][:5]  # 限制到最相关的5条记忆
                    if memories:
                        user_context = "\n\n用户背景信息（请在回复中自然体现对用户的了解）：\n"
                        for memory in memories:
                            user_context += f"- {memory['key']}: {memory['value']}\n"
            
            # 增强提示词
            enhanced_prompt = base_prompt + user_context
            
            # 构建用户消息
            user_content = []
            
            # 如果有图片，优先处理图片
            if image_path:
                # 编码图片
                base64_image = self._encode_image(image_path)
                if base64_image:
                    user_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    })
            
            # 构建文字内容，将系统提示词融入用户消息中
            text_prompt = enhanced_prompt + "\n\n"
            
            # 添加文字内容（如果有的话）
            if text_content:
                text_prompt += f"文字内容：{text_content}"
            elif image_path:
                # 如果只有图片没有文字，添加默认提示
                text_prompt += "请分析这张图片中的内容。"
            
            user_content.append({
                "type": "text",
                "text": text_prompt
            })
            
            if not user_content:
                return "没有内容可分析"
            
            # 根据是否有图片选择不同的消息格式
            if image_path:
                # 图片分析接口：只使用user角色，不使用system角色
                messages = [{
                    "role": "user",
                    "content": user_content
                }]
            else:
                # 纯文本接口：可以使用system角色
                messages = [
                    {
                        "role": "system",
                        "content": enhanced_prompt
                    },
                    {
                        "role": "user",
                        "content": text_content or "请进行分析。"
                    }
                ]

            # 调用AI API
            ai_response = self._call_ai_api(
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            # 在后台线程中处理记忆提取（不阻塞响应）
            if user_id:
                import threading
                memory_thread = threading.Thread(
                    target=self._extract_and_store_memories_sync,
                    args=(user_id, text_content, ai_response, image_path)
                )
                memory_thread.daemon = True
                memory_thread.start()
            
            return ai_response
            
        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            return f"AI分析失败: {str(e)}"
    
    def _get_user_context_sync(self, user_id, content):
        """获取用户上下文信息（同步版本）- 改进资源管理"""
        loop = None
        try:
            mcp_manager = get_mcp_manager(db.session)
            if mcp_manager and mcp_manager.builtin_usermcp:
                # 创建临时事件循环运行异步代码，确保正确关闭
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return loop.run_until_complete(
                    mcp_manager.query_user_context(user_id, content)
                )
            return {}
        except Exception as e:
            logger.error(f"获取用户上下文失败: {e}")
            return {}
        finally:
            # 确保事件循环被正确关闭
            if loop:
                try:
                    loop.close()
                except Exception as close_e:
                    logger.error(f"关闭事件循环失败: {close_e}")
    
    async def _get_user_context(self, user_id, content):
        """获取用户上下文信息"""
        try:
            mcp_manager = get_mcp_manager(db.session)
            if mcp_manager and mcp_manager.builtin_usermcp:
                return await mcp_manager.query_user_context(user_id, content)
            return {}
        except Exception as e:
            logger.error(f"获取用户上下文失败: {e}")
            return {}
    
    def _extract_and_store_memories_sync(self, user_id, content, ai_response, image_path=None):
        """同步版本的记忆提取和存储（用于线程调用）- 避免循环导入"""
        loop = None
        try:
            # 避免循环导入 - 延迟导入
            import sys
            if 'src.main' in sys.modules:
                app = sys.modules['src.main'].app
                with app.app_context():
                    # 创建新的事件循环（因为线程中没有事件循环），确保正确关闭
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(
                        self._extract_and_store_memories(user_id, content, ai_response, image_path)
                    )
            else:
                logger.warning("应用上下文不可用，跳过记忆存储")
                    
        except Exception as e:
            logger.error(f"同步提取存储记忆失败: {e}")
        finally:
            # 确保事件循环被正确关闭
            if loop:
                try:
                    loop.close()
                except Exception as close_e:
                    logger.error(f"关闭事件循环失败: {close_e}")
    
    async def _extract_and_store_memories(self, user_id, content, ai_response, image_path=None):
        """提取并存储用户记忆"""
        try:
            mcp_manager = get_mcp_manager(db.session)
            if not mcp_manager or not mcp_manager.builtin_usermcp:
                return
            
            # 使用AI提取记忆信息
            memories_to_store = await self._extract_memories_with_ai(content, ai_response)
            
            # 存储记忆
            for memory in memories_to_store:
                await mcp_manager.builtin_usermcp.insert_user_profile(
                    key=memory['key'],
                    value=memory['value'],
                    user_id=user_id,
                    memory_type=memory['type'],
                    confidence=memory.get('confidence', 0.8)
                )
                
        except Exception as e:
            logger.error(f"提取存储记忆失败: {e}")
    
    async def _extract_memories_with_ai(self, content, ai_response):
        """使用AI提取记忆信息"""
        if not self.client:
            return []
        
        try:
            extraction_prompt = """
            分析用户的日记内容和AI理解，提取可以记忆的用户信息。
            请返回JSON格式的记忆列表，每个记忆包含：key（简短关键词），value（具体描述），type（类型：preference/habit/fact/emotion/experience）
            
            示例输出：
            [
                {"key": "兰州拉面", "value": "喜欢吃，觉得味道很棒", "type": "preference"},
                {"key": "运动习惯", "value": "喜欢晨跑", "type": "habit"}
            ]
            
            如果没有明显的记忆信息，返回空数组 []
            """
            
            messages = [
                {"role": "system", "content": extraction_prompt},
                {"role": "user", "content": f"日记内容：{content}\n\nAI理解：{ai_response}"}
            ]
            result = self._call_ai_api(
                messages=messages,
                max_tokens=300,
                temperature=0.3
            )
            
            # 尝试解析JSON
            try:
                memories = json.loads(result)
                if isinstance(memories, list):
                    # 验证每个记忆的格式
                    valid_memories = []
                    for memory in memories:
                        if (isinstance(memory, dict) and 
                            'key' in memory and 'value' in memory and 'type' in memory):
                            valid_memories.append(memory)
                    return valid_memories
                return []
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试正则提取
                return self._extract_memories_with_regex(result)
                
        except Exception as e:
            logger.error(f"AI提取记忆失败: {e}")
            return []
    
    def _extract_memories_with_regex(self, text):
        """使用正则表达式作为备用方案提取记忆"""
        try:
            # 简单的关键词匹配
            memories = []
            
            # 偏好模式
            preference_patterns = [
                r'喜欢([^，。！？\n]+)',
                r'爱吃([^，。！？\n]+)',
                r'不喜欢([^，。！？\n]+)',
            ]
            
            for pattern in preference_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if match.strip():
                        memories.append({
                            "key": match.strip(),
                            "value": f"用户提到了关于 {match.strip()} 的偏好",
                            "type": "preference"
                        })
            
            return memories[:3]  # 最多返回3个
            
        except Exception as e:
            logger.error(f"正则提取记忆失败: {e}")
            return []
    
    def generate_daily_summary(self, entries):
        """生成每日汇总"""
        # 重新加载配置
        self._load_config()
        
        if not self.client:
            return "AI服务未配置"
        
        try:
            from src.models.diary import Config
            
            # 获取汇总提示词
            summary_prompt_config = Config.query.filter_by(key='ai_summary_prompt').first()
            summary_prompt = summary_prompt_config.value if summary_prompt_config else "请根据用户今天的所有日记条目，生成一份完整的日记总结。"
            
            # 构建条目内容
            entries_text = ""
            for i, entry in enumerate(entries, 1):
                entry_time = entry.timestamp.strftime("%H:%M")
                entries_text += f"\n{i}. {entry_time} - "
                
                if entry.text_content:
                    entries_text += f"文字：{entry.text_content} "
                
                if entry.ai_analysis:
                    entries_text += f"AI理解：{entry.ai_analysis}"
                
                entries_text += "\n"
            
            messages = [
                {
                    "role": "system",
                    "content": summary_prompt
                },
                {
                    "role": "user",
                    "content": f"今天的日记条目：{entries_text}"
                }
            ]

            # 调用AI API
            return self._call_ai_api(
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
        except Exception as e:
            logger.error(f"生成日记汇总失败: {e}")
            return f"生成日记汇总失败: {str(e)}"

# 全局AI服务实例
ai_service = AIService()


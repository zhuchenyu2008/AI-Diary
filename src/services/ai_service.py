import openai
import base64
import json
from datetime import datetime

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
        """加载AI配置"""
        try:
            from src.models.diary import Config
            
            api_url_config = Config.query.filter_by(key='ai_api_url').first()
            api_key_config = Config.query.filter_by(key='ai_api_key').first()
            model_config = Config.query.filter_by(key='ai_model').first()
            
            if api_url_config and api_key_config and model_config:
                self.api_url = api_url_config.value
                self.api_key = api_key_config.value
                self.model = model_config.value
                
                # 初始化OpenAI客户端
                if self.api_key:
                    self.client = openai.OpenAI(
                        api_key=self.api_key,
                        base_url=self.api_url
                    )
            else:
                print("AI配置不完整，请检查配置")
        except Exception as e:
            print(f"加载AI配置失败: {e}")
    
    def _encode_image(self, image_path):
        """将图片编码为base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"图片编码失败: {e}")
            return None
    
    def analyze_entry(self, text_content=None, image_path=None):
        """分析日记条目"""
        # 重新加载配置
        self._load_config()
        
        if not self.client:
            return "AI服务未配置"
        
        try:
            from src.models.diary import Config
            
            # 获取提示词模板
            prompt_config = Config.query.filter_by(key='ai_prompt_template').first()
            prompt_template = prompt_config.value if prompt_config else "请分析这个用户的日记内容，猜测用户在做什么。"
            
            messages = [
                {
                    "role": "system",
                    "content": prompt_template
                }
            ]
            
            # 构建用户消息
            user_content = []
            
            if text_content:
                user_content.append({
                    "type": "text",
                    "text": f"文字内容：{text_content}"
                })
            
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
            
            if not user_content:
                return "没有内容可分析"
            
            messages.append({
                "role": "user",
                "content": user_content
            })
            
            # 调用AI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"AI分析失败: {e}")
            return f"AI分析失败: {str(e)}"
    
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"生成日记汇总失败: {e}")
            return f"生成日记汇总失败: {str(e)}"

# 全局AI服务实例
ai_service = AIService()


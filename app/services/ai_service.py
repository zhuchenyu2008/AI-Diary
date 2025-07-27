import asyncio
from typing import Optional
import openai
import anthropic
import google.generativeai as genai
from app.core.config import settings


class AIService:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.google_client = None
        
        # 初始化OpenAI客户端
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            openai.api_base = settings.openai_base_url
            self.openai_client = openai

        # 初始化Anthropic客户端
        if settings.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(
                api_key=settings.anthropic_api_key,
                base_url=settings.anthropic_base_url,
            )

        # 初始化Google客户端
        if settings.google_api_key:
            genai.configure(
                api_key=settings.google_api_key,
                client_options={"api_endpoint": settings.google_base_url},
            )
            self.google_client = genai
    
    async def analyze_moment(self, text: Optional[str] = None, image_url: Optional[str] = None) -> str:
        """分析瞬间内容，生成描述"""
        if not text and not image_url:
            return "无内容可分析"
        
        # 构建提示词
        prompt = self._build_moment_prompt(text, image_url)
        
        # 尝试不同的AI服务
        try:
            if self.openai_client:
                return await self._analyze_with_openai(prompt, image_url)
            elif self.anthropic_client:
                return await self._analyze_with_anthropic(prompt, image_url)
            elif self.google_client:
                return await self._analyze_with_google(prompt, image_url)
            else:
                return "AI服务未配置"
        except Exception as e:
            return f"AI分析失败: {str(e)}"
    
    def _build_moment_prompt(self, text: Optional[str], image_url: Optional[str]) -> str:
        """构建分析提示词"""
        prompt = "请分析这个生活瞬间，用简洁生动的语言描述其中的情感、场景和意义。"
        
        if text:
            prompt += f"\n\n用户文字: {text}"
        
        if image_url:
            prompt += f"\n\n图片URL: {image_url}"
        
        prompt += "\n\n请用中文回复，描述要自然流畅，体现生活的美好。"
        return prompt
    
    async def _analyze_with_openai(self, prompt: str, image_url: Optional[str] = None) -> str:
        """使用OpenAI分析"""
        try:
            if image_url:
                # 如果有图片，使用自定义视觉模型
                response = await asyncio.to_thread(
                    self.openai_client.ChatCompletion.acreate,
                    model=settings.openai_vision_model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": image_url}}
                            ]
                        }
                    ],
                    max_tokens=300
                )
            else:
                # 纯文字使用自定义模型
                response = await asyncio.to_thread(
                    self.openai_client.ChatCompletion.acreate,
                    model=settings.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300
                )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI分析失败: {str(e)}")
    
    async def _analyze_with_anthropic(self, prompt: str, image_url: Optional[str] = None) -> str:
        """使用Anthropic分析"""
        try:
            if image_url:
                # Claude支持图片分析
                response = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model=settings.anthropic_vision_model,
                    max_tokens=300,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image", "source": {"type": "url", "url": image_url}}
                            ]
                        }
                    ]
                )
            else:
                response = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model=settings.anthropic_model,
                    max_tokens=300,
                    messages=[{"role": "user", "content": prompt}]
                )
            
            return response.content[0].text.strip()
        except Exception as e:
            raise Exception(f"Anthropic分析失败: {str(e)}")
    
    async def _analyze_with_google(self, prompt: str, image_url: Optional[str] = None) -> str:
        """使用Google Gemini分析"""
        try:
            model_name = settings.google_vision_model if image_url else settings.google_model
            model = self.google_client.GenerativeModel(model_name)
            
            if image_url:
                # 需要下载图片数据
                import requests
                response = requests.get(image_url)
                image_data = response.content
                
                response = await asyncio.to_thread(
                    model.generate_content,
                    [prompt, image_data],
                    generation_config={"max_output_tokens": 300}
                )
            else:
                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                    generation_config={"max_output_tokens": 300}
                )
            
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Google分析失败: {str(e)}")
    
    async def generate_daily_summary(self, moments_data: list) -> str:
        """生成每日总结"""
        if not moments_data:
            return "今天没有记录任何瞬间。"
        
        # 构建总结提示词
        prompt = "请根据以下今天的生活瞬间，生成一篇完整的日记。要求：\n"
        prompt += "1. 语言生动自然，体现生活的美好\n"
        prompt += "2. 结构完整，有开头、主体和结尾\n"
        prompt += "3. 情感真挚，体现个人特色\n"
        prompt += "4. 用中文写作\n\n"
        prompt += "今天的瞬间记录：\n"
        
        for i, moment in enumerate(moments_data, 1):
            prompt += f"{i}. {moment}\n"
        
        prompt += "\n请生成一篇完整的日记："
        
        # 使用AI生成总结
        try:
            if self.openai_client:
                response = await asyncio.to_thread(
                    self.openai_client.ChatCompletion.acreate,
                    model=settings.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=800
                )
                return response.choices[0].message.content.strip()
            elif self.anthropic_client:
                response = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model=settings.anthropic_model,
                    max_tokens=800,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
            elif self.google_client:
                model = self.google_client.GenerativeModel(settings.google_model)
                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                    generation_config={"max_output_tokens": 800}
                )
                return response.text.strip()
            else:
                return "AI服务未配置，无法生成日记"
        except Exception as e:
            return f"生成日记失败: {str(e)}" 
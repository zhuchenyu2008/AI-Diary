"""
默认配置管理模块
统一管理应用的默认配置，避免重复定义
"""
import os

def load_prompt_from_file(filename):
    """从文件加载提示词"""
    try:
        prompt_file = os.path.join(os.path.dirname(__file__), 'prompts', filename)
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        # 如果文件不存在，返回简化的默认提示词
        if 'analysis' in filename:
            return "请分析这个用户的日记内容（包括文字和图片），猜测用户在做什么，用简洁的中文描述用户的活动和心情。"
        else:
            return "请根据用户今天的所有日记条目，生成一份完整的日记总结。总结应该包含今天的主要活动、心情变化和重要事件。"

def get_default_configs():
    """获取默认配置列表"""
    return [
        {
            'key': 'ai_api_url',
            'value': 'https://api.openai.com/v1',
            'description': 'AI API地址'
        },
        {
            'key': 'ai_api_key',
            'value': '',
            'description': 'AI API密钥'
        },
        {
            'key': 'ai_model',
            'value': 'gpt-3.5-turbo',
            'description': 'AI模型名称'
        },
        {
            'key': 'ai_prompt_template',
            'value': load_prompt_from_file('ai_analysis_prompt.txt'),
            'description': 'AI分析提示词模板'
        },
        {
            'key': 'ai_summary_prompt',
            'value': load_prompt_from_file('ai_summary_prompt.txt'),
            'description': 'AI每日汇总提示词'
        },
        {
            'key': 'telegram_bot_token',
            'value': '',
            'description': 'Telegram机器人Token'
        },
        {
            'key': 'telegram_chat_id',
            'value': '',
            'description': 'Telegram聊天ID'
        },
        {
            'key': 'telegram_enabled',
            'value': 'false',
            'description': '是否启用Telegram推送'
        }
    ]
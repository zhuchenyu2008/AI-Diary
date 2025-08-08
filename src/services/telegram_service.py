import requests
import json
import logging

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self):
        self.bot_token = None
        self.chat_id = None
        self.enabled = False
    
    def _load_config(self):
        """加载Telegram配置。

        如果配置不完整，则重置已加载的配置，避免残留旧值导致误判。
        """
        try:
            from src.models.diary import Config

            token_config = Config.query.filter_by(key='telegram_bot_token').first()
            chat_id_config = Config.query.filter_by(key='telegram_chat_id').first()
            enabled_config = Config.query.filter_by(key='telegram_enabled').first()

            # 如果token和chat_id均存在，则使用它们；否则清除所有配置
            if token_config and chat_id_config and token_config.value and chat_id_config.value:
                self.bot_token = token_config.value.strip() if token_config.value else None
                self.chat_id = chat_id_config.value.strip() if chat_id_config.value else None
                self.enabled = enabled_config.value.lower() == 'true' if enabled_config and enabled_config.value else False
            else:
                # 配置不完整，清除旧配置
                if any([self.bot_token, self.chat_id, self.enabled]):
                    logger.warning("Telegram配置不完整，已重置旧值")
                self.bot_token = None
                self.chat_id = None
                self.enabled = False
        except Exception as e:
            # 出现异常时也清除配置
            self.bot_token = None
            self.chat_id = None
            self.enabled = False
            logger.error(f"加载Telegram配置失败: {e}")
    
    def send_message(self, text):
        """发送消息到Telegram"""
        # 重新加载配置
        self._load_config()
        
        if not self.enabled or not self.bot_token or not self.chat_id:
            logger.warning("Telegram服务未启用或配置不完整")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info("Telegram消息发送成功")
                return True
            else:
                logger.error(f"Telegram消息发送失败: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"发送Telegram消息异常: {e}")
            return False
    
    def send_daily_summary(self, date, summary_content, entry_count):
        """发送每日汇总"""
        # 重新加载配置
        self._load_config()
        
        if not self.enabled:
            return False
        
        try:
            # 格式化消息
            message = f"""📖 *每日日记汇总*

📅 日期：{date}
📝 记录条数：{entry_count}

{summary_content}

---
来自杯子日记"""
            
            return self.send_message(message)

        except Exception as e:
            logger.error(f"发送每日汇总失败: {e}")
            return False
    
    def test_connection(self):
        """测试Telegram连接"""
        # 重新加载配置
        self._load_config()
        
        if not self.bot_token:
            return False, "Bot Token未配置"
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    return True, f"连接成功！机器人：{bot_info.get('first_name', 'Unknown')}"
                else:
                    return False, "Bot Token无效"
            else:
                try:
                    err_text = response.text
                except Exception:
                    err_text = ''
                return False, f"连接失败: {response.status_code} {err_text}"
                
        except Exception as e:
            return False, f"连接异常: {str(e)}"

# 全局Telegram服务实例
telegram_service = TelegramService()


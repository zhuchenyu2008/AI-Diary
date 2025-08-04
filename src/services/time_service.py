import requests
from datetime import datetime
from zoneinfo import ZoneInfo

class TimeService:
    # 使用 HTTPS 协议访问时间服务，避免中间人攻击
    API_URL = "https://worldtimeapi.org/api/timezone/Asia/Shanghai"

    def get_beijing_time(self):
        """Fetch current Beijing time from the network.
        If network request fails, fall back to local time in Asia/Shanghai zone.
        """
        try:
            response = requests.get(self.API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            dt_str = data.get("datetime")
            if dt_str:
                return datetime.fromisoformat(dt_str).astimezone(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None)
        except Exception:
            pass
        return datetime.now(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None)

time_service = TimeService()

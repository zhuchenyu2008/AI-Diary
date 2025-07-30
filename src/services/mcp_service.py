"""
MCP (Model Context Protocol) 服务
提供时间、位置、天气等上下文信息
"""

import json
import time
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from src.services.time_service import time_service

class MCPService:
    def __init__(self):
        self.enabled_servers = {
            'time': True,
            'location': False,  # 需要用户授权
            'weather': False,   # 需要API配置
            'system': True
        }
        self.location_permission = False
        self.weather_api_key = None
        
    def get_server_config(self) -> Dict[str, Any]:
        """获取MCP服务器配置"""
        return {
            'servers': [
                {
                    'name': 'time',
                    'description': '时间服务器 - 提供当前时间、时区信息等',
                    'enabled': self.enabled_servers.get('time', True),
                    'tools': ['getCurrentTime', 'getTimezone', 'calculateDuration'],
                    'resources': ['time://current', 'time://timezone/{zone}'],
                    'requires_permission': False
                },
                {
                    'name': 'location',
                    'description': '位置服务器 - 提供用户位置信息',
                    'enabled': self.enabled_servers.get('location', False),
                    'tools': ['getCurrentLocation', 'getLocationInfo'],
                    'resources': ['location://current', 'location://history'],
                    'requires_permission': True,
                    'permission_granted': self.location_permission
                },
                {
                    'name': 'weather',
                    'description': '天气服务器 - 提供天气信息和预报',
                    'enabled': self.enabled_servers.get('weather', False),
                    'tools': ['getWeather', 'getWeatherForecast'],
                    'resources': ['weather://current/{location}', 'weather://forecast/{location}/{days}'],
                    'requires_permission': False,
                    'requires_api_key': True,
                    'api_key_configured': self.weather_api_key is not None
                },
                {
                    'name': 'system',
                    'description': '系统信息服务器 - 提供设备和系统信息',
                    'enabled': self.enabled_servers.get('system', True),
                    'tools': ['getDeviceInfo', 'getBatteryStatus'],
                    'resources': ['system://device', 'system://battery'],
                    'requires_permission': False
                }
            ]
        }
    
    def update_server_config(self, config: Dict[str, Any]) -> bool:
        """更新MCP服务器配置"""
        try:
            for server_name, enabled in config.get('enabled_servers', {}).items():
                if server_name in self.enabled_servers:
                    self.enabled_servers[server_name] = enabled
            
            # 更新位置权限
            if 'location_permission' in config:
                self.location_permission = config['location_permission']
            
            # 更新天气API密钥
            if 'weather_api_key' in config:
                self.weather_api_key = config['weather_api_key']
            
            return True
        except Exception as e:
            print(f"更新MCP配置失败: {e}")
            return False
    
    def call_tool(self, server_name: str, tool_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """调用MCP工具"""
        if not self.enabled_servers.get(server_name, False):
            return {'success': False, 'error': f'服务器 {server_name} 未启用'}
        
        try:
            if server_name == 'time':
                return self._call_time_tool(tool_name, parameters or {})
            elif server_name == 'location':
                return self._call_location_tool(tool_name, parameters or {})
            elif server_name == 'weather':
                return self._call_weather_tool(tool_name, parameters or {})
            elif server_name == 'system':
                return self._call_system_tool(tool_name, parameters or {})
            else:
                return {'success': False, 'error': f'未知服务器: {server_name}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_resource(self, uri: str) -> Dict[str, Any]:
        """获取MCP资源"""
        try:
            if uri.startswith('time://'):
                return self._get_time_resource(uri)
            elif uri.startswith('location://'):
                return self._get_location_resource(uri)
            elif uri.startswith('weather://'):
                return self._get_weather_resource(uri)
            elif uri.startswith('system://'):
                return self._get_system_resource(uri)
            else:
                return {'success': False, 'error': f'未知资源URI: {uri}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _call_time_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用时间工具"""
        if tool_name == 'getCurrentTime':
            current_time = time_service.get_beijing_time()
            return {
                'success': True,
                'result': {
                    'timestamp': current_time.isoformat(),
                    'formatted': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'timezone': 'Asia/Shanghai',
                    'weekday': current_time.strftime('%A'),
                    'unix_timestamp': int(current_time.timestamp())
                }
            }
        elif tool_name == 'getTimezone':
            zone = parameters.get('zone', 'Asia/Shanghai')
            return {
                'success': True,
                'result': {
                    'timezone': zone,
                    'offset': '+08:00',
                    'name': '中国标准时间'
                }
            }
        elif tool_name == 'calculateDuration':
            start_time = parameters.get('start_time')
            end_time = parameters.get('end_time')
            if not start_time or not end_time:
                return {'success': False, 'error': '需要提供开始时间和结束时间'}
            
            try:
                start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                duration = end - start
                
                return {
                    'success': True,
                    'result': {
                        'duration_seconds': int(duration.total_seconds()),
                        'duration_minutes': int(duration.total_seconds() / 60),
                        'duration_hours': int(duration.total_seconds() / 3600),
                        'duration_days': duration.days,
                        'formatted': str(duration)
                    }
                }
            except ValueError as e:
                return {'success': False, 'error': f'时间格式错误: {e}'}
        else:
            return {'success': False, 'error': f'未知时间工具: {tool_name}'}
    
    def _call_location_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用位置工具"""
        if not self.location_permission:
            return {'success': False, 'error': '位置权限未授权'}
        
        if tool_name == 'getCurrentLocation':
            # 模拟位置信息（实际应用中需要从浏览器获取）
            return {
                'success': True,
                'result': {
                    'latitude': 39.9042,
                    'longitude': 116.4074,
                    'accuracy': 10,
                    'city': '北京',
                    'country': '中国',
                    'timestamp': time_service.get_beijing_time().isoformat()
                }
            }
        elif tool_name == 'getLocationInfo':
            lat = parameters.get('latitude')
            lng = parameters.get('longitude')
            if not lat or not lng:
                return {'success': False, 'error': '需要提供经纬度'}
            
            return {
                'success': True,
                'result': {
                    'latitude': lat,
                    'longitude': lng,
                    'address': '模拟地址信息',
                    'city': '未知城市',
                    'country': '未知国家'
                }
            }
        else:
            return {'success': False, 'error': f'未知位置工具: {tool_name}'}
    
    def _call_weather_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用天气工具"""
        if not self.weather_api_key:
            return {'success': False, 'error': '天气API密钥未配置'}
        
        if tool_name == 'getWeather':
            location = parameters.get('location', '北京')
            # 模拟天气信息（实际应用中需要调用天气API）
            return {
                'success': True,
                'result': {
                    'location': location,
                    'temperature': 22,
                    'humidity': 65,
                    'weather': '晴天',
                    'wind_speed': 5,
                    'timestamp': time_service.get_beijing_time().isoformat()
                }
            }
        elif tool_name == 'getWeatherForecast':
            location = parameters.get('location', '北京')
            days = parameters.get('days', 3)
            
            forecast = []
            for i in range(days):
                date = (time_service.get_beijing_time() + timedelta(days=i)).date()
                forecast.append({
                    'date': date.isoformat(),
                    'temperature_high': 25 + i,
                    'temperature_low': 15 + i,
                    'weather': '晴天',
                    'humidity': 60 + i * 5
                })
            
            return {
                'success': True,
                'result': {
                    'location': location,
                    'forecast': forecast
                }
            }
        else:
            return {'success': False, 'error': f'未知天气工具: {tool_name}'}
    
    def _call_system_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用系统工具"""
        if tool_name == 'getDeviceInfo':
            return {
                'success': True,
                'result': {
                    'platform': 'Web',
                    'user_agent': 'AI Diary System',
                    'language': 'zh-CN',
                    'screen_resolution': '1920x1080',
                    'timestamp': time_service.get_beijing_time().isoformat()
                }
            }
        elif tool_name == 'getBatteryStatus':
            return {
                'success': True,
                'result': {
                    'level': 85,
                    'charging': False,
                    'charge_time': None,
                    'discharge_time': 300,
                    'timestamp': time_service.get_beijing_time().isoformat()
                }
            }
        else:
            return {'success': False, 'error': f'未知系统工具: {tool_name}'}
    
    def _get_time_resource(self, uri: str) -> Dict[str, Any]:
        """获取时间资源"""
        if uri == 'time://current':
            current_time = time_service.get_beijing_time()
            return {
                'success': True,
                'content': {
                    'timestamp': current_time.isoformat(),
                    'formatted': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'timezone': 'Asia/Shanghai',
                    'weekday': current_time.strftime('%A'),
                    'unix_timestamp': int(current_time.timestamp())
                },
                'mime_type': 'application/json'
            }
        elif uri.startswith('time://timezone/'):
            zone = uri.split('/')[-1]
            return {
                'success': True,
                'content': {
                    'timezone': zone,
                    'offset': '+08:00',
                    'name': '中国标准时间'
                },
                'mime_type': 'application/json'
            }
        else:
            return {'success': False, 'error': f'未知时间资源: {uri}'}
    
    def _get_location_resource(self, uri: str) -> Dict[str, Any]:
        """获取位置资源"""
        if not self.location_permission:
            return {'success': False, 'error': '位置权限未授权'}
        
        if uri == 'location://current':
            return {
                'success': True,
                'content': {
                    'latitude': 39.9042,
                    'longitude': 116.4074,
                    'accuracy': 10,
                    'city': '北京',
                    'country': '中国',
                    'timestamp': time_service.get_beijing_time().isoformat()
                },
                'mime_type': 'application/json'
            }
        elif uri == 'location://history':
            return {
                'success': True,
                'content': {
                    'locations': [
                        {
                            'latitude': 39.9042,
                            'longitude': 116.4074,
                            'city': '北京',
                            'timestamp': time_service.get_beijing_time().isoformat()
                        }
                    ]
                },
                'mime_type': 'application/json'
            }
        else:
            return {'success': False, 'error': f'未知位置资源: {uri}'}
    
    def _get_weather_resource(self, uri: str) -> Dict[str, Any]:
        """获取天气资源"""
        if not self.weather_api_key:
            return {'success': False, 'error': '天气API密钥未配置'}
        
        # 解析URI参数
        parts = uri.split('/')
        if len(parts) >= 3:
            location = parts[2] if len(parts) > 2 else '北京'
            
            if uri.startswith('weather://current/'):
                return {
                    'success': True,
                    'content': {
                        'location': location,
                        'temperature': 22,
                        'humidity': 65,
                        'weather': '晴天',
                        'wind_speed': 5,
                        'timestamp': time_service.get_beijing_time().isoformat()
                    },
                    'mime_type': 'application/json'
                }
            elif uri.startswith('weather://forecast/'):
                days = int(parts[3]) if len(parts) > 3 else 3
                forecast = []
                for i in range(days):
                    date = (time_service.get_beijing_time() + timedelta(days=i)).date()
                    forecast.append({
                        'date': date.isoformat(),
                        'temperature_high': 25 + i,
                        'temperature_low': 15 + i,
                        'weather': '晴天',
                        'humidity': 60 + i * 5
                    })
                
                return {
                    'success': True,
                    'content': {
                        'location': location,
                        'forecast': forecast
                    },
                    'mime_type': 'application/json'
                }
        
        return {'success': False, 'error': f'未知天气资源: {uri}'}
    
    def _get_system_resource(self, uri: str) -> Dict[str, Any]:
        """获取系统资源"""
        if uri == 'system://device':
            return {
                'success': True,
                'content': {
                    'platform': 'Web',
                    'user_agent': 'AI Diary System',
                    'language': 'zh-CN',
                    'screen_resolution': '1920x1080',
                    'timestamp': time_service.get_beijing_time().isoformat()
                },
                'mime_type': 'application/json'
            }
        elif uri == 'system://battery':
            return {
                'success': True,
                'content': {
                    'level': 85,
                    'charging': False,
                    'charge_time': None,
                    'discharge_time': 300,
                    'timestamp': time_service.get_beijing_time().isoformat()
                },
                'mime_type': 'application/json'
            }
        else:
            return {'success': False, 'error': f'未知系统资源: {uri}'}
    
    def get_context_for_ai(self, entry_text: str = None, image_path: str = None) -> str:
        """为AI分析获取MCP上下文信息"""
        context_parts = []
        
        # 获取时间上下文
        if self.enabled_servers.get('time', False):
            time_result = self.call_tool('time', 'getCurrentTime')
            if time_result.get('success'):
                time_info = time_result['result']
                context_parts.append(f"当前时间: {time_info['formatted']} ({time_info['weekday']})")
        
        # 获取位置上下文
        if self.enabled_servers.get('location', False) and self.location_permission:
            location_result = self.call_tool('location', 'getCurrentLocation')
            if location_result.get('success'):
                location_info = location_result['result']
                context_parts.append(f"当前位置: {location_info['city']}")
        
        # 获取天气上下文
        if self.enabled_servers.get('weather', False) and self.weather_api_key:
            weather_result = self.call_tool('weather', 'getWeather')
            if weather_result.get('success'):
                weather_info = weather_result['result']
                context_parts.append(f"当前天气: {weather_info['weather']}, 温度{weather_info['temperature']}°C")
        
        # 获取系统上下文
        if self.enabled_servers.get('system', False):
            device_result = self.call_tool('system', 'getDeviceInfo')
            if device_result.get('success'):
                device_info = device_result['result']
                context_parts.append(f"设备平台: {device_info['platform']}")
        
        if context_parts:
            return "上下文信息: " + ", ".join(context_parts)
        else:
            return ""

# 全局MCP服务实例
mcp_service = MCPService()


import requests
import json
import asyncio
import re
import logging
from datetime import datetime, date
from src.models.user import db
from src.services.time_service import time_service

logger = logging.getLogger(__name__)

class NotionService:
    def __init__(self):
        self.api_token = None
        self.database_id = None
        self.diary_page_id = None
        self.client = None
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    def _load_config(self):
        """加载Notion配置"""
        try:
            from src.models.diary import Config
            
            token_config = Config.query.filter_by(key='notion_api_token').first()
            database_config = Config.query.filter_by(key='notion_database_id').first()
            page_config = Config.query.filter_by(key='notion_diary_page_id').first()
            
            # 清理旧配置，避免残留导致误判
            self.api_token = None
            self.database_id = None
            self.diary_page_id = None
            if "Authorization" in self.headers:
                self.headers.pop("Authorization", None)

            # 重新设置当前有效配置
            if token_config and token_config.value:
                self.api_token = token_config.value.strip()
                if self.api_token:
                    self.headers["Authorization"] = f"Bearer {self.api_token}"
            if database_config and database_config.value:
                self.database_id = database_config.value.strip()
            if page_config and page_config.value:
                self.diary_page_id = page_config.value.strip()
                
        except Exception as e:
            logger.error(f"加载Notion配置失败: {e}")
    
    def _save_config(self, key, value):
        """保存配置到数据库"""
        try:
            from src.models.diary import Config
            
            config = Config.query.filter_by(key=key).first()
            if config:
                config.value = value
            else:
                config = Config(key=key, value=value)
                db.session.add(config)
            
            db.session.commit()
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            db.session.rollback()
    
    def _call_notion_api(self, method, endpoint, data=None, params=None):
        """调用Notion API"""
        if not self.api_token:
            raise ValueError("Notion API Token未配置")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            
            if response.status_code == 429:
                # 处理限流
                retry_after = response.headers.get('Retry-After', '1')
                logger.warning(f"API限流，等待 {retry_after} 秒")
                import time
                time.sleep(int(retry_after))
                return self._call_notion_api(method, endpoint, data, params)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Notion API调用失败: {e}")
            raise
    
    def test_connection(self):
        """测试Notion连接"""
        self._load_config()
        
        if not self.api_token:
            return False, "API Token未配置"
        
        try:
            # 调用用户信息接口测试连接
            result = self._call_notion_api('GET', '/users/me')
            return True, f"连接成功，用户: {result.get('name', 'Unknown')}"
        except Exception as e:
            return False, f"连接失败: {str(e)}"
    
    def auto_setup(self, api_token):
        """一键自动配置Notion集成"""
        try:
            # 1. 保存Token并验证
            self._save_config('notion_api_token', api_token)
            self._load_config()
            
            success, message = self.test_connection()
            if not success:
                raise ValueError(f"Token验证失败: {message}")
            
            # 2. 搜索或创建"日记"页面
            diary_page = self._find_or_create_diary_page()
            
            # 3. 在"日记"页面下创建数据库
            database = self._create_diary_database(diary_page['id'])
            
            # 4. 保存配置
            self._save_config('notion_diary_page_id', diary_page['id'])
            self._save_config('notion_database_id', database['id'])
            self._save_config('notion_setup_completed', 'true')
            self._save_config('notion_enabled', 'true')
            
            # 5. 重新加载配置
            self._load_config()
            
            return {
                'success': True,
                'page_title': diary_page['title'],
                'database_id': database['id'],
                'setup_completed': True
            }
            
        except Exception as e:
            logger.error(f"自动配置失败: {e}")
            # 清理失败的配置
            self._save_config('notion_setup_completed', 'false')
            self._save_config('notion_enabled', 'false')
            raise
    
    def _find_or_create_diary_page(self):
        """智能查找或创建日记页面"""
        try:
            # 1. 搜索现有页面
            search_terms = ['日记', '日记本', 'Diary', 'diary', '个人日记']
            
            for term in search_terms:
                pages = self._search_pages(term)
                if pages:
                    logger.info(f"找到现有日记页面: {pages[0]['title']}")
                    return pages[0]
            
            # 2. 如果找不到，创建新的"日记"页面
            logger.info("未找到现有日记页面，创建新页面")
            return self._create_diary_page()
            
        except Exception as e:
            logger.error(f"查找或创建日记页面失败: {e}")
            raise
    
    def _search_pages(self, query):
        """搜索页面"""
        try:
            search_data = {
                "query": query,
                "filter": {
                    "value": "page",
                    "property": "object"
                }
            }
            
            result = self._call_notion_api('POST', '/search', search_data)
            pages = []
            
            for item in result.get('results', []):
                if item.get('object') == 'page':
                    title = self._extract_page_title(item)
                    if title and any(term.lower() in title.lower() for term in ['日记', 'diary']):
                        pages.append({
                            'id': item['id'],
                            'title': title
                        })
            
            return pages
            
        except Exception as e:
            logger.error(f"搜索页面失败: {e}")
            return []
    
    def _extract_page_title(self, page):
        """提取页面标题"""
        try:
            properties = page.get('properties', {})
            title_prop = properties.get('title') or properties.get('Title')
            
            if title_prop and title_prop.get('title'):
                title_texts = title_prop['title']
                if title_texts:
                    return title_texts[0].get('text', {}).get('content', '')
            
            # 备用方案：从page对象中获取标题
            if 'title' in page:
                title_list = page['title']
                if title_list:
                    return title_list[0].get('text', {}).get('content', '')
            
            return None
        except:
            return None
    
    def _create_diary_page(self):
        """创建新的日记页面"""
        page_data = {
            "parent": {"type": "workspace", "workspace": True},
            "properties": {
                "title": [
                    {
                        "text": {
                            "content": "日记"
                        }
                    }
                ]
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": "这里是我的个人日记空间，由AI日记应用自动创建和同步。"
                                }
                            }
                        ]
                    }
                }
            ]
        }
        
        try:
            result = self._call_notion_api('POST', '/pages', page_data)
            return {
                'id': result['id'],
                'title': '日记'
            }
        except Exception as e:
            logger.error(f"创建日记页面失败: {e}")
            raise
    
    def _create_diary_database(self, parent_page_id):
        """在指定页面下创建标准日记数据库"""
        database_schema = {
            "parent": {"page_id": parent_page_id},
            "title": [{"text": {"content": "日记数据库"}}],
            "properties": {
                "Name": {"title": {}},
                "Date": {"date": {}},
                "Content": {"rich_text": {}},
                "Mood": {
                    "select": {
                        "options": [
                            {"name": "开心", "color": "green"},
                            {"name": "平静", "color": "blue"},
                            {"name": "思考", "color": "purple"},
                            {"name": "忙碌", "color": "orange"},
                            {"name": "疲惫", "color": "gray"},
                            {"name": "兴奋", "color": "red"},
                            {"name": "放松", "color": "pink"},
                            {"name": "专注", "color": "brown"},
                            {"name": "满足", "color": "yellow"}
                        ]
                    }
                },
                "Tags": {"multi_select": {"options": []}},
                "Word Count": {"number": {}},
                "Created By": {
                    "select": {
                        "options": [
                            {"name": "AI自动生成", "color": "blue"},
                            {"name": "手动同步", "color": "green"}
                        ]
                    }
                }
            }
        }
        
        try:
            result = self._call_notion_api('POST', '/databases', database_schema)
            logger.info(f"创建日记数据库成功: {result['id']}")
            return result
        except Exception as e:
            logger.error(f"创建日记数据库失败: {e}")
            raise
    
    def _auto_extract_mood_and_tags(self, summary_content):
        """从日记内容中自动提取心情和标签"""
        # 心情关键词映射
        mood_keywords = {
            '开心': ['开心', '高兴', '快乐', '愉快', '兴奋', '激动', '满意'],
            '平静': ['平静', '安静', '宁静', '轻松', '舒适', '温和'],
            '思考': ['思考', '反思', '想', '考虑', '琢磨', '沉思'],
            '忙碌': ['忙', '忙碌', '紧张', '赶', '匆忙', '繁忙'],
            '疲惫': ['累', '疲惫', '困', '疲劳', '疲倦', '乏力'],
            '满足': ['满足', '充实', '满意', '收获', '有成就感'],
            '放松': ['放松', '休息', '悠闲', '自在', '惬意'],
            '专注': ['专注', '集中', '投入', '认真', '全神贯注']
        }
        
        detected_mood = '平静'  # 默认值
        for mood, keywords in mood_keywords.items():
            if any(keyword in summary_content for keyword in keywords):
                detected_mood = mood
                break
        
        # 标签关键词映射
        tags = []
        tag_keywords = {
            '工作': ['工作', '会议', '项目', '任务', '办公', '加班'],
            '学习': ['学习', '读书', '课程', '培训', '看书', '研究'],
            '运动': ['跑步', '健身', '运动', '锻炼', '游泳', '瑜伽'],
            '美食': ['吃', '菜', '餐厅', '做饭', '美食', '料理'],
            '娱乐': ['电影', '游戏', '音乐', '购物', '聚会', '玩'],
            '家庭': ['家', '父母', '孩子', '家人', '亲戚', '家庭'],
            '旅行': ['旅行', '出差', '景点', '酒店', '旅游', '出游'],
            '健康': ['医院', '体检', '药', '健康', '看病', '治疗'],
            '社交': ['朋友', '聚餐', '见面', '聊天', '交流', '社交']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in summary_content for keyword in keywords):
                tags.append(tag)
        
        return detected_mood, tags[:3]  # 最多3个标签
    
    def sync_daily_summary(self, date_obj, summary_content):
        """同步每日总结到Notion"""
        self._load_config()
        
        if not self._is_enabled():
            logger.info("Notion同步未启用，跳过")
            return False, "Notion同步未启用"
        
        if not self.database_id:
            return False, "Notion数据库ID未配置"
        
        try:
            # 1. 检查是否已存在
            existing_page = self._find_existing_entry(date_obj)
            
            # 2. 自动提取心情和标签
            mood, tags = self._auto_extract_mood_and_tags(summary_content)
            
            # 3. 生成页面标题
            title = f"日记 {date_obj.strftime('%Y年%m月%d日')}"
            
            # 4. 构建页面数据（不再包含 Summary 字段）
            page_data = {
                "properties": {
                    "Name": {"title": [{"text": {"content": title}}]},
                    "Date": {"date": {"start": date_obj.isoformat()}},
                    "Content": {"rich_text": [{"text": {"content": summary_content}}]},
                    "Mood": {"select": {"name": mood}},
                    "Tags": {"multi_select": [{"name": tag} for tag in tags]},
                    "Word Count": {"number": len(summary_content)},
                    "Created By": {"select": {"name": "AI自动生成"}}
                }
            }
            
            if existing_page:
                # 更新现有页面
                result = self._call_notion_api('PATCH', f'/pages/{existing_page["id"]}', page_data)
                logger.info(f"更新Notion页面成功: {date_obj}")
            else:
                # 创建新页面
                page_data["parent"] = {"database_id": self.database_id}
                result = self._call_notion_api('POST', '/pages', page_data)
                logger.info(f"创建Notion页面成功: {date_obj}")
            
            # 6. 记录同步日志
            self._log_sync_result(date_obj, result['id'], 'success')
            
            return True, "同步成功"
            
        except Exception as e:
            logger.error(f"同步到Notion失败: {e}")
            self._log_sync_result(date_obj, None, 'failed', str(e))
            return False, f"同步失败: {str(e)}"
    
    def _find_existing_entry(self, date_obj):
        """查找指定日期的现有条目"""
        try:
            filter_data = {
                "filter": {
                    "property": "Date",
                    "date": {
                        "equals": date_obj.isoformat()
                    }
                }
            }
            
            result = self._call_notion_api('POST', f'/databases/{self.database_id}/query', filter_data)
            results = result.get('results', [])
            
            if results:
                return results[0]  # 返回第一个匹配的页面
            
            return None
            
        except Exception as e:
            logger.error(f"查找现有条目失败: {e}")
            return None
    
    def _is_enabled(self):
        """检查Notion同步是否启用"""
        try:
            from src.models.diary import Config
            enabled_config = Config.query.filter_by(key='notion_enabled').first()
            return enabled_config and enabled_config.value.lower() == 'true'
        except:
            return False
    
    def _log_sync_result(self, date_obj, page_id, status, error_message=None):
        """记录同步结果"""
        try:
            from src.models.diary import Config
            
            # 简单的日志记录到配置表
            log_key = f"notion_sync_log_{date_obj.strftime('%Y%m%d')}"
            log_value = {
                'date': date_obj.isoformat(),
                'page_id': page_id,
                'status': status,
                'error_message': error_message,
                'timestamp': datetime.now().isoformat()
            }
            
            self._save_config(log_key, json.dumps(log_value))
            
        except Exception as e:
            logger.error(f"记录同步日志失败: {e}")
    
    def sync_daily_summary_async(self, date_obj, summary_content):
        """异步同步每日总结（用于定时任务）"""
        import threading
        
        def sync_thread():
            try:
                # 在Flask应用上下文中运行
                from src.main import app
                with app.app_context():
                    self.sync_daily_summary(date_obj, summary_content)
            except Exception as e:
                logger.error(f"异步同步失败: {e}")
        
        thread = threading.Thread(target=sync_thread)
        thread.daemon = True
        thread.start()
    
    def get_setup_status(self):
        """获取配置状态"""
        self._load_config()
        
        try:
            from src.models.diary import Config
            
            setup_completed = Config.query.filter_by(key='notion_setup_completed').first()
            is_completed = setup_completed and setup_completed.value.lower() == 'true'
            
            status = {
                'configured': is_completed and bool(self.api_token and self.database_id),
                'has_token': bool(self.api_token),
                'has_database': bool(self.database_id),
                'enabled': self._is_enabled()
            }
            
            if status['configured']:
                # 获取页面和数据库信息
                try:
                    if self.diary_page_id:
                        page_info = self._call_notion_api('GET', f'/pages/{self.diary_page_id}')
                        status['page_title'] = self._extract_page_title(page_info)
                    
                    if self.database_id:
                        db_info = self._call_notion_api('GET', f'/databases/{self.database_id}')
                        db_title = db_info.get('title', [])
                        status['database_name'] = db_title[0].get('text', {}).get('content', '') if db_title else ''
                except:
                    pass
            
            return status
            
        except Exception as e:
            logger.error(f"获取配置状态失败: {e}")
            return {'configured': False, 'error': str(e)}

# 全局Notion服务实例
notion_service = NotionService()

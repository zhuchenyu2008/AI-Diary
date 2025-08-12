from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import date, timedelta
from src.models.diary import DailySummary, DiaryEntry
from src.models.user import db
from src.services.ai_service import ai_service
from src.services.telegram_service import telegram_service
from src.services.notion_service import notion_service
from src.services.time_service import time_service
import logging
import os
from zoneinfo import ZoneInfo

try:
    import fcntl  # Unix 文件锁，用于防止并发重复执行
    _HAS_FCNTL = True
except Exception:
    _HAS_FCNTL = False

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        # 显式使用北京时区，避免受服务器本地时区影响
        self.tz = ZoneInfo('Asia/Shanghai')
        self.scheduler = BackgroundScheduler(timezone=self.tz)
        self.app = None

    def start(self, app):
        """启动定时任务"""
        if self.scheduler.running:
            return

        self.app = app
        self.scheduler.add_job(
            self._generate_daily_summary_job,
            trigger=CronTrigger(hour=0, minute=0, timezone=self.tz),
            id='daily_summary_job',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("定时任务服务已启动，每日总结任务已设定在 00:00 (北京时间)")

    def stop(self):
        """停止定时任务"""
        if self.scheduler.running:
            self.scheduler.shutdown()
        logger.info("定时任务服务已停止")

    def _generate_daily_summary_job(self):
        """定时任务调用的函数"""
        with self.app.app_context():
            today_beijing = time_service.get_beijing_time().date()
            yesterday = today_beijing - timedelta(days=1)
            self._generate_daily_summary(yesterday)

    def _generate_daily_summary(self, target_date, force_update=False):
        """生成指定日期的日记汇总"""
        lock_file = None
        lock_path = None
        try:
            # 进程级防重：同一天只允许一个生成流程在运行（避免重复推送/同步）
            if _HAS_FCNTL:
                base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
                os.makedirs(base_dir, exist_ok=True)
                lock_path = os.path.join(base_dir, f"summary_{target_date.strftime('%Y%m%d')}.lock")
                lock_file = open(lock_path, 'w')
                try:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except Exception:
                    logger.info(f"已有进程在生成 {target_date} 的汇总，跳过本次执行")
                    try:
                        lock_file.close()
                    except Exception:
                        pass
                    return None

            # 检查是否已存在该日期的汇总（对于手动调用，可以选择强制更新）
            existing_summary = DailySummary.query.filter(DailySummary.date == target_date).first()
            if existing_summary and not force_update:
                logger.info(f"日期 {target_date} 的汇总已存在，跳过生成")
                return existing_summary.summary_content

            # 检查当天是否有有效的日记条目（不包括旧的总结）
            entries = DiaryEntry.query.filter(
                db.func.date(DiaryEntry.timestamp) == target_date,
                DiaryEntry.is_daily_summary != True  # 排除已有的总结条目
            ).order_by(DiaryEntry.timestamp.asc()).all()

            if not entries:
                logger.info(f"日期 {target_date} 没有日记条目，跳过汇总")
                return

            logger.info(f"开始生成日期 {target_date} 的汇总，共 {len(entries)} 条记录")

            summary_content = ai_service.generate_daily_summary(entries)

            # 基础校验：AI未配置或生成失败时不应继续写库/推送
            if not summary_content or not str(summary_content).strip():
                logger.warning(f"日期 {target_date} 的汇总内容为空，终止后续流程")
                return None

            failure_markers = [
                "AI服务未配置",
                "生成日记汇总失败",
                "AI分析失败"
            ]
            if any(marker in str(summary_content) for marker in failure_markers):
                logger.error(f"日期 {target_date} 的汇总生成失败，检测到失败标记，终止后续流程")
                return None

            # 处理重复条目的情况：如果已存在则更新，不存在则插入
            existing_summary = DailySummary.query.filter(DailySummary.date == target_date).first()
            if existing_summary:
                existing_summary.summary_content = summary_content
                existing_summary.entry_count = len(entries)
            else:
                daily_summary = DailySummary(
                    date=target_date,
                    summary_content=summary_content,
                    entry_count=len(entries)
                )
                db.session.add(daily_summary)

            # 为总结条目设置正确的日期时间
            # 使用当前时间的北京时区时间，但设置为目标日期的23:59:59
            from datetime import datetime
            summary_timestamp = datetime(
                year=target_date.year,
                month=target_date.month,
                day=target_date.day,
                hour=23,
                minute=59,
                second=59
            )
            
            # 删除同一天的历史总结条目（清理所有，避免重复显示）
            prev_summaries = DiaryEntry.query.filter(
                DiaryEntry.is_daily_summary == True,
                db.func.date(DiaryEntry.timestamp) == target_date
            ).all()
            for prev in prev_summaries:
                db.session.delete(prev)
            
            # 创建新的总结条目，明确设置为每日总结
            summary_entry = DiaryEntry(
                text_content=summary_content,
                timestamp=summary_timestamp,
                created_at=summary_timestamp,  # 确保创建时间一致
                is_daily_summary=True,
                ai_analysis=None
            )
            db.session.add(summary_entry)

            db.session.commit()

            logger.info(f"日期 {target_date} 的汇总生成完成")

            telegram_service.send_daily_summary(
                target_date.strftime('%Y年%m月%d日'),
                summary_content,
                len(entries)
            )

            # 自动同步到Notion（异步执行，不影响主流程）
            notion_service.sync_daily_summary_async(target_date, summary_content)

            return summary_content

        except Exception as e:
            logger.error(f"生成日记汇总失败: {e}")
            db.session.rollback()
            return None
        finally:
            # 释放并清理锁文件
            if lock_file:
                try:
                    if _HAS_FCNTL:
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    lock_file.close()
                except Exception:
                    pass
            if lock_path and os.path.exists(lock_path):
                # 最佳努力清理，不影响主流程
                try:
                    os.remove(lock_path)
                except Exception:
                    pass

    def _generate_summary_for_date(self, target_date):
        """为指定日期生成总结（用于手动调用）"""
        try:
            if not self.app:
                from src.main import app
                self.app = app
            
            # 使用应用上下文
            from src.main import app
            with app.app_context():
                return self._generate_daily_summary(target_date)
        except Exception as e:
            logger.error(f"手动生成总结失败: {e}")
            return f"服务初始化错误: {str(e)}"

    def generate_summary_manually(self, target_date):
        """手动生成指定日期的汇总"""
        try:
            with self.app.app_context():
                result = self._generate_daily_summary(target_date)
                if result is None:
                    return False, "汇总生成失败，可能是数据问题"
            return True, "汇总生成成功"
        except Exception as e:
            return False, f"汇总生成失败: {str(e)}"

scheduler_service = SchedulerService()

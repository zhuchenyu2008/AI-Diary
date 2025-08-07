from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import date, timedelta
from src.models.diary import DailySummary, db, DiaryEntry
from src.services.ai_service import ai_service
from src.services.telegram_service import telegram_service
from src.services.time_service import time_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
        self.app = None

    def start(self, app):
        """启动定时任务"""
        if self.scheduler.running:
            return

        self.app = app
        self.scheduler.add_job(
            self._generate_daily_summary_job,
            trigger=CronTrigger(hour=0, minute=0),
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
        try:
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
            
            # 删除同一天的历史总结条目
            prev_summary = DiaryEntry.query.filter(
                DiaryEntry.is_daily_summary == True,
                db.func.date(DiaryEntry.timestamp) == target_date
            ).first()
            
            if prev_summary:
                db.session.delete(prev_summary)
            
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

            return summary_content

        except Exception as e:
            logger.error(f"生成日记汇总失败: {e}")
            db.session.rollback()
            return None

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
            print(f"手动生成总结失败: {e}")
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

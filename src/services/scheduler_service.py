from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import date, timedelta
from src.models.diary import DailySummary, db, DiaryEntry
from src.services.ai_service import ai_service
from src.services.telegram_service import telegram_service
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
            yesterday = date.today() - timedelta(days=1)
            self._generate_daily_summary(yesterday)

    def _generate_daily_summary(self, target_date):
        """生成指定日期的日记汇总"""
        try:
            existing_summary = DailySummary.query.filter_by(date=target_date).first()
            if existing_summary:
                logger.info(f"日期 {target_date} 的汇总已存在，跳过")
                return

            entries = DiaryEntry.query.filter(
                db.func.date(DiaryEntry.timestamp) == target_date
            ).order_by(DiaryEntry.timestamp.asc()).all()

            if not entries:
                logger.info(f"日期 {target_date} 没有日记条目，跳过汇总")
                return

            logger.info(f"开始生成日期 {target_date} 的汇总，共 {len(entries)} 条记录")

            summary_content = ai_service.generate_daily_summary(entries)

            daily_summary = DailySummary(
                date=target_date,
                summary_content=summary_content,
                entry_count=len(entries)
            )

            db.session.add(daily_summary)
            db.session.commit()

            logger.info(f"日期 {target_date} 的汇总生成完成")

            telegram_service.send_daily_summary(
                target_date.strftime('%Y年%m月%d日'),
                summary_content,
                len(entries)
            )

        except Exception as e:
            logger.error(f"生成日记汇总失败: {e}")
            db.session.rollback()

    def generate_summary_manually(self, target_date):
        """手动生成指定日期的汇总"""
        try:
            with self.app.app_context():
                self._generate_daily_summary(target_date)
            return True, "汇总生成成功"
        except Exception as e:
            return False, f"汇总生成失败: {str(e)}"

scheduler_service = SchedulerService()

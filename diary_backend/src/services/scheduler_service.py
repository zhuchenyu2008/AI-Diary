import threading
import time
from datetime import datetime, date, timedelta
from src.models.diary import DiaryEntry, DailySummary, db
from src.services.ai_service import ai_service
from src.services.telegram_service import telegram_service

class SchedulerService:
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """启动定时任务"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        print("定时任务服务已启动")
    
    def stop(self):
        """停止定时任务"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("定时任务服务已停止")
    
    def _run_scheduler(self):
        """运行定时任务循环"""
        last_check_date = None
        
        while self.running:
            try:
                current_time = datetime.now()
                current_date = current_time.date()
                
                # 检查是否到了新的一天（凌晨0点后）
                if (last_check_date is None or 
                    (current_date > last_check_date and current_time.hour == 0 and current_time.minute < 5)):
                    
                    # 生成昨天的日记汇总
                    yesterday = current_date - timedelta(days=1)
                    self._generate_daily_summary(yesterday)
                    last_check_date = current_date
                
                # 每分钟检查一次
                time.sleep(60)
                
            except Exception as e:
                print(f"定时任务执行异常: {e}")
                time.sleep(60)
    
    def _generate_daily_summary(self, target_date):
        """生成指定日期的日记汇总"""
        try:
            # 检查是否已经生成过汇总
            existing_summary = DailySummary.query.filter_by(date=target_date).first()
            if existing_summary:
                print(f"日期 {target_date} 的汇总已存在，跳过")
                return
            
            # 获取指定日期的所有日记条目
            entries = DiaryEntry.query.filter(
                db.func.date(DiaryEntry.timestamp) == target_date
            ).order_by(DiaryEntry.timestamp.asc()).all()
            
            if not entries:
                print(f"日期 {target_date} 没有日记条目，跳过汇总")
                return
            
            print(f"开始生成日期 {target_date} 的汇总，共 {len(entries)} 条记录")
            
            # 使用AI生成汇总
            summary_content = ai_service.generate_daily_summary(entries)
            
            # 保存汇总到数据库
            daily_summary = DailySummary(
                date=target_date,
                summary_content=summary_content,
                entry_count=len(entries)
            )
            
            db.session.add(daily_summary)
            db.session.commit()
            
            print(f"日期 {target_date} 的汇总生成完成")
            
            # 发送到Telegram
            telegram_service.send_daily_summary(
                target_date.strftime('%Y年%m月%d日'),
                summary_content,
                len(entries)
            )
            
        except Exception as e:
            print(f"生成日记汇总失败: {e}")
            db.session.rollback()
    
    def generate_summary_manually(self, target_date):
        """手动生成指定日期的汇总"""
        try:
            self._generate_daily_summary(target_date)
            return True, "汇总生成成功"
        except Exception as e:
            return False, f"汇总生成失败: {str(e)}"

# 全局调度器实例
scheduler_service = SchedulerService()


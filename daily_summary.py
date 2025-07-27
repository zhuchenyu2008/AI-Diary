from datetime import datetime, timedelta, date
import db
import ai
import telegram_util


def run():
    today = date.today()
    yesterday = today - timedelta(days=1)
    start_dt = datetime.combine(yesterday, datetime.min.time())
    end_dt = datetime.combine(today, datetime.min.time())

    entries = db.get_entries_between(start_dt, end_dt)
    if not entries:
        return
    summary = ai.summarize_day(entries)
    db.save_summary(yesterday, summary)
    telegram_util.send_message(f"{yesterday} 的日记总结:\n{summary}")


if __name__ == '__main__':
    db.init_db()
    run()

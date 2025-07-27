import os
import configparser
from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_apscheduler import APScheduler
import mysql.connector
from datetime import datetime, timedelta
import requests
from ai_service import get_summary_from_ai

# +----------------+
# |  Configuration |
# +----------------+

config = configparser.ConfigParser()
# Make sure to create a config.ini file from the template
if not os.path.exists('config.ini'):
    import shutil
    shutil.copy('config.ini.template', 'config.ini')
config.read('config.ini')


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# +----------------+
# |  Login         |
# +----------------+

@app.route('/api/login', methods=['POST'])
def login():
    password = request.json.get('password')
    if not password:
        return jsonify({"error": "Password is required"}), 400

    hashed_password = generate_password_hash(config['DEFAULT']['LOGIN_PASSWORD'])
    if check_password_hash(hashed_password, password):
        # In a real app, you'd return a JWT token here.
        # For this simple case, we'll return a static token.
        return jsonify({"token": "static_token"}), 200
    else:
        return jsonify({"error": "Invalid password"}), 401

# +----------------+
# |  Database      |
# +----------------+

def get_db_connection():
    conn = mysql.connector.connect(
        host=config['DEFAULT']['DB_HOST'],
        user=config['DEFAULT']['DB_USER'],
        password=config['DEFAULT']['DB_PASSWORD'],
        database=config['DEFAULT']['DB_NAME']
    )
    return conn

# +----------------+
# |  Events        |
# +----------------+

@app.route('/api/events', methods=['POST'])
def create_event():
    event_type = request.form.get('event_type')
    content = request.form.get('content')
    file = request.files.get('file')

    if not event_type or (event_type == 'text' and not content) or (event_type == 'image' and not file):
        return jsonify({"error": "Invalid request"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    file_path = None
    if event_type == 'image' and file:
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

    query = "INSERT INTO events (event_type, content, file_path) VALUES (%s, %s, %s)"
    cursor.execute(query, (event_type, content, file_path))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Event created successfully"}), 201


@app.route('/api/events/timeline', methods=['GET'])
def get_event_timeline():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM events WHERE DATE(created_at) = CURDATE() ORDER BY created_at DESC"
    cursor.execute(query)
    events = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(events)


@app.route('/api/summaries', methods=['GET'])
def get_summaries():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM daily_summaries ORDER BY summary_date DESC LIMIT %s OFFSET %s"
    cursor.execute(query, (per_page, offset))
    summaries = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(summaries)


@app.route('/api/summaries/<string:date>', methods=['GET'])
def get_summary_by_date(date):
    try:
        summary_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM daily_summaries WHERE summary_date = %s"
    cursor.execute(query, (summary_date,))
    summary = cursor.fetchone()

    cursor.close()
    conn.close()

    if summary:
        return jsonify(summary)
    else:
        return jsonify({"error": "Summary not found"}), 404


# +----------------+
# | Telegram Bot   |
# +----------------+

def send_telegram_message(message):
    token = config['DEFAULT']['TELEGRAM_BOT_TOKEN']
    chat_id = config['DEFAULT']['TELEGRAM_CHAT_ID']
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram message: {e}")


# +----------------+
# | Scheduler      |
# +----------------+

def daily_summary_job():
    with app.app_context():
        yesterday = datetime.now().date() - timedelta(days=1)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM events WHERE DATE(created_at) = %s"
        cursor.execute(query, (yesterday,))
        events = cursor.fetchall()

        if events:
            summary = get_summary_from_ai(events)
            if summary:
                insert_query = "INSERT INTO daily_summaries (summary_date, content) VALUES (%s, %s)"
                cursor.execute(insert_query, (yesterday, summary))
                conn.commit()
                send_telegram_message(f"*Your AI Diary for {yesterday}*:\n\n{summary}")

        cursor.close()
        conn.close()


scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Schedule the job to run daily at midnight
scheduler.add_job(id='daily_summary_job', func=daily_summary_job, trigger='cron', hour=0, minute=0)


if __name__ == '__main__':
    app.run(port=config['DEFAULT']['BACKEND_PORT'], debug=True)

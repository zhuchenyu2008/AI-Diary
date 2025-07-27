from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
from datetime import datetime, date, timedelta
import os

import db
import ai
import config

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret')
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def check_login():
    return session.get('logged_in')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == config.PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
    if not check_login():
        return render_template('login.html')
    summaries = db.get_summaries()
    return render_template('index.html', summaries=summaries)


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if not check_login():
        return redirect(url_for('index'))
    if request.method == 'POST':
        text = request.form.get('text')
        file = request.files.get('image')
        image_path = None
        if file and file.filename:
            image_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(image_path)
        image_url = None
        if image_path:
            image_url = request.url_root.rstrip('/') + url_for('uploaded_file', filename=file.filename)
        analysis = ai.analyze_entry(text, image_url=image_url)
        db.add_entry(text, image_path, analysis)
        return redirect(url_for('submit'))
    return render_template('submit.html')


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/api/diary')
def api_diary():
    if not check_login():
        return jsonify({'error': 'unauthorized'}), 401
    days = int(request.args.get('days', 30))
    days = min(days, 30)
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=days)
    entries = db.get_entries_between(start_dt, end_dt)
    return jsonify(entries)


if __name__ == '__main__':
    db.init_db()
    app.run(host='0.0.0.0', port=8000, debug=True)

from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename
from src.models.diary import DiaryEntry, DailySummary, db, beijing_now
from src.services.ai_service import ai_service
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import os
import uuid
import threading

diary_bp = Blueprint('diary', __name__)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_auth(f):
    """认证装饰器"""
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated', False):
            return jsonify({'success': False, 'message': '未认证'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def analyze_entry_async(entry_id, text_content, image_path):
    """异步分析日记条目"""
    try:
        # 重新获取数据库连接
        from src.main import app
        with app.app_context():
            analysis = ai_service.analyze_entry(text_content, image_path)
            
            # 更新数据库
            entry = DiaryEntry.query.get(entry_id)
            if entry:
                entry.ai_analysis = analysis
                db.session.commit()
                print(f"AI分析完成，条目ID: {entry_id}")
    except Exception as e:
        print(f"异步AI分析失败: {e}")

@diary_bp.route('/entries', methods=['POST'])
@require_auth
def create_entry():
    """创建日记条目"""
    try:
        text_content = request.form.get('text_content', '')
        image_path = None
        full_image_path = None
        
        # 处理图片上传
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                # 创建上传目录
                upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', UPLOAD_FOLDER)
                os.makedirs(upload_dir, exist_ok=True)
                
                # 生成唯一文件名
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                image_path = f'{UPLOAD_FOLDER}/{filename}'
                full_image_path = file_path
        
        # 创建日记条目
        entry = DiaryEntry(
            text_content=text_content,
            image_path=image_path,
            timestamp=beijing_now()
        )
        
        db.session.add(entry)
        db.session.commit()
        
        # 异步进行AI分析
        if text_content or full_image_path:
            thread = threading.Thread(
                target=analyze_entry_async,
                args=(entry.id, text_content, full_image_path)
            )
            thread.daemon = True
            thread.start()
        
        return jsonify({
            'success': True,
            'message': '日记条目创建成功',
            'entry': entry.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@diary_bp.route('/entries', methods=['GET'])
@require_auth
def get_entries():
    """获取日记条目列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        date_str = request.args.get('date')  # 格式: YYYY-MM-DD
        
        query = DiaryEntry.query
        
        # 按日期过滤
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                query = query.filter(
                    db.func.date(DiaryEntry.timestamp) == target_date
                )
            except ValueError:
                return jsonify({'success': False, 'message': '日期格式错误'}), 400
        
        # 按时间倒序排列并分页
        entries = query.order_by(DiaryEntry.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'entries': [entry.to_dict() for entry in entries.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': entries.total,
                'pages': entries.pages,
                'has_next': entries.has_next,
                'has_prev': entries.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@diary_bp.route('/entries/<int:entry_id>', methods=['GET'])
@require_auth
def get_entry(entry_id):
    """获取单个日记条目"""
    try:
        entry = DiaryEntry.query.get_or_404(entry_id)
        return jsonify({
            'success': True,
            'entry': entry.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@diary_bp.route('/entries/<int:entry_id>', methods=['DELETE'])
@require_auth
def delete_entry(entry_id):
    """删除日记条目"""
    try:
        entry = DiaryEntry.query.get_or_404(entry_id)
        
        # 删除关联的图片文件
        if entry.image_path:
            file_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'static', 
                entry.image_path
            )
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '日记条目删除成功'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@diary_bp.route('/summaries', methods=['GET'])
@require_auth
def get_summaries():
    """获取每日汇总列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 30, type=int)
        days = request.args.get('days', 365, type=int)  # 默认获取一年内的
        
        # 计算日期范围
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # 查询汇总
        summaries = DailySummary.query.filter(
            DailySummary.date >= start_date,
            DailySummary.date <= end_date
        ).order_by(DailySummary.date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'summaries': [summary.to_dict() for summary in summaries.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': summaries.total,
                'pages': summaries.pages,
                'has_next': summaries.has_next,
                'has_prev': summaries.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@diary_bp.route('/summaries/<string:date_str>', methods=['GET'])
@require_auth
def get_summary(date_str):
    """获取指定日期的汇总"""
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        summary = DailySummary.query.filter_by(date=target_date).first()
        
        if summary:
            return jsonify({
                'success': True,
                'summary': summary.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': '未找到该日期的汇总'
            }), 404
            
    except ValueError:
        return jsonify({'success': False, 'message': '日期格式错误'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@diary_bp.route('/today-countdown', methods=['GET'])
def get_today_countdown():
    """获取距离今日结束的倒计时"""
    try:
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        # 计算到明天0点的时间
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        remaining = tomorrow - now
        
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        seconds = remaining.seconds % 60
        
        return jsonify({
            'success': True,
            'countdown': {
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
                'total_seconds': remaining.seconds
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


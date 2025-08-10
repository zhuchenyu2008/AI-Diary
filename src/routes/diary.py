from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename
from src.models.diary import DiaryEntry, DailySummary, db
from src.services.ai_service import ai_service
from src.utils.auth import require_auth
from datetime import datetime, date, timedelta
from src.services.time_service import time_service
import logging
import os
import uuid
import threading

logger = logging.getLogger(__name__)

diary_bp = Blueprint('diary', __name__)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_entry_async(entry_id, text_content, image_path, user_id=None):
    """异步分析日记条目 - 改进线程安全"""
    try:
        # 重新获取数据库连接
        from src.main import app
        with app.app_context():
            try:
                analysis = ai_service.analyze_entry(text_content, image_path, user_id)

                # 线程安全的数据库更新 - 使用单独的事务
                try:
                    entry = DiaryEntry.query.get(entry_id)
                    if entry:
                        entry.ai_analysis = analysis
                        db.session.commit()
                        logger.info(f"AI分析完成，条目ID: {entry_id}, 分析结果: {analysis[:50]}...")
                    else:
                        logger.info(f"未找到条目ID: {entry_id}")
                        db.session.rollback()
                except Exception as db_e:
                    logger.warning(f"数据库更新失败: {db_e}")
                    db.session.rollback()
                    # 如果数据库更新失败，尝试设置错误状态
                    try:
                        entry = DiaryEntry.query.get(entry_id)
                        if entry:
                            entry.ai_analysis = f"数据库更新失败: {str(db_e)}"
                            db.session.commit()
                    except Exception as e2:
                        logger.error(f"错误状态更新失败: {e2}")
                        db.session.rollback()
            finally:
                # 清理线程本地的 Session，防止资源泄漏
                db.session.remove()
    except Exception as e:
        logger.warning(f"异步AI分析失败: {e}")
        # 如果分析失败，将状态更新为错误信息
        try:
            from src.main import app
            with app.app_context():
                try:
                    entry = DiaryEntry.query.get(entry_id)
                    if entry:
                        entry.ai_analysis = f"AI分析失败: {str(e)}"
                        db.session.commit()
                    else:
                        db.session.rollback()
                except Exception as db_e:
                    logger.error(f"错误状态更新失败: {db_e}")
                    db.session.rollback()
                finally:
                    # 清理线程本地的 Session
                    db.session.remove()
        except:
            pass

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
        
        # 创建日记条目，初始AI分析状态为"AI理解中"
        entry = DiaryEntry(
            text_content=text_content,
            image_path=image_path,
            timestamp=time_service.get_beijing_time(),
            ai_analysis="AI理解中..." if (text_content or full_image_path) else None
        )
        
        db.session.add(entry)
        db.session.commit()
        
        # 异步进行AI分析
        if text_content or full_image_path:
            # 获取当前用户ID
            user_id = session.get('user_id')
            thread = threading.Thread(
                target=analyze_entry_async,
                args=(entry.id, text_content, full_image_path, user_id)
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

@diary_bp.route('/generate-daily-summary', methods=['POST'])
@require_auth
def generate_daily_summary():
    """手动生成指定日期的每日总结"""
    try:
        data = request.get_json()
        target_date = data.get('date')
        
        if not target_date:
            return jsonify({'success': False, 'message': '请提供日期'}), 400
        
        # 解析日期
        try:
            date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': '日期格式错误'}), 400
        
        # 获取指定日期的所有日记条目（排除已存在的每日总结）
        entries = DiaryEntry.query.filter(
            db.func.date(DiaryEntry.timestamp) == date_obj,
            DiaryEntry.is_daily_summary != True
        ).all()
        
        if not entries:
            return jsonify({'success': False, 'message': '该日期没有日记条目'}), 400
        
        # 导入调度服务并生成总结（强制更新已存在的总结）
        from src.services.scheduler_service import scheduler_service
        
        # 直接调用内部已处理事务的生成逻辑，避免嵌套事务
        summary_content = scheduler_service._generate_daily_summary(date_obj, force_update=True)
        summary_text = summary_content or "总结内容为空"
        
        logger.info(f"生成总结文本: {summary_text}")
        
        # 仅当生成的总结不为空且不包含失败标志时才视为成功
        if summary_text and summary_text.strip() and "失败" not in summary_text and summary_text != "总结内容为空":
            return jsonify({
                'success': True, 
                'message': '每日总结生成成功',
                'summary': summary_text
            }), 201
        else:
            error_msg = summary_text or '生成总结时出现未知错误'
            logger.error(f"生成总结失败原因: {error_msg}")
            return jsonify({'success': False, 'message': f'生成总结失败: {error_msg}'}), 500
            
    except Exception as e:
        logger.error(f"生成每日总结失败: {e}")
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
        
        # 时间线视图：只显示普通日记，排除每日总结
        if request.args.get('view') != 'history':  # 默认时间线视图
            query = query.filter(DiaryEntry.is_daily_summary != True)
        # 历史日记视图：显示包括每日总结在内的所有记录
        
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

@diary_bp.route('/entries/<int:entry_id>', methods=['PUT'])
@require_auth
def update_entry(entry_id):
    """更新日记条目"""
    try:
        entry = DiaryEntry.query.get_or_404(entry_id)
        
        # 获取新的文本内容
        data = request.get_json()
        new_text = data.get('text_content', '').strip()
        
        if not new_text:
            return jsonify({'success': False, 'message': '文本内容不能为空'}), 400
        
        # 更新文本内容
        entry.text_content = new_text
        
        # 如果有新的文本内容，重新进行AI分析
        entry.ai_analysis = "AI理解中..."
        db.session.commit()
        
        # 异步进行AI分析
        thread = threading.Thread(
            target=analyze_entry_async,
            args=(entry.id, new_text, None)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': '日记条目更新成功',
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
        now = time_service.get_beijing_time()
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



@diary_bp.route('/entries/<int:entry_id>/analysis-status', methods=['GET'])
@require_auth
def get_analysis_status(entry_id):
    """获取日记条目的AI分析状态"""
    try:
        entry = DiaryEntry.query.get_or_404(entry_id)
        return jsonify({
            'success': True,
            'entry_id': entry_id,
            'ai_analysis': entry.ai_analysis,
            'is_analyzing': entry.ai_analysis == "AI理解中..." if entry.ai_analysis else False
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@diary_bp.route('/entries/today/analysis-status', methods=['GET'])
@require_auth
def get_today_analysis_status():
    """获取今日所有条目的AI分析状态"""
    try:
        today = time_service.get_beijing_time().date()
        entries = DiaryEntry.query.filter(
            db.func.date(DiaryEntry.timestamp) == today
        ).order_by(DiaryEntry.timestamp.desc()).all()
        
        result = []
        for entry in entries:
            # 判断是否还在分析中
            is_analyzing = False
            if entry.ai_analysis:
                # 检查多种"分析中"的状态
                analyzing_keywords = ['AI理解中', 'AI理解中...', '分析中', '处理中']
                is_analyzing = any(keyword in entry.ai_analysis for keyword in analyzing_keywords)
            
            result.append({
                'id': entry.id,
                'ai_analysis': entry.ai_analysis,
                'is_analyzing': is_analyzing,
                'timestamp': entry.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'entries': result
        })
    except Exception as e:
        logger.error(f"获取分析状态失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

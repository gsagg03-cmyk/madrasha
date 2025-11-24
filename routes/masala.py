"""
Masala Routes
API endpoints for teacher stories/articles (Masala)
Teachers can post Islamic stories, lessons, and advice
"""
from flask import Blueprint, request, jsonify, session
from models import db, Masala, User
from functools import wraps
from datetime import datetime

masala_bp = Blueprint('masala', __name__)

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'success': False, 'message': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    """Decorator to require teacher role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'success': False, 'message': 'Login required'}), 401
        if session['user'].get('role') not in ['teacher', 'super_user']:
            return jsonify({'success': False, 'message': 'Teacher access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@masala_bp.route('', methods=['GET'])
def get_masala_list():
    """
    Get list of published masala posts
    Query params: page, limit, category, author_id
    """
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        category = request.args.get('category')
        author_id = request.args.get('author_id', type=int)
        
        # Build query
        query = Masala.query.filter_by(is_published=True)
        
        if category:
            query = query.filter_by(category=category)
        if author_id:
            query = query.filter_by(author_id=author_id)
        
        # Order by latest first
        query = query.order_by(Masala.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        
        masala_list = [m.to_dict() for m in pagination.items]
        
        return jsonify({
            'success': True,
            'data': masala_list,
            'pagination': {
                'page': page,
                'per_page': limit,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@masala_bp.route('/<int:masala_id>', methods=['GET'])
def get_masala_detail(masala_id):
    """Get single masala post by ID and increment view count"""
    try:
        masala = Masala.query.get(masala_id)
        
        if not masala:
            return jsonify({'success': False, 'message': 'Masala not found'}), 404
        
        if not masala.is_published:
            # Check if requester is the author or admin
            if 'user' not in session or (
                session['user'].get('id') != masala.author_id and 
                session['user'].get('role') != 'super_user'
            ):
                return jsonify({'success': False, 'message': 'Masala not published'}), 403
        
        # Increment view count
        masala.views_count += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': masala.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@masala_bp.route('/my-posts', methods=['GET'])
@login_required
def get_my_masala():
    """Get all masala posts by current logged-in teacher"""
    try:
        user_id = session['user'].get('id')
        
        masala_list = Masala.query.filter_by(author_id=user_id)\
            .order_by(Masala.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [m.to_dict() for m in masala_list]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@masala_bp.route('', methods=['POST'])
@teacher_required
def create_masala():
    """Create a new masala post (teacher only)"""
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('title') or not data.get('content'):
            return jsonify({'success': False, 'message': 'Title and content are required'}), 400
        
        # Create excerpt if not provided
        excerpt = data.get('excerpt')
        if not excerpt:
            content = data['content']
            excerpt = content[:200] + '...' if len(content) > 200 else content
        
        masala = Masala(
            title=data['title'],
            content=data['content'],
            excerpt=excerpt,
            author_id=session['user']['id'],
            category=data.get('category'),
            image_url=data.get('image_url'),
            is_published=data.get('is_published', True)
        )
        
        db.session.add(masala)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Masala created successfully',
            'data': masala.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@masala_bp.route('/<int:masala_id>', methods=['PUT'])
@teacher_required
def update_masala(masala_id):
    """Update masala post (author or super_user only)"""
    try:
        masala = Masala.query.get(masala_id)
        
        if not masala:
            return jsonify({'success': False, 'message': 'Masala not found'}), 404
        
        # Check permission
        if session['user']['id'] != masala.author_id and session['user'].get('role') != 'super_user':
            return jsonify({'success': False, 'message': 'Permission denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            masala.title = data['title']
        if 'content' in data:
            masala.content = data['content']
        if 'excerpt' in data:
            masala.excerpt = data['excerpt']
        elif 'content' in data:
            # Auto-generate excerpt from content
            masala.excerpt = data['content'][:200] + '...' if len(data['content']) > 200 else data['content']
        if 'category' in data:
            masala.category = data['category']
        if 'image_url' in data:
            masala.image_url = data['image_url']
        if 'is_published' in data:
            masala.is_published = data['is_published']
        
        masala.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Masala updated successfully',
            'data': masala.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@masala_bp.route('/<int:masala_id>', methods=['DELETE'])
@teacher_required
def delete_masala(masala_id):
    """Delete masala post (author or super_user only)"""
    try:
        masala = Masala.query.get(masala_id)
        
        if not masala:
            return jsonify({'success': False, 'message': 'Masala not found'}), 404
        
        # Check permission
        if session['user']['id'] != masala.author_id and session['user'].get('role') != 'super_user':
            return jsonify({'success': False, 'message': 'Permission denied'}), 403
        
        db.session.delete(masala)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Masala deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@masala_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get list of all unique categories"""
    try:
        categories = db.session.query(Masala.category)\
            .filter(Masala.category.isnot(None))\
            .filter(Masala.is_published == True)\
            .distinct().all()
        
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({
            'success': True,
            'data': category_list
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

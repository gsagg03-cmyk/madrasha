"""
User Management Routes
Provides endpoints for user management including teachers list
"""
from flask import Blueprint, jsonify
from models import db, User, UserRole
from utils.auth import login_required, require_role
from utils.response import success_response, error_response

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
def list_users():
	"""Return a basic users list placeholder.
	This can be expanded or deprecated; kept for backward compatibility with tests.
	"""
	return jsonify({
		'success': True,
		'message': 'Users endpoint placeholder',
		'data': []
	})

@users_bp.route('/teachers', methods=['GET'])
@login_required
@require_role(UserRole.SUPER_USER)
def get_teachers():
	"""Get all teachers with their SMS balances (Super Admin only)"""
	try:
		teachers = User.query.filter_by(role=UserRole.TEACHER, is_active=True).all()
		
		teachers_data = [{
			'id': teacher.id,
			'name': f"{teacher.first_name} {teacher.last_name}",
			'phoneNumber': teacher.phoneNumber,
			'email': teacher.email,
			'smsCount': teacher.sms_count or 0,
			'lastLogin': teacher.last_login.isoformat() if teacher.last_login else None,
			'createdAt': teacher.created_at.isoformat() if teacher.created_at else None
		} for teacher in teachers]
		
		return success_response('Teachers retrieved successfully', teachers_data)
		
	except Exception as e:
		return error_response(f'Failed to load teachers: {str(e)}', 500)

@users_bp.route('/health', methods=['GET'])
def users_health():
	return jsonify({'status': 'ok', 'component': 'users'})
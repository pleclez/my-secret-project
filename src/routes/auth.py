"""
Authentication API Routes
"""
from flask import Blueprint, request, jsonify, current_app

from src.services.auth_service import AuthService


bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    auth_service = AuthService(current_app.db_connection)
    result = auth_service.authenticate_user(username, password)
    
    if result:
        return jsonify(result), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401


@bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'error': 'Username, email, and password required'}), 400
    
    auth_service = AuthService(current_app.db_connection)
    user_id = auth_service.create_user(
        username=username,
        email=email,
        password=password,
        first_name=data.get('first_name'),
        last_name=data.get('last_name')
    )
    
    if user_id:
        return jsonify({'user_id': user_id, 'message': 'User created successfully'}), 201
    
    return jsonify({'error': 'Failed to create user'}), 500


@bp.route('/verify', methods=['POST'])
def verify_token():
    """Verify JWT token"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'error': 'Token required'}), 400
    
    auth_service = AuthService(current_app.db_connection)
    payload = auth_service.verify_token(token)
    
    if payload:
        return jsonify({'valid': True, 'payload': payload}), 200
    
    return jsonify({'valid': False, 'error': 'Invalid token'}), 401


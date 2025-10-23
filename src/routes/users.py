"""
User Management API Routes
"""
from flask import Blueprint, jsonify, current_app


bp = Blueprint('users', __name__)


@bp.route('', methods=['GET'])
def list_users():
    """List all users"""
    query = "SELECT id, username, email, first_name, last_name, is_active, created_at FROM users"
    users = current_app.db_connection.execute_query(query)
    return jsonify(users if users else []), 200


@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details"""
    query = """
    SELECT id, username, email, first_name, last_name, is_active, created_at, last_login
    FROM users WHERE id = %s
    """
    user = current_app.db_connection.execute_query(query, (user_id,), fetch_one=True)
    
    if user:
        return jsonify(user), 200
    
    return jsonify({'error': 'User not found'}), 404


@bp.route('/<int:user_id>/roles', methods=['GET'])
def get_user_roles(user_id):
    """Get user's roles"""
    query = """
    SELECT r.id, r.name, r.description, ur.granted_at, ur.expires_at
    FROM roles r
    JOIN user_roles ur ON r.id = ur.role_id
    WHERE ur.user_id = %s
    AND (ur.expires_at IS NULL OR ur.expires_at > NOW())
    """
    
    roles = current_app.db_connection.execute_query(query, (user_id,))
    return jsonify(roles if roles else []), 200


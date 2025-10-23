"""
Role Management API Routes
"""
from flask import Blueprint, jsonify, request, current_app

from src.services.rbac_service import RBACService


bp = Blueprint('roles', __name__)


@bp.route('', methods=['GET'])
def list_roles():
    """List all roles"""
    query = "SELECT * FROM roles ORDER BY name"
    roles = current_app.db_connection.execute_query(query)
    return jsonify(roles if roles else []), 200


@bp.route('/<int:role_id>', methods=['GET'])
def get_role(role_id):
    """Get role details"""
    query = "SELECT * FROM roles WHERE id = %s"
    role = current_app.db_connection.execute_query(query, (role_id,), fetch_one=True)
    
    if role:
        return jsonify(role), 200
    
    return jsonify({'error': 'Role not found'}), 404


@bp.route('/<int:role_id>/permissions', methods=['GET'])
def get_role_permissions(role_id):
    """Get permissions for a role"""
    rbac_service = RBACService(current_app.db_connection)
    permissions = rbac_service.get_role_permissions(role_id)
    
    return jsonify([p.__dict__ for p in permissions]), 200


@bp.route('/assign', methods=['POST'])
def assign_role():
    """Assign role to user"""
    data = request.get_json()
    
    user_id = data.get('user_id')
    role_id = data.get('role_id')
    granted_by = data.get('granted_by', 1)  # TODO: Get from JWT token
    
    if not user_id or not role_id:
        return jsonify({'error': 'user_id and role_id required'}), 400
    
    rbac_service = RBACService(current_app.db_connection)
    assignment_id = rbac_service.assign_role_to_user(user_id, role_id, granted_by)
    
    if assignment_id:
        return jsonify({'assignment_id': assignment_id, 'message': 'Role assigned successfully'}), 201
    
    return jsonify({'error': 'Failed to assign role'}), 500


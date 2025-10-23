"""
Permission Management API Routes
"""
from flask import Blueprint, jsonify, current_app


bp = Blueprint('permissions', __name__)


@bp.route('', methods=['GET'])
def list_permissions():
    """List all permissions"""
    query = "SELECT * FROM permissions ORDER BY resource, action"
    permissions = current_app.db_connection.execute_query(query)
    return jsonify(permissions if permissions else []), 200


@bp.route('/<int:permission_id>', methods=['GET'])
def get_permission(permission_id):
    """Get permission details"""
    query = "SELECT * FROM permissions WHERE id = %s"
    permission = current_app.db_connection.execute_query(query, (permission_id,), fetch_one=True)
    
    if permission:
        return jsonify(permission), 200
    
    return jsonify({'error': 'Permission not found'}), 404


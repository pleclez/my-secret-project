"""
Item Access Control API Routes
"""
from flask import Blueprint, jsonify, request, current_app

from src.services.rbac_service import RBACService


bp = Blueprint('items', __name__)


@bp.route('', methods=['GET'])
def list_items():
    """List all items"""
    query = "SELECT * FROM items ORDER BY created_at DESC LIMIT 100"
    items = current_app.db_connection.execute_query(query)
    return jsonify(items if items else []), 200


@bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get item details"""
    query = "SELECT * FROM items WHERE id = %s"
    item = current_app.db_connection.execute_query(query, (item_id,), fetch_one=True)
    
    if item:
        return jsonify(item), 200
    
    return jsonify({'error': 'Item not found'}), 404


@bp.route('/accessible', methods=['GET'])
def get_accessible_items():
    """Get items accessible by current user"""
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action', 'read')
    
    if not user_id:
        return jsonify({'error': 'user_id parameter required'}), 400
    
    rbac_service = RBACService(current_app.db_connection)
    items = rbac_service.get_accessible_items(user_id, action)
    
    return jsonify([item.__dict__ for item in items]), 200


@bp.route('/<int:item_id>/check-access', methods=['POST'])
def check_access(item_id):
    """Check if user has access to item"""
    data = request.get_json()
    
    user_id = data.get('user_id')
    action = data.get('action', 'read')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    rbac_service = RBACService(current_app.db_connection)
    has_access = rbac_service.check_user_permission(user_id, item_id, action)
    
    return jsonify({
        'item_id': item_id,
        'user_id': user_id,
        'action': action,
        'has_access': has_access
    }), 200


@bp.route('/<int:item_id>/grant', methods=['POST'])
def grant_access(item_id):
    """Grant access to item"""
    data = request.get_json()
    
    user_id = data.get('user_id')
    role_id = data.get('role_id')
    permission_id = data.get('permission_id')
    granted_by = data.get('granted_by', 1)  # TODO: Get from JWT token
    
    if not permission_id:
        return jsonify({'error': 'permission_id required'}), 400
    
    if not user_id and not role_id:
        return jsonify({'error': 'Either user_id or role_id required'}), 400
    
    rbac_service = RBACService(current_app.db_connection)
    access_id = rbac_service.grant_item_access(
        item_id=item_id,
        user_id=user_id,
        role_id=role_id,
        permission_id=permission_id,
        granted_by=granted_by
    )
    
    if access_id:
        return jsonify({'access_id': access_id, 'message': 'Access granted successfully'}), 201
    
    return jsonify({'error': 'Failed to grant access'}), 500


@bp.route('/access/<int:access_id>/revoke', methods=['DELETE'])
def revoke_access(access_id):
    """Revoke access to item"""
    rbac_service = RBACService(current_app.db_connection)
    success = rbac_service.revoke_item_access(access_id)
    
    if success:
        return jsonify({'message': 'Access revoked successfully'}), 200
    
    return jsonify({'error': 'Failed to revoke access'}), 500


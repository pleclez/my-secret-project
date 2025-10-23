"""
Middleware for authentication and authorization
"""
import logging
from functools import wraps
from flask import request, jsonify, current_app

from src.services.auth_service import AuthService


logger = logging.getLogger(__name__)


def require_auth(f):
    """
    Decorator to require authentication for API endpoints
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401
        
        # Extract token (format: "Bearer <token>")
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Invalid authorization header format'}), 401
        
        token = parts[1]
        
        # Verify token
        auth_service = AuthService(current_app.db_connection)
        payload = auth_service.verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user info to request context
        request.user_id = payload.get('user_id')
        request.username = payload.get('username')
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_role(*roles):
    """
    Decorator to require specific roles for API endpoints
    
    Args:
        roles: Role names required to access the endpoint
    """
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            # Get user roles
            query = """
            SELECT r.name FROM roles r
            JOIN user_roles ur ON r.id = ur.role_id
            WHERE ur.user_id = %s
            AND (ur.expires_at IS NULL OR ur.expires_at > NOW())
            """
            
            user_roles = current_app.db_connection.execute_query(
                query,
                (request.user_id,)
            )
            
            user_role_names = [r['name'] for r in user_roles] if user_roles else []
            
            # Check if user has any of the required roles
            if not any(role in user_role_names for role in roles):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


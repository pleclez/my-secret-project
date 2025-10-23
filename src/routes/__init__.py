"""
API Routes Registration
"""
from flask import Flask

from src.routes import auth, users, roles, permissions, items


def register_routes(app: Flask):
    """Register all API routes"""
    
    # Register blueprints
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(users.bp, url_prefix='/api/users')
    app.register_blueprint(roles.bp, url_prefix='/api/roles')
    app.register_blueprint(permissions.bp, url_prefix='/api/permissions')
    app.register_blueprint(items.bp, url_prefix='/api/items')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'rbac-service'}


"""
Unit tests for Authentication Service
"""
import pytest
from unittest.mock import Mock, patch

from src.services.auth_service import AuthService


class TestAuthService:
    
    @pytest.fixture
    def mock_db(self):
        """Mock database connection"""
        return Mock()
    
    @pytest.fixture
    def auth_service(self, mock_db):
        """Create auth service instance with mock database"""
        return AuthService(mock_db)
    
    def test_authenticate_user_success(self, auth_service, mock_db):
        """Test successful user authentication"""
        mock_db.execute_query.return_value = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'password_hash': '$2b$12$dummy_hash'
        }
        
        with patch.object(auth_service, '_verify_password', return_value=True):
            with patch.object(auth_service, '_update_last_login'):
                with patch.object(auth_service, '_generate_token', return_value='dummy_token'):
                    result = auth_service.authenticate_user('testuser', 'password123')
        
        assert result is not None
        assert result['username'] == 'testuser'
        assert result['token'] == 'dummy_token'
    
    def test_authenticate_user_invalid_password(self, auth_service, mock_db):
        """Test authentication with invalid password"""
        mock_db.execute_query.return_value = {
            'id': 1,
            'username': 'testuser',
            'password_hash': '$2b$12$dummy_hash'
        }
        
        with patch.object(auth_service, '_verify_password', return_value=False):
            result = auth_service.authenticate_user('testuser', 'wrongpassword')
        
        assert result is None
    
    def test_authenticate_user_not_found(self, auth_service, mock_db):
        """Test authentication with non-existent user"""
        mock_db.execute_query.return_value = None
        
        result = auth_service.authenticate_user('nonexistent', 'password123')
        
        assert result is None
    
    def test_create_user(self, auth_service, mock_db):
        """Test user creation"""
        mock_db.execute_query.return_value = {'id': 1}
        
        with patch.object(auth_service, '_hash_password', return_value='hashed_password'):
            user_id = auth_service.create_user(
                username='newuser',
                email='newuser@example.com',
                password='password123'
            )
        
        assert user_id == 1
        assert mock_db.execute_query.called


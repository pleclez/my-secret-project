"""
Unit tests for RBAC Service
"""
import pytest
from unittest.mock import Mock, MagicMock

from src.services.rbac_service import RBACService


class TestRBACService:
    
    @pytest.fixture
    def mock_db(self):
        """Mock database connection"""
        return Mock()
    
    @pytest.fixture
    def rbac_service(self, mock_db):
        """Create RBAC service instance with mock database"""
        return RBACService(mock_db)
    
    def test_check_user_permission_granted(self, rbac_service, mock_db):
        """Test permission check when user has access"""
        mock_db.execute_query.return_value = {'count': 1}
        
        result = rbac_service.check_user_permission(
            user_id=1,
            item_id=100,
            action='read'
        )
        
        assert result is True
        assert mock_db.execute_query.called
    
    def test_check_user_permission_denied(self, rbac_service, mock_db):
        """Test permission check when user doesn't have access"""
        mock_db.execute_query.return_value = {'count': 0}
        
        result = rbac_service.check_user_permission(
            user_id=1,
            item_id=100,
            action='delete'
        )
        
        assert result is False
    
    def test_grant_item_access(self, rbac_service, mock_db):
        """Test granting access to an item"""
        mock_db.execute_query.return_value = {'id': 1}
        
        access_id = rbac_service.grant_item_access(
            item_id=100,
            user_id=1,
            role_id=None,
            permission_id=1,
            granted_by=1
        )
        
        assert access_id == 1
        assert mock_db.execute_query.called
    
    def test_revoke_item_access(self, rbac_service, mock_db):
        """Test revoking access to an item"""
        mock_db.execute_update.return_value = 1
        
        result = rbac_service.revoke_item_access(access_id=1)
        
        assert result is True
        assert mock_db.execute_update.called
    
    def test_assign_role_to_user(self, rbac_service, mock_db):
        """Test assigning a role to a user"""
        mock_db.execute_query.return_value = {'id': 1}
        
        result = rbac_service.assign_role_to_user(
            user_id=1,
            role_id=2,
            granted_by=1
        )
        
        assert result == 1
        assert mock_db.execute_query.called


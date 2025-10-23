"""
RBAC Service - Core business logic for access control
"""
import logging
from typing import List, Optional, Dict
from datetime import datetime

from src.database.connection import DatabaseConnection
from src.database.models import User, Role, Permission, Item, ItemAccess


logger = logging.getLogger(__name__)


class RBACService:
    """
    Role-Based Access Control Service
    Handles permission checks and access management
    """
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def check_user_permission(self, user_id: int, item_id: int, action: str) -> bool:
        """
        Check if a user has permission to perform an action on an item
        
        Args:
            user_id: User ID
            item_id: Item ID
            action: Action to perform (read, write, delete, etc.)
            
        Returns:
            True if user has permission, False otherwise
        """
        query = """
        SELECT COUNT(*) as count
        FROM item_access ia
        JOIN permissions p ON ia.permission_id = p.id
        WHERE ia.item_id = %s
        AND p.action = %s
        AND (ia.expires_at IS NULL OR ia.expires_at > NOW())
        AND (
            ia.user_id = %s
            OR ia.role_id IN (
                SELECT role_id FROM user_roles
                WHERE user_id = %s
                AND (expires_at IS NULL OR expires_at > NOW())
            )
        )
        """
        
        result = self.db.execute_query(query, (item_id, action, user_id, user_id), fetch_one=True)
        has_permission = result['count'] > 0 if result else False
        
        # Log the access attempt
        self._log_access_attempt(user_id, item_id, action, has_permission)
        
        return has_permission
    
    def grant_item_access(
        self,
        item_id: int,
        user_id: Optional[int],
        role_id: Optional[int],
        permission_id: int,
        granted_by: int,
        expires_at: Optional[datetime] = None
    ) -> int:
        """
        Grant access to an item for a user or role
        
        Args:
            item_id: Item ID
            user_id: User ID (optional if role_id is provided)
            role_id: Role ID (optional if user_id is provided)
            permission_id: Permission ID
            granted_by: User ID who granted the access
            expires_at: Expiration datetime (optional)
            
        Returns:
            ID of the created access record
        """
        query = """
        INSERT INTO item_access (item_id, user_id, role_id, permission_id, granted_by, expires_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (item_id, user_id, role_id, permission_id, granted_by, expires_at),
            fetch_one=True
        )
        
        logger.info(f"Access granted to item {item_id} by user {granted_by}")
        return result['id'] if result else None
    
    def revoke_item_access(self, access_id: int) -> bool:
        """
        Revoke access to an item
        
        Args:
            access_id: Access record ID
            
        Returns:
            True if revoked successfully
        """
        query = "DELETE FROM item_access WHERE id = %s"
        rows_affected = self.db.execute_update(query, (access_id,))
        
        logger.info(f"Access {access_id} revoked")
        return rows_affected > 0
    
    def get_user_roles(self, user_id: int) -> List[Role]:
        """
        Get all active roles for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of Role objects
        """
        query = """
        SELECT r.* FROM roles r
        JOIN user_roles ur ON r.id = ur.role_id
        WHERE ur.user_id = %s
        AND (ur.expires_at IS NULL OR ur.expires_at > NOW())
        """
        
        results = self.db.execute_query(query, (user_id,))
        return [Role(**row) for row in results] if results else []
    
    def get_role_permissions(self, role_id: int) -> List[Permission]:
        """
        Get all permissions for a role
        
        Args:
            role_id: Role ID
            
        Returns:
            List of Permission objects
        """
        query = """
        SELECT p.* FROM permissions p
        JOIN role_permissions rp ON p.id = rp.permission_id
        WHERE rp.role_id = %s
        """
        
        results = self.db.execute_query(query, (role_id,))
        return [Permission(**row) for row in results] if results else []
    
    def get_accessible_items(self, user_id: int, action: str = 'read') -> List[Item]:
        """
        Get all items accessible by a user for a specific action
        
        Args:
            user_id: User ID
            action: Action type (default: read)
            
        Returns:
            List of Item objects
        """
        query = """
        SELECT DISTINCT i.* FROM items i
        JOIN item_access ia ON i.id = ia.item_id
        JOIN permissions p ON ia.permission_id = p.id
        WHERE p.action = %s
        AND (ia.expires_at IS NULL OR ia.expires_at > NOW())
        AND (
            i.is_public = TRUE
            OR i.owner_id = %s
            OR ia.user_id = %s
            OR ia.role_id IN (
                SELECT role_id FROM user_roles
                WHERE user_id = %s
                AND (expires_at IS NULL OR expires_at > NOW())
            )
        )
        ORDER BY i.created_at DESC
        """
        
        results = self.db.execute_query(query, (action, user_id, user_id, user_id))
        return [Item(**row) for row in results] if results else []
    
    def assign_role_to_user(
        self,
        user_id: int,
        role_id: int,
        granted_by: int,
        expires_at: Optional[datetime] = None
    ) -> int:
        """
        Assign a role to a user
        
        Args:
            user_id: User ID
            role_id: Role ID
            granted_by: User ID who granted the role
            expires_at: Expiration datetime (optional)
            
        Returns:
            ID of the created user_role record
        """
        query = """
        INSERT INTO user_roles (user_id, role_id, granted_by, expires_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, role_id) DO UPDATE
        SET granted_by = EXCLUDED.granted_by,
            granted_at = CURRENT_TIMESTAMP,
            expires_at = EXCLUDED.expires_at
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (user_id, role_id, granted_by, expires_at),
            fetch_one=True
        )
        
        logger.info(f"Role {role_id} assigned to user {user_id} by {granted_by}")
        return result['id'] if result else None
    
    def _log_access_attempt(
        self,
        user_id: int,
        item_id: int,
        action: str,
        granted: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Log an access attempt for audit purposes
        
        Args:
            user_id: User ID
            item_id: Item ID
            action: Action attempted
            granted: Whether access was granted
            ip_address: Client IP address (optional)
            user_agent: Client user agent (optional)
        """
        query = """
        INSERT INTO access_logs (user_id, item_id, action, granted, ip_address, user_agent)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        try:
            self.db.execute_update(query, (user_id, item_id, action, granted, ip_address, user_agent))
        except Exception as e:
            logger.error(f"Failed to log access attempt: {e}")
    
    def get_access_logs(
        self,
        user_id: Optional[int] = None,
        item_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve access logs with optional filtering
        
        Args:
            user_id: Filter by user ID (optional)
            item_id: Filter by item ID (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of access log dictionaries
        """
        conditions = []
        params = []
        
        if user_id:
            conditions.append("user_id = %s")
            params.append(user_id)
        
        if item_id:
            conditions.append("item_id = %s")
            params.append(item_id)
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)
        
        query = f"""
        SELECT * FROM access_logs
        {where_clause}
        ORDER BY created_at DESC
        LIMIT %s
        """
        
        results = self.db.execute_query(query, tuple(params))
        return results if results else []


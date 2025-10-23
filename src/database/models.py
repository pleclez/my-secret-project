"""
Database models for RBAC system
Defines the schema structure for PostgreSQL
"""
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class User:
    """User model"""
    id: int
    username: str
    email: str
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    last_login: Optional[datetime] = None


@dataclass
class Role:
    """Role model"""
    id: int
    name: str
    description: Optional[str] = None
    parent_role_id: Optional[int] = None  # For role hierarchy
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class Permission:
    """Permission model"""
    id: int
    name: str
    resource: str
    action: str  # read, write, delete, execute, etc.
    description: Optional[str] = None
    created_at: datetime = None


@dataclass
class Item:
    """Protected item/resource model"""
    id: int
    name: str
    item_type: str
    owner_id: int
    metadata: Optional[dict] = None
    is_public: bool = False
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class UserRole:
    """User-Role association"""
    id: int
    user_id: int
    role_id: int
    granted_by: int
    granted_at: datetime = None
    expires_at: Optional[datetime] = None


@dataclass
class RolePermission:
    """Role-Permission association"""
    id: int
    role_id: int
    permission_id: int
    created_at: datetime = None


@dataclass
class ItemAccess:
    """Item access control"""
    id: int
    item_id: int
    user_id: Optional[int] = None
    role_id: Optional[int] = None
    permission_id: int
    granted_by: int
    granted_at: datetime = None
    expires_at: Optional[datetime] = None


@dataclass
class AccessLog:
    """Audit log for access attempts"""
    id: int
    user_id: int
    item_id: int
    action: str
    granted: bool
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = None


# SQL Schema Creation Scripts
SCHEMA_SQL = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Roles table
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_role_id INTEGER REFERENCES roles(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Permissions table
CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(resource, action)
);

-- Items table
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    metadata JSONB,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User-Role associations
CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    granted_by INTEGER REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    UNIQUE(user_id, role_id)
);

-- Role-Permission associations
CREATE TABLE IF NOT EXISTS role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)
);

-- Item access control
CREATE TABLE IF NOT EXISTS item_access (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    granted_by INTEGER REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    CHECK (user_id IS NOT NULL OR role_id IS NOT NULL)
);

-- Access audit log
CREATE TABLE IF NOT EXISTS access_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    granted BOOLEAN NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_item_access_item_id ON item_access(item_id);
CREATE INDEX IF NOT EXISTS idx_item_access_user_id ON item_access(user_id);
CREATE INDEX IF NOT EXISTS idx_items_owner_id ON items(owner_id);
CREATE INDEX IF NOT EXISTS idx_access_logs_user_id ON access_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_access_logs_created_at ON access_logs(created_at);
"""


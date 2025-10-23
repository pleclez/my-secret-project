# RBAC Access Control Service

A Python-based backend service for managing Role-Based Access Control (RBAC) between users and database items. This service provides fine-grained permission management for resource access control.

## Features

- **Role-Based Access Control**: Manage user roles and permissions
- **PostgreSQL Integration**: Connects to AWS RDS PostgreSQL instances
- **RESTful API**: Flask-based API for access management
- **JWT Authentication**: Secure token-based authentication
- **Hierarchical Roles**: Support for role inheritance
- **Item-Level Permissions**: Granular control over database items
- **Audit Logging**: Track all access control changes

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │─────▶│  RBAC API    │─────▶│  PostgreSQL │
└─────────────┘      └──────────────┘      │  RDS (AWS)  │
                            │               └─────────────┘
                            ▼
                     ┌──────────────┐
                     │  Redis Cache │
                     └──────────────┘
```

## Database Schema

- **users**: User accounts and authentication
- **roles**: Role definitions (admin, editor, viewer, etc.)
- **permissions**: Granular permissions (read, write, delete, etc.)
- **role_permissions**: Many-to-many relationship
- **user_roles**: User role assignments
- **items**: Protected resources in the database
- **item_access**: User/role access to specific items

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 13+ (AWS RDS)
- Redis (optional, for caching)

### Setup

1. Clone the repository
```bash
git clone <repository-url>
cd gg-demo
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Run database migrations
```bash
alembic upgrade head
```

6. Start the service
```bash
python app.py
```

## Configuration

Set the following environment variables in `.env`:

- `DATABASE_URL`: PostgreSQL RDS connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `REDIS_URL`: Redis connection string (optional)
- `AWS_REGION`: AWS region for RDS
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## API Endpoints

### Authentication
- `POST /api/auth/login` - User authentication
- `POST /api/auth/logout` - Logout user
- `POST /api/auth/refresh` - Refresh JWT token

### User Management
- `GET /api/users` - List all users
- `POST /api/users` - Create new user
- `GET /api/users/{id}` - Get user details
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Role Management
- `GET /api/roles` - List all roles
- `POST /api/roles` - Create new role
- `GET /api/roles/{id}` - Get role details
- `PUT /api/roles/{id}` - Update role
- `DELETE /api/roles/{id}` - Delete role

### Permission Management
- `GET /api/permissions` - List all permissions
- `POST /api/users/{user_id}/roles/{role_id}` - Assign role to user
- `DELETE /api/users/{user_id}/roles/{role_id}` - Remove role from user

### Item Access Control
- `GET /api/items/{item_id}/access` - Check user access to item
- `POST /api/items/{item_id}/grant` - Grant access to item
- `DELETE /api/items/{item_id}/revoke` - Revoke access to item
- `GET /api/items/accessible` - List accessible items for current user

## Testing

Run the test suite:

```bash
pytest tests/
```

With coverage:

```bash
pytest --cov=src tests/
```

## Docker Deployment

Build and run with Docker:

```bash
docker-compose up -d
```

## License

MIT License


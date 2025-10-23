"""
Authentication Service
Handles user authentication, JWT tokens, and session management
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict

import jwt
import bcrypt

from src.config import Config
from src.database.connection import DatabaseConnection
from src.database.models import User


logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication service for user login and token management
    """
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.config = Config()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user credentials
        
        Args:
            username: Username or email
            password: Plain text password
            
        Returns:
            User data with JWT token if successful, None otherwise
        """
        # Fetch user from database
        query = """
        SELECT * FROM users
        WHERE (username = %s OR email = %s)
        AND is_active = TRUE
        """
        
        user_data = self.db.execute_query(query, (username, username), fetch_one=True)
        
        if not user_data:
            logger.warning(f"Authentication failed: User {username} not found")
            return None
        
        # Verify password
        if not self._verify_password(password, user_data['password_hash']):
            logger.warning(f"Authentication failed: Invalid password for user {username}")
            return None
        
        # Update last login
        self._update_last_login(user_data['id'])
        
        # Generate JWT token
        token = self._generate_token(user_data)
        
        logger.info(f"User {username} authenticated successfully")
        
        return {
            'user_id': user_data['id'],
            'username': user_data['username'],
            'email': user_data['email'],
            'token': token,
            'token_type': 'Bearer'
        }
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.config.JWT_SECRET_KEY,
                algorithms=[self.config.JWT_ALGORITHM]
            )
            
            # Check if token is expired
            exp = payload.get('exp')
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                logger.warning("Token has expired")
                return None
            
            return payload
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Optional[int]:
        """
        Create a new user
        
        Args:
            username: Username
            email: Email address
            password: Plain text password
            first_name: First name (optional)
            last_name: Last name (optional)
            
        Returns:
            User ID if created successfully, None otherwise
        """
        # Hash password
        password_hash = self._hash_password(password)
        
        query = """
        INSERT INTO users (username, email, password_hash, first_name, last_name)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """
        
        try:
            result = self.db.execute_query(
                query,
                (username, email, password_hash, first_name, last_name),
                fetch_one=True
            )
            
            user_id = result['id'] if result else None
            logger.info(f"User {username} created successfully with ID {user_id}")
            return user_id
            
        except Exception as e:
            logger.error(f"Failed to create user {username}: {e}")
            return None
    
    def _generate_token(self, user_data: Dict) -> str:
        """
        Generate JWT token for user
        
        Args:
            user_data: User data dictionary
            
        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        exp = now + timedelta(hours=self.config.JWT_EXPIRATION_HOURS)
        
        payload = {
            'user_id': user_data['id'],
            'username': user_data['username'],
            'email': user_data['email'],
            'iat': now,
            'exp': exp
        }
        
        token = jwt.encode(
            payload,
            self.config.JWT_SECRET_KEY,
            algorithm=self.config.JWT_ALGORITHM
        )
        
        return token
    
    def _hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            password_hash: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def _update_last_login(self, user_id: int):
        """
        Update user's last login timestamp
        
        Args:
            user_id: User ID
        """
        query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s"
        self.db.execute_update(query, (user_id,))


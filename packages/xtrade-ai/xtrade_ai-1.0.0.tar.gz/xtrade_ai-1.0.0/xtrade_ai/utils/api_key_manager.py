"""
API Key Management Utility

This module provides utilities for creating, managing, and validating API keys
for the XTrade-AI framework.
"""

import os
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import psycopg2
import bcrypt
from .logger import get_logger

logger = get_logger(__name__)


class APIKeyManager:
    """Manages API keys for the XTrade-AI framework."""
    
    def __init__(self, db_config: Optional[Dict[str, Any]] = None):
        """Initialize the API key manager.
        
        Args:
            db_config: Database configuration dictionary
        """
        self.db_config = db_config or {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'xtrade_ai'),
            'user': os.getenv('POSTGRES_USER', 'xtrade_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'xtrade_password')
        }
    
    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(**self.db_config)
    
    def generate_api_key(self, length: int = 32) -> str:
        """Generate a secure API key.
        
        Args:
            length: Length of the API key
            
        Returns:
            Generated API key
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def create_user(self, username: str, email: str, password: str, is_admin: bool = False) -> str:
        """Create a new user.
        
        Args:
            username: Username
            email: Email address
            password: Password (will be hashed)
            is_admin: Whether user is admin
            
        Returns:
            User ID
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insert user
            cursor.execute("""
                INSERT INTO api.users (username, email, password_hash, is_admin)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (username, email, password_hash, is_admin))
            
            user_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Created user: {username}")
            return str(user_id)
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def create_api_key(
        self, 
        user_id: str, 
        key_name: str, 
        permissions: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None
    ) -> str:
        """Create a new API key for a user.
        
        Args:
            user_id: User ID
            key_name: Name for the API key
            permissions: List of permissions
            expires_in_days: Days until expiration (None for no expiration)
            
        Returns:
            Generated API key
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Generate API key
            api_key = self.generate_api_key()
            
            # Set expiration
            expires_at = None
            if expires_in_days:
                expires_at = datetime.now() + timedelta(days=expires_in_days)
            
            # Insert API key
            cursor.execute("""
                INSERT INTO api.api_keys (user_id, key_name, api_key, permissions, expires_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (user_id, key_name, api_key, permissions or [], expires_at))
            
            key_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Created API key: {key_name} for user: {user_id}")
            return api_key
            
        except Exception as e:
            logger.error(f"Failed to create API key: {e}")
            raise
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate an API key and return user information.
        
        Args:
            api_key: API key to validate
            
        Returns:
            User information if valid, None otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT u.id, u.username, u.email, u.is_admin, ak.permissions, ak.expires_at
                FROM api.users u
                JOIN api.api_keys ak ON u.id = ak.user_id
                WHERE ak.api_key = %s AND ak.is_active = TRUE AND u.is_active = TRUE
                AND (ak.expires_at IS NULL OR ak.expires_at > NOW())
            """, (api_key,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                user_id, username, email, is_admin, permissions, expires_at = result
                return {
                    "user_id": str(user_id),
                    "username": username,
                    "email": email,
                    "is_admin": is_admin,
                    "permissions": permissions or [],
                    "expires_at": expires_at
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to validate API key: {e}")
            return None
    
    def list_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """List API keys for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of API key information
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, key_name, permissions, is_active, last_used, created_at, expires_at
                FROM api.api_keys
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            
            keys = []
            for row in cursor.fetchall():
                keys.append({
                    "id": str(row[0]),
                    "key_name": row[1],
                    "permissions": row[2] or [],
                    "is_active": row[3],
                    "last_used": row[4],
                    "created_at": row[5],
                    "expires_at": row[6]
                })
            
            cursor.close()
            conn.close()
            
            return keys
            
        except Exception as e:
            logger.error(f"Failed to list API keys: {e}")
            return []
    
    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key.
        
        Args:
            key_id: API key ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE api.api_keys
                SET is_active = FALSE
                WHERE id = %s
            """, (key_id,))
            
            success = cursor.rowcount > 0
            conn.commit()
            cursor.close()
            conn.close()
            
            if success:
                logger.info(f"Revoked API key: {key_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to revoke API key: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate a user with username and password.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User ID if authentication successful, None otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, password_hash
                FROM api.users
                WHERE username = %s AND is_active = TRUE
            """, (username,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                user_id, password_hash = result
                if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                    return str(user_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to authenticate user: {e}")
            return None


def create_default_admin():
    """Create default admin user and API key."""
    try:
        manager = APIKeyManager()
        
        # Check if admin user exists
        conn = manager._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM api.users WHERE username = 'admin'")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            logger.info("Admin user already exists")
            return
        
        # Create admin user
        user_id = manager.create_user(
            username="admin",
            email="admin@xtrade-ai.com",
            password="admin123",
            is_admin=True
        )
        
        # Create API key
        api_key = manager.create_api_key(
            user_id=user_id,
            key_name="Default Admin Key",
            permissions=["*"],
            expires_in_days=None
        )
        
        logger.info(f"Created default admin user and API key: {api_key}")
        
    except Exception as e:
        logger.error(f"Failed to create default admin: {e}")


if __name__ == "__main__":
    # Create default admin when run directly
    create_default_admin()

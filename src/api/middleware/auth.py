"""
JWT Authentication Middleware.

Provides JWT token generation, verification, and user authentication.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt
from loguru import logger

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Security scheme
security = HTTPBearer()

# In-memory user store (replace with database in production)
USERS_DB = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode(),
        "role": "admin",
        "tier": "enterprise"
    },
    "user": {
        "username": "user",
        "email": "user@example.com",
        "hashed_password": bcrypt.hashpw(b"user123", bcrypt.gensalt()).decode(),
        "role": "user",
        "tier": "free"
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Bcrypt hashed password
        
    Returns:
        True if password matches
    """
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_user(username: str) -> Optional[Dict[str, Any]]:
    """
    Get user from database.
    
    Args:
        username: Username
        
    Returns:
        User dict or None
    """
    return USERS_DB.get(username)


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate user with username and password.
    
    Args:
        username: Username
        password: Password
        
    Returns:
        User dict if authenticated, None otherwise
    """
    user = get_user(username)
    if not user:
        return None
    
    if not verify_password(password, user["hashed_password"]):
        return None
    
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Data to encode in token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    logger.info(f"Created access token for user: {data.get('sub')}")
    
    return encoded_jwt


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    Verify JWT token and return payload.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        Token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        return payload
        
    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise credentials_exception


async def get_current_user(
    payload: Dict[str, Any] = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get current authenticated user.
    
    Args:
        payload: JWT token payload
        
    Returns:
        User dict
        
    Raises:
        HTTPException: If user not found
    """
    username = payload.get("sub")
    user = get_user(username)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_current_active_admin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current user and verify admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User dict
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user


def create_user(username: str, email: str, password: str, role: str = "user", tier: str = "free") -> Dict[str, Any]:
    """
    Create a new user (for testing/demo purposes).
    
    Args:
        username: Username
        email: Email
        password: Plain password
        role: User role
        tier: User tier
        
    Returns:
        Created user dict
    """
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    user = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "role": role,
        "tier": tier
    }
    
    USERS_DB[username] = user
    logger.info(f"Created user: {username}")
    
    return user

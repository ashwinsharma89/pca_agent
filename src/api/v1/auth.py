"""
Authentication endpoints (v1).
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Dict, Any

from ..middleware.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    create_user
)

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class RegisterRequest(BaseModel):
    """Registration request model."""
    username: str
    email: EmailStr
    password: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login endpoint.
    
    Authenticates user and returns JWT token.
    
    Args:
        request: Login credentials
        
    Returns:
        Access token and user info
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user = authenticate_user(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"], "tier": user["tier"]}
    )
    
    # Remove sensitive data
    user_safe = {k: v for k, v in user.items() if k != "hashed_password"}
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_safe
    }


@router.post("/register", response_model=Dict[str, Any])
async def register(request: RegisterRequest):
    """
    Register new user.
    
    Args:
        request: Registration data
        
    Returns:
        Created user info
        
    Raises:
        HTTPException: If username already exists
    """
    # Check if user exists
    from ..middleware.auth import get_user
    
    if get_user(request.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create user
    user = create_user(
        username=request.username,
        email=request.email,
        password=request.password
    )
    
    # Remove sensitive data
    user_safe = {k: v for k, v in user.items() if k != "hashed_password"}
    
    return {
        "message": "User created successfully",
        "user": user_safe
    }


@router.get("/me", response_model=Dict[str, Any])
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user info.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User info
    """
    # Remove sensitive data
    user_safe = {k: v for k, v in current_user.items() if k != "hashed_password"}
    
    return user_safe

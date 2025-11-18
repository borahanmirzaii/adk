"""Authentication middleware with Supabase Auth and RBAC"""

from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from enum import Enum
import logging
from supabase import create_client, Client
from jose import JWTError, jwt
from app.config import settings

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)

# Supabase client for auth
supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client for authentication"""
    global supabase_client
    if supabase_client is None:
        supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_ANON_KEY
        )
    return supabase_client


class Role(str, Enum):
    """User roles for RBAC"""
    USER = "user"
    ADMIN = "admin"
    AGENT = "agent"
    SERVICE = "service"  # For service-to-service auth


class UserContext:
    """User context from authenticated request"""
    
    def __init__(self, user_id: str, email: str, role: Role, metadata: Dict[str, Any] = None, tenant_id: Optional[str] = None):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.metadata = metadata or {}
        self.tenant_id = tenant_id  # Multi-tenancy support
    
    def has_role(self, required_role: Role) -> bool:
        """Check if user has required role"""
        role_hierarchy = {
            Role.USER: [Role.USER],
            Role.AGENT: [Role.USER, Role.AGENT],
            Role.ADMIN: [Role.USER, Role.AGENT, Role.ADMIN],
            Role.SERVICE: [Role.SERVICE],
        }
        return required_role in role_hierarchy.get(self.role, [])


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserContext]:
    """
    Get current user from JWT token
    
    Returns:
        UserContext if authenticated, None if no credentials provided
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        supabase = get_supabase_client()
        
        # Verify token with Supabase
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            logger.warning("Invalid token: user not found")
            return None
        
        user = user_response.user
        user_metadata = user.user_metadata or {}
        
        # Extract role from metadata or default to USER
        role_str = user_metadata.get("role", "user")
        try:
            role = Role(role_str.lower())
        except ValueError:
            role = Role.USER
        
        # Extract tenant_id from metadata or app_metadata
        tenant_id = user_metadata.get("tenant_id") or getattr(user, "app_metadata", {}).get("tenant_id")
        
        return UserContext(
            user_id=user.id,
            email=user.email or "",
            role=role,
            metadata=user_metadata,
            tenant_id=tenant_id
        )
    
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        return None


async def require_auth(
    user: Optional[UserContext] = Depends(get_current_user)
) -> UserContext:
    """
    Require authentication - raises 401 if not authenticated
    
    Returns:
        UserContext of authenticated user
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_role(required_role: Role):
    """
    Dependency factory for role-based access control
    
    Args:
        required_role: Minimum role required to access the endpoint
    
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(
        user: UserContext = Depends(require_auth)
    ) -> UserContext:
        if not user.has_role(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role.value}",
            )
        return user
    
    return role_checker


async def verify_api_key(request: Request) -> bool:
    """
    Verify API key from request headers (for service-to-service auth)
    
    Returns:
        True if valid API key, False otherwise
    """
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return False
    
    # Check against configured service key
    if api_key == settings.SUPABASE_SERVICE_KEY:
        return True
    
    # TODO: Add API key storage and validation
    return False


def require_api_key():
    """
    Dependency factory for API key authentication
    
    Returns:
        Dependency function that verifies API key
    """
    async def api_key_checker(request: Request) -> bool:
        is_valid = await verify_api_key(request)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key"
            )
        return True
    
    return api_key_checker


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserContext]:
    """
    Get user if authenticated, but don't require it
    
    Useful for endpoints that work with or without auth
    """
    return await get_current_user(credentials)


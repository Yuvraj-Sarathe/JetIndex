"""
JetIndex - Authentication & RBAC Module
"""

from .models import User, UserRole, LoginRequest, LoginResponse, SwitchRoleRequest, ROLE_PERMISSIONS
from .security import hash_password, verify_password, create_access_token, verify_access_token, check_has_permission
from .service import (
    authenticate_user,
    get_user_by_id,
    get_demo_users,
    switch_user_role,
    init_auth_tables,
    get_current_user,
    get_current_user_optional,
    require_permission,
    get_default_guest_user,
    PRE_SEEDED_USERS
)

__all__ = [
    "User",
    "UserRole",
    "LoginRequest",
    "LoginResponse",
    "SwitchRoleRequest",
    "ROLE_PERMISSIONS",
    "hash_password",
    "verify_password",
    "create_access_token",
    "verify_access_token",
    "check_has_permission",
    "authenticate_user",
    "get_user_by_id",
    "get_demo_users",
    "switch_user_role",
    "init_auth_tables",
    "get_current_user",
    "get_current_user_optional",
    "require_permission",
    "get_default_guest_user",
    "PRE_SEEDED_USERS"
]

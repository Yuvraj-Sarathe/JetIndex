"""
JetIndex - Authentication & RBAC Module
"""

from .models import ROLE_PERMISSIONS, LoginRequest, LoginResponse, SwitchRoleRequest, User, UserRole
from .security import check_has_permission, create_access_token, hash_password, verify_access_token, verify_password
from .service import (
    PRE_SEEDED_USERS,
    authenticate_user,
    get_current_user,
    get_current_user_optional,
    get_default_guest_user,
    get_demo_users,
    get_user_by_id,
    init_auth_tables,
    require_permission,
    switch_user_role,
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
    "PRE_SEEDED_USERS",
]

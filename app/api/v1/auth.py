"""
JetIndex - Authentication & RBAC API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from auth.models import ROLE_PERMISSIONS, SwitchRoleRequest, User, UserRole
from auth.security import create_access_token
from auth.service import (
    authenticate_user,
    get_current_user,
    get_demo_users,
    get_user_by_id,
    switch_user_role,
)

router = APIRouter()


class LoginRequestAPI(BaseModel):
    username_or_email: str
    password: str


class LoginResponseAPI(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict
    role_description: str
    accessible_features: list[str]


@router.post("/login", response_model=LoginResponseAPI)
async def login(req: LoginRequestAPI):
    """Authenticate user and return JWT token."""
    user = authenticate_user(req)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user_id=user.user_id, username=user.username, email=user.email, role=user.role)

    role_descriptions = {
        UserRole.MOSPI_ADMIN: "MoSPI Administrator - Full statutory data management",
        UserRole.MOSPI_ANALYST: "MoSPI Analyst - Read CPI weights and projections",
        UserRole.RBI_MPC: "RBI MPC Member - Policy simulations and dashboards",
        UserRole.RBI_ECONOMIST: "RBI Economist - CPI dashboard and basic forecasts",
        UserRole.DGCA_REGULATOR: "DGCA Regulator - Route monitoring and alerts",
        UserRole.DGCA_INSPECTOR: "DGCA Inspector - Route corridor tracking",
        UserRole.SYSTEM_ADMIN: "System Administrator - Full platform access",
        UserRole.PUBLIC_AUDITOR: "Public Auditor - Read-only dashboard",
    }

    return LoginResponseAPI(
        access_token=token,
        expires_in=86400 * 7,
        user={
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "designation": user.designation,
            "organization": user.organization,
            "department": user.department,
            "avatar_color": user.avatar_color,
            "permissions": user.permissions,
        },
        role_description=role_descriptions.get(user.role, "Unknown role"),
        accessible_features=user.permissions,
    )


@router.get("/demo-users")
async def list_demo_users():
    """List all pre-seeded demo users with credentials."""
    return get_demo_users()


@router.post("/demo-login")
async def demo_login(username: str):
    """Quick login as a demo user by username."""
    users = get_demo_users()
    user = next((u for u in users if u["username"] == username), None)
    if not user:
        raise HTTPException(status_code=404, detail="Demo user not found")

    # Get the full user object
    full_user = get_user_by_id(user["user_id"])
    if not full_user:
        raise HTTPException(status_code=404, detail="User not found in database")

    token = create_access_token(
        user_id=full_user.user_id, username=full_user.username, email=full_user.email, role=full_user.role
    )

    return {"access_token": token, "token_type": "bearer", "user": full_user.model_dump()}


@router.get("/me")
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current authenticated user's profile."""
    return user.model_dump()


@router.post("/switch-role")
async def switch_role(req: SwitchRoleRequest, user: User = Depends(get_current_user)):
    """Switch to a different demo role (demo mode only)."""
    new_user = switch_user_role(user.user_id, req)
    if not new_user:
        raise HTTPException(status_code=404, detail="Target role not found")

    token = create_access_token(
        user_id=new_user.user_id, username=new_user.username, email=new_user.email, role=new_user.role
    )

    return {"access_token": token, "user": new_user.model_dump()}


@router.get("/roles")
async def get_roles():
    """List all available roles and their permissions."""
    return {
        role.value: {"permissions": permissions, "description": f"{role.value} role"}
        for role, permissions in ROLE_PERMISSIONS.items()
    }


@router.post("/logout")
async def logout(user: User = Depends(get_current_user)):
    """Logout current user (client-side token removal)."""
    return {"message": "Logged out successfully"}

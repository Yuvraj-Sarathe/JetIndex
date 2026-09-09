"""
JetIndex - Authentication & RBAC Data Models
Supports MoSPI, RBI MPC, DGCA, System Administration, and Public Auditor roles.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    MOSPI_ADMIN = "MOSPI_ADMIN"
    MOSPI_ANALYST = "MOSPI_ANALYST"
    RBI_MPC = "RBI_MPC"
    RBI_ECONOMIST = "RBI_ECONOMIST"
    DGCA_REGULATOR = "DGCA_REGULATOR"
    DGCA_INSPECTOR = "DGCA_INSPECTOR"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"
    PUBLIC_AUDITOR = "PUBLIC_AUDITOR"


ROLE_PERMISSIONS: dict[UserRole, list[str]] = {
    UserRole.SYSTEM_ADMIN: [
        "view_all", "mospi_read", "mospi_write", "rbi_read", "rbi_write",
        "dgca_read", "dgca_write", "system_admin", "manage_alerts",
        "manage_workers", "train_models", "trigger_ingest", "sync_esankhyiki",
        "simulate_policy", "export_all", "inspect_provenance"
    ],
    UserRole.MOSPI_ADMIN: [
        "view_all", "mospi_read", "mospi_write", "export_statutory",
        "sync_esankhyiki", "trigger_cpi_calc", "simulate_policy",
        "inspect_provenance", "export_reports"
    ],
    UserRole.MOSPI_ANALYST: [
        "view_all", "mospi_read", "export_statutory", "simulate_policy",
        "inspect_provenance", "export_reports"
    ],
    UserRole.RBI_MPC: [
        "view_all", "rbi_read", "rbi_write", "simulate_policy",
        "macro_stress_test", "export_reports", "view_forecasting",
        "inspect_provenance"
    ],
    UserRole.RBI_ECONOMIST: [
        "view_all", "rbi_read", "simulate_policy", "view_forecasting",
        "export_reports"
    ],
    UserRole.DGCA_REGULATOR: [
        "view_all", "dgca_read", "dgca_write", "manage_alerts",
        "inspect_corridors", "monitor_collusion", "export_reports",
        "inspect_provenance"
    ],
    UserRole.DGCA_INSPECTOR: [
        "view_all", "dgca_read", "inspect_corridors", "export_reports",
        "inspect_provenance"
    ],
    UserRole.PUBLIC_AUDITOR: [
        "view_all", "inspect_provenance", "export_reports",
        "view_validation"
    ]
}


class User(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    designation: str
    organization: str
    department: str
    avatar_color: str = "#38bdf8"
    permissions: list[str] = Field(default_factory=list)
    is_active: bool = True
    last_login_at: Optional[str] = None
    created_at: str


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class SwitchRoleRequest(BaseModel):
    target_role: UserRole


class TokenPayload(BaseModel):
    user_id: str
    username: str
    email: str
    role: UserRole
    exp: int


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User
    role_description: str
    accessible_features: list[str]


class DemoUserCredential(BaseModel):
    user_id: str
    username: str
    email: str
    default_password: str
    role: UserRole
    role_title: str
    full_name: str
    designation: str
    organization: str
    badge_theme: str
    description: str
    key_features: list[str]

"""
JetIndex - Authentication Service
User login/session management, role switching, demo role switching, and database interaction.
"""

import os
import sqlite3
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .models import LoginRequest, SwitchRoleRequest, User, UserRole
from .security import (
    get_permissions_for_role,
    hash_password,
    verify_access_token,
    verify_password,
)

DATABASE_DIR = os.path.join(os.path.expanduser("~"), ".jetindex", "data")
DATABASE_PATH = os.path.join(DATABASE_DIR, "auth.db")
DEMO_PASSWORD = "JetIndex2026!"

security = HTTPBearer(auto_error=False)


def get_db_connection():
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_auth_tables():
    """Creates users, sessions, and audit tables if they do not exist."""
    conn = get_db_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                designation TEXT,
                organization TEXT,
                department TEXT,
                avatar_color TEXT DEFAULT '#38bdf8',
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                last_login_at TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY,
                user_id TEXT,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)
        conn.commit()
    finally:
        conn.close()


PRE_SEEDED_USERS = [
    {
        "user_id": "usr_mospi_admin",
        "username": "mospi.admin",
        "email": "admin@mospi.gov.in",
        "full_name": "MoSPI Admin",
        "role": UserRole.MOSPI_ADMIN,
        "designation": "Deputy Director",
        "organization": "Ministry of Statistics and Programme Implementation",
        "department": "CPI Division",
        "avatar_color": "#ef4444",
    },
    {
        "user_id": "usr_mospi_analyst",
        "username": "mospi.analyst",
        "email": "analyst@mospi.gov.in",
        "full_name": "MoSPI Analyst",
        "role": UserRole.MOSPI_ANALYST,
        "designation": "Statistical Officer",
        "organization": "Ministry of Statistics and Programme Implementation",
        "department": "Price Statistics",
        "avatar_color": "#f59e0b",
    },
    {
        "user_id": "usr_rbi_mpc",
        "username": "rbi.mpc",
        "email": "mpc@rbi.org.in",
        "full_name": "RBI MPC Member",
        "role": UserRole.RBI_MPC,
        "designation": "Executive Director",
        "organization": "Reserve Bank of India",
        "department": "Monetary Policy Committee",
        "avatar_color": "#6366f1",
    },
    {
        "user_id": "usr_rbi_economist",
        "username": "rbi.economist",
        "email": "economist@rbi.org.in",
        "full_name": "RBI Economist",
        "role": UserRole.RBI_ECONOMIST,
        "designation": "Research Officer",
        "organization": "Reserve Bank of India",
        "department": "Department of Economic and Policy Research",
        "avatar_color": "#8b5cf6",
    },
    {
        "user_id": "usr_dgca_regulator",
        "username": "dgca.regulator",
        "email": "regulator@dgca.gov.in",
        "full_name": "DGCA Regulator",
        "role": UserRole.DGCA_REGULATOR,
        "designation": "Joint Director",
        "organization": "Directorate General of Civil Aviation",
        "department": "Economic Regulation",
        "avatar_color": "#10b981",
    },
    {
        "user_id": "usr_dgca_inspector",
        "username": "dgca.inspector",
        "email": "inspector@dgca.gov.in",
        "full_name": "DGCA Inspector",
        "role": UserRole.DGCA_INSPECTOR,
        "designation": "Air Safety Inspector",
        "organization": "Directorate General of Civil Aviation",
        "department": "Flight Operations",
        "avatar_color": "#3b82f6",
    },
    {
        "user_id": "usr_sys_admin",
        "username": "sys.admin",
        "email": "sysadmin@jetindex.dev",
        "full_name": "System Administrator",
        "role": UserRole.SYSTEM_ADMIN,
        "designation": "Lead Platform Engineer",
        "organization": "JetIndex Platform",
        "department": "Engineering",
        "avatar_color": "#64748b",
    },
    {
        "user_id": "usr_public_auditor",
        "username": "public.auditor",
        "email": "auditor@public.gov.in",
        "full_name": "Public Auditor",
        "role": UserRole.PUBLIC_AUDITOR,
        "designation": "Independent Auditor",
        "organization": "Comptroller and Auditor General",
        "department": "Performance Audit",
        "avatar_color": "#f59e0b",
    },
]


def ensure_demo_users_seeded():
    """Inserts pre-seeded users into database if not already present."""
    conn = get_db_connection()
    try:
        for user in PRE_SEEDED_USERS:
            existing = conn.execute("SELECT user_id FROM users WHERE user_id = ?", (user["user_id"],)).fetchone()
            if not existing:
                password_hash, password_salt = hash_password(DEMO_PASSWORD)
                conn.execute(
                    """
                    INSERT INTO users (user_id, username, email, full_name, role, designation,
                                       organization, department, avatar_color, password_hash, password_salt, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        user["user_id"],
                        user["username"],
                        user["email"],
                        user["full_name"],
                        user["role"].value,
                        user["designation"],
                        user["organization"],
                        user["department"],
                        user["avatar_color"],
                        password_hash,
                        password_salt,
                        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    ),
                )
        conn.commit()
    finally:
        conn.close()


def authenticate_user(req: LoginRequest) -> User | None:
    """Authenticates user with username/email and password."""
    conn = get_db_connection()
    try:
        user_row = conn.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?", (req.username_or_email, req.username_or_email)
        ).fetchone()
        if not user_row:
            return None
        if not verify_password(req.password, user_row["password_hash"], user_row["password_salt"]):
            return None
        if not user_row["is_active"]:
            return None

        role = UserRole(user_row["role"])
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        conn.execute("UPDATE users SET last_login_at = ? WHERE user_id = ?", (now, user_row["user_id"]))
        conn.commit()

        return User(
            user_id=user_row["user_id"],
            username=user_row["username"],
            email=user_row["email"],
            full_name=user_row["full_name"],
            role=role,
            designation=user_row["designation"],
            organization=user_row["organization"],
            department=user_row["department"],
            avatar_color=user_row["avatar_color"],
            permissions=get_permissions_for_role(role),
            is_active=bool(user_row["is_active"]),
            last_login_at=now,
            created_at=user_row["created_at"],
        )
    finally:
        conn.close()


def get_user_by_id(user_id: str) -> User | None:
    """Fetches user by ID."""
    conn = get_db_connection()
    try:
        user_row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not user_row:
            return None
        role = UserRole(user_row["role"])
        return User(
            user_id=user_row["user_id"],
            username=user_row["username"],
            email=user_row["email"],
            full_name=user_row["full_name"],
            role=role,
            designation=user_row["designation"],
            organization=user_row["organization"],
            department=user_row["department"],
            avatar_color=user_row["avatar_color"],
            permissions=get_permissions_for_role(role),
            is_active=bool(user_row["is_active"]),
            last_login_at=user_row["last_login_at"],
            created_at=user_row["created_at"],
        )
    finally:
        conn.close()


def get_demo_users() -> list[dict]:
    """Returns list of pre-seeded demo user profiles (safe for public exposure)."""
    demo_roles = [
        {
            "user_id": u["user_id"],
            "username": u["username"],
            "full_name": u["full_name"],
            "role": u["role"].value,
            "designation": u["designation"],
            "organization": u["organization"],
            "department": u["department"],
            "avatar_color": u["avatar_color"],
            "default_password": DEMO_PASSWORD,
            "role_description": f"{u['role'].value} - {u['designation']}",
            "key_features": _get_key_features(u["role"]),
            "badge_theme": _get_badge_theme(u["role"]),
        }
        for u in PRE_SEEDED_USERS
    ]
    return demo_roles


def _get_key_features(role: UserRole) -> list[str]:
    features = {
        UserRole.MOSPI_ADMIN: [
            "Statutory data management",
            "National index configuration",
            "CPI data sync from eSankhyiki",
            "Audit trail export",
        ],
        UserRole.MOSPI_ANALYST: [
            "Read CPI weights",
            "Price scenario projections",
            "Provenance inspection",
            "Statistical reports",
        ],
        UserRole.RBI_MPC: [
            "Policy impact simulations",
            "Real-time dashboard",
            "Model training",
            "High-level CPI tracking",
        ],
        UserRole.RBI_ECONOMIST: ["CPI dashboard", "Basic forecasts", "Report export"],
        UserRole.DGCA_REGULATOR: ["Route monitoring", "Alert management", "Corridor tracking", "Collusion detection"],
        UserRole.DGCA_INSPECTOR: ["Route corridor tracking", "Public dashboard", "Audit trails"],
        UserRole.SYSTEM_ADMIN: ["Full platform access", "Worker management", "Model training", "All dashboards"],
        UserRole.PUBLIC_AUDITOR: ["Read-only dashboard", "Provenance inspection", "Validation reports"],
    }
    return features.get(role, ["Basic dashboard access"])


def _get_badge_theme(role: UserRole) -> str:
    themes = {
        UserRole.MOSPI_ADMIN: "moef",
        UserRole.MOSPI_ANALYST: "moef",
        UserRole.RBI_MPC: "rbi",
        UserRole.RBI_ECONOMIST: "rbi",
        UserRole.DGCA_REGULATOR: "dgca",
        UserRole.DGCA_INSPECTOR: "dgca",
        UserRole.SYSTEM_ADMIN: "dev",
        UserRole.PUBLIC_AUDITOR: "public",
    }
    return themes.get(role, "default")


def switch_user_role(user_id: str, req: SwitchRoleRequest) -> User | None:
    """Switches user to a different pre-seeded role (demo mode only)."""
    new_user = next((u for u in PRE_SEEDED_USERS if u["role"] == req.target_role), None)
    if not new_user:
        return None
    return get_user_by_id(new_user["user_id"])


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Extracts and verifies current user from HTTPBearer token header."""
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization required")
    payload = verify_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = get_user_by_id(payload["uid"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User | None:
    """Non-raising user extraction for public endpoints."""
    if not credentials:
        return None
    try:
        payload = verify_access_token(credentials.credentials)
        if not payload:
            return None
        return get_user_by_id(payload["uid"])
    except Exception:
        return None


def require_permission(permission: str):
    """FastAPI dependency enforcing specific permission."""

    async def _check(user: User = Depends(get_current_user)):
        if permission not in user.permissions and "system_admin" not in user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"Missing required permission: {permission}"
            )
        return user

    return _check


def get_default_guest_user() -> User:
    """Returns a PUBLIC_AUDITOR default guest user when no token is provided."""
    return User(
        user_id="usr_public_auditor",
        username="public.auditor",
        email="auditor@public.gov.in",
        full_name="Public Auditor",
        role=UserRole.PUBLIC_AUDITOR,
        designation="Independent Auditor",
        organization="Comptroller and Auditor General",
        department="Performance Audit",
        avatar_color="#f59e0b",
        permissions=get_permissions_for_role(UserRole.PUBLIC_AUDITOR),
        is_active=True,
        last_login_at=None,
        created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )

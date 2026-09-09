"""
JetIndex - Security & Token Management
Cryptographic hashing, token signing, session lifecycle, and RBAC verification.
"""

import hashlib
import hmac
import secrets
import time
import json
import base64
import os
from typing import Optional
from .models import UserRole, ROLE_PERMISSIONS

# Platform secret for HMAC token signing (REQUIRED from the environment in production).
AUTH_SECRET = os.environ.get("AUTH_SECRET_KEY", "").strip() or "dev-only-insecure-secret--set-AUTH_SECRET_KEY-before-production"
TOKEN_EXPIRY_SECONDS = 86400 * 7  # 7 days


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a cryptographically secure salt."""
    if not salt:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000
    ).hex()
    return pw_hash, salt


def verify_password(plain_password: str, stored_hash: str, salt: str) -> bool:
    """Verifies a password against the stored PBKDF2 hash and salt."""
    pw_hash, _ = hash_password(plain_password, salt)
    return hmac.compare_digest(pw_hash, stored_hash)


def create_access_token(user_id: str, username: str, email: str, role: UserRole, custom_expiry: Optional[int] = None) -> str:
    """Creates a signed tamper-proof token containing user payload."""
    expiry = int(time.time()) + (custom_expiry or TOKEN_EXPIRY_SECONDS)
    payload = {
        "uid": user_id,
        "usr": username,
        "eml": email,
        "rol": role.value if hasattr(role, "value") else str(role),
        "exp": expiry,
        "iat": int(time.time()),
        "iss": "jetindex"
    }
    raw_payload = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    encoded_payload = base64.urlsafe_b64encode(raw_payload).decode("utf-8").rstrip("=")

    signature = hmac.new(
        AUTH_SECRET.encode("utf-8"),
        encoded_payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return f"{encoded_payload}.{signature}"


def verify_access_token(token: str) -> Optional[dict]:
    """Verifies signature and expiration of access token. Returns payload dict or None."""
    try:
        parts = token.strip().split(".")
        if len(parts) != 2:
            return None
        encoded_payload, signature = parts[0], parts[1]

        # Verify HMAC signature
        expected_sig = hmac.new(
            AUTH_SECRET.encode("utf-8"),
            encoded_payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_sig):
            return None

        # Decode payload
        padding = "=" * ((4 - len(encoded_payload) % 4) % 4)
        raw_payload = base64.urlsafe_b64decode(encoded_payload + padding)
        payload = json.loads(raw_payload.decode("utf-8"))

        # Check expiry
        if payload.get("exp", 0) < int(time.time()):
            return None

        return payload
    except Exception:
        return None


def get_permissions_for_role(role: UserRole) -> list:
    """Returns list of allowed actions for given user role."""
    return ROLE_PERMISSIONS.get(role, ["view_all"])


def check_has_permission(role: UserRole, required_permission: str) -> bool:
    """Checks whether the user role has the required permission."""
    perms = get_permissions_for_role(role)
    return required_permission in perms or "system_admin" in perms

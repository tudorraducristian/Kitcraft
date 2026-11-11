"""Conturi, parole și sesiuni. Nu importă `web.app`, ca să se poată testa singur."""

import hashlib
import hmac
import logging
import os
import secrets
import sqlite3
import uuid
from dataclasses import dataclass

ROLES = ("client", "admin", "inspector")
SESSION_COOKIE = "kitcraft_session"
SESSION_DAYS = 7
MIN_PASSWORD = 8

_SCRYPT = {"n": 2**14, "r": 8, "p": 1}

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class User:
    id: str
    email: str
    role: str
    brand_name: str | None


class EmailTaken(Exception):
    """Adresa de email are deja un cont."""


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, **_SCRYPT)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt_hex, digest_hex = stored.split("$")
    except ValueError:
        return False
    if scheme != "scrypt":
        return False
    digest = hashlib.scrypt(password.encode("utf-8"), salt=bytes.fromhex(salt_hex), **_SCRYPT)
    return hmac.compare_digest(digest.hex(), digest_hex)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _user_from_row(row) -> User:
    return User(id=row[0], email=row[1], role=row[2], brand_name=row[3])


def create_user(conn: sqlite3.Connection, email: str, password: str, role: str,
                brand_name: str | None = None) -> User:
    email = _normalize_email(email)
    if role not in ROLES:
        raise ValueError(f"Rol necunoscut: {role}")
    local, _, domain = email.partition("@")
    if not local or not domain:
        raise ValueError("Adresa de email nu e validă.")
    if len(password) < MIN_PASSWORD:
        raise ValueError(f"Parola trebuie să aibă cel puțin {MIN_PASSWORD} caractere.")
    if conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
        raise EmailTaken(email)
    uid = str(uuid.uuid4())
    try:
        conn.execute(
            "INSERT INTO users (id, email, password_hash, role, brand_name) VALUES (?, ?, ?, ?, ?)",
            (uid, email, hash_password(password), role, brand_name),
        )
    except sqlite3.IntegrityError as exc:  # două înregistrări simultane pe aceeași adresă
        raise EmailTaken(email) from exc
    conn.commit()
    return User(id=uid, email=email, role=role, brand_name=brand_name)


def authenticate(conn: sqlite3.Connection, email: str, password: str) -> User | None:
    row = conn.execute(
        "SELECT id, email, role, brand_name, password_hash FROM users WHERE email = ?",
        (_normalize_email(email),),
    ).fetchone()
    if row is None or not verify_password(password, row[4]):
        return None
    return _user_from_row(row)


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(conn: sqlite3.Connection, user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    conn.execute(
        "INSERT INTO auth_sessions (token_hash, user_id, expires_at) "
        "VALUES (?, ?, datetime('now', ?))",
        (_token_hash(token), user_id, f"+{SESSION_DAYS} days"),
    )
    conn.commit()
    return token


def user_for_token(conn: sqlite3.Connection, token: str | None) -> User | None:
    if not token:
        return None
    row = conn.execute(
        """
        SELECT u.id, u.email, u.role, u.brand_name
        FROM auth_sessions s JOIN users u ON u.id = s.user_id
        WHERE s.token_hash = ? AND s.expires_at > datetime('now')
        """,
        (_token_hash(token),),
    ).fetchone()
    return _user_from_row(row) if row else None


def delete_session(conn: sqlite3.Connection, token: str | None) -> None:
    if not token:
        return
    conn.execute("DELETE FROM auth_sessions WHERE token_hash = ?", (_token_hash(token),))
    conn.commit()


_PUBLIC_PATHS = ("/login", "/register", "/logout", "/healthz")
_ROLE_PREFIXES = (("/client", "client"), ("/inspector", "inspector"))
_HOMES = {"admin": "/", "client": "/client/cereri", "inspector": "/inspector/"}


def _under(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix + "/")


def required_role(path: str) -> str | None:
    """Rolul cerut de o cale. `None` înseamnă public. Tot ce nu e scris altfel e al adminului."""
    if path in _PUBLIC_PATHS or path.startswith("/static/"):
        return None
    for prefix, role in _ROLE_PREFIXES:
        if _under(path, prefix):
            return role
    return "admin"


def home_for(role: str) -> str:
    return _HOMES[role]


def ensure_staff_accounts(conn: sqlite3.Connection) -> None:
    """Creează o singură dată contul de admin și pe cel de inspector, din `.env`."""
    staff = (
        ("admin", "KITCRAFT_ADMIN_EMAIL", "admin@kitcraft.local", "KITCRAFT_ADMIN_PASSWORD"),
        ("inspector", "KITCRAFT_INSPECTOR_EMAIL", "inspector@kitcraft.local", "KITCRAFT_INSPECTOR_PASSWORD"),
    )
    for role, email_var, default_email, password_var in staff:
        if conn.execute("SELECT 1 FROM users WHERE role = ?", (role,)).fetchone():
            continue
        password = os.environ.get(password_var)
        if not password:
            log.warning("Contul de %s nu e creat: lipsește %s din .env.", role, password_var)
            continue
        try:
            create_user(conn, os.environ.get(email_var, default_email), password, role)
        except (ValueError, EmailTaken) as exc:
            # O parolă prea scurtă în .env nu trebuie să oprească pornirea aplicației.
            log.warning("Contul de %s nu e creat, verifică %s și %s din .env: %s",
                        role, email_var, password_var, exc or "adresa e deja folosită")

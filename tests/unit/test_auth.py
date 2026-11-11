import pytest

from web.auth import (
    EmailTaken,
    authenticate,
    create_session,
    create_user,
    delete_session,
    ensure_staff_accounts,
    hash_password,
    user_for_token,
    verify_password,
)


def test_hash_is_not_the_password_and_verifies():
    stored = hash_password("parola-buna")
    assert "parola-buna" not in stored and stored.startswith("scrypt$")
    assert verify_password("parola-buna", stored) and not verify_password("alta", stored)


def test_create_user_lowercases_email(conn):
    assert create_user(conn, "Ana@Brand.RO", "parola-buna", "client", "Aurora").email == "ana@brand.ro"


def test_duplicate_email_with_other_case_is_refused(conn):
    create_user(conn, "ana@brand.ro", "parola-buna", "client", "Aurora")
    with pytest.raises(EmailTaken):
        create_user(conn, "ANA@brand.ro", "parola-buna", "client", "Aurora")


@pytest.mark.parametrize("email,password,role", [
    ("fara-arond", "parola-buna", "client"), ("a@b.ro", "scurta", "client"), ("a@b.ro", "parola-buna", "sef"),
])
def test_create_user_rejects_bad_input(conn, email, password, role):
    with pytest.raises(ValueError):
        create_user(conn, email, password, role)


def test_authenticate(conn):
    create_user(conn, "ana@brand.ro", "parola-buna", "client", "Aurora")
    assert authenticate(conn, "ANA@brand.ro", "parola-buna").role == "client"
    assert authenticate(conn, "ana@brand.ro", "gresita") is None
    assert authenticate(conn, "nimeni@brand.ro", "parola-buna") is None


def test_session_roundtrip_and_delete(conn):
    user = create_user(conn, "ana@brand.ro", "parola-buna", "client", "Aurora")
    token = create_session(conn, user.id)
    assert user_for_token(conn, token).id == user.id
    assert token not in str(conn.execute("SELECT token_hash FROM auth_sessions").fetchone()[0])
    delete_session(conn, token)
    assert user_for_token(conn, token) is None


def test_expired_session_is_ignored(conn):
    user = create_user(conn, "ana@brand.ro", "parola-buna", "client", "Aurora")
    token = create_session(conn, user.id)
    conn.execute("UPDATE auth_sessions SET expires_at = datetime('now', '-1 minute')")
    assert user_for_token(conn, token) is None


def test_ensure_staff_accounts_creates_once(conn, monkeypatch):
    monkeypatch.setenv("KITCRAFT_ADMIN_PASSWORD", "parola-admin")
    monkeypatch.setenv("KITCRAFT_INSPECTOR_PASSWORD", "parola-insp")
    ensure_staff_accounts(conn)
    monkeypatch.setenv("KITCRAFT_ADMIN_PASSWORD", "alta-parola")
    ensure_staff_accounts(conn)
    assert authenticate(conn, "admin@kitcraft.local", "parola-admin").role == "admin"
    assert authenticate(conn, "inspector@kitcraft.local", "parola-insp").role == "inspector"


def test_ensure_staff_accounts_skips_without_password(conn, monkeypatch):
    monkeypatch.delenv("KITCRAFT_ADMIN_PASSWORD", raising=False)
    monkeypatch.delenv("KITCRAFT_INSPECTOR_PASSWORD", raising=False)
    ensure_staff_accounts(conn)
    assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0

import sqlite3
from pathlib import Path
import pytest


SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


@pytest.fixture
def conn():
    """In-memory SQLite connection with schema applied."""
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    yield c
    c.close()


from fastapi.testclient import TestClient


ADMIN_EMAIL = "admin@kitcraft.local"
ADMIN_PASSWORD = "test-admin-pass"
INSPECTOR_EMAIL = "inspector@kitcraft.local"
INSPECTOR_PASSWORD = "test-inspector-pass"


@pytest.fixture
def anon_client(tmp_path, monkeypatch):
    """FastAPI TestClient bound to an isolated DB + uploads dir, not logged in."""
    db_path = tmp_path / "test.db"
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("UPLOADS_DIR", str(uploads_dir))
    monkeypatch.setenv("KITCRAFT_ADMIN_EMAIL", ADMIN_EMAIL)
    monkeypatch.setenv("KITCRAFT_ADMIN_PASSWORD", ADMIN_PASSWORD)
    monkeypatch.setenv("KITCRAFT_INSPECTOR_EMAIL", INSPECTOR_EMAIL)
    monkeypatch.setenv("KITCRAFT_INSPECTOR_PASSWORD", INSPECTOR_PASSWORD)

    from web import app as web_app
    # Force re-evaluation of env-derived module constants
    import importlib
    importlib.reload(web_app)
    web_app.init_database()
    return TestClient(web_app.app)


def _login(test_client: TestClient, email: str, password: str) -> TestClient:
    r = test_client.post("/login", data={"email": email, "password": password},
                         follow_redirects=False)
    assert r.status_code == 303, f"login failed for {email}: {r.status_code}"
    return test_client


@pytest.fixture
def client(anon_client):
    """The old fixture name: a TestClient logged in as admin."""
    return _login(anon_client, ADMIN_EMAIL, ADMIN_PASSWORD)


@pytest.fixture
def login_as(anon_client):
    """Factory: a fresh TestClient on the same app, logged in with the given role.
    For `client` it registers a new account with a unique email."""
    from web import app as web_app
    counter = {"n": 0}

    def _make(role: str) -> TestClient:
        c = TestClient(web_app.app)
        if role == "admin":
            return _login(c, ADMIN_EMAIL, ADMIN_PASSWORD)
        if role == "inspector":
            return _login(c, INSPECTOR_EMAIL, INSPECTOR_PASSWORD)
        if role == "client":
            counter["n"] += 1
            r = c.post("/register", data={
                "email": f"client{counter['n']}@brand.ro",
                "password": "parola-buna",
                "brand_name": f"Brand {counter['n']}",
            }, follow_redirects=False)
            assert r.status_code == 303, f"register failed: {r.status_code}"
            return c
        raise ValueError(f"unknown role: {role}")

    return _make


class _FakeLLM:
    """Replacement for LLMClient used in E2E tests."""

    def __init__(self):
        self.text_responses: list[str] = []
        self.vision_responses: list[str] = []
        self.text_calls: list[tuple[str, str]] = []
        self.vision_calls: list[tuple[str, list]] = []

    def queue_text(self, response: str) -> None:
        self.text_responses.append(response)

    def queue_vision(self, response: str) -> None:
        self.vision_responses.append(response)

    def complete_text(self, system: str, user: str) -> str:
        self.text_calls.append((system, user))
        if not self.text_responses:
            raise RuntimeError("FakeLLM: no queued text responses")
        return self.text_responses.pop(0)

    def complete_vision(self, system: str, content_blocks: list) -> str:
        self.vision_calls.append((system, content_blocks))
        if not self.vision_responses:
            raise RuntimeError("FakeLLM: no queued vision responses")
        return self.vision_responses.pop(0)


@pytest.fixture
def fake_llm(monkeypatch):
    fake = _FakeLLM()
    from web import app as web_app
    monkeypatch.setattr(web_app, "get_llm_client", lambda: fake)
    return fake


@pytest.fixture
def fake_image_engine(monkeypatch):
    """Patch image_matcher.engine functions used by web routes.
    Tests set .sim_response / .compare_response before triggering the route."""
    class _Engine:
        sim_response: dict = {"criteria": []}
        compare_response: dict = {"rows": [], "summary": {"matched": 0, "mismatched": 0}}
        analyze_calls: list = []
        compare_calls: list = []

        @classmethod
        def reset(cls):
            cls.analyze_calls = []
            cls.compare_calls = []

    _Engine.reset()

    def fake_analyze_sim(sim_path, model="claude-sonnet-4-6"):
        _Engine.analyze_calls.append(str(sim_path))
        return _Engine.sim_response

    def fake_compare_real(sim_report, sim_path, real_path, model="claude-sonnet-4-6", max_tokens=8192):
        _Engine.compare_calls.append((sim_report, str(sim_path), str(real_path)))
        return _Engine.compare_response

    from web import app as web_app
    monkeypatch.setattr(web_app, "analyze_sim", fake_analyze_sim)
    monkeypatch.setattr(web_app, "compare_real", fake_compare_real)

    return _Engine

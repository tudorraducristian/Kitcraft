import pytest


ADMIN_PAGES = ["/", "/sessions/new", "/matches/new", "/docs", "/openapi.json"]


def _form(email):
    return {"email": email, "password": "parola-buna", "brand_name": "Aurora"}


@pytest.mark.parametrize("path", ADMIN_PAGES + ["/client/cereri", "/inspector/", "/clientx", "/inspector-x", "/loginx"])
def test_anonymous_is_sent_to_login(anon_client, path):
    r = anon_client.get(path, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/login"


@pytest.mark.parametrize("path", ["/healthz", "/login", "/register", "/static/styles.css"])
def test_public_pages_stay_public(anon_client, path):
    assert anon_client.get(path).status_code == 200


@pytest.mark.parametrize("role", ["client", "inspector"])
@pytest.mark.parametrize("path", ["/sessions/new", "/matches/new", "/docs", "/clientx"])
def test_other_roles_cannot_reach_admin_pages(login_as, role, path):
    assert login_as(role).get(path, follow_redirects=False).status_code == 403


def test_client_cannot_post_to_admin_routes(login_as):
    r = login_as("client").post("/email-agent/fetch", data={"date_start": "2026-01-01", "date_end": "2026-01-02"})
    assert r.status_code == 403


def test_roles_cannot_reach_each_others_pages(login_as):
    assert login_as("client").get("/inspector/").status_code == 403
    assert login_as("inspector").get("/client/cereri").status_code == 403
    assert login_as("admin").get("/client/cereri").status_code == 403
    assert login_as("admin").get("/inspector/").status_code == 403


@pytest.mark.parametrize("role,home", [("client", "/client/cereri"), ("inspector", "/inspector/")])
def test_root_sends_each_role_home(login_as, role, home):
    r = login_as(role).get("/", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == home


def test_admin_keeps_the_chooser(client):
    assert "Am o descriere" in client.get("/").text


def test_register_creates_client_and_logs_in(anon_client):
    r = anon_client.post("/register", data=_form("ana@brand.ro"), follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/client/cereri"
    assert anon_client.get("/client/cereri").status_code == 200


def test_register_ignores_a_forged_role(anon_client):
    anon_client.post("/register", data={**_form("ana@brand.ro"), "role": "admin"})
    assert anon_client.get("/sessions/new", follow_redirects=False).status_code == 403


@pytest.mark.parametrize("change", [{"email": "fara-arond"}, {"password": "scurta"}, {"brand_name": "  "}])
def test_register_rejects_bad_input_with_a_message(anon_client, change):
    r = anon_client.post("/register", data={**_form("ana@brand.ro"), **change})
    assert r.status_code == 422 and "kitcraft_session" not in r.cookies


def test_register_duplicate_email_shows_message(anon_client):
    anon_client.post("/register", data=_form("ana@brand.ro"))
    anon_client.post("/logout")
    r = anon_client.post("/register", data=_form("ANA@brand.ro"))
    assert r.status_code == 409 and "folosit" in r.text


def test_login_wrong_password(anon_client):
    r = anon_client.post("/login", data={"email": "admin@kitcraft.local", "password": "gresita"})
    assert r.status_code == 401 and "kitcraft_session" not in r.cookies


def test_session_cookie_flags(anon_client):
    r = anon_client.post("/login", data={"email": "admin@kitcraft.local", "password": "test-admin-pass"}, follow_redirects=False)
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie


def test_logout_invalidates_the_session_on_the_server(login_as):
    c = login_as("client")
    stale = c.cookies.get("kitcraft_session")
    c.post("/logout")
    c.cookies.set("kitcraft_session", stale)
    assert c.get("/client/cereri", follow_redirects=False).status_code == 303


def test_htmx_request_without_session_redirects_the_whole_page(anon_client):
    r = anon_client.post("/email-agent/fetch", headers={"HX-Request": "true"}, follow_redirects=False)
    assert r.headers["HX-Redirect"] == "/login"


def test_app_is_called_kitcraft(anon_client):
    html = anon_client.get("/login").text
    assert "Kitcraft" in html and "Ciptronic" not in html

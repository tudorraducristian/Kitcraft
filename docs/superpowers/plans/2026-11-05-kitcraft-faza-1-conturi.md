# Kitcraft, faza 1: cele trei conturi, plan de implementare

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** aplicația are conturi de client, admin și inspector, iar fiecare rol ajunge doar la paginile lui.

**Architecture:** un middleware cu regula „totul e al adminului, în afară de ce e scris altfel”, deci o rută nouă uitată rămâne protejată. Parolele stau ca hash cu `hashlib.scrypt`, iar sesiunea e un token aleator în cookie, cu hash-ul în baza de date. Nu apar dependențe noi. Rutele noi stau în `web/routes_*.py`, cu `APIRouter`, ca `web/app.py` să nu mai crească.

**Tech Stack:** FastAPI, Jinja2, SQLite, biblioteca standard Python (`hashlib`, `secrets`, `hmac`), pytest cu `TestClient`.

**Spec:** `docs/superpowers/specs/2026-11-05-kitcraft-client-admin-inspector-design.md`, secțiunile 7.1.1, 7.3.1, 7.3.12, 7.4.1, 7.4.6, 9.11, 9.13.

## Global Constraints

- Trei roluri: `client`, `admin`, `inspector`, tot local. Regula „nu expune serverul pe rețea fără protecție” rămâne.
- Clientul își face singur cont, cu email, parolă și numele brandului.
- Adminul și inspectorul au câte un singur cont, creat la instalare, nu prin înregistrare publică. Parolele inițiale vin din `.env`, care nu se comite.
- Parolele se stochează doar ca hash, iar sesiunea stă într-un cookie.
- Paginile de azi rămân și se comportă la fel, dar aparțin adminului. `/healthz` rămâne public.
- Tabelele de azi rămân neschimbate. Doar tabele noi, cu `CREATE TABLE IF NOT EXISTS`.
- Cele 168 de teste trec, iar verificările din ele nu se schimbă. Fixture-ul `client` intră logat ca admin.
- Comanda de bază: `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`.

## Review Focus

- Căi asemănătoare, ca `/clientx`, `/inspector-x`, `/loginx`: rămân ale adminului, nu devin publice sau ale clientului. Test în Task 2.
- Paginile generate de FastAPI, `/docs` și `/openapi.json`: nu sunt publice. Test în Task 2.
- O cerere HTMX cu sesiunea expirată: redirecționează toată pagina la login, nu pune formularul de login în mijlocul paginii. Test în Task 2.
- Același email scris cu alte majuscule la înregistrare sau la login: e același cont. Teste în Task 1.
- Un câmp `role=admin` adăugat de mână în formularul de înregistrare: e ignorat, contul rămâne de client. Test în Task 2.

---

### Task 1: Utilizatorii, parolele și sesiunile

**Files:**
- Modify: `db/schema.sql`, se adaugă la sfârșit
- Create: `web/auth.py`
- Test: `tests/unit/test_auth.py`

**Interfaces:**
- Produces, în `web/auth.py`. Modulul nu importă `web.app`, ca să se poată testa singur:
  - `ROLES = ("client", "admin", "inspector")`
  - `SESSION_COOKIE = "kitcraft_session"`, `SESSION_DAYS = 7`, `MIN_PASSWORD = 8`
  - `@dataclass(frozen=True) class User: id: str; email: str; role: str; brand_name: str | None`
  - `class EmailTaken(Exception)`
  - `hash_password(password: str) -> str`, format `scrypt$<sare_hex>$<hash_hex>`
  - `verify_password(password: str, stored: str) -> bool`, cu `hmac.compare_digest`
  - `create_user(conn, email, password, role, brand_name=None) -> User`. Email-ul se salvează cu litere mici. `ValueError` la rol necunoscut, email fără `@` sau parolă sub 8 caractere. `EmailTaken` la duplicat.
  - `authenticate(conn, email, password) -> User | None`
  - `create_session(conn, user_id) -> str` întoarce tokenul brut, iar în bază stă doar SHA-256 al lui
  - `user_for_token(conn, token) -> User | None`, cu `None` dacă tokenul e necunoscut sau expirat
  - `delete_session(conn, token) -> None`
  - `ensure_staff_accounts(conn) -> None`. Citește `KITCRAFT_ADMIN_EMAIL`, implicit `admin@kitcraft.local`, `KITCRAFT_ADMIN_PASSWORD`, `KITCRAFT_INSPECTOR_EMAIL`, implicit `inspector@kitcraft.local`, și `KITCRAFT_INSPECTOR_PASSWORD`. Dacă parola lipsește din mediu, sare peste cont și scrie un `logging.warning`. Dacă rolul are deja un cont, nu schimbă nimic.

- [ ] **Step 1: Adaugă tabelele în `db/schema.sql`**

```sql
CREATE TABLE IF NOT EXISTS users (
    id            TEXT PRIMARY KEY,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('client', 'admin', 'inspector')),
    brand_name    TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    token_hash TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    expires_at TEXT NOT NULL
);
```

- [ ] **Step 2: Scrie testele care pică, în `tests/unit/test_auth.py`, cu fixture-ul `conn`**

```python
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
```

- [ ] **Step 3: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_auth.py -v`
Expected: FAIL, `ModuleNotFoundError: web.auth`.

- [ ] **Step 4: Implementează `web/auth.py`**

`hashlib.scrypt` cu `n=2**14, r=8, p=1`, sare de 16 octeți din `secrets.token_bytes`. `id`-urile sunt `uuid4`, ca în `db/repository.py`. Funcțiile fac singure `conn.commit()`, ca în `db/repository.py`.

- [ ] **Step 5: Rulează testele și verifică faptul că trec**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_auth.py -v`
Expected: toate trec.

- [ ] **Step 6: Commit**

```bash
git add db/schema.sql web/auth.py tests/unit/test_auth.py
git commit -m "feat(auth): utilizatori cu trei roluri, parole cu scrypt si sesiuni"
```

### Task 2: Protejarea paginilor, login și înregistrare

**Files:**
- Modify: `web/auth.py`, `web/app.py`, `web/templates/base.html`, `tests/conftest.py`
- Create: `web/routes_auth.py`, `web/routes_client.py`, `web/routes_inspector.py`, `web/templates/login.html`, `web/templates/register.html`, `web/templates/client/cereri.html`, `web/templates/inspector/index.html`
- Test: `tests/e2e/test_auth_routes.py`

**Interfaces:**
- Consumes: tot din `web/auth.py`, din Task 1.
- Produces:
  - `web.auth.required_role(path: str) -> str | None`, unde `None` înseamnă public. Public: `/login`, `/register`, `/logout`, `/healthz`, tot ce începe cu `/static/`. `/client` și `/client/...` cer `client`. `/inspector` și `/inspector/...` cer `inspector`. Orice altceva cere `admin`, cu excepția lui `/`, tratat separat în middleware.
  - `web.auth.home_for(role: str) -> str`: `admin` → `/`, `client` → `/client/cereri`, `inspector` → `/inspector/`
  - `request.state.user: User | None`, pus de middleware pe fiecare cerere
  - Rute: `GET/POST /login`, `GET/POST /register`, `POST /logout`, `GET /client/cereri`, `GET /inspector/`
  - Fixture-uri în `tests/conftest.py`: `anon_client`, `client`, care rămâne numele vechi, logat ca admin, și `login_as(role: str) -> TestClient`, care face câte un client de test nou pe aceeași aplicație și, pentru `client`, își face singur cont

**Regula de import a routerelor:** fiecare `web/routes_*.py` are la început `from web import app as web_app` și folosește la apel `web_app.get_conn()` și `web_app.TEMPLATES`. La sfârșitul lui `web/app.py`, importurile `from web import routes_auth, routes_client, routes_inspector` sunt urmate de câte un `app.include_router(...)`. Așa, `importlib.reload(web_app)` din fixture primește din nou routerele, iar testele pot înlocui în continuare `web_app.get_llm_client`.

- [ ] **Step 1: Scrie testele care pică, în `tests/e2e/test_auth_routes.py`**

```python
ADMIN_PAGES = ["/", "/sessions/new", "/matches/new", "/docs", "/openapi.json"]

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
```

`_form(email)` întoarce `{"email": email, "password": "parola-buna", "brand_name": "Aurora"}`.

- [ ] **Step 2: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/e2e/test_auth_routes.py -v`
Expected: FAIL, fixture-ul `anon_client` nu există.

- [ ] **Step 3: Schimbă fixture-urile din `tests/conftest.py`**

`anon_client` e fostul `client`, cu în plus `KITCRAFT_ADMIN_PASSWORD=test-admin-pass` și `KITCRAFT_INSPECTOR_PASSWORD=test-inspector-pass`, puse înainte de `importlib.reload`. `client` cere `anon_client`, face `POST /login` ca admin și îl întoarce. `login_as` construiește de fiecare dată un `TestClient(web_app.app)` nou. Pentru `client` face `POST /register` cu un email unic.

- [ ] **Step 4: Implementează `required_role`, `home_for` și middleware-ul**

În `web/app.py`, `init_database()` cheamă `auth.ensure_staff_accounts` după schemă. Middleware-ul, cu `@app.middleware("http")`:

1. citește cookie-ul, deschide `get_conn()`, pune `request.state.user`;
2. `required_role(path) is None` → lasă cererea să treacă;
3. fără utilizator: dacă cererea are antetul `HX-Request`, răspunde 200 cu `HX-Redirect: /login`, altfel 303 la `/login`;
4. `path == "/"`: orice rol logat poate. Dacă nu e admin, 303 la `home_for(role)`;
5. rolul nu corespunde: `HTTPException` nu ajunge la handler din middleware, deci răspunde direct cu 403, cu aceeași logică din `http_exception_handler`: pagină `error.html` pentru `Accept: text/html`, JSON altfel.

`required_role` compară exact: `path == p or path.startswith(p + "/")`, deci `/clientx` rămâne al adminului.

- [ ] **Step 5: Implementează `web/routes_auth.py`, `web/routes_client.py`, `web/routes_inspector.py` și șabloanele**

- `POST /register` citește doar `email`, `password`, `brand_name` și creează mereu rolul `client`. Răspunde 422 la date greșite, 409 la email folosit, cu mesajul „Adresa e deja folosită”.
- `POST /login` dă 401 și mesajul „Email sau parolă greșită”, fără să spună care dintre ele.
- Cookie-ul: `httponly=True`, `samesite="lax"`, `max_age=SESSION_DAYS*86400`, `path="/"`. `POST /logout` șterge sesiunea din bază și cookie-ul, apoi 303 la `/login`.
- `GET /client/cereri` și `GET /inspector/` sunt pagini goale, cu titlu și un mesaj „Nu ai încă nimic aici”. Se umplu în fazele 2 și 3.
- `base.html` arată, când `request.state.user` există, emailul și un formular `POST /logout`. Paginile vechi nu primesc nimic în plus, pentru că șablonul citește din `request`.

- [ ] **Step 6: Rulează testele noi**

Run: `.venv/Scripts/python.exe -m pytest tests/e2e/test_auth_routes.py -v`
Expected: toate trec.

- [ ] **Step 7: Rulează toate testele**

Run: `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`
Expected: toate trec, inclusiv cele 168 vechi, fără să fi schimbat vreo verificare din ele.

- [ ] **Step 8: Commit**

```bash
git add web tests/conftest.py tests/e2e/test_auth_routes.py
git commit -m "feat(auth): fiecare rol ajunge doar la paginile lui, cu login si inregistrare"
```

### Task 3: Numele Kitcraft și regulile proiectului

**Files:**
- Modify: `web/app.py:80`, `web/templates/base.html`, `web/templates/index.html`, `.env.example`, `README.md`
- Modify, în AIS-OS: `Licenta\ciptronic-validator\CLAUDE.md`
- Test: `tests/e2e/test_auth_routes.py`

**Interfaces:** nimic nou.

- [ ] **Step 1: Scrie testul care pică**

```python
def test_app_is_called_kitcraft(anon_client):
    html = anon_client.get("/login").text
    assert "Kitcraft" in html and "Ciptronic" not in html
```

- [ ] **Step 2: Rulează testul și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/e2e/test_auth_routes.py::test_app_is_called_kitcraft -v`
Expected: FAIL, pagina conține „Ciptronic”.

- [ ] **Step 3: Schimbă numele**

Titlul FastAPI, `<title>` și marca din `base.html` devin Kitcraft, iar `brand__mark` devine `K`. Prompturile `prompts/discovery.md` și `prompts/inspector.md` rămân neatinse, deși specul 12 pomenește `discovery.md`: textul lor nu se vede în aplicație, iar `tests/unit/test_discovery.py:162` și `tests/unit/test_inspector.py:151` verifică exact acele fraze. Numele din baza de date, `ciptronic.db`, și folderul rămân.

- [ ] **Step 4: Documentează**

- `.env.example`: `KITCRAFT_ADMIN_PASSWORD=`, `KITCRAFT_INSPECTOR_PASSWORD=`, plus emailurile opționale.
- `README.md`: cum se pornește cu parolele din `.env`.
- `Licenta\ciptronic-validator\CLAUDE.md`, secțiunea D: regula „Single-user, fără auth, deliberat” devine „Trei roluri, client, admin și inspector, tot local. Nu expune serverul pe rețea fără protecție.” Secțiunea A: „Aplicație web locală, cu trei roluri”.

- [ ] **Step 5: Tudor își pune parolele în `.env`**

Tudor adaugă în `.env` `KITCRAFT_ADMIN_PASSWORD=` și `KITCRAFT_INSPECTOR_PASSWORD=`, cu parole alese de el, apoi repornește aplicația. Fără ele, aplicația pornește, dar nu există conturi de staff.

- [ ] **Step 6: Rulează toate testele și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`
Expected: toate trec.

```bash
git add web .env.example README.md tests/e2e/test_auth_routes.py
git commit -m "feat(ui): aplicatia se numeste Kitcraft"
```

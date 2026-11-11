# Kitcraft, faza 5: istoricul și contractele, plan de implementare

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** contul de client are istoricul comenzilor și contractele lui, iar adminul încarcă PDF-ul contractului la cerere.

**Architecture:** contractul doar se stochează și se servește, fără parsare. Analiza are specul ei, mai târziu. Trimiterea pe email refolosește `outbox` și `EmailNotifier` din faza 4. Istoricul sunt chiar cererile, pentru că prețurile și cantitățile rămân în afara proiectului.

**Tech Stack:** FastAPI, Jinja2, SQLite, pytest.

**Spec:** `docs/superpowers/specs/2026-11-05-kitcraft-client-admin-inspector-design.md`, secțiunile 6.2, 7.1.8, 7.1.10, 7.2.7, 7.3.11, 9.8, 9.9, 9.12.

**Depinde de:** fazele 1–4.

## Global Constraints

- Aplicația nu scrie și nu analizează contracte în această fază.
- Adminul încarcă PDF-ul la cerere, după ce clientul aprobă modelul. Încărcarea nu oprește și nu condiționează verificările.
- O cerere are un singur contract, iar o încărcare nouă îl înlocuiește.
- Clientul cu cont îl vede în interfață, doar pentru citire. Clientul de pe email îl primește ca PDF atașat, automat la încărcare.
- Se verifică tipul și limita de 5 MB. Contractul se servește doar celui care are dreptul.
- Tabelele de azi rămân neschimbate.
- Comanda de bază: `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`.

## Review Focus

- Un fișier cu extensia `.pdf` care nu e PDF: e refuzat, fără să se piardă contractul existent. Test în Task 1.
- Adminul apasă de două ori la încărcarea aceluiași PDF pe o cerere din email: clientul primește un singur email. Test în Task 1.
- Adminul înlocuiește contractul cu altul: clientul de pe email primește noul PDF, iar cel cu cont vede doar varianta nouă. Test în Task 1.
- Un nume de fișier cu `../` sau cu caractere ciudate: nu ajunge pe disc și nu strică antetul de descărcare. Test în Task 1.
- Un client cere contractul altui client, știind id-ul: primește 404. Test în Task 2.

---

### Task 1: Încărcarea contractului

**Files:**
- Modify: `db/schema.sql`, `cereri/notifier.py`, `cereri/email_notifier.py`, `web/routes_admin.py`, `web/templates/admin/cerere.html`
- Create: `cereri/contracts.py`, `prompts/emailuri/contract.md`
- Test: `tests/unit/test_contracts.py`, `tests/e2e/test_admin_contracte.py`

**Interfaces:**
- Consumes: `cereri.outbox`.
- Produces, în `cereri/notifier.py`: `Notifier.contract_ready(cerere, path: Path) -> bool`. La `AccountNotifier`, scrie cu `add_message` „Contractul e disponibil.” La `EmailNotifier`, `action_key` e `contract:<primele 12 caractere din SHA-256 al fișierului>`, cu PDF-ul atașat.
- Produces, în `cereri/contracts.py`:
  - `class ContractRejected(Exception)`
  - `save_contract(conn, notifier, uploads_dir: Path, cerere_id: str, content: bytes, original_name: str) -> Path`
  - `get_contract(conn, cerere_id) -> Row | None`
  - `contracts_for_user(conn, user_id) -> list[Row]`
- Produces, ruta: `POST /admin/cereri/{id}/contract`, cu `fisier`.

- [ ] **Step 1: Adaugă tabelul în `db/schema.sql`**

```sql
CREATE TABLE IF NOT EXISTS contracte (
    cerere_id     TEXT PRIMARY KEY REFERENCES cereri(id),
    path          TEXT NOT NULL,
    original_name TEXT NOT NULL,
    uploaded_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
```

- [ ] **Step 2: Scrie testele care pică**

```python
def test_saves_pdf_with_our_own_name(...):
    assert path.name == "contract.pdf" and path.parent.name == cid

@pytest.mark.parametrize("content", [b"nu e pdf", b"", b"\x89PNG\r\n"])
def test_rejects_what_is_not_a_pdf(content, ...): ...
def test_rejects_over_five_mb(...): ...

@pytest.mark.parametrize("status", [IN_DESCRIERE, MODEL_DE_APROBAT])
def test_refused_before_client_approval(status, ...): ...            # InvalidState

@pytest.mark.parametrize("status", [APROBATA, IN_VERIFICARE, VALIDATA])
def test_allowed_after_approval(status, ...): ...

def test_rejected_file_keeps_the_existing_contract(...):
    assert get_contract(conn, cid)["path"] == old and Path(old).read_bytes() == old_bytes

def test_new_upload_replaces_the_old_one(...): ...
def test_strange_file_name_stays_only_as_display_name(...):
    assert "contract.pdf" == path.name and get_contract(conn, cid)["original_name"] == "contract.pdf"
    # numele original păstrează doar baza, fără cale și fără caractere de control

def test_contract_does_not_change_request_or_piece_status(...): ...
def test_email_client_gets_the_pdf_attached(...):
    assert gmail.last_attachments[0].suffix == ".pdf" and gmail.last_to == "ana@brand.ro"

def test_same_file_twice_sends_one_email(...):
    assert gmail.sent_count == 1

def test_different_file_sends_again(...): ...
def test_failed_email_shows_in_outbox_and_keeps_the_contract(...): ...
def test_account_client_gets_a_message_not_an_email(...): ...
```

```python
def test_admin_uploads_from_the_request_page(client, ...): ...
def test_upload_form_appears_only_after_approval(client, ...): ...
def test_bad_file_answers_422_with_a_message(client, ...): ...
def test_other_roles_cannot_upload(login_as, ...): ...               # 403
```

- [ ] **Step 3: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_contracts.py tests/e2e/test_admin_contracte.py -v`
Expected: FAIL.

- [ ] **Step 4: Implementează**

Verificarea PDF: conținutul începe cu `%PDF-`. Fișierul se scrie întâi ca `contract.tmp`, apoi se înlocuiește cu `Path.replace`, deci un refuz sau o eroare nu atinge varianta veche. Calea e `uploads_dir/cereri/<cid>/contract.pdf`. `original_name` păstrează doar `Path(name).name`, fără caractere de control, tăiat la 120 de caractere. Textul din `contract.md` folosește „sunt”.

- [ ] **Step 5: Rulează testele și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_contracts.py tests/e2e/test_admin_contracte.py -v`
Expected: toate trec.

```bash
git add db/schema.sql cereri prompts/emailuri/contract.md web tests/unit/test_contracts.py tests/e2e/test_admin_contracte.py
git commit -m "feat(contracte): adminul incarca PDF-ul, iar clientul de pe email il primeste"
```

### Task 2: Contractele și istoricul în contul clientului

**Files:**
- Modify: `web/routes_client.py`, `web/templates/client/cereri.html`, `web/templates/client/cerere.html`, `web/templates/base.html`
- Create: `web/templates/client/contracte.html`
- Test: `tests/e2e/test_client_istoric_contracte.py`

**Interfaces:**
- Consumes: `cereri.contracts.get_contract`, `contracts_for_user`.
- Produces, rutele: `GET /client/contracte`, `GET /client/cereri/{id}/contract`.

- [ ] **Step 1: Scrie testele care pică**

```python
def test_history_separates_current_and_validated_requests(login_as, ...):
    assert page.index("În curs") < page.index("Istoric") and "Validată" not in other_section

def test_history_shows_date_pieces_and_label(login_as, ...): ...
def test_history_shows_only_my_requests(login_as, ...): ...
def test_empty_history_shows_a_message(login_as): ...

def test_contracts_page_lists_only_mine(login_as, ...): ...
def test_empty_contracts_page_shows_a_message(login_as): ...
def test_request_page_links_to_its_contract(login_as, ...): ...

def test_contract_is_served_inline_as_pdf(login_as, ...):
    assert r.headers["content-type"] == "application/pdf"
    assert r.headers["content-disposition"].startswith("inline")
    assert r.headers["x-content-type-options"] == "nosniff"

def test_no_contract_answers_404(login_as, ...): ...
def test_other_client_gets_404(login_as, ...): ...
def test_inspector_and_admin_do_not_use_client_routes(login_as, client, ...): ...   # 403
def test_client_has_no_upload_or_delete_for_contracts(login_as, ...): ...
```

- [ ] **Step 2: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/e2e/test_client_istoric_contracte.py -v`
Expected: FAIL.

- [ ] **Step 3: Implementează**

`GET /client/cereri` are două secțiuni, „În curs” și „Istoric”. În „Istoric” stau cererile `validata`, cu data validării. Navigarea din `base.html` arată clientului „Cererile mele” și „Contractele mele”.

- [ ] **Step 4: Rulează toate testele**

Run: `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`
Expected: toate trec.

- [ ] **Step 5: Actualizează documentele și fă commit**

- `Licenta\ciptronic-validator\CLAUDE.md`: stadiul, cele trei roluri, fișierele noi.
- `README.md`: fluxul complet și variabilele din `.env`.
- `AIS-OS\Licenta\memory\stare.md`: ce s-a terminat, rezultatele evalurilor și ce rămâne.

```bash
git add web README.md tests/e2e/test_client_istoric_contracte.py
git commit -m "feat(client): istoricul comenzilor si contractele in cont"
```

- [ ] **Step 6: Tudor parcurge contul complet**

Tudor intră pe rând ca client, admin și inspector, cu aplicația reală, și parcurge o cerere din cont până la validare, inclusiv contractul și istoricul. Ce nu se potrivește cu specul devine o listă de reparații.

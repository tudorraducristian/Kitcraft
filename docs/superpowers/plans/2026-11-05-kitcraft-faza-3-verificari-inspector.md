# Kitcraft, faza 3: verificările pe piesă și inspectorul, plan de implementare

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** adminul verifică fiecare piesă pe două poze, inspectorul aprobă sau trimite înapoi fiecare piesă, iar clientul primește confirmarea când toate sunt aprobate.

**Architecture:** logica stă în `cereri/verification.py`, fără FastAPI. O verificare e completă sau nu există deloc: întâi se calculează toate rapoartele, abia apoi se scrie în bază. Rapoartele folosesc tabelele și motoarele de azi, neschimbate. Tot ce se întâmplă la validare stă într-o singură funcție, `on_validated`, unde se va adăuga pe viitor mesajul către producție.

**Tech Stack:** FastAPI, Jinja2, SQLite, `agents/inspector.py`, `image_matcher/engine.py`, pytest.

**Spec:** `docs/superpowers/specs/2026-11-05-kitcraft-client-admin-inspector-design.md`, secțiunile 6.2, 7.3.8–7.3.10, 7.4, 8.1, 8.2, 9.5, 15.

**Depinde de:** fazele 1 și 2.

## Global Constraints

- Adminul încarcă două poze pe piesă, față și spate. O piesă are un raport de la agent și două de la Image Match.
- „Verificată” înseamnă că are toate cele trei rapoarte, nu că rapoartele sunt bune. Adminul decide dacă o trimite.
- Butonul „Trimite la inspector” se activează când toate piesele neaprobate au toate cele trei rapoarte. După o întoarcere, trimite doar piesele refăcute.
- Inspectorul vede cele două imagini ale setului aprobate de client, apoi, pe fiecare vedere a fiecărei piese, imaginea aprobată și poza încărcată de admin, plus cele trei rapoarte.
- Aprobarea e pe piesă, nu pe vedere. Piesele aprobate rămân aprobate. Trimiterea înapoi cere un text cu ce nu e bine.
- Inspectorul nu poate schimba nimic altceva.
- Clientul primește confirmarea doar când toate piesele sunt aprobate, o singură dată. Cât timp o piesă se reface, vede doar „în verificare”, fără motiv și fără rapoarte.
- În aplicație, agentul apare ca „verificare pe specificații”. În cod, numele `inspector` rămâne neatins.
- Încărcările: 5 MB și tip verificat. Motorul din `image_matcher/` nu se schimbă.
- Comanda de bază: `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`.

## Review Focus

- Inspectorul apasă de două ori sau are două taburi deschise: piesa se decide o singură dată, iar confirmarea pleacă o singură dată. Test în Task 1.
- Motivul de la trimiterea înapoi e gol sau doar spații: e refuzat. Test în Task 1.
- Agentul sau Image Match pică la jumătatea verificării: nu rămâne nimic pe jumătate, piesa își păstrează starea, iar adminul vede mesajul. Test în Task 1.
- Adminul reface imaginea unei piese deja verificate: verificarea veche nu mai e valabilă, deci piesa trebuie verificată din nou. Test în Task 1.
- Inspectorul deschide, știind id-ul, un raport care nu e al unei piese trimise la el sau o variantă veche: primește 404. Test în Task 3.

---

### Task 1: Logica verificării și a deciziilor

**Files:**
- Modify: `db/schema.sql`, `cereri/notifier.py`, `cereri/flow.py`, `cereri/repository.py`, `prompts/inspector.md`
- Create: `cereri/verification.py`
- Test: `tests/unit/test_cereri_verification.py`

**Interfaces:**
- Consumes: `db.repository.save_report`, `create_match_session`, `update_match_compare_report`, `agents.inspector.build_messages`, `parse_report`, `cereri.uploads.save_image_upload`.
- Produces, în `cereri/notifier.py`: `Notifier.validated(cerere) -> bool`. La `AccountNotifier`, scrie cu `add_message` textul „Validarea a fost realizată, iar modelul urmează să fie trimis spre producție.” și întoarce `True`.
- Produces, în `cereri/verification.py`:
  - `@dataclass class ImageEngine: analyze_sim: Callable; compare_real: Callable`
  - `class VerificationFailed(Exception)`
  - `verify_piece(conn, llm, engine, uploads_dir, piesa_id, foto_fata: bytes | None, foto_spate: bytes | None) -> str` întoarce id-ul verificării. O poză `None` refolosește poza din verificarea precedentă. La prima verificare, ambele sunt obligatorii, altfel `ValueError`.
  - `latest_verification(conn, piesa_id) -> Row | None`
  - `can_send_to_inspector(conn, cerere_id) -> bool`
  - `send_to_inspector(conn, cerere_id) -> int` întoarce câte piese au plecat
  - `decide_piece(conn, notifier, inspector_user_id, piesa_id, verdict: str, motiv: str = "") -> None`, cu `verdict` în `PIESA_APROBATA`, `TRIMISA_INAPOI`
  - `on_validated(conn, notifier, cerere_id) -> None`, singurul loc care trece cererea în `VALIDATA`
- Modifică `cereri.flow.redo_piece_image`: refuză cu `InvalidState` dacă piesa e `PIESA_APROBATA` sau `LA_INSPECTOR`, iar după refacere piesa revine la `DE_VERIFICAT`.

- [ ] **Step 1: Adaugă tabelele în `db/schema.sql`**

```sql
CREATE TABLE IF NOT EXISTS verificari (
    id              TEXT PRIMARY KEY,
    piesa_id        TEXT NOT NULL REFERENCES piese(id),
    foto_fata_path  TEXT NOT NULL,
    foto_spate_path TEXT NOT NULL,
    raport_id       TEXT NOT NULL REFERENCES validation_reports(id),
    match_fata_id   TEXT NOT NULL REFERENCES match_sessions(id),
    match_spate_id  TEXT NOT NULL REFERENCES match_sessions(id),
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS sim_rapoarte (
    image_id        TEXT PRIMARY KEY REFERENCES imagini(id),
    sim_report_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decizii_inspector (
    id           TEXT PRIMARY KEY,
    piesa_id     TEXT NOT NULL REFERENCES piese(id),
    verdict      TEXT NOT NULL CHECK (verdict IN ('aprobata', 'trimisa_inapoi')),
    motiv        TEXT,
    inspector_id TEXT NOT NULL REFERENCES users(id),
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
```

- [ ] **Step 2: Scrie testele care pică**

```python
def test_verify_saves_three_reports_and_marks_piece_verified(...):
    assert piesa["status"] == VERIFICATA and cerere["status"] == IN_VERIFICARE
    assert ver["raport_id"] and ver["match_fata_id"] != ver["match_spate_id"]

def test_agent_receives_both_photos(...):
    assert image_blocks_in(llm.vision_calls[-1]) == 2

def test_image_match_compares_each_photo_with_the_same_view(...):
    assert engine.compare_calls[0][1:] == (str(piece_front), str(photo_front))
    assert engine.compare_calls[1][1:] == (str(piece_back), str(photo_back))

def test_back_branding_is_accepted_by_the_report_parser(...): ...   # raport cu branding_spate.*
def test_sim_analysis_runs_once_per_image_and_is_reused(...):
    assert len(engine.analyze_calls) == 2

@pytest.mark.parametrize("failing", ["agent", "analyze_sim", "compare_real"])
def test_failure_leaves_nothing_half_done(failing, ...):
    with pytest.raises(VerificationFailed):
        verify_piece(...)
    assert latest_verification(conn, pid) is None and piesa["status"] == DE_VERIFICAT

def test_first_verification_needs_both_photos(...): ...
def test_reverify_can_replace_only_one_photo(...): ...
def test_non_image_photo_is_rejected(...): ...                      # UploadRejected, fără apel LLM
def test_verify_refused_before_client_approval(...): ...            # InvalidState
def test_verify_refused_for_approved_or_inspector_piece(...): ...

def test_cannot_send_until_all_pieces_have_reports(...):
    assert not can_send_to_inspector(conn, cid)
    with pytest.raises(InvalidState):
        send_to_inspector(conn, cid)

def test_send_moves_only_verified_pieces(...):
    assert send_to_inspector(conn, cid) == 2

def test_return_needs_a_reason(...):
    with pytest.raises(ValueError):
        decide_piece(conn, notifier, uid, pid, TRIMISA_INAPOI, "   ")

def test_returned_piece_keeps_others_approved(...):
    assert status_of(tricou) == PIESA_APROBATA and status_of(sapca) == TRIMISA_INAPOI
    assert get_piesa(conn, sapca)["return_reason"] == "sigla e imprimata"

def test_second_round_sends_only_the_redone_piece(...):
    assert send_to_inspector(conn, cid) == 1

def test_validated_only_after_last_piece_and_only_once(...):
    assert notifier.validated_calls == 0
    decide_piece(conn, notifier, uid, last, PIESA_APROBATA)
    assert notifier.validated_calls == 1 and cerere["status"] == VALIDATA and cerere["validated_at"]

def test_double_decision_is_refused_and_does_not_notify_twice(...):
    with pytest.raises(InvalidState):
        decide_piece(conn, notifier, uid, last, PIESA_APROBATA)
    assert notifier.validated_calls == 1

def test_status_stays_if_confirmation_cannot_be_delivered(...):     # notifier.validated -> False
    assert cerere["status"] == IN_VERIFICARE

def test_redo_after_verification_requires_a_new_one(...):
    assert get_piesa(conn, pid)["status"] == DE_VERIFICAT

def test_redo_refused_at_inspector_or_approved(...): ...
```

- [ ] **Step 3: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_cereri_verification.py -v`
Expected: FAIL, modulul nu există.

- [ ] **Step 4: Implementează `cereri/verification.py` și restul**

Ordinea din `verify_piece`:
1. verifică stările. Cererea e în `APROBATA` sau `IN_VERIFICARE`, iar piesa în `DE_VERIFICAT`, `VERIFICATA` sau `TRIMISA_INAPOI`, cu ambele imagini generate;
2. salvează pozele în `uploads_dir/cereri/<cid>/verificari/<uuid>/`;
3. cheamă agentul, cu `load_schema(tip, pentru_cerere=True)` la `parse_report`;
4. pentru fiecare vedere, ia `sim_report` din `sim_rapoarte` sau cheamă `analyze_sim`, apoi `compare_real(sim, imagine, poza, max_tokens=8192)`;
5. abia acum scrie: raportul, cele două `match_sessions`, rândul din `verificari`, statusurile, iar `return_reason` se golește.

Orice excepție din pașii 3–4 devine `VerificationFailed`, fără scrieri în bază. `decide_piece` folosește `UPDATE ... WHERE id = ? AND status = 'la_inspector'` și verifică `rowcount`. După ultima aprobare cheamă `on_validated`. Acolo, starea devine `VALIDATA` doar dacă `notifier.validated(cerere)` întoarce `True`.

În `prompts/inspector.md`, la regulile structurale, adaugă: „Regulile 7 și 8 se aplică la fel oricărui obiect de branding din specificație, inclusiv `branding_spate`.”

- [ ] **Step 5: Rulează testele, apoi toate testele, și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`
Expected: toate trec.

```bash
git add db/schema.sql cereri prompts/inspector.md tests/unit/test_cereri_verification.py
git commit -m "feat(verificare): verificari pe doua poze si decizii ale inspectorului pe piesa"
```

### Task 2: Verificările în pagina adminului

**Files:**
- Modify: `web/routes_admin.py`, `web/templates/admin/cerere.html`, `web/templates/admin/cereri.html`, `web/app.py`, `web/templates/report.html`, `web/templates/match_report.html`, `web/templates/index.html`, `web/templates/sessions_new.html`
- Test: `tests/e2e/test_admin_verificari.py`

**Interfaces:**
- Consumes: `cereri.verification` din Task 1.
- Produces, în `web/app.py`:
  - `image_engine() -> ImageEngine`, care citește la apel `analyze_sim` și `compare_real` din modul, ca `fake_image_engine` să meargă
  - `validation_report_context(row, image_url_prefix: str, read_only: bool) -> dict`, `match_report_context(row, image_url_prefix: str, read_only: bool) -> dict`. Rutele de azi, `view_report` și `view_match_report`, le folosesc cu `read_only=False`, deci paginile lor rămân la fel.
- Produces, rutele:
  - `POST /admin/cereri/{id}/piese/{piesa_id}/verifica`, cu `foto_fata`, `foto_spate`
  - `POST /admin/cereri/{id}/trimite-la-inspector`
  - `GET /admin/rapoarte/{report_id}`, `GET /admin/rapoarte/{report_id}/poza/{idx}`
  - `GET /admin/matches/{match_id}`, `GET /admin/matches/{match_id}/imagine/{kind}`

- [ ] **Step 1: Scrie testele care pică**

```python
def test_page_shows_upload_form_for_each_piece_after_approval(client, ...): ...
def test_upload_runs_verification_and_shows_reports(client, fake_llm, fake_image_engine, ...): ...
def test_agent_is_called_verificare_pe_specificatii_in_the_page(client, ...):
    assert "Verificare pe specificații" in page

def test_send_button_is_disabled_until_all_pieces_have_reports(client, ...): ...
def test_send_moves_pieces_to_the_inspector(client, ...): ...
def test_send_too_early_answers_409(client, ...): ...
def test_failed_verification_answers_502_with_a_message(client, ...): ...
def test_returned_piece_shows_the_reason_in_page_and_list(client, ...): ...
def test_read_only_report_pages_have_no_forms(client, ...):
    assert "<form" not in client.get(f"/admin/matches/{match_id}").text.split('class="topbar"')[1].split("</header>")[1]

def test_old_match_pages_keep_their_forms(client, ...):              # „Schimbă poza” rămâne la /matches/{id}/report
    assert "Schimbă poza" in client.get(f"/matches/{match_id}/report").text
```

- [ ] **Step 2: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/e2e/test_admin_verificari.py -v`
Expected: FAIL.

- [ ] **Step 3: Implementează**

Șabloanele `report.html` și `match_report.html` primesc `{% if not read_only %}` în jurul formularelor și al butoanelor „Începe...”. Titlul din `report.html` devine „Verificare pe specificații”. Textele „Discovery → Inspector” din `index.html` și „Discovery & Inspector” din `sessions_new.html` devin „Discovery → verificare pe specificații”, respectiv „Discovery și verificare”. Dacă un test vechi verifică unul dintre aceste texte, textul rămâne și se notează în raportul de task.

- [ ] **Step 4: Rulează toate testele și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`
Expected: toate trec.

```bash
git add web tests/e2e/test_admin_verificari.py
git commit -m "feat(admin): verificarile pe fiecare piesa si trimiterea la inspector"
```

### Task 3: Contul de inspector

**Files:**
- Modify: `web/routes_inspector.py`, `web/templates/inspector/index.html`
- Create: `web/templates/inspector/cerere.html`
- Test: `tests/e2e/test_inspector_routes.py`

**Interfaces:**
- Consumes: `cereri.verification.decide_piece`, `latest_verification`; `validation_report_context`, `match_report_context`, din Task 2.
- Produces, rutele:
  - `GET /inspector/`, cu „De verificat” și „Verificate”, și cu „1 din 2 piese aprobate”
  - `GET /inspector/cereri/{id}`
  - `POST /inspector/piese/{piesa_id}/decizie`, cu `verdict`, `motiv`
  - `GET /inspector/imagini/{image_id}`, `GET /inspector/poze/{verificare_id}/{vedere}`
  - `GET /inspector/rapoarte/{report_id}`, `GET /inspector/rapoarte/{report_id}/poza/{idx}`
  - `GET /inspector/matches/{match_id}`, `GET /inspector/matches/{match_id}/imagine/{kind}`

**Regula de acces:** o resursă se servește doar dacă aparține ultimei verificări a unei piese cu starea `la_inspector` sau `aprobata`, sau, la imagini, unei cereri care are o asemenea piesă. Altfel, 404. „De verificat” arată cererile cu cel puțin o piesă `la_inspector` sau `trimisa_inapoi`, care nu sunt încă validate. O piesă `trimisa_inapoi` apare cu „la admin”, fără butoane și fără rapoarte.

- [ ] **Step 1: Scrie testele care pică**

```python
def test_list_shows_only_requests_sent_to_inspector(login_as, ...): ...
def test_request_page_shows_all_images_and_three_reports(login_as, ...):
    assert page.count("/inspector/rapoarte/") == 2 and page.count("/inspector/matches/") == 4
    assert "imaginea setului" in page.lower()

def test_approve_piece_keeps_the_rest_pending(login_as, ...): ...
def test_return_without_reason_answers_422(login_as, ...): ...
def test_return_with_reason_goes_back_to_admin(login_as, ...): ...
def test_double_decision_answers_409(login_as, ...): ...
def test_approved_piece_has_no_buttons(login_as, ...): ...
def test_returned_piece_shows_no_reports_until_resent(login_as, ...): ...
def test_validated_request_moves_to_verificate(login_as, ...): ...

def test_report_pages_have_no_change_forms(login_as, ...):
    assert "Schimbă poza" not in insp.get(f"/inspector/matches/{mid}").text

def test_report_of_a_piece_not_sent_yet_is_404(login_as, ...): ...
def test_old_verification_is_404(login_as, ...): ...
def test_unknown_view_or_image_is_404(login_as, ...): ...
def test_inspector_cannot_reach_uploads_or_admin_pages(login_as, ...): ...      # 403
def test_admin_and_client_cannot_decide(login_as, client, ...): ...             # 403
```

- [ ] **Step 2: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/e2e/test_inspector_routes.py -v`
Expected: FAIL.

- [ ] **Step 3: Implementează rutele și șabloanele**

Așezarea urmează `ecran-inspector-v2.html`, cu două vederi pe piesă. `get_conn` și `notifier_for(conn, cerere)` vin din `web_app`. Imaginile cu ramă se servesc refolosind funcția `match_image` din `web/app.py`.

- [ ] **Step 4: Rulează testele și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/e2e/test_inspector_routes.py -v`
Expected: toate trec.

```bash
git add web tests/e2e/test_inspector_routes.py
git commit -m "feat(inspector): contul de inspector, cu aprobare pe fiecare piesa"
```

### Task 4: Confirmarea la client și lanțul complet

**Files:**
- Modify: `web/routes_client.py`, `web/templates/client/cerere.html`, `web/templates/client/cereri.html`
- Test: `tests/e2e/test_lant_cont.py`

**Interfaces:**
- Consumes: `cereri.repository.messages`.
- Produces: pagina cererii arată mesajele, iar lista cererilor are un semn la cererile cu mesaj necitit. Citirea se ține minte în `mesaje_citite(mesaj_id PRIMARY KEY)`, un tabel nou în `db/schema.sql`.

- [ ] **Step 1: Scrie testele care pică**

```python
def test_client_sees_only_in_verificare_while_a_piece_is_redone(login_as, ...):
    assert "în verificare" in page and "imprimată" not in page and "/rapoarte/" not in page

def test_message_appears_only_after_all_pieces_are_approved(login_as, ...): ...
def test_list_marks_new_message_then_clears_after_reading(login_as, ...): ...
def test_client_cannot_open_reports(login_as, ...):
    assert c.get(f"/reports/{rid}", follow_redirects=False).status_code == 403

def test_full_chain_from_account(login_as, client, fake_llm, fake_image_provider, fake_image_engine):
    """Client: cerere, aprobă. Admin: verifică, trimite. Inspector: aprobă tricoul,
    întoarce șapca. Admin: reface șapca, retrimite. Inspector: aprobă. Client: validat."""
    assert "validat" in client_page and "Validarea a fost realizată" in client_page
```

- [ ] **Step 2: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/e2e/test_lant_cont.py -v`
Expected: FAIL.

- [ ] **Step 3: Adaugă tabelul `mesaje_citite` și afișează mesajele**

Deschiderea paginii cererii marchează mesajele ei ca citite. Textul de stare vine din `CLIENT_LABELS`, deci motivul întoarcerii nu ajunge niciodată în contextul șablonului clientului.

- [ ] **Step 4: Rulează toate testele și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`
Expected: toate trec.

```bash
git add db/schema.sql web tests/e2e/test_lant_cont.py
git commit -m "feat(client): confirmarea apare in interfata cand toate piesele sunt aprobate"
```

# Kitcraft, faza 2: cererea din cont, plan de implementare

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** clientul cere în contul lui un set de piese, răspunde la întrebări, aprobă sau modifică cele două imagini ale setului și primește imaginile pe piese, iar adminul vede totul.

**Architecture:** logica stă în pachetul nou `cereri/`, fără FastAPI, ca să poată fi testată singură și folosită în faza 4 și de email. Diferența dintre cont și email e un singur obiect, `Notifier`. Fiecare piesă are o sesiune în `discovery_sessions`, în formatul de azi, deci agentul și rapoartele merg neschimbate. Conversația pentru toată cererea e un singur apel LLM, cu promptul ei.

**Tech Stack:** FastAPI, Jinja2, HTMX, SQLite, Claude prin `agents/llm_client.py`, Gemini prin `image_gen/`, Pillow, pytest.

**Spec:** `docs/superpowers/specs/2026-11-05-kitcraft-client-admin-inspector-design.md`, secțiunile 7.1, 7.3.1–7.3.7, 8.1, 9.1, 9.2, 9.4, 9.10, 9.12, 10.

**Depinde de:** faza 0, pentru `image_gen/provider.py`, și faza 1, pentru conturi și fixture-urile `login_as`, `client`.

## Global Constraints

- Limite: cel mult 6 piese pe cerere, 6 poze de referință, 5 runde de întrebări pe toată cererea, 8 întrebări pe rundă, 5 runde de modificări, 2 refaceri pe fiecare vedere a unei piese.
- Două vederi pentru toate piesele, `fata` și `spate`, inclusiv șosetele.
- O piesă nouă înseamnă doar `schemas/<nume>.json`. Promptul de generare nu are text scris pe piese.
- Aplicația nu completează din burtă. Generarea pornește doar când specificația fiecărei piese e completă.
- Modificarea nu poate schimba piesele. Pentru alte piese se face o cerere nouă.
- Clientul nu vede rapoartele. Un client vede doar cererile și imaginile lui.
- Încărcări: 5 MB, tip verificat. Plafon lunar: implicit 280 de imagini, setabil prin `KITCRAFT_IMAGE_CAP`.
- Rezoluție 1K. Prompt nou înseamnă fișier `.md`, nu text în cod.
- Fluxul A de azi nu vede câmpul nou pentru spate. Tabelele de azi rămân neschimbate.
- Comanda de bază: `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`.

## Review Focus

- LLM-ul spune `done: true` cu câmpuri goale, sau nu pune nicio întrebare deși lipsesc câmpuri: decide codul, iar clientul primește întrebări din câmpurile lipsă. Test în Task 5.
- Clientul apasă de două ori „Aprob”: imaginile pe piese se generează o singură dată. Test în Task 6.
- Plafonul se atinge la jumătatea imaginilor pe piese: cele gata rămân, iar reluarea face doar ce lipsește. Test în Task 6.
- Un fișier cu extensia `.png` care nu e imagine, un SVG sau un text cu `{{piese}}` în descriere: fișierul e refuzat, iar textul rămâne text. Teste în Task 2 și Task 4.
- Un client deschide cererea sau imaginea altui client, știind id-ul: primește 404. Test în Task 7.

---

### Task 1: Piesele noi și schema pentru cereri

**Files:**
- Create: `schemas/hanorac.json`, `schemas/geaca.json`, `schemas/sapca.json`, `schemas/sosete.json`, `schemas/pantaloni.json`
- Modify: `schemas/tricou.json`, `schemas/loader.py`
- Test: `tests/unit/test_schema_loader.py`

**Interfaces:**
- Produces, în `schemas/loader.py`:
  - `load_schema(product_type: str, pentru_cerere: bool = False) -> dict`. Implicit scoate câmpurile cu `"doar_cerere": true`, deci Fluxul A rămâne la fel.
  - `catalog() -> list[dict]`, cu `{"id", "name_ro"}` pentru fiecare schemă, sortat după `name_ro`
- Chei opționale noi în scheme: `doar_cerere`, `vizibil_in_poza` (implicit `true`), `din_identitate` (implicit `false`). Codul care nu le cunoaște le ignoră.

- [ ] **Step 1: Scrie testele care pică**

```python
def test_default_schema_keeps_the_nine_keys_of_flow_a():
    assert len(loader.leaf_keys(loader.load_schema("tricou"))) == 9

def test_request_schema_adds_the_back_branding():
    keys = loader.leaf_keys(loader.load_schema("tricou", pentru_cerere=True))
    assert "branding_spate.pozitie" in keys and "branding.pozitie" in keys

def test_catalog_has_the_six_pieces():
    assert {p["id"] for p in loader.catalog()} == {"tricou", "hanorac", "geaca", "sapca", "sosete", "pantaloni"}

@pytest.mark.parametrize("ptype", ["tricou", "hanorac", "geaca", "sapca", "sosete", "pantaloni"])
def test_every_piece_can_declare_no_branding_on_each_side(ptype):
    schema = loader.load_schema(ptype, pentru_cerere=True)
    state = {"branding": {"pozitie": "fără branding"}, "branding_spate": {"pozitie": "fără branding"}}
    keys = loader.applicable_leaf_keys(schema, state)
    assert "branding.tehnica" not in keys and "branding_spate.tehnica" not in keys

def test_new_schema_file_joins_the_catalog_without_code(tmp_path, monkeypatch):
    (tmp_path / "vesta.json").write_text('{"id":"vesta","name_ro":"Vestă","fields":[]}', encoding="utf-8")
    monkeypatch.setattr(loader, "SCHEMAS_DIR", tmp_path)
    assert loader.catalog() == [{"id": "vesta", "name_ro": "Vestă"}]
```

- [ ] **Step 2: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_schema_loader.py -v`
Expected: FAIL, `load_schema` nu primește `pentru_cerere`.

- [ ] **Step 3: Scrie schemele și schimbă `loader.py`**

Câmpurile, cu indicii în stilul din `tricou.json`. Toate au și `branding`, față, și `branding_spate`, spate, cu aceleași subcâmpuri ca azi, `allow_none_value: "fără branding"` și `doar_cerere: true` pe `branding_spate`:

| Fișier | `name_ro` | Câmpuri proprii |
|---|---|---|
| `hanorac.json` | Hanorac | `culoare_principala`, `material`, `croiala`, `gluga`, `inchidere` |
| `geaca.json` | Geacă | `culoare_principala`, `material`, `croiala`, `gluga`, `inchidere` |
| `sapca.json` | Șapcă | `culoare_principala`, `material`, `model`, `cozoroc` |
| `sosete.json` | Șosete | `culoare_principala`, `material`, `lungime` |
| `pantaloni.json` | Pantaloni | `culoare_principala`, `material`, `croiala`, `lungime` |

Marcaje: `material` și `branding.tehnica` au `vizibil_in_poza: false`. `culoare_principala` are `din_identitate: true`. La `tricou.json` se adaugă doar `branding_spate` și aceste marcaje.

- [ ] **Step 4: Rulează toate testele și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`
Expected: toate trec.

```bash
git add schemas tests/unit/test_schema_loader.py
git commit -m "feat(schemas): cinci piese noi si branding pe spate doar pentru cereri"
```

### Task 2: Cererile în baza de date și încărcările

**Files:**
- Modify: `db/schema.sql`
- Create: `cereri/__init__.py`, `cereri/states.py`, `cereri/repository.py`, `cereri/uploads.py`
- Test: `tests/unit/test_cereri_repository.py`, `tests/unit/test_cereri_uploads.py`

**Interfaces:**
- Produces, în `cereri/states.py`:
  - Stările cererii: `NOUA="noua"`, `IN_DESCRIERE="in_descriere"`, `MODEL_DE_APROBAT="model_de_aprobat"`, `APROBATA="aprobata"`, `IN_VERIFICARE="in_verificare"`, `VALIDATA="validata"`
  - Stările piesei: `DE_VERIFICAT="de_verificat"`, `VERIFICATA="verificata"`, `LA_INSPECTOR="la_inspector"`, `PIESA_APROBATA="aprobata"`, `TRIMISA_INAPOI="trimisa_inapoi"`
  - Vederile: `FATA="fata"`, `SPATE="spate"`, `VEDERI=(FATA, SPATE)`
  - Limitele: `MAX_PIESE=6`, `MAX_REFERINTE=6`, `MAX_RUNDE=5`, `MAX_MODIFICARI=5`, `MAX_REFACERI=2`
  - `CLIENT_LABELS: dict[str,str]`: în descriere, model de aprobat, aprobat, piese gata, în verificare, validat
  - `class InvalidState(Exception)`
- Produces, în `cereri/repository.py`:
  - `piece_labels(product_types: list[str]) -> list[str]`. Un tip unic are numele din `name_ro`, iar un tip repetat „Tricou 1”, „Tricou 2”.
  - `create_cerere(conn, *, source, client_email, description, product_types, client_user_id=None, prefilled=None, status=IN_DESCRIERE) -> str`. Creează piesele și câte o sesiune cu `db.repository.create_session`. Starea inițială e `loader.empty_state`, peste care se pune `prefilled[i]`.
  - `get_cerere(conn, id)`, `list_cereri(conn)`, `list_cereri_for_user(conn, user_id)`, `set_status(conn, id, status)`
  - `update_progress(conn, id, **fields)`, pentru `question_rounds`, `modification_rounds`, `identity_json`, `history_json`, `pending_questions_json`, `pending_instruction`, `blocaj`. Numele coloanelor sunt verificate pe o listă fixă.
  - `get_piese(conn, cerere_id) -> list[Row]`, cu `state_json` din sesiune, în ordinea `position`
  - `get_piesa(conn, piesa_id)`, `set_piesa_status(conn, piesa_id, status)`
  - `save_piece_state(conn, piesa_id, state: dict, complete: bool) -> None`, prin `db.repository.update_session_state` și `finalize_session`
  - `add_upload(conn, cerere_id, kind, path) -> str`, cu `kind` în `sigla`, `referinta`. `uploads(conn, cerere_id, kind=None) -> list[Row]`. O a doua siglă o înlocuiește pe prima.
  - `add_image(conn, cerere_id, kind, vedere, path, round_no, piesa_id=None) -> str`, `get_image(conn, image_id)`, `latest_set_images(conn, cerere_id) -> dict[str, Row]`, `piece_images(conn, piesa_id) -> dict[str, Row]`, `count_redos(conn, piesa_id, vedere) -> int`
  - `add_message(conn, cerere_id, text) -> None`, `messages(conn, cerere_id) -> list[Row]`
- Produces, în `cereri/uploads.py`:
  - `class UploadRejected(Exception)`
  - `save_image_upload(content: bytes, dest_dir: Path, stem: str) -> Path`. Numele vine din `stem` și din formatul real, niciodată de la client.

- [ ] **Step 1: Adaugă tabelele în `db/schema.sql`**

```sql
CREATE TABLE IF NOT EXISTS cereri (
    id                     TEXT PRIMARY KEY,
    source                 TEXT NOT NULL CHECK (source IN ('cont', 'email')),
    client_user_id         TEXT REFERENCES users(id),
    client_email           TEXT NOT NULL,
    description            TEXT NOT NULL,
    identity_json          TEXT NOT NULL DEFAULT '{}',
    status                 TEXT NOT NULL CHECK (status IN
        ('noua','in_descriere','model_de_aprobat','aprobata','in_verificare','validata')),
    question_rounds        INTEGER NOT NULL DEFAULT 0,
    modification_rounds    INTEGER NOT NULL DEFAULT 0,
    history_json           TEXT NOT NULL DEFAULT '[]',
    pending_questions_json TEXT NOT NULL DEFAULT '[]',
    pending_instruction    TEXT,
    blocaj                 TEXT CHECK (blocaj IN ('plafon', 'eroare')),
    created_at             TEXT NOT NULL DEFAULT (datetime('now')),
    validated_at           TEXT
);
CREATE TABLE IF NOT EXISTS piese (
    id                   TEXT PRIMARY KEY,
    cerere_id            TEXT NOT NULL REFERENCES cereri(id),
    product_type         TEXT NOT NULL,
    label                TEXT NOT NULL,
    position             INTEGER NOT NULL,
    discovery_session_id TEXT NOT NULL REFERENCES discovery_sessions(id),
    status               TEXT NOT NULL DEFAULT 'de_verificat' CHECK (status IN
        ('de_verificat','verificata','la_inspector','aprobata','trimisa_inapoi')),
    return_reason        TEXT
);
CREATE TABLE IF NOT EXISTS incarcari (
    id TEXT PRIMARY KEY, cerere_id TEXT NOT NULL REFERENCES cereri(id),
    kind TEXT NOT NULL CHECK (kind IN ('sigla', 'referinta')), path TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS imagini (
    id TEXT PRIMARY KEY, cerere_id TEXT NOT NULL REFERENCES cereri(id),
    piesa_id TEXT REFERENCES piese(id), kind TEXT NOT NULL CHECK (kind IN ('set', 'piesa')),
    vedere TEXT NOT NULL CHECK (vedere IN ('fata', 'spate')), round_no INTEGER NOT NULL,
    path TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS mesaje_client (
    id TEXT PRIMARY KEY, cerere_id TEXT NOT NULL REFERENCES cereri(id),
    text TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS consum_imagini (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

- [ ] **Step 2: Scrie testele care pică**

```python
def test_labels_number_only_the_repeated_types():
    assert piece_labels(["tricou", "sapca", "tricou"]) == ["Tricou 1", "Șapcă", "Tricou 2"]

def test_create_cerere_makes_one_session_per_piece(conn):
    cid = create_cerere(conn, source="cont", client_email="a@b.ro", description="d",
                        product_types=["tricou", "sapca"], prefilled=[{"material": "bumbac"}, {}])
    piese = get_piese(conn, cid)
    assert [p["product_type"] for p in piese] == ["tricou", "sapca"]
    assert json.loads(piese[0]["state_json"])["material"] == "bumbac"
    assert "branding_spate" in json.loads(piese[0]["state_json"])

def test_list_cereri_for_user_returns_only_theirs(conn): ...
def test_update_progress_refuses_unknown_column(conn): ...   # ValueError
def test_second_logo_replaces_the_first(conn): ...
def test_latest_set_images_returns_the_newest_round(conn): ...
def test_count_redos_counts_rounds_after_the_first(conn): ...
```

```python
def test_saves_real_png_with_our_name(tmp_path):
    assert save_image_upload(_png(), tmp_path, "sigla").name == "sigla.png"

def test_extension_comes_from_real_format(tmp_path):
    assert save_image_upload(_jpeg(), tmp_path, "poza").suffix == ".jpg"

@pytest.mark.parametrize("content", [b"nu sunt imagine", b"<svg xmlns='http://www.w3.org/2000/svg'/>", b""])
def test_rejects_what_is_not_an_image(tmp_path, content):
    with pytest.raises(UploadRejected):
        save_image_upload(content, tmp_path, "x")

def test_rejects_over_five_mb(tmp_path):
    with pytest.raises(UploadRejected, match="5 MB"):
        save_image_upload(b"0" * (5 * 1024 * 1024 + 1), tmp_path, "x")
```

- [ ] **Step 3: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_cereri_repository.py tests/unit/test_cereri_uploads.py -v`
Expected: FAIL, `ModuleNotFoundError: cereri`.

- [ ] **Step 4: Implementează `cereri/states.py`, `cereri/repository.py`, `cereri/uploads.py`**

Schemele se încarcă mereu cu `pentru_cerere=True`. `save_image_upload` verifică mărimea, apoi `Image.open(...).verify()`, iar formatele permise sunt PNG, JPEG și WEBP. Orice excepție Pillow devine `UploadRejected`.

- [ ] **Step 5: Rulează testele, apoi toate testele, și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`
Expected: toate trec.

```bash
git add db/schema.sql cereri tests/unit/test_cereri_repository.py tests/unit/test_cereri_uploads.py
git commit -m "feat(cereri): tabelele cererii, ale pieselor si incarcarile verificate"
```

### Task 3: Conversația pentru toată cererea

**Files:**
- Create: `agents/cerere_discovery.py`, `prompts/cerere_discovery.md`
- Test: `tests/unit/test_cerere_discovery.py`

**Interfaces:**
- Consumes: `agents.discovery.is_schema_complete`, `merge_answers`, `_extract_json`.
- Produces, în `agents/cerere_discovery.py`:
  - `SIGLA_ID = "sigla"`, `MAX_INTREBARI = 8`
  - `@dataclass(frozen=True) class PiesaInput: id: str; product_type: str; label: str; schema: dict; state: dict`
  - `@dataclass(frozen=True) class Intrebare: id: str; piesa_id: str | None; camp: str | None; text: str; variante: tuple[str, ...] = ()`. `id` e `"<piesa_id>::<camp>"`, sau `SIGLA_ID` pentru întrebarea despre siglă.
  - `@dataclass class PasCerere: states: dict[str, dict]; intrebari: list[Intrebare]; identitate: dict`
  - `build_messages(piese, description, identitate, reference_paths, history, are_sigla) -> tuple[str, list[dict]]`
  - `parse_step(raw: str, piese) -> PasCerere`. `ValueError` dacă nu e JSON valid.
  - `request_step(llm, piese, description, identitate, reference_paths, history, are_sigla) -> PasCerere`. Cu o reîncercare, ca `discovery.request_step`. Cu poze cheamă `complete_vision`, fără poze `complete_text`.
  - `missing_by_piece(piese) -> dict[str, list[str]]`, `all_complete(piese) -> bool`
  - `questions_from_missing(piese) -> list[Intrebare]`, cu textul din `label` și sugestiile din `hint`
  - `merge_client_answers(piese, answers: dict[str, str]) -> dict[str, dict]`. Cheile sunt `id`-uri de întrebare, cele necunoscute se ignoră, valorile goale se ignoră, iar câmpurile cu `type: list` se despart după virgulă.
- Răspunsul pe care îl cere promptul:

```json
{ "identitate": {"brand": "", "culori": [], "stil": ""},
  "piese": {"<piesa_id>": {"state": {}}},
  "intrebari": [{"piesa_id": "<id>", "camp": "material", "text": "", "variante": []}] }
```

- [ ] **Step 1: Scrie testele care pică**

```python
def test_parse_merges_state_for_each_piece(): ...          # states[id]["material"] == "bumbac"
def test_parse_drops_keys_outside_the_schema():
    step = parse_step(_raw(state={"material": "bumbac", "inventat": "x"}), [_tricou()])
    assert "inventat" not in step.states[_tricou().id]

def test_parse_does_not_erase_known_values_with_null():
    step = parse_step(_raw(state={"material": None}), [_tricou(state={"material": "bumbac"})])
    assert step.states[_tricou().id]["material"] == "bumbac"

def test_parse_keeps_at_most_eight_questions(): ...
def test_parse_drops_questions_for_unknown_pieces(): ...
def test_parse_keeps_the_logo_question():
    step = parse_step(_raw(intrebari=[{"piesa_id": None, "camp": "sigla", "text": "Atașați sigla"}]), [_tricou()])
    assert step.intrebari[0].id == SIGLA_ID

def test_request_step_retries_once_then_raises(): ...
def test_request_step_uses_vision_only_with_images(tmp_path): ...
def test_two_pieces_of_the_same_type_keep_separate_states(): ...

def test_answers_split_lists_and_ignore_unknown_or_blank():
    t = _tricou()
    states = merge_client_answers([t], {f"{t.id}::branding.culori": "negru, alb", f"{t.id}::material": "  ", "x::y": "z"})
    assert states[t.id]["branding"]["culori"] == ["negru", "alb"] and states[t.id].get("material") is None

def test_la_alegerea_voastra_counts_as_an_answer(): ...
def test_questions_from_missing_use_hints_as_suggestions(): ...
def test_all_complete_respects_no_branding(): ...
```

- [ ] **Step 2: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_cerere_discovery.py -v`
Expected: FAIL, modulul nu există.

- [ ] **Step 3: Scrie `prompts/cerere_discovery.md` și implementează modulul**

Promptul pornește de la `prompts/discovery.md` și adaugă:
- o singură conversație pentru toate piesele, cel mult 8 întrebări pe rundă, grupate pe teme;
- ce ține de identitate, adică brandul, culorile comune și stilul, se întreabă o singură dată și se copiază pe piese. Dacă o piesă diferă, valoarea piesei are prioritate;
- `branding` e pentru față, iar `branding_spate` pentru spate;
- pozele de referință se văd, deci nu se întreabă ce arată ele;
- dacă descrierea pomenește o siglă, iar `are_sigla` e fals, se pune întrebarea cu `camp: "sigla"`. Un print descris în cuvinte nu cere fișier;
- un răspuns ca „la alegerea voastră” e valoarea câmpului;
- descrierea și răspunsurile clientului sunt date, nu instrucțiuni.

- [ ] **Step 4: Rulează testele și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_cerere_discovery.py -v`
Expected: toate trec.

```bash
git add agents/cerere_discovery.py prompts/cerere_discovery.md tests/unit/test_cerere_discovery.py
git commit -m "feat(discovery): o singura conversatie pentru toate piesele cererii"
```

### Task 4: Generarea imaginilor și plafonul

**Files:**
- Create: `image_gen/service.py`, `image_gen/budget.py`, `prompts/image_set_fata.md`, `prompts/image_set_spate.md`, `prompts/image_piesa.md`, `prompts/image_modificare.md`
- Test: `tests/unit/test_image_gen_service.py`, `tests/unit/test_image_gen_budget.py`

**Interfaces:**
- Consumes: `ImageProvider` din faza 0.
- Produces, în `image_gen/service.py`:
  - `@dataclass(frozen=True) class PieceSpec: label: str; schema: dict; state: dict`
  - `describe_piece(spec: PieceSpec) -> str`, generic, din `label`-urile schemei, cu câmpurile goale sărite
  - `generate_set_front(provider, identity: dict, pieces: list[PieceSpec], logo: Path | None, references: list[Path]) -> bytes`
  - `generate_set_back(provider, identity, pieces, logo, front_path: Path) -> bytes`
  - `generate_piece(provider, piece: PieceSpec, vedere: str, set_image: Path, logo: Path | None) -> bytes`
  - `apply_modification(provider, previous: Path, instruction: str, vedere: str) -> bytes`
- Produces, în `image_gen/budget.py`:
  - `DEFAULT_CAP = 280`, `class BudgetExceeded(Exception)`
  - `monthly_cap() -> int`, din `KITCRAFT_IMAGE_CAP`, cu valoarea implicită la o valoare invalidă
  - `used_this_month(conn) -> int`, `ensure_available(conn, needed: int) -> None`, `record(conn, count: int = 1) -> None`

- [ ] **Step 1: Scrie testele care pică**

```python
def test_set_front_sends_logo_first_then_references(): ...      # provider.last_refs == [logo, ref1, ref2]
def test_set_back_uses_the_front_image_as_reference(): ...
def test_piece_uses_the_set_image_of_the_same_view(): ...
def test_modification_uses_the_previous_image_and_the_instruction(): ...

def test_prompt_is_built_from_schema_fields_without_piece_names_in_code():
    schema = {"id": "vesta", "name_ro": "Vestă", "fields": [{"key": "buzunare", "label": "Buzunare"}]}
    assert "Buzunare: două" in describe_piece(PieceSpec("Vestă", schema, {"buzunare": "două"}))

def test_placeholder_text_from_the_client_is_not_expanded():
    prompt = _prompt_for(instruction="scrie {{piese}} pe tricou")
    assert "{{piese}}" in prompt

def test_prompt_files_exist_and_ask_for_uniform_background_on_pieces(): ...
```

```python
def test_records_and_counts_only_this_month(conn):
    record(conn, 3)
    conn.execute("INSERT INTO consum_imagini (created_at) VALUES (datetime('now', '-40 days'))")
    assert used_this_month(conn) == 3

def test_ensure_available_blocks_over_the_cap(conn, monkeypatch):
    monkeypatch.setenv("KITCRAFT_IMAGE_CAP", "2")
    record(conn, 1)
    ensure_available(conn, 1)
    with pytest.raises(BudgetExceeded):
        ensure_available(conn, 2)

def test_invalid_cap_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("KITCRAFT_IMAGE_CAP", "multe")
    assert monthly_cap() == 280
```

- [ ] **Step 2: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_image_gen_service.py tests/unit/test_image_gen_budget.py -v`
Expected: FAIL, modulele nu există.

- [ ] **Step 3: Scrie prompturile și implementează**

Înlocuirea din prompt se face într-o singură trecere, cu `re.sub` pe `{{identitate}}`, `{{piese}}`, `{{vedere}}`, `{{instructiune}}`, ca un text al clientului să nu fie extins la rândul lui. Prompturile cer:
- `image_set_fata.md`: toate piesele, văzute din față, separate clar, fără elemente necerute, cu sigla neschimbată;
- `image_set_spate.md`: aceleași piese din spate, cu același stil, culori și așezare ca în imaginea de referință;
- `image_piesa.md`: doar piesa numită, din imaginea de referință, cu aceleași culori și sigla în același loc, pe fundal alb uniform;
- `image_modificare.md`: schimbă doar ce cere instrucțiunea, restul imaginii rămâne.

- [ ] **Step 4: Rulează testele și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_image_gen_service.py tests/unit/test_image_gen_budget.py -v`
Expected: toate trec.

```bash
git add image_gen prompts/image_*.md tests/unit/test_image_gen_service.py tests/unit/test_image_gen_budget.py
git commit -m "feat(image-gen): setul, piesele, modificarea si plafonul lunar"
```

### Task 5: Fluxul, de la descriere la model

**Files:**
- Create: `cereri/notifier.py`, `cereri/flow.py`
- Test: `tests/unit/test_cereri_flow_discovery.py`
- Modify: `tests/conftest.py`, pentru `FakeImageProvider`

**Interfaces:**
- Consumes: `cereri.repository`, `agents.cerere_discovery`, `image_gen.service`, `image_gen.budget`.
- Produces, în `cereri/notifier.py`:
  - `class Notifier(Protocol)`, cu metode care întorc `True` dacă mesajul a ajuns la client. Starea cererii avansează doar atunci:
    - `questions_ready(cerere, intrebari: list[Intrebare], ultima_runda: bool) -> bool`
    - `model_ready(cerere, images: list[Path]) -> bool`
    - `modification_limit(cerere) -> bool`
    - `other_pieces(cerere) -> bool`
  - `class AccountNotifier(Notifier)`, cu `__init__(self, conn)`. Primele două doar întorc `True`, pentru că pagina arată starea. Ultimele două scriu cu `add_message`.
- Produces, în `cereri/flow.py`:
  - `@dataclass class Services: llm: Any; provider: ImageProvider; notifier: Notifier; uploads_dir: Path`
  - `start_discovery(conn, services, cerere_id) -> None`
  - `submit_answers(conn, services, cerere_id, answers: dict[str, str]) -> None`
  - `generate_model(conn, services, cerere_id) -> None`
  - `piese_input(conn, cerere_id) -> list[PiesaInput]`
- Produces, în `tests/conftest.py`: fixture-ul `fake_image_provider`, cu `calls` și `generate(prompt, reference_paths)`, care întoarce un PNG mic. Înlocuiește `web_app.get_image_provider`.

**Regulile rundelor:**
1. Dacă toate piesele sunt complete, se trece la `generate_model`, indiferent ce spune LLM-ul.
2. Dacă `question_rounds >= MAX_RUNDE`, nu se mai cheamă LLM-ul. Întrebările vin din `questions_from_missing`, cu `ultima_runda=True`, iar răspunsurile se adună fără limită de runde.
3. Altfel se cheamă `request_step`, `question_rounds` crește cu 1, iar dacă nu vin întrebări deși lipsesc câmpuri, se folosește `questions_from_missing`.

- [ ] **Step 1: Scrie testele care pică**

```python
def test_complete_description_generates_both_images_directly(...):
    assert cerere["status"] == MODEL_DE_APROBAT and fake.count == 2
    assert fake.calls[1].references[-1].name.startswith("set_fata")

def test_questions_are_saved_and_status_stays_in_descriere(...): ...
def test_llm_saying_done_with_empty_fields_does_not_generate(...): ...
def test_no_questions_but_missing_fields_asks_from_schema(...): ...
def test_answers_are_merged_and_next_round_runs(...): ...
def test_after_five_rounds_llm_is_not_called_and_form_asks_the_rest(...):
    assert llm.text_calls == before and notifier.last_ultima_runda is True
def test_generation_waits_until_every_piece_is_complete(...): ...

def test_budget_exceeded_blocks_without_calling_provider(...):
    assert cerere["blocaj"] == "plafon" and fake.count == 0 and cerere["status"] == IN_DESCRIERE

def test_provider_error_blocks_and_keeps_state(...):
    assert cerere["blocaj"] == "eroare" and cerere["status"] == IN_DESCRIERE

def test_status_does_not_advance_if_notifier_fails(...):      # notifier.model_ready -> False
    assert cerere["status"] == IN_DESCRIERE and images_exist

def test_each_image_is_counted_in_the_budget(...): ...
def test_answers_refused_when_not_in_descriere(...):          # InvalidState
```

- [ ] **Step 2: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_cereri_flow_discovery.py -v`
Expected: FAIL, modulul nu există.

- [ ] **Step 3: Implementează `cereri/notifier.py` și `cereri/flow.py`**

Imaginile se scriu în `uploads_dir/cereri/<cerere_id>/`, cu numele `set_fata_r<runda>.png`. La `generate_model`, se cheamă `ensure_available(conn, 2)`, apoi față, apoi spate cu fața ca referință. Dacă există `pending_instruction`, din Task 6, cele două imagini se fac cu `apply_modification`. `blocaj` se șterge la reușită. Sigla și pozele vin din `uploads`.

- [ ] **Step 4: Rulează testele și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_cereri_flow_discovery.py -v`
Expected: toate trec.

```bash
git add cereri tests/conftest.py tests/unit/test_cereri_flow_discovery.py
git commit -m "feat(cereri): de la descriere la cele doua imagini ale setului"
```

### Task 6: Modificările, aprobarea și piesele

**Files:**
- Create: `agents/modificare.py`, `prompts/modificare.md`
- Modify: `cereri/flow.py`
- Test: `tests/unit/test_modificare.py`, `tests/unit/test_cereri_flow_model.py`

**Interfaces:**
- Produces, în `agents/modificare.py`:
  - `@dataclass class Modificare: kind: Literal["modificare", "alte_piese"]; changes: dict[str, dict]`, cu `changes` pe `piesa_id`, cheie cu punct și valoare
  - `read_modification(llm, piese: list[PiesaInput], instruction: str) -> Modificare`. Cheile din afara schemei se ignoră. O modificare fără câmp, ca „dungile mai late”, are `changes` gol și `kind="modificare"`.
- Produces, în `cereri/flow.py`:
  - `request_modification(conn, services, cerere_id, instruction: str) -> None`
  - `approve_model(conn, services, cerere_id) -> None`
  - `generate_piece_images(conn, services, cerere_id) -> None`, face doar ce lipsește
  - `redo_piece_image(conn, services, piesa_id, vedere: str) -> None`
  - `resume(conn, services, cerere_id) -> None`, pentru `blocaj`: în `in_descriere` cheamă `generate_model`, în `aprobata` cheamă `generate_piece_images`

- [ ] **Step 1: Scrie testele care pică**

```python
def test_modification_changes_only_the_touched_fields(...): ...
def test_read_modification_detects_other_pieces(...): ...
def test_read_modification_ignores_unknown_keys(...): ...

def test_modification_updates_spec_first_then_redoes_both_images(...):
    assert state["culoare_principala"] == "negru" and fake.count == 4
    assert fake.calls[2].references == [prev_front] and cerere["modification_rounds"] == 1

def test_modification_without_a_field_only_changes_the_images(...): ...
def test_sixth_modification_is_refused_and_notifies(...):
    assert cerere["modification_rounds"] == 5 and fake.count == before and notifier.limit_called

def test_other_pieces_do_not_change_the_set(...):
    assert len(get_piese(conn, cid)) == 2 and notifier.other_pieces_called and fake.count == before

def test_modification_leaving_empty_fields_returns_to_questions(...):
    # „pune sigla pe piept” la o piesă fără branding
    assert cerere["status"] == IN_DESCRIERE and cerere["pending_instruction"]

def test_after_answers_images_are_redone_from_previous_not_from_scratch(...): ...

def test_approve_makes_two_images_for_each_piece_from_the_matching_view(...):
    assert fake.count == before + 4
    assert piece_call_for("tricou", "spate").references[0] == set_back

def test_second_approve_does_not_generate_again(...):
    with pytest.raises(InvalidState):
        approve_model(conn, services, cid)
    assert fake.count == count_after_first

def test_budget_stops_midway_and_resume_makes_only_what_is_missing(...):
    assert len(done_images) == 1 and cerere["blocaj"] == "plafon"
    resume(conn, services, cid)
    assert fake.count == 4 and cerere["blocaj"] is None

def test_redo_piece_image_allows_two_per_view(...):
    with pytest.raises(InvalidState):
        redo_piece_image(conn, services, pid, "fata")   # a treia oară

def test_modification_refused_after_approval(...): ...
```

- [ ] **Step 2: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_modificare.py tests/unit/test_cereri_flow_model.py -v`
Expected: FAIL.

- [ ] **Step 3: Scrie `prompts/modificare.md` și implementează**

`approve_model` trece întâi starea pe `APROBATA`, cu un `UPDATE ... WHERE status = 'model_de_aprobat'`, și verifică `rowcount`, deci un dublu click nu generează de două ori. Abia apoi cheamă `generate_piece_images`. Acolo, `ensure_available(conn, 1)` se cheamă înainte de fiecare imagine, iar fiecare imagine se salvează imediat.

- [ ] **Step 4: Rulează testele și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_modificare.py tests/unit/test_cereri_flow_model.py -v`
Expected: toate trec.

```bash
git add agents/modificare.py prompts/modificare.md cereri/flow.py tests/unit/test_modificare.py tests/unit/test_cereri_flow_model.py
git commit -m "feat(cereri): modificari, aprobarea setului si imaginile pe piese"
```

### Task 7: Paginile clientului

**Files:**
- Modify: `web/routes_client.py`, `web/templates/client/cereri.html`, `web/app.py`, pentru `get_image_provider()`, `notifier_for(conn, cerere)` și `services_for(conn, cerere)`
- Create: `web/templates/client/cerere_noua.html`, `cerere.html`, `_intrebari.html`, `_model.html`, `_piese.html`
- Test: `tests/e2e/test_client_routes.py`

**Interfaces:**
- Consumes: `cereri.flow`, `cereri.repository`, `cereri.uploads`, `schemas.loader.catalog`.
- Produces, în `web/app.py`:
  - `get_image_provider() -> ImageProvider`, un singleton leneș, înlocuit în teste
  - `notifier_for(conn, cerere) -> Notifier`. În această fază dă mereu `AccountNotifier`. Faza 4 alege după `cerere["source"]`.
  - `services_for(conn, cerere) -> Services`, cu `notifier_for`, `get_llm_client()`, `get_image_provider()` și `UPLOADS_DIR`. Rutele care au nevoie doar de notificare cheamă `notifier_for`, ca o cheie Gemini lipsă să nu le afecteze.
- Produces, rutele:
  - `GET /client/cereri`, `GET /client/cereri/noua`, `POST /client/cereri`
  - `GET /client/cereri/{id}`
  - `POST /client/cereri/{id}/raspunsuri`, `POST /client/cereri/{id}/aproba`, `POST /client/cereri/{id}/modifica`
  - `GET /client/cereri/{id}/imagini/{image_id}`

Câmpurile formularului de cerere: `piesa_<product_type>`, câte modele diferite din fiecare, de la 0 la 6, `description`, `sigla`, opțional, și `poze`, multiplu. Pagina de întrebări are câmpuri `raspuns:<id întrebare>`, iar la `SIGLA_ID` un câmp de încărcare. Pagina permite oricând adăugarea de poze, până la 6.

Rutele de generare sunt `POST` sincrone, ca `POST /matches`. Blocarea butonului și „Se procesează…” vin deja din scriptul din `base.html`.

- [ ] **Step 1: Scrie testele care pică**

```python
def test_form_lists_the_catalog_from_schemas(login_as): ...
def test_create_runs_discovery_and_shows_questions(login_as, fake_llm, fake_image_provider): ...

def test_two_tshirts_stay_in_one_request(login_as, fake_llm, fake_image_provider):
    r = c.post("/client/cereri", data={"piesa_tricou": "2", "description": "d"})
    assert "Tricou 1" in page and "Tricou 2" in page

@pytest.mark.parametrize("data", [{"description": "d"}, {"piesa_tricou": "7", "description": "d"}, {"piesa_tricou": "1", "description": " "}, {"piesa_inventata": "1", "description": "d"}])
def test_create_rejects_bad_selection(login_as, data): ...         # 422, fără apel LLM

def test_seven_reference_photos_are_refused(login_as, ...): ...
def test_non_image_upload_shows_a_message_and_creates_nothing(login_as, ...): ...
def test_answers_lead_to_model_with_both_images(login_as, ...): ...
def test_short_form_after_last_round(login_as, ...): ...
def test_logo_can_be_uploaded_at_the_questions_step(login_as, ...): ...
def test_modify_shows_new_images(login_as, ...): ...
def test_other_pieces_shows_the_new_request_message(login_as, ...): ...
def test_after_limit_only_approve_remains(login_as, ...): ...
def test_approve_shows_piece_images(login_as, ...): ...
def test_list_shows_client_labels(login_as, ...): ...

def test_cap_shows_a_clear_message(login_as, monkeypatch, ...):
    assert "plafon" in page.lower()

def test_other_client_gets_404_on_request_and_image(login_as, ...):
    other = login_as("client")
    assert other.get(f"/client/cereri/{cid}").status_code == 404
    assert other.get(f"/client/cereri/{cid}/imagini/{img}").status_code == 404
    assert other.post(f"/client/cereri/{cid}/aproba").status_code == 404

def test_image_of_another_request_is_404_under_my_request(login_as, ...): ...
def test_double_approve_answers_409_and_generates_nothing(login_as, ...): ...
```

- [ ] **Step 2: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/e2e/test_client_routes.py -v`
Expected: FAIL.

- [ ] **Step 3: Implementează rutele și șabloanele**

O funcție `_own_cerere(conn, request, id)` dă 404 dacă `client_user_id` nu e al utilizatorului logat, iar toate rutele cu `{id}` trec prin ea. `InvalidState` devine 409, iar `UploadRejected` 422 cu mesajul în pagină. Așezarea urmează `client-model-v2.html` din schițe. Pentru cele două imagini se folosesc clasele `match-compare` din `styles.css`.

- [ ] **Step 4: Rulează testele, apoi toate testele, și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`
Expected: toate trec.

```bash
git add web tests/e2e/test_client_routes.py
git commit -m "feat(client): cererea, intrebarile, modelul si piesele in cont"
```

### Task 8: Paginile adminului

**Files:**
- Create: `web/routes_admin.py`, `web/templates/admin/cereri.html`, `web/templates/admin/cerere.html`
- Modify: `web/app.py`, pentru includerea routerului, `web/templates/index.html`, pentru un link spre lista cererilor
- Test: `tests/e2e/test_admin_routes.py`

**Interfaces:**
- Consumes: `cereri.repository`, `cereri.flow.redo_piece_image`, `cereri.flow.resume`, `image_gen.budget`.
- Produces, rutele:
  - `GET /admin/cereri`, cu sursă, client, piese și stare, plus contorul „X din Y imagini luna aceasta”
  - `GET /admin/cereri/{id}`
  - `GET /admin/cereri/{id}/specificatii/{piesa_id}.json`
  - `GET /admin/cereri/{id}/imagini/{image_id}`, `GET /admin/cereri/{id}/incarcari/{upload_id}`
  - `POST /admin/cereri/{id}/piese/{piesa_id}/reface/{vedere}`
  - `POST /admin/cereri/{id}/reia`

- [ ] **Step 1: Scrie testele care pică**

```python
def test_list_shows_requests_of_all_clients_and_counter(client, ...): ...
def test_open_request_shows_description_answers_specs_and_images(client, ...): ...
def test_spec_download_is_the_piece_state_as_json(client, ...):
    assert r.json()["material"] == "bumbac" and "attachment" in r.headers["content-disposition"]
def test_redo_limit_is_shown_and_enforced(client, ...): ...         # a treia oară, 409
def test_redo_rejects_unknown_view(client, ...): ...                # 422
def test_resume_after_cap_finishes_the_images(client, ...): ...
def test_piece_from_another_request_is_404(client, ...): ...
def test_client_and_inspector_cannot_open_admin_requests(login_as, ...): ...   # 403
```

- [ ] **Step 2: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/e2e/test_admin_routes.py -v`
Expected: FAIL.

- [ ] **Step 3: Implementează rutele și șabloanele**

Pe cererea deschisă, zona de verificări lipsește deocamdată. O adaugă faza 3. Butonul „Reia” apare doar când `blocaj` nu e gol.

- [ ] **Step 4: Rulează toate testele și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`
Expected: toate trec.

```bash
git add web tests/e2e/test_admin_routes.py
git commit -m "feat(admin): lista cererilor, cererea deschisa, refacerea pieselor si contorul"
```

### Task 9: Evalurile 1–3, pe imagini

Consumă 108 imagini la o rulare completă, deci rularea reală cere acordul lui Tudor. Scorurile sunt funcții pure, testate fără API.

**Files:**
- Create: `evals/__init__.py`, `evals/imagini/__init__.py`, `evals/imagini/cazuri.json`, `evals/imagini/scoruri.py`, `evals/imagini/run.py`, `evals/imagini/sigle/`, `prompts/eval_consistenta.md`, `prompts/eval_sigla.md`
- Modify: `.gitignore`, pentru `evals/rezultate/`
- Test: `tests/unit/test_eval_scoruri.py`

**Interfaces:**
- Consumes: `image_gen.service`, `agents.inspector`, `schemas.loader`.
- Produces, în `evals/imagini/scoruri.py`:
  - `PRAG = 0.8`
  - `fidelitate_ok(report: ValidationReport, schema: dict, state: dict) -> bool`
  - `consistenta_ok(judecata: dict) -> bool`, `sigla_ok(judecata: dict) -> bool`
  - `rulare_trece(rezultate: list[bool]) -> bool`
- `run.py`: `--rulari N`, implicit 3, și `--confirma`. Fără `--confirma` doar afișează câte imagini ar consuma și cât a rămas din plafon. Rezultatele merg în `evals/rezultate/<data>.json`.

- [ ] **Step 1: Scrie testele care pică**

```python
def test_any_nonconform_field_fails_the_piece(): ...
def test_invisible_material_is_allowed_to_be_nevizibil(): ...
def test_visible_field_marked_nevizibil_fails_the_piece(): ...
def test_threshold_is_eighty_percent():
    assert rulare_trece([True] * 8 + [False] * 2) and not rulare_trece([True] * 7 + [False] * 3)
def test_consistency_needs_colors_logo_and_elements(): ...
def test_logo_needs_present_undeformed_not_mirrored(): ...
def test_cases_file_has_six_requests_with_two_complete_pieces():
    cazuri = json.loads(Path("evals/imagini/cazuri.json").read_text(encoding="utf-8"))
    assert len(cazuri) == 6 and all(len(c["piese"]) == 2 for c in cazuri)
```

- [ ] **Step 2: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_eval_scoruri.py -v`
Expected: FAIL.

- [ ] **Step 3: Implementează**

Cele 6 cazuri au branduri inventate, specificații complete, cu și fără print pe spate, iar sigla o desenează `scripts/sigla_exemplu.py`, din faza 0, cu alte texte. Un caz acoperă două tricouri în aceeași cerere. Evalul 1 trece prin `inspector.build_messages(spec, [fata, spate])`. Evalul 2 și 3 folosesc judecători cu Claude vision, iar răspunsul lor e JSON. Pentru consistență se folosește judecătorul, nu Image Match, ca piesa să se poată compara cu un set care are mai multe piese.

- [ ] **Step 4: Rulează testele și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_eval_scoruri.py -v`
Expected: toate trec.

```bash
git add evals prompts/eval_*.md .gitignore tests/unit/test_eval_scoruri.py
git commit -m "feat(evals): fidelitatea, consistenta si sigla, pe imaginile generate"
```

- [ ] **Step 5: Rularea reală, cu acordul lui Tudor**

Run: `.venv/Scripts/python.exe -m evals.imagini.run` și, după acord, `.venv/Scripts/python.exe -m evals.imagini.run --confirma`
Expected: pentru fiecare eval, cel puțin 80% la fiecare dintre cele 3 rulări. Rezultatul ajunge la Tudor. Un eval picat nu oprește faza următoare, dar modulul nu e „gata” până nu trece.

# Kitcraft, faza 0: creditele Google și furnizorul de imagini, plan de implementare

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** dovedim că Gemini generează imagini din creditele lui Tudor și că metoda „spatele și piesa pornesc de la o imagine de referință” dă rezultate folosibile.

**Architecture:** un singur fișier știe de Google. Restul aplicației vede doar `ImageProvider.generate(prompt, reference_paths) -> bytes`. Schimbarea pe OpenAI înseamnă alt fișier și o setare.

**Tech Stack:** Python 3.14 din `.venv`, SDK-ul `google-genai`, Pillow, pytest.

**Spec:** `docs/superpowers/specs/2026-11-05-kitcraft-client-admin-inspector-design.md`, secțiunile 9.4, 9.10 și 13.

## Global Constraints

- Modelul: `gemini-nano-banana-2.1`. Rezoluția implicită: 1K.
- Cheia stă în `.env`, ca `GEMINI_API_KEY`, și nu se comite niciodată.
- Furnizorul stă într-un singur fișier.
- Nicio cheltuială peste credite fără acordul explicit al lui Tudor. Dacă creditele nu se activează, înainte de orice trecere pe OpenAI se revine la Tudor cu costul estimat.
- În Google Cloud există o alertă de buget la 10 dolari.
- Pentru încercări se folosesc branduri inventate, cu sigle proprii.
- Claude nu introduce carduri, parole sau chei. Pașii din Task 1 îi face Tudor.
- Testele de bază rulează cu `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`. Pornim de la 168 de teste verzi.

## Review Focus

- `GEMINI_API_KEY` lipsește din mediu: aplicația dă o eroare care spune ce lipsește, nu o eroare din SDK. Test în Task 2.
- Modelul refuză sau răspunde fără imagine: `ImageGenerationError` cu motivul, nu `IndexError`. Test în Task 2.
- SDK-ul aruncă o eroare de rețea sau de cotă: devine `ImageGenerationError`, fără cheia în mesaj. Test în Task 2.
- O imagine de referință lipsește de pe disc: eroare clară, fără apel plătit. Test în Task 2.
- Mai mult de 10 imagini de referință: eroare înainte de apel, pentru că modelul nu primește mai multe. Test în Task 2.

---

### Task 1: Tudor activează creditele și face cheia

Pasul e al lui Tudor. La execuție, Claude citește paginile actuale ale Google, pentru că meniurile se schimbă, și îi dă lui Tudor pașii numerotați, pe o singură cale.

**Files:** niciunul din repo. `.env` se editează de Tudor și nu se comite.

- [ ] **Step 1: Claude verifică paginile Google și scrie pașii pentru Tudor**

Paginile: beneficiile pentru dezvoltatori din Google AI Pro, Google AI Studio, facturarea din Google Cloud. Pașii acoperă: activarea creditelor, proiectul din Google Cloud, contul de facturare, alerta de buget la 10 dolari și cheia API.

- [ ] **Step 2: Tudor face pașii și pune cheia în `.env`, pe rândul `GEMINI_API_KEY=`**

Verificare, fără să afișeze cheia:

```bash
.venv/Scripts/python.exe -c "from dotenv import dotenv_values; print('cheie prezenta' if dotenv_values('.env').get('GEMINI_API_KEY') else 'lipseste')"
```

Expected: `cheie prezenta`.

- [ ] **Step 3: Punct de oprire**

Dacă oferta pentru studenți nu intră la beneficiu sau România nu e inclusă, execuția se oprește aici. Claude îi prezintă lui Tudor costul pe OpenAI și așteaptă acordul explicit.

### Task 2: Furnizorul de imagini

**Files:**
- Create: `image_gen/__init__.py`, `image_gen/provider.py`, `image_gen/gemini.py`
- Modify: `requirements.txt`, `.env.example`
- Test: `tests/unit/test_image_gen_gemini.py`, `tests/integration/test_gemini_real.py`

**Interfaces:**
- Produces, în `image_gen/provider.py`:
  - `class ImageGenerationError(Exception)`
  - `class ImageProvider(Protocol): def generate(self, prompt: str, reference_paths: list[Path]) -> bytes` întoarce octeți PNG
- Produces, în `image_gen/gemini.py`:
  - `DEFAULT_IMAGE_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-nano-banana-2.1")`
  - `MAX_REFERENCE_IMAGES = 10`
  - `class GeminiProvider(ImageProvider)`, cu `__init__(self, api_key: str | None = None, model: str = DEFAULT_IMAGE_MODEL, client: Any = None)`. Dacă primește `client`, nu mai construiește unul, ca testele să nu cheme API-ul.

- [ ] **Step 1: Scrie testele care pică, în `tests/unit/test_image_gen_gemini.py`**

Clientul fals are `models.generate_content(...)` și întoarce un răspuns cu `candidates[0].content.parts`.

```python
def test_generate_returns_png_bytes(tmp_path):
    provider = GeminiProvider(api_key="x", client=_fake_client(image=_png()))
    assert provider.generate("un tricou", [])[:8] == b"\x89PNG\r\n\x1a\n"

def test_generate_sends_prompt_and_references(tmp_path):
    ref = _write_png(tmp_path / "sigla.png")
    client = _fake_client(image=_png())
    GeminiProvider(api_key="x", client=client).generate("un tricou", [ref])
    assert client.last_model == "gemini-nano-banana-2.1"
    assert "un tricou" in client.last_text
    assert client.last_image_count == 1

def test_no_image_in_response_raises(tmp_path):
    provider = GeminiProvider(api_key="x", client=_fake_client(text_only="nu pot"))
    with pytest.raises(ImageGenerationError, match="nu pot"):
        provider.generate("x", [])

def test_sdk_error_becomes_generation_error_without_the_key():
    provider = GeminiProvider(api_key="SECRET", client=_fake_client(raises=RuntimeError("cota SECRET")))
    with pytest.raises(ImageGenerationError) as e:
        provider.generate("x", [])
    assert "SECRET" not in str(e.value)

def test_missing_reference_raises_before_calling_api(tmp_path):
    client = _fake_client(image=_png())
    with pytest.raises(ImageGenerationError, match="referin"):
        GeminiProvider(api_key="x", client=client).generate("x", [tmp_path / "nu-exista.png"])
    assert client.calls == 0

def test_more_than_ten_references_raises_before_calling_api(tmp_path):
    refs = [_write_png(tmp_path / f"{i}.png") for i in range(11)]
    client = _fake_client(image=_png())
    with pytest.raises(ImageGenerationError):
        GeminiProvider(api_key="x", client=client).generate("x", refs)
    assert client.calls == 0

def test_missing_key_raises_clear_error(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ImageGenerationError, match="GEMINI_API_KEY"):
        GeminiProvider()
```

- [ ] **Step 2: Rulează testele și verifică faptul că pică**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_image_gen_gemini.py -v`
Expected: FAIL, `ModuleNotFoundError: image_gen`.

- [ ] **Step 3: Implementează `image_gen/provider.py` și `image_gen/gemini.py`**

Forma exactă a apelului se ia din documentația curentă Google pentru generarea de imagini: răspuns cu imagine și dimensiunea `1K`. Dacă imaginea nu vine ca PNG, se convertește cu Pillow, ca toți ceilalți să primească PNG. Mesajul de eroare scoate cheia prin `str.replace`.

Adaugă `google-genai` în `requirements.txt` și `GEMINI_API_KEY=` în `.env.example`, apoi instalează:

```bash
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

- [ ] **Step 4: Rulează testele și verifică faptul că trec**

Run: `.venv/Scripts/python.exe -m pytest tests/unit/test_image_gen_gemini.py -v`
Expected: 7 passed.

- [ ] **Step 5: Scrie testul real, separat, după modelul din `tests/integration/test_llm_client.py`**

```python
pytestmark = pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")

def test_generate_real_image():
    data = GeminiProvider().generate("un tricou alb simplu, pe fundal alb", [])
    assert Image.open(io.BytesIO(data)).size[0] > 0
```

Testul consumă o imagine, deci nu intră în comanda de bază.

- [ ] **Step 6: Rulează testele de bază și fă commit**

Run: `.venv/Scripts/python.exe -m pytest tests/unit tests/e2e image_matcher/tests -q`
Expected: 175 passed.

```bash
git add image_gen requirements.txt .env.example tests/unit/test_image_gen_gemini.py tests/integration/test_gemini_real.py
git commit -m "feat(image-gen): furnizorul de imagini pe Gemini, intr-un singur fisier"
```

### Task 3: Încercarea metodei, pe un brand inventat

Consumă cam 5 imagini. Metoda „din imaginea setului” e o presupunere a specului, iar aici o verificăm înainte să construim pe ea.

**Files:**
- Create: `scripts/incearca_gemini.py`, `scripts/sigla_exemplu.py`

**Interfaces:**
- Consumes: `GeminiProvider.generate(prompt, reference_paths)` din Task 2.

- [ ] **Step 1: Scrie `scripts/sigla_exemplu.py`**

Desenează cu Pillow o siglă inventată, „AURORA”, într-un cerc, și o salvează în `uploads/incercare/sigla.png`.

- [ ] **Step 2: Scrie `scripts/incearca_gemini.py`**

Generează, în `uploads/incercare/`, care e ignorat de git, în ordine:

1. `set_fata.png`: tricou negru și șapcă neagră, văzute din față, cu sigla pe piept și pe șapcă;
2. `set_spate.png`: aceleași piese din spate, cu un print pe spatele tricoului, cu `set_fata.png` ca referință;
3. `tricou_fata.png`: doar tricoul, pe fundal alb, din `set_fata.png`;
4. `tricou_spate.png`: doar tricoul din spate, pe fundal alb, din `set_spate.png`;
5. `set_fata_mod.png`: `set_fata.png` cu instrucțiunea „fă șapca albă”.

Scriptul afișează câte imagini a generat și se oprește la prima eroare.

- [ ] **Step 3: Rulează scriptul**

Run: `.venv/Scripts/python.exe scripts/sigla_exemplu.py` și apoi `.venv/Scripts/python.exe scripts/incearca_gemini.py`
Expected: `5 imagini generate`.

- [ ] **Step 4: Tudor se uită la imagini și spune dacă metoda e bună**

Întrebările: sigla e nedeformată? Spatele aparține acelorași piese? Tricoul separat arată ca în set? Modificarea a schimbat doar șapca?

- [ ] **Step 5: Verifică prețul**

Tudor citește din facturarea Google Cloud costul celor 5 imagini. Specul presupune 0,0336 dolari la 1K. Dacă diferă mult, plafonul de 280 de imagini din faza 2 se recalculează.

- [ ] **Step 6: Notează rezultatul și fă commit**

Notează în `AIS-OS\Licenta\memory\stare.md`: dacă creditele merg, cât a costat, ce a ieșit bine și ce nu. Dacă metoda nu e bună, se revine la Tudor înainte de faza 2.

```bash
git add scripts/incearca_gemini.py scripts/sigla_exemplu.py
git commit -m "chore(image-gen): script de incercare a metodei cu imagine de referinta"
```

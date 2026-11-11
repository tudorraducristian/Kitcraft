import io
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

from image_gen.gemini import GeminiProvider
from image_gen.provider import ImageGenerationError


def _png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (4, 4), "white").save(buf, format="PNG")
    return buf.getvalue()


def _write_png(path: Path) -> Path:
    path.write_bytes(_png())
    return path


class _FakeModels:
    def __init__(self, image=None, text_only=None, raises=None):
        self._image = image
        self._text_only = text_only
        self._raises = raises
        self.calls = 0
        self.last_model = None
        self.last_text = ""
        self.last_image_count = 0

    def generate_content(self, *, model, contents, config=None):
        self.calls += 1
        self.last_model = model
        self.last_text = " ".join(c for c in contents if isinstance(c, str))
        self.last_image_count = sum(1 for c in contents if not isinstance(c, str))
        if self._raises is not None:
            raise self._raises
        if self._image is not None:
            part = SimpleNamespace(
                text=None,
                inline_data=SimpleNamespace(data=self._image, mime_type="image/png"),
            )
        else:
            part = SimpleNamespace(text=self._text_only, inline_data=None)
        return SimpleNamespace(
            candidates=[SimpleNamespace(content=SimpleNamespace(parts=[part]))]
        )


class _FakeClient:
    """Imită `genai.Client`: `client.models.generate_content(...)`."""

    def __init__(self, **kwargs):
        self.models = _FakeModels(**kwargs)

    def __getattr__(self, name):
        return getattr(self.models, name)


def _fake_client(**kwargs) -> _FakeClient:
    return _FakeClient(**kwargs)


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

"""Singurul fișier care știe de Google. Schimbarea pe alt furnizor înseamnă alt fișier."""

import io
import mimetypes
import os
from pathlib import Path
from typing import Any

from google.genai import types
from PIL import Image

from image_gen.provider import ImageGenerationError, ImageProvider

DEFAULT_IMAGE_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-nano-banana-2.1")
MAX_REFERENCE_IMAGES = 10
IMAGE_SIZE = "1K"

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class GeminiProvider(ImageProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_IMAGE_MODEL,
        client: Any = None,
    ):
        self._model = model
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY") or ""
        if client is not None:
            self._client = client
            return
        if not self._api_key:
            raise ImageGenerationError(
                "Lipsește GEMINI_API_KEY. Pune cheia în .env, pe rândul GEMINI_API_KEY=."
            )
        from google import genai

        self._client = genai.Client(api_key=self._api_key)

    def generate(self, prompt: str, reference_paths: list[Path]) -> bytes:
        if len(reference_paths) > MAX_REFERENCE_IMAGES:
            raise ImageGenerationError(
                f"Prea multe imagini de referință: {len(reference_paths)}, "
                f"modelul primește cel mult {MAX_REFERENCE_IMAGES}."
            )
        missing = [str(p) for p in reference_paths if not Path(p).is_file()]
        if missing:
            raise ImageGenerationError(
                "Lipsește imaginea de referință: " + ", ".join(missing)
            )

        contents: list[Any] = [prompt]
        contents.extend(self._image_part(Path(p)) for p in reference_paths)

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=contents,
                config=self._config(),
            )
        except Exception as exc:  # orice eroare din SDK: rețea, cotă, cheie
            raise ImageGenerationError(
                self._scrub(f"Gemini a dat eroare: {type(exc).__name__}: {exc}")
            ) from None

        return _to_png(self._image_bytes(response))

    @staticmethod
    def _config() -> Any:
        return types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(image_size=IMAGE_SIZE),
        )

    @staticmethod
    def _image_part(path: Path) -> Any:
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        return types.Part.from_bytes(data=path.read_bytes(), mime_type=mime)

    def _image_bytes(self, response: Any) -> bytes:
        texts: list[str] = []
        for candidate in getattr(response, "candidates", None) or []:
            content = getattr(candidate, "content", None)
            for part in getattr(content, "parts", None) or []:
                inline = getattr(part, "inline_data", None)
                if inline is not None and getattr(inline, "data", None):
                    return inline.data
                text = getattr(part, "text", None)
                if text:
                    texts.append(text)
        reason = " ".join(texts) or "răspuns fără imagine și fără explicație"
        raise ImageGenerationError(self._scrub(f"Gemini nu a generat imaginea: {reason}"))

    def _scrub(self, message: str) -> str:
        if self._api_key:
            message = message.replace(self._api_key, "***")
        return message


def _to_png(data: bytes) -> bytes:
    if data[:8] == _PNG_SIGNATURE:
        return data
    try:
        with Image.open(io.BytesIO(data)) as img:
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
    except Exception as exc:
        raise ImageGenerationError(f"Imaginea primită nu se poate citi: {exc}") from None

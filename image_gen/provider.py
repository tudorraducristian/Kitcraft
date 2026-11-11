from pathlib import Path
from typing import Protocol


class ImageGenerationError(Exception):
    """Generarea unei imagini a eșuat. Mesajul spune motivul, fără chei."""


class ImageProvider(Protocol):
    def generate(self, prompt: str, reference_paths: list[Path]) -> bytes:
        """Întoarce octeții unei imagini PNG."""
        ...

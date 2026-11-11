import io
import os

import pytest
from PIL import Image

from image_gen.gemini import GeminiProvider


pytestmark = pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set",
)


def test_generate_real_image():
    """Consumă o imagine din credite, deci nu intră în comanda de bază."""
    data = GeminiProvider().generate("un tricou alb simplu, pe fundal alb", [])
    assert Image.open(io.BytesIO(data)).size[0] > 0

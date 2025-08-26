# -*- coding: utf-8 -*-
# src/homemade_mcp/adapters/utils.py
"""Helpers for image encoding and message assembly.

Utilities here convert PIL images to base64 with simple heuristics and map the
`blocks` sequence into a single internal user message used by adapters.
"""

import base64
import io
from typing import Any, Dict, List, Sequence, Tuple, Union

import pypdfium2 as pdfium
from PIL import Image as PILImageModule
from PIL.Image import Image as PILImage

from homemade_mcp.schemas import PDFDoc

# Pillow 10+ moved resampling filters under Image.Resampling
try:  # pragma: no cover - import-time branch
    RESAMPLE_LANCZOS = PILImageModule.Resampling.LANCZOS  # type: ignore[attr-defined]
except AttributeError:  # Pillow <10
    RESAMPLE_LANCZOS = getattr(PILImageModule, "LANCZOS", 2)  # 2 ~ BILINEAR fallback


def to_internal_message(blocks: Sequence[Union[str, PILImage]]) -> Dict[str, Any]:
    """Create a single user message with ordered text/image parts.

    Strings become `{type: "text"}`, images are converted to `{type: "image"}`
    with base64 data and mime type.
    """
    parts = []
    for b in blocks:
        if isinstance(b, str):
            parts.append({"type": "text", "text": b})
        elif isinstance(b, PILImage):
            b64, mime = pil_to_b64(b)  # auto PNG/JPEG + optional resize
            parts.append({"type": "image", "image": {"mime": mime, "b64": b64}})
        elif isinstance(b, PDFDoc):
            text = extract_pdf_text(b.source, pages=b.pages, max_pages=b.max_pages)
            parts.append({"type": "text", "text": text})
        else:
            raise TypeError("Each block must be str or PIL.Image.Image")
    return {"role": "user", "content": parts}


# Images Utils


def _img_to_bytes(img: PILImage, fmt: str, *, quality: int = 85) -> bytes:
    buf = io.BytesIO()
    save_kwargs = {}
    if fmt == "JPEG":
        save_kwargs.update({"quality": quality, "optimize": True})
        if img.mode in ("RGBA", "LA"):
            img = img.convert("RGB")  # JPEG has no alpha
    img.save(buf, format=fmt, **save_kwargs)
    return buf.getvalue()


def _choose_fmt(img: PILImage, prefer: str | None = None) -> str:
    if prefer:
        return prefer.upper()
    if img.mode in ("RGBA", "LA"):  # has alpha
        return "PNG"
    # Heuristic: photos → JPEG; flat/diagrammatic images → PNG
    return "JPEG"


def _maybe_resize(img: PILImage, max_side: int | None = 2048) -> PILImage:
    if not max_side:
        return img
    w, h = img.size
    m = max(w, h)
    if m <= max_side:
        return img
    scale = max_side / m
    return img.resize((int(w * scale), int(h * scale)), resample=RESAMPLE_LANCZOS)


def pil_to_b64(
    img: PILImage,
    *,
    prefer: str | None = None,
    max_side: int | None = 2048,
    quality: int = 85,
) -> Tuple[str, str]:
    """Convert a PIL image to base64 with simple resizing and format selection.

    Returns a tuple of `(b64, mime)`.
    """
    img = _maybe_resize(img, max_side=max_side)
    fmt = _choose_fmt(img, prefer)
    raw = _img_to_bytes(img, fmt, quality=quality)
    b64 = base64.b64encode(raw).decode("ascii")
    mime = "image/png" if fmt == "PNG" else "image/jpeg"
    return b64, mime


def extract_pdf_text(
    path: str, *, pages: Sequence[int] | None = None, max_pages: int = 20
) -> str:
    """Extract text from a local PDF file.

    Keeps implementation intentionally lightweight. Limits pages to `max_pages`
    for safety.
    """
    doc = pdfium.PdfDocument(path)
    total = len(doc)
    if pages is None:
        idxs = list(range(min(total, max_pages)))
    else:
        idxs = [i for i in pages if 0 <= i < total][:max_pages]
    texts = []
    for i in idxs:
        page = doc[i]
        texts.append(page.extract_text() or "")
    return "\n\n".join([t for t in texts if t]) or ""


def pdf_to_images(
    path: str, pages: Sequence[int] | None = None, max_side: int = 1024
) -> List[PILImage]:
    """Render PDF pages to PIL images (longest side ≤ max_side).

    Requires `pypdfium2`. Renders selected `pages` or the whole document. Images
    are resized to keep the longest side under `max_side`.
    """
    if pdfium is None:  # pragma: no cover
        raise RuntimeError(
            "pypdfium2 is required for PDF rendering. Please install `pypdfium2`."
        )
    doc = pdfium.PdfDocument(path)
    total = len(doc)
    idxs = list(range(total)) if pages is None else [i for i in pages if 0 <= i < total]
    pil_images: List[PILImage] = []
    for i in idxs:
        page = doc[i]
        bitmap = page.render(scale=1.0).to_pil()
        w, h = bitmap.size
        m = max(w, h)
        if m > max_side:
            scale = max_side / m
            bitmap = bitmap.resize(
                (int(w * scale), int(h * scale)), resample=RESAMPLE_LANCZOS
            )
        pil_images.append(bitmap)
    return pil_images


def pdf_to_text(path: str, pages: Sequence[int] | None = None) -> str:
    """Extract text from a PDF using `pypdf`. Wrapper for convenience."""
    return extract_pdf_text(path, pages=pages)


def pdf_to_blocks(
    path: str, pages: Sequence[int] | None = None, as_images: bool = True
) -> List[Union[str, PILImage]]:
    """Return blocks representing PDF pages.

    - If `as_images=True`, returns a list of PIL images.
    - Otherwise returns a single string with concatenated text.
    """
    if as_images:
        return pdf_to_images(path, pages=pages)
    text = pdf_to_text(path, pages=pages)
    return [text]

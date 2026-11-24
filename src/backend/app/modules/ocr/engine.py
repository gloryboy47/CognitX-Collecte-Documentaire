"""Extraction de texte depuis un PDF ou une image."""

from pathlib import Path


def extract_text(file_path: str) -> tuple[str, float, str]:
    """Retourne (texte, confiance, engine).

    Strategie :
    1. PDF avec couche texte → pymupdf (rapide, confiance haute)
    2. Sinon → Tesseract OCR
    """
    path = Path(file_path)

    if path.suffix.lower() == ".pdf":
        text, confidence = _extract_pdf_text(path)
        if text.strip():
            return text, confidence, "pymupdf"

    text, confidence = _ocr_tesseract(path)
    return text, confidence, "tesseract"


def _extract_pdf_text(pdf_path: Path) -> tuple[str, float]:
    import pymupdf
    doc = pymupdf.open(str(pdf_path))
    pages_text = []
    for page in doc:
        pages_text.append(page.get_text())
    doc.close()
    full = "\n".join(pages_text).strip()
    confidence = 0.95 if full else 0.0
    return full, confidence


def _ocr_tesseract(file_path: Path) -> tuple[str, float]:
    try:
        import pytesseract
        from PIL import Image

        if file_path.suffix.lower() == ".pdf":
            import pymupdf
            doc = pymupdf.open(str(file_path))
            images = []
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)
            doc.close()
        else:
            images = [Image.open(file_path)]

        texts = []
        for img in images:
            data = pytesseract.image_to_data(img, lang="fra+eng", output_type=pytesseract.Output.DICT)
            page_text = " ".join(w for w, c in zip(data["text"], data["conf"]) if int(c) > 0)
            texts.append(page_text)
            confidences = [int(c) for c in data["conf"] if int(c) > 0]

        full = "\n".join(texts).strip()
        avg_conf = sum(confidences) / len(confidences) / 100 if confidences else 0.0
        return full, avg_conf

    except Exception:
        return "", 0.0

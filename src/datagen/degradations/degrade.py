"""Pipeline de degradation pour simuler scans, photos et documents abimes."""

from __future__ import annotations

import random
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np


def pdf_to_images(pdf_path: Path, dpi: int = 200) -> list[Image.Image]:
    import fitz  # pymupdf
    doc = fitz.open(str(pdf_path))
    images = []
    for page in doc:
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    doc.close()
    return images


def apply_rotation(img: Image.Image, max_angle: float = 3.0) -> tuple[Image.Image, str]:
    angle = random.uniform(-max_angle, max_angle)
    rotated = img.rotate(angle, expand=True, fillcolor=(255, 255, 255))
    return rotated, f"rotation:{angle:.1f}"


def apply_blur(img: Image.Image, radius: float = 1.0) -> tuple[Image.Image, str]:
    blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
    return blurred, f"flou:{radius}"


def apply_noise(img: Image.Image, intensity: int = 15) -> tuple[Image.Image, str]:
    arr = np.array(img)
    noise = np.random.normal(0, intensity, arr.shape).astype(np.int16)
    noisy = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy), f"bruit:{intensity}"


def apply_contrast(img: Image.Image, factor: float = 0.8) -> tuple[Image.Image, str]:
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(factor), f"contraste:{factor}"


def apply_jpeg_compression(img: Image.Image, quality: int = 50) -> tuple[Image.Image, str]:
    from io import BytesIO
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    return Image.open(buf).copy(), f"jpeg:{quality}"


def apply_spots(img: Image.Image, count: int = 5) -> tuple[Image.Image, str]:
    arr = np.array(img)
    for _ in range(count):
        x = random.randint(0, arr.shape[1] - 1)
        y = random.randint(0, arr.shape[0] - 1)
        radius = random.randint(2, 8)
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < arr.shape[0] and 0 <= nx < arr.shape[1]:
                        arr[ny, nx] = arr[ny, nx] * random.uniform(0.3, 0.7)
    return Image.fromarray(arr), f"taches:{count}"


def degrade_level_0(pdf_path: Path) -> tuple[Path, int, list[str]]:
    """Niveau 0 : PDF natif, pas de degradation."""
    return pdf_path, 0, []


def degrade_level_1(pdf_path: Path, output_path: Path, seed: int) -> tuple[Path, int, list[str]]:
    """Niveau 1 : scan correct (rotation legere, bruit faible, JPEG moyen)."""
    random.seed(seed)
    np.random.seed(seed)

    images = pdf_to_images(pdf_path, dpi=200)
    degradations = []
    result_images = []

    for img in images:
        img, d = apply_rotation(img, max_angle=3.0)
        degradations.append(d)
        if random.random() > 0.5:
            img, d = apply_noise(img, intensity=10)
            degradations.append(d)
        img, d = apply_jpeg_compression(img, quality=random.randint(60, 80))
        degradations.append(d)
        result_images.append(img)

    _save_as_pdf(result_images, output_path)
    return output_path, 1, degradations


def degrade_level_2(pdf_path: Path, output_path: Path, seed: int) -> tuple[Path, int, list[str]]:
    """Niveau 2 : scan difficile (rotation forte, flou, contraste faible, bruit, taches)."""
    random.seed(seed)
    np.random.seed(seed)

    images = pdf_to_images(pdf_path, dpi=random.randint(100, 150))
    degradations = [f"dpi:{150}"]
    result_images = []

    for img in images:
        img, d = apply_rotation(img, max_angle=7.0)
        degradations.append(d)
        img, d = apply_blur(img, radius=random.uniform(0.8, 2.0))
        degradations.append(d)
        img, d = apply_contrast(img, factor=random.uniform(0.5, 0.8))
        degradations.append(d)
        img, d = apply_noise(img, intensity=random.randint(15, 30))
        degradations.append(d)
        if random.random() > 0.5:
            img, d = apply_spots(img, count=random.randint(3, 8))
            degradations.append(d)
        img, d = apply_jpeg_compression(img, quality=random.randint(25, 50))
        degradations.append(d)
        result_images.append(img)

    _save_as_pdf(result_images, output_path)
    return output_path, 2, degradations


def _save_as_pdf(images: list[Image.Image], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if len(images) == 1:
        images[0].save(str(output_path), "PDF")
    else:
        images[0].save(str(output_path), "PDF", save_all=True, append_images=images[1:])


def degrade(pdf_path: Path, output_dir: Path, level: int, seed: int) -> tuple[Path, int, list[str]]:
    if level == 0:
        return degrade_level_0(pdf_path)
    elif level == 1:
        out = output_dir / f"{pdf_path.stem}_deg1.pdf"
        return degrade_level_1(pdf_path, out, seed)
    else:
        out = output_dir / f"{pdf_path.stem}_deg2.pdf"
        return degrade_level_2(pdf_path, out, seed)

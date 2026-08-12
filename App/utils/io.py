# ============================================================
# Project:      OpenCD Change Detection
# Version:      v1.0
# Created:      2026-07-10
# Purpose:      Image I/O utilities (load/save PNG)
# Last Updated: 2026-07-10
# ============================================================

from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def load_image(path):
    """Load an image as BGR numpy array (H, W, 3) uint8."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"Input image not found: {p.resolve()}"
        )
    img = cv2.imread(str(p), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Failed to read image: {p}")
    return img


def save_image(path, image):
    """Save a numpy array as PNG. Creates parent directories."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(p), image):
        raise IOError(f"Failed to write image: {p}")
    return p


def load_image_rgb(path):
    """Load an image as RGB numpy array (H, W, 3) uint8."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"Input image not found: {p.resolve()}"
        )
    img = Image.open(p).convert("RGB")
    return np.array(img)

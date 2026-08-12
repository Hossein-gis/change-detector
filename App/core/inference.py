# ============================================================
# Project:      OpenCD Change Detection
# Version:      v1.0
# Created:      2026-07-10
# Purpose:      ChangeStar inference pipeline
# Last Updated: 2026-07-10
# ============================================================

import time
from pathlib import Path

import cv2
import numpy as np
import torch

import opencd  # noqa: F401  triggers registry setup

from mmengine.config import Config


class ChangeStarInference:
    """Production inference pipeline for ChangeStar change detection."""

    def __init__(
        self,
        config_path,
        checkpoint_path,
        device="cpu",
        threshold=0.5,
        logger=None,
    ):
        self.device = torch.device(device)
        self.threshold = threshold
        self.logger = logger

        self._log("INFO", f"Loading config: {config_path}")
        cfg = Config.fromfile(config_path)

        self._log("INFO", "Building model from config")
        from mmseg.models import build_segmentor

        self.model = build_segmentor(cfg.model)
        self.model.to(self.device)
        self.model.eval()

        self._log("INFO", f"Loading checkpoint: {checkpoint_path}")
        ckpt = torch.load(
            checkpoint_path, map_location=self.device
        )
        if "state_dict" in ckpt:
            state_dict = ckpt["state_dict"]
        else:
            state_dict = ckpt

        clean_state_dict = {}
        for k, v in state_dict.items():
            new_key = k.replace("module.", "")
            clean_state_dict[new_key] = v

        missing, unexpected = self.model.load_state_dict(
            clean_state_dict, strict=False
        )
        if missing:
            self._log(
                "WARNING",
                f"Missing keys in checkpoint: {len(missing)}",
            )
        if unexpected:
            self._log(
                "WARNING",
                f"Unexpected keys in checkpoint: {len(unexpected)}",
            )

        self._log("INFO", "Model ready")

    def _log(self, level, msg):
        if self.logger:
            getattr(self.logger, level.lower(), self.logger.info)(
                msg
            )

    @torch.no_grad()
    def predict(self, before_path, after_path):
        """Run inference on a pair of images.

        Returns:
            probability_map: np.ndarray (H, W) float32 in [0, 1]
            binary_mask: np.ndarray (H, W) uint8, values {0, 255}
        """
        self._log("INFO", f"Loading before: {before_path}")
        before_bgr = cv2.imread(str(before_path), cv2.IMREAD_COLOR)
        if before_bgr is None:
            raise ValueError(
                f"Failed to read image: {before_path}"
            )

        self._log("INFO", f"Loading after: {after_path}")
        after_bgr = cv2.imread(str(after_path), cv2.IMREAD_COLOR)
        if after_bgr is None:
            raise ValueError(
                f"Failed to read image: {after_path}"
            )

        h, w = before_bgr.shape[:2]

        before_rgb = cv2.cvtColor(before_bgr, cv2.COLOR_BGR2RGB)
        after_rgb = cv2.cvtColor(after_bgr, cv2.COLOR_BGR2RGB)

        before_tensor = (
            torch.from_numpy(before_rgb)
            .permute(2, 0, 1)
            .unsqueeze(0)
            .float()
            .to(self.device)
        )
        after_tensor = (
            torch.from_numpy(after_rgb)
            .permute(2, 0, 1)
            .unsqueeze(0)
            .float()
            .to(self.device)
        )

        combined = torch.cat([before_tensor, after_tensor], dim=1)

        self._log("INFO", "Running inference...")
        start = time.time()
        result = self.model(combined)
        elapsed = time.time() - start
        self._log("INFO", f"Inference complete in {elapsed:.3f}s")

        if isinstance(result, dict):
            logits = result.get("logits", result.get("out_0"))
        else:
            logits = result

        if isinstance(logits, (list, tuple)):
            logits = logits[-1]

        probs = torch.sigmoid(logits).squeeze().cpu().numpy()

        if probs.ndim == 3:
            probs = probs[0]

        probs_resized = cv2.resize(
            probs, (w, h), interpolation=cv2.INTER_LINEAR
        )

        binary = (
            (probs_resized >= self.threshold).astype(np.uint8) * 255
        )

        return probs_resized, binary

    def predict_overlay(
        self,
        before_path,
        after_path,
        alpha=0.5,
    ):
        """Run inference and return a colored overlay.

        Returns:
            overlay: np.ndarray (H, W, 3) uint8 BGR
        """
        before_bgr = cv2.imread(
            str(before_path), cv2.IMREAD_COLOR
        )
        _probs, binary = self.predict(before_path, after_path)

        change_mask = (binary > 0).astype(np.uint8)
        overlay = before_bgr.copy()
        color = np.array([0, 0, 255], dtype=np.uint8)

        mask_3ch = np.stack([change_mask] * 3, axis=-1)
        color_3ch = np.broadcast_to(color, overlay.shape)

        overlay = np.where(
            mask_3ch,
            cv2.addWeighted(
                overlay, 1 - alpha, color_3ch, alpha, 0
            ),
            overlay,
        )

        return overlay.astype(np.uint8)

#!/usr/bin/env python
# ============================================================
# Project:      OpenCD Change Detection
# Version:      v1.0
# Created:      2026-07-10
# Purpose:      CLI entry point for change detection inference
# Last Updated: 2026-07-10
# ============================================================

import argparse
import sys
import time
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="opencd",
        description="OpenCD Change Detection Inference",
    )

    parser.add_argument(
        "--before",
        required=True,
        help="Path to before image (pre-event)",
    )
    parser.add_argument(
        "--after",
        required=True,
        help="Path to after image (post-event)",
    )
    parser.add_argument(
        "--output",
        default="Data/output",
        help="Output directory (default: Data/output)",
    )
    parser.add_argument(
        "--mask-name",
        default="change_mask.png",
        help="Output mask filename (default: change_mask.png)",
    )
    parser.add_argument(
        "--config",
        default="App/configs/changestar.py",
        help="OpenCD config file (default: App/configs/changestar.py)",
    )
    parser.add_argument(
        "--checkpoint",
        default="weights/changestar/changestar.pth",
        help="Model checkpoint (default: weights/changestar/changestar.pth)",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cpu"],
        help="Device (default: cpu)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Binary threshold (default: 0.5)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing outputs",
    )
    parser.add_argument(
        "--save-probability",
        action="store_true",
        help="Save probability map",
    )
    parser.add_argument(
        "--save-overlay",
        action="store_true",
        help="Save colored overlay",
    )
    parser.add_argument(
        "--overlay-alpha",
        type=float,
        default=0.5,
        help="Overlay transparency (default: 0.5)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO)",
    )
    parser.add_argument(
        "--log-file",
        default="logs/inference.log",
        help="Log file path (default: logs/inference.log)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose console output",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate environment only, skip inference",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="OpenCD Change Detection v1.0",
    )

    return parser.parse_args(argv)


def validate_paths(args, logger):
    """Validate all file paths. Returns exit code or 0 on success."""
    before = Path(args.before)
    if not before.exists():
        logger.error(
            f"Before image not found: {before.resolve()}"
        )
        return 2

    after = Path(args.after)
    if not after.exists():
        logger.error(
            f"After image not found: {after.resolve()}"
        )
        return 2

    ckpt = Path(args.checkpoint)
    if not ckpt.exists():
        logger.error(
            f"Checkpoint not found: {ckpt.resolve()}"
        )
        return 3

    cfg = Path(args.config)
    if not cfg.exists():
        logger.error(
            f"Config not found: {cfg.resolve()}"
        )
        return 4

    out_dir = Path(args.output)
    if out_dir.exists() and list(out_dir.glob(args.mask_name)):
        if not args.overwrite:
            logger.error(
                f"Output exists: {out_dir / args.mask_name}. "
                "Use --overwrite to replace."
            )
            return 7

    return 0


def main(argv=None):
    args = parse_args(argv)

    from utils.logging import setup_logger

    logger = setup_logger(
        log_file=args.log_file,
        level=args.log_level,
        verbose=args.verbose,
    )

    logger.info("=" * 60)
    logger.info("OpenCD Change Detection Inference v1.0")
    logger.info("=" * 60)

    exit_code = validate_paths(args, logger)
    if exit_code != 0:
        return exit_code

    logger.info(f"Before:  {args.before}")
    logger.info(f"After:   {args.after}")
    logger.info(f"Config:  {args.config}")
    logger.info(f"Checkpoint: {args.checkpoint}")
    logger.info(f"Threshold:  {args.threshold}")
    logger.info(f"Device:     {args.device}")

    if args.dry_run:
        logger.info("Dry run complete - environment valid")
        return 0

    from core.inference import ChangeStarInference

    logger.info("Initializing ChangeStar model...")
    try:
        pipeline = ChangeStarInference(
            config_path=args.config,
            checkpoint_path=args.checkpoint,
            device=args.device,
            threshold=args.threshold,
            logger=logger,
        )
    except Exception as e:
        logger.error(f"Model initialization failed: {e}")
        return 5

    logger.info("Running inference...")
    start_time = time.time()
    try:
        probs, mask = pipeline.predict(
            args.before, args.after
        )
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        return 6

    elapsed = time.time() - start_time
    logger.info(f"Inference completed in {elapsed:.3f}s")

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    from utils.io import save_image

    mask_path = out_dir / args.mask_name
    try:
        save_image(mask_path, mask)
        logger.info(f"Saved mask: {mask_path}")
    except Exception as e:
        logger.error(f"Failed to save mask: {e}")
        return 7

    if args.save_probability:
        prob_path = out_dir / "probability.png"
        try:
            import cv2
            import numpy as np

            prob_vis = (probs * 255).astype(np.uint8)
            prob_color = cv2.applyColorMap(
                prob_vis, cv2.COLORMAP_JET
            )
            save_image(prob_path, prob_color)
            logger.info(
                f"Saved probability map: {prob_path}"
            )
        except Exception as e:
            logger.warning(
                f"Failed to save probability map: {e}"
            )

    if args.save_overlay:
        overlay_path = out_dir / "overlay.png"
        try:
            overlay = pipeline.predict_overlay(
                args.before,
                args.after,
                alpha=args.overlay_alpha,
            )
            save_image(overlay_path, overlay)
            logger.info(f"Saved overlay: {overlay_path}")
        except Exception as e:
            logger.warning(f"Failed to save overlay: {e}")

    logger.info("=" * 60)
    logger.info("DONE")
    logger.info("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())

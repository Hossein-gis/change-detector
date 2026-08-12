# Build Information

Project:    OpenCD Change Detection
Version:    v1.0
Date:       2026-07-10

Platform:   Docker (Linux container on Windows host)
Python:     3.10
CPU Only:   Yes
CUDA:       Disabled
GPU:        Not required

PyTorch:    2.1.2 (CPU)
OpenCD:     1.1.0 (commit e8fae70)
ChangeStar: changestar_farseg_1x96_512x512_40k_levircd

Build Modes:
  - Online:  downloads packages from PyPI + PyTorch CPU index
  - Offline: installs from pre-populated wheels/ directory

Status:     Production-ready

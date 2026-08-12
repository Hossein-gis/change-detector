# OpenCD Change Detection

Offline binary change detection using OpenCD + ChangeStar.
No GPU. No web interface. Docker only.

## Stack

| Component    | Version |
|-------------|---------|
| Python       | 3.10    |
| PyTorch      | 2.1.2 (CPU) |
| TorchVision  | 0.16.2 |
| MMEngine     | 0.10.4 |
| MMCV-Lite    | 2.1.0 |
| MMDetection  | 3.3.0 |
| MMSegmentation | 1.2.2 |
| OpenCD       | 1.1.0 (commit e8fae70) |

## Prerequisites

- Docker Desktop for Windows
- Git
- ~2 GB free disk space

## Setup

### 1. Clone with Submodule

```powershell
git clone <repo-url> Change-Detecting
cd Change-Detecting
git submodule update --init --recursive
```

### 2. Download Weights

```powershell
# ChangeStar checkpoint (~211 MB)
# Download from: https://huggingface.co/likyoo/Open-CD_Model_Zoo
# Place at: weights/changestar/changestar.pth

# ResNet-18 backbone (~45 MB)
# Place at: weights/changestar/resnet18_v1c_batchnorm.pth
```

### 3. Download Wheels (for offline mode)

```powershell
pip download -r requirements/runtime.txt -d ./wheels/
```

## Quick Start

### Online Build

```powershell
.\build.ps1 -Mode online
```

### Offline Build

```powershell
.\build.ps1 -Mode offline
```

### Direct Docker Commands

```powershell
# Build
docker compose -f Docker/docker-compose.yml build --build-arg INSTALL_MODE=online

# Run
docker compose -f Docker/docker-compose.yml run --rm opencd
```

## CLI Usage

```
python App/run.py \
  --before Data/input/before.png \
  --after Data/input/after.png \
  --output Data/output
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--before` | (required) | Path to before image |
| `--after` | (required) | Path to after image |
| `--output` | Data/output | Output directory |
| `--mask-name` | change_mask.png | Output filename |
| `--config` | App/configs/changestar.py | Config file |
| `--checkpoint` | weights/changestar/changestar.pth | Model weights |
| `--threshold` | 0.5 | Binary threshold |
| `--save-probability` | false | Save probability map |
| `--save-overlay` | false | Save colored overlay |
| `--dry-run` | false | Validate only |
| `--version` | | Show version |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments |
| 2 | Missing input image |
| 3 | Missing checkpoint |
| 4 | Config error |
| 5 | Model init failed |
| 6 | Inference failed |
| 7 | Output write failed |

## Project Structure

```
Change-Detecting/
├── App/
│   ├── run.py                  # CLI entry point
│   ├── configs/changestar.py   # Model config
│   ├── core/inference.py       # Inference pipeline
│   └── utils/                  # I/O, logging
├── Data/
│   ├── input/                  # Input images
│   └── output/                 # Output masks
├── Docker/                     # Docker files
├── OpenCD/                     # Git submodule (pinned)
├── requirements/               # Python dependencies
├── weights/                    # Model checkpoints
└── wheels/                     # Pre-downloaded packages
```

## License

OpenCD: Apache 2.0

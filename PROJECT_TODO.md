# PROJECT_TODO.md

## Overall Progress

| Metric | Value |
|--------|-------|
| Architecture Review | **DONE** |
| File Generation | **DONE** |
| Syntax Validation | **PASSED** |
| Docker Compose Validation | **PASSED** |
| Cross-Reference Validation | **PASSED** |
| Project Tree Validation | **PASSED** |
| Current Step | Complete |
| Status | **PASS** (pending Docker build test) |

## Current Sprint

| Field | Value |
|-------|-------|
| Current Sprint | Phase 4 - File Generation COMPLETE |
| Next Action | Docker build test (requires Docker daemon) |
| Blocked By | None |
| Completed Today | All 26 files generated and validated |
| Estimated Finish | Complete |

---

## Milestones

| Milestone | Status | Progress |
|-----------|--------|----------|
| Architecture Review | **DONE** | 100% |
| Project Structure | **DONE** | 100% |
| Requirements | **DONE** | 100% |
| App Package Markers | **DONE** | 100% |
| App Utilities | **DONE** | 100% |
| Config | **DONE** | 100% |
| Core Inference | **DONE** | 100% |
| CLI Entry Point | **DONE** | 100% |
| Docker | **DONE** | 100% |
| Lock File | **DONE** | 100% |
| Documentation | **DONE** | 100% |
| Syntax Validation | **DONE** | 100% |
| Docker Compose Validation | **DONE** | 100% |
| Docker Build (online) | **READY** | 0% |
| Docker Build (offline) | **READY** | 0% |
| Import Validation | **READY** | 0% |
| Runtime Validation | **READY** | 0% |
| Output Validation | **READY** | 0% |
| Final Audit | **READY** | 0% |

---

## Detailed Tasks

### 1. File Generation

| Task | Priority | Status | Dependencies | Notes |
|------|----------|--------|-------------|-------|
| .gitignore | HIGH | DONE | None | Complete Python/Docker/OS rules |
| .gitkeep files | MEDIUM | DONE | None | Data/output, Data/temp, logs |
| requirements/build.txt | LOW | DONE | None | Kept as-is |
| requirements/runtime.txt | LOW | DONE | None | Kept as-is |
| requirements/offline.txt | HIGH | DONE | None | Self-contained, no -r runtime.txt |
| requirements/wheels.lock | MEDIUM | DONE | None | Template with expected filenames |
| Sample images | HIGH | DONE | None | Synthetic 256x256 PNGs |
| configs/__init__.py | MEDIUM | DONE | None | Package marker |
| core/__init__.py | MEDIUM | DONE | None | Package marker |
| utils/__init__.py | MEDIUM | DONE | None | Package marker |
| utils/io.py | HIGH | DONE | None | Image I/O with OpenCV+Pillow |
| utils/logging.py | HIGH | DONE | None | Structured logging |
| configs/changestar.py | HIGH | DONE | None | Self-contained model config |
| core/inference.py | HIGH | DONE | OpenCD, configs | Full inference pipeline |
| run.py | HIGH | DONE | core, utils, configs | Full argparse CLI |
| Dockerfile | HIGH | DONE | requirements, App, OpenCD | Single file, build-arg toggle |
| docker-compose.yml | HIGH | DONE | Dockerfile | Volume mounts, no OpenCD mount |
| .dockerignore | HIGH | DONE | None | wheels/ allowed |
| build.ps1 | MEDIUM | DONE | docker-compose.yml | Mode parameter |
| .gitmodules | MEDIUM | DONE | None | OpenCD submodule |
| README.md | MEDIUM | DONE | All files | Complete documentation |
| BUILD_INFO.md | LOW | DONE | None | Build metadata |
| CHECKPOINTS.md | LOW | DONE | None | Checkpoint info |
| VERSIONS.md | LOW | DONE | None | Pinned versions |
| PROJECT_TODO.md | MEDIUM | DONE | None | This file |

### 2. Validation

| Task | Priority | Status | Dependencies | Notes |
|------|----------|--------|-------------|-------|
| Python syntax check | HIGH | DONE | All .py files | py_compile passed |
| Docker Compose config | HIGH | DONE | docker-compose.yml | Validated |
| Cross-reference validation | HIGH | DONE | All files | 19 checks passed |
| Project tree validation | HIGH | DONE | All files | 29 files verified |
| Docker build (online) | HIGH | READY | Docker image | Requires Docker daemon |
| Docker build (offline) | HIGH | READY | wheels/ populated | Requires wheels |
| Import validation | HIGH | READY | Docker container | torch, mm*, opencd |
| Model construction | HIGH | READY | imports OK | Config + checkpoint |
| Runtime validation | HIGH | READY | model OK | --dry-run + inference |
| Output validation | HIGH | READY | inference OK | PNG file check |

---

## Decision Log

| Date | Decision | Reason | Impact | Alternative |
|------|----------|--------|--------|-------------|
| 2026-07-10 | Bundle ResNet-18 backbone | Fully offline requirement | Extra ~45MB download | First-run download |
| 2026-07-10 | Regular pip install | Production-grade self-contained | No volume mount for OpenCD | Editable install |
| 2026-07-10 | Full CLI with argparse | Production CLI with exit codes | ~20 arguments | Minimal args |
| 2026-07-10 | Include sample PNGs | Quick validation | Synthetic images | Empty |
| 2026-07-10 | Single Dockerfile + ARG | No duplication | --build-arg toggle | Two Dockerfiles |
| 2026-07-10 | Self-contained offline.txt | Avoid --extra-index-url conflict | No -r runtime.txt | Inherit from runtime.txt |
| 2026-07-10 | Remove OpenCD volume mount | Prevent host overwrite | Baked into image | Editable install |
| 2026-07-10 | python:3.10-slim base | Smaller image (~145MB vs ~900MB) | Need build-essential | python:3.10 full |

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation | Status |
|------|--------|------------|------------|--------|
| OpenCD commit e8fae70 incompatible with deps | High | Low | Version constraints verified | Monitored |
| mmcv-lite missing needed ops | High | Low | Inference-only, no deformable conv | Monitored |
| ChangeStar config needs datasets | Medium | Medium | Self-contained config, no dataset deps | Resolved |
| ResNet pretrained unavailable offline | Medium | High | Bundle weights, patch config | Resolved |
| Volume mount overwrites OpenCD | High | Certain | Remove OpenCD mount | Resolved |
| .dockerignore excludes wheels | High | Certain | Remove wheels/ from ignore | Resolved |
| offline.txt inherits extra-index-url | High | Certain | Self-contained file | Resolved |
| torch CPU inference slow | Low | Medium | Documented, accepted | Monitored |

---

## Change Log

| Date | File | Action | Version | Reason |
|------|------|--------|---------|--------|
| 2026-07-10 | .gitignore | REWRITE | v1.0 | Add missing patterns (LEVIR-CD, weights, wheels) |
| 2026-07-10 | .gitmodules | NEW | v1.0 | OpenCD submodule reference |
| 2026-07-10 | Data/output/.gitkeep | NEW | v1.0 | Track empty directory |
| 2026-07-10 | Data/temp/.gitkeep | NEW | v1.0 | Track empty directory |
| 2026-07-10 | Data/input/sample_before.png | NEW | v1.0 | Synthetic test image (256x256) |
| 2026-07-10 | Data/input/sample_after.png | NEW | v1.0 | Synthetic test image (256x256) |
| 2026-07-10 | logs/.gitkeep | NEW | v1.0 | Track empty directory |
| 2026-07-10 | requirements/offline.txt | REWRITE | v1.0 | Self-contained, no runtime.txt inheritance |
| 2026-07-10 | requirements/wheels.lock | NEW | v1.0 | Wheel manifest with SHA256 template |
| 2026-07-10 | App/configs/__init__.py | NEW | v1.0 | Package marker |
| 2026-07-10 | App/core/__init__.py | NEW | v1.0 | Package marker |
| 2026-07-10 | App/utils/__init__.py | NEW | v1.0 | Package marker |
| 2026-07-10 | App/utils/io.py | NEW | v1.0 | Image I/O utilities |
| 2026-07-10 | App/utils/logging.py | NEW | v1.0 | Structured logging |
| 2026-07-10 | App/configs/changestar.py | NEW | v1.0 | Self-contained ChangeStar config |
| 2026-07-10 | App/core/inference.py | NEW | v1.0 | Inference pipeline |
| 2026-07-10 | App/run.py | REWRITE | v1.0 | Full argparse CLI |
| 2026-07-10 | Docker/Dockerfile | REWRITE | v1.0 | Single file with build-arg mode |
| 2026-07-10 | Docker/docker-compose.yml | REWRITE | v1.0 | Updated mounts (no OpenCD) |
| 2026-07-10 | Docker/.dockerignore | REWRITE | v1.0 | Allow wheels/, exclude *.md |
| 2026-07-10 | build.ps1 | REWRITE | v1.0 | Add Mode parameter |
| 2026-07-10 | README.md | REWRITE | v1.0 | Complete documentation |
| 2026-07-10 | BUILD_INFO.md | REWRITE | v1.0 | Complete build metadata |
| 2026-07-10 | CHECKPOINTS.md | REWRITE | v1.0 | Checkpoint documentation |
| 2026-07-10 | VERSIONS.md | REWRITE | v1.0 | Filled commit hash |
| 2026-07-10 | PROJECT_TODO.md | NEW | v1.0 | Master task tracker |

---

## Remaining Manual Steps

1. **Download ChangeStar checkpoint** (~211 MB)
   - Source: https://huggingface.co/likyoo/Open-CD_Model_Zoo
   - Destination: `weights/changestar/changestar.pth`

2. **Download ResNet-18 backbone** (~45 MB)
   - Source: OpenMMLab model zoo
   - Destination: `weights/changestar/resnet18_v1c_batchnorm.pth`

3. **Initialize OpenCD submodule**
   ```powershell
   git init
   git submodule add https://github.com/likyoo/open-cd.git OpenCD
   cd OpenCD && git checkout e8fae70 && cd ..
   ```

4. **Populate wheels** (for offline mode)
   ```powershell
   pip download -r requirements/runtime.txt -d ./wheels/
   ```

5. **Fill SHA256 in CHECKPOINTS.md and wheels.lock**

6. **Docker build and test**
   ```powershell
   .\build.ps1 -Mode online
   ```

---

## Known Limitations

- CPU-only inference (no GPU support)
- Single image pair processing (no batch mode)
- ChangeStar model only (no other architectures)
- LEVIR-CD domain (satellite change detection)
- Requires ~2 GB disk for Docker image + weights
- Synthetic test images are not representative of real data

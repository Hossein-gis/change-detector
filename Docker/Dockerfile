FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-devel

# RTX 5080 = Blackwell, compute capability sm_120. Needs CUDA 12.8+ and a
# PyTorch build with sm_120 kernels — the base image above already ships
# torch 2.7.0 built for cu128, which covers this. (torch==1.13.1+cpu from
# the old CPU Dockerfile will NOT run on this GPU at all.)

RUN apt-get update && apt-get install -y git build-essential ninja-build && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /workspace

ENV FORCE_CUDA=1
ENV TORCH_CUDA_ARCH_LIST="12.0"

# OpenMMLab stack.
# mmengine/mmpretrain have normal PyPI/mim wheels that work fine here.
# mmcv is the tricky one: OpenMMLab's own prebuilt wheel index does not yet
# publish binaries for torch 2.7 + cu128, and building mmcv==2.1.0 from
# source against torch 2.7 is unreliable (older code, long build time).
# Instead we pull a community-built wheel matched exactly to this
# torch+CUDA combo (includes sm_120 kernels), from:
#   https://github.com/open-mmlab/mmdetection/discussions/12062
RUN pip install -U openmim && \
    mim install mmengine==0.10.4 && \
    pip install --extra-index-url https://miropsota.github.io/torch_packages_builder \
        mmcv==2.2.0+pt2.7.0cu128 && \
    mim install mmpretrain==1.2.0 && \
    pip install mmsegmentation==1.2.2 mmdet==3.3.0 ftfy regex

RUN pip uninstall -y opencv-python && \
    pip install opencv-python-headless

# clone once + install open-cd
RUN git clone https://github.com/likyoo/open-cd.git && \
    cd open-cd && pip install -v -e .

WORKDIR /workspace/open-cd

CMD ["bash"]

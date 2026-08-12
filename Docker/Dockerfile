FROM python:3.8-slim

RUN apt-get update && apt-get install -y git build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace

# CPU torch  ← CPU change (+cpu wheels + cpu index)
RUN pip install torch==1.13.1+cpu torchvision==0.14.1+cpu torchaudio==0.13.1 \
    --extra-index-url https://download.pytorch.org/whl/cpu

# OpenMMLab stack — mmcv picks the CPU wheel because torch is CPU
RUN pip install -U openmim && \
    mim install mmengine==0.10.4 && \
    mim install mmcv==2.1.0 && \
    mim install mmpretrain==1.2.0 && \
    pip install mmsegmentation==1.2.2 mmdet==3.3.0 ftfy regex

RUN pip uninstall -y opencv-python && \
    pip install opencv-python-headless

# clone once + install open-cd
RUN git clone https://github.com/likyoo/open-cd.git && \
    cd open-cd && pip install -v -e .

WORKDIR /workspace/open-cd

CMD ["bash"]
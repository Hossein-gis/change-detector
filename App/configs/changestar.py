# ============================================================
# Project:      OpenCD Change Detection
# Version:      v1.0
# Created:      2026-07-10
# Purpose:      Self-contained ChangeStar inference config
# Last Updated: 2026-07-10
# ============================================================
#
# ChangeStar + FarSeg + ResNet-18 for LEVIR-CD change detection.
# Fully self-contained: no _base_ inheritance.
# Backbone weights loaded from checkpoint, not pretrained URL.
#
# Source: OpenCD commit e8fae70
# Reference: configs/changestar/changestar_farseg_1x96_512x512_40k_levircd.py

model = dict(
    type="SiamEncoderDecoder",
    data_preprocessor=dict(
        type="DualInputSegDataPreProcessor",
        mean=[123.675, 116.28, 103.53] * 2,
        std=[58.395, 57.12, 57.375] * 2,
        bgr_to_rgb=True,
        size_divisor=32,
    ),
    backbone=dict(
        type="mmseg.ResNetV1c",
        pretrained=None,
        depth=18,
        num_stages=4,
        out_indices=(0, 1, 2, 3),
        norm_cfg=dict(type="SyncBN", requires_grad=True),
        act_cfg=dict(type="ReLU"),
        init_cfg=dict(type="Pretrained", checkpoint=None),
    ),
    neck=dict(
        type="FarSegFPN",
        policy="concat",
        in_channels=[64, 128, 256, 512],
        out_channels=256,
        num_outs=4,
    ),
    decode_head=dict(
        type="ChangeStarHead",
        inference_mode="t1t2",
        channels=96,
        num_classes=2,
        out_channels=1,
        threshold=0.5,
        seg_head_cfg=dict(
            type="FarSegHead",
            in_channels=[256, 256, 256, 256, 512],
            fsr_channels=256,
            channels=128,
        ),
        changemixin_cfg=dict(
            in_channels=256,
            inner_channels=96,
            num_convs=1,
        ),
        loss_decode=[
            dict(
                type="mmseg.CrossEntropyLoss",
                use_sigmoid=True,
                loss_weight=1.0,
            ),
            dict(
                type="mmseg.DiceLoss",
                use_sigmoid=True,
                loss_weight=1.0,
            ),
        ],
    ),
)

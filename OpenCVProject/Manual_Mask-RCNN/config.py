#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: config.py
@time: 2022/4/1 上午10:07
@function: 
"""

import math
import numpy as np


class Config(object):
    NAME = None

    GPU_COUNT = 1

    IMAGES_PER_GPU = 2

    STEPS_PER_EPOCH = 1000

    VALIDATION_STEPS = 50

    BACKBONE = "resnet101"

    BACKBONE_STRIDES = [4, 8, 16, 32, 64]

    NUM_CLASSES = 1

    RPN_ANCHOR_SCALES = (32, 64, 128, 256, 512)

    RPN_ANCHOR_RATIOS = [0.5, 1, 2]

    RPN_ANCHOR_STRIDE = 1

    RPN_NMS_THRESHOLD = 0.7

    RPN_TRAIN_ANCHORS_PER_IMAGE = 256

    POST_NMS_ROIS_TRAINING = 2000
    POST_NMS_ROIS_INFERENCE = 1000

    USE_MINI_MASK = True
    MINI_MASK_SHAPE = (56, 56)

    IMAGE_MIN_DIM = 800
    IMAGE_MAX_DIM = 1024

    IMAGE_PADDING = True

    MEAN_PIXEL = np.array([123.7, 116.8, 103.9])

    TRAIN_ROIS_PRE_IMAGE = 200

    ROI_POSITIVE_RATIO = 0.33

    POOL_SIZE = 7
    MASK_POOL_SIZE = 14
    MASK_SHAPE = [28, 28]

    MAX_GT_INSTANCES = 100

    RPN_BBOX_STD_DEV = np.array([0.1, 0.1, 0.2, 0.2])
    BBOX_STD_DEV = np.array([0.1, 0.1, 0.2, 0.2])

    DETECTION_MAX_INSTANCES = 100

    DETECTION_MIN_CONFIDENCE = 0.7

    DETECTION_NMS_THRESHOLD = 0.3

    LEARNING_RATE = 0.001
    LEARNING_MOMENTUM = 0.9

    WEIGHT_DECAY = 0.0001

    USE_RPN_ROIS = True

    def __init__(self):

        self.BATCH_SIZE = self.IMAGES_PER_GPU * self.GPU_COUNT

        self.IMAGE_SHAPE = np.array(
            [self.IMAGE_MAX_DIM, self.IMAGE_MAX_DIM, 3])

        self.BACKBONE_SHAPES = np.array(
            [[int(math.ceil(self.IMAGE_SHAPE[0] / stride)),
              int(math.ceil(self.IMAGE_SHAPE[1] / stride))]
             for stride in self.BACKBONE_STRIDES])

    def display(self):
        print("\nConfigurations:")
        for a in dir(self):
            if not a.startswith("__") and not callable(getattr(self, a)):
                print("{:30} {}".format(a, getattr(self, a)))
        print("\n")

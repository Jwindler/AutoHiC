#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: test.py
@time: 2022/3/16 下午10:51
@function:
"""


import cv2 as cv
from matplotlib import pyplot as plt
import numpy as np

img_path = "./images/HiC2.png"
img = cv.imread(img_path)

cv.imshow('a', img)
cv.waitKey(0)
cv.destroyAllWindows()
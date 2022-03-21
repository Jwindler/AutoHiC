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
import numpy as np
from matplotlib import pyplot as plt
img = cv.imread('./images/HiC2.png', 0)
lower_reso = cv.pyrDown(img)
plt.imshow(lower_reso)
plt.show()
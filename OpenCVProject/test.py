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
img = cv.imread('./images/hic.png', 0)
blur = cv.bilateralFilter(img,9,75,75)
plt.subplot(121),plt.imshow(img),plt.title('Original')
plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(blur),plt.title('Blurred')
plt.xticks([]), plt.yticks([])
plt.show()
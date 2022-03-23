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
from scipy import ndimage

img = cv.imread('./images/HiC2.png', 0)

kernel_3x3 = np.array([[-1, -1, -1],
                      [-1, 8, -1],
                      [-1, -1, -1]])

kernel_5x5 = np.array([[-1, -1, -1, -1, -1],
                      [-1, 1, 2, 1, -1],
                      [-1, 2, 4, 2, -1],
                      [-1, 1, 2, 1, -1],
                      [-1, -1, -1, -1, -1]])

k3 = ndimage.convolve(img, kernel_3x3)
k5 = ndimage.convolve(img, kernel_5x5)

blurred = cv.GaussianBlur(img, (11, 11), 0)
g_hpf = img - blurred

plt.subplot(131); plt.imshow(k3); plt.title('k3')
plt.subplot(132); plt.imshow(k5); plt.title('k4')
plt.subplot(133); plt.imshow(g_hpf); plt.title('g_hpf')
plt.show()
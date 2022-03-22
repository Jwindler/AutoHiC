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
imput_img = './images/HiC2.png'

ori = cv.imread(imput_img)
image = cv.imread(imput_img)
gray = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
gray = np.float32(gray)
dst = cv.cornerHarris(gray,2,3,0.04)
dst = cv.dilate(dst,None)
image[dst>0.01*dst.max()]=[0,0,255]
cv.imshow('Original',ori)
cv.imshow('Harris',image)
if cv.waitKey(0) & 0xff == 27:
    cv.destroyAllWindows()
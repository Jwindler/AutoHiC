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

img1 = cv.imread('./images/hic.png')

e1 = cv.getTickCount()

for i in range(5,49,2):
    img1 = cv.medianBlur(img1,i)

e2 = cv.getTickCount()
t = (e2 - e1)/cv.getTickFrequency()
print( t )
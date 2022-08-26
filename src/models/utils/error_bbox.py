#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: error_bbox.py
@time: 6/23/22 5:35 PM
@function: 根据目标检测模型的结果，获取错误的染色体位置
"""


result = inference_detector(model, img)


img_size = (1440, 1440)

# Straw 的 b
img_chr_a_s = 0
img_chr_a_e = 1000


# Straw 的 a
img_chr_b_s = 0
img_chr_b_e = 1000

img_chr_w = img_chr_a_e - img_chr_a_s
img_chr_h = img_chr_b_e - img_chr_b_s

w_ration = img_chr_w / img_size[0]
h_ration = img_chr_h / img_size[1]

error = {}  # a_s, a_e, b_s, b_e


for index, value in enumerate(result[0][0]):

    x, y, w, h, s = value
    # probability filter
    if s >= 0.9:
        a_s = x * w_ration + img_chr_a_s
        a_e = w * w_ration + img_chr_a_s
        b_s = y * h_ration + img_chr_b_s
        b_e = h * h_ration + img_chr_b_s
        error[index] = [a_s, a_e, b_s, b_e, s]
    else:
        continue


def main():
    pass


if __name__ == "__main__":
    main()

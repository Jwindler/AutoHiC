#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: error_locate.py
@time: 6/6/22 10:18 PM
@function: 根据错误检测模型的推断结果，获取错误在染色体上的真实位置
"""


result = inference_detector(model, img)


img_size = (1440, 1440)
img_chr_a_s = 0
img_chr_a_e = 1000
img_chr_b_s = 0
img_chr_b_e = 1000

img_chr_w = img_chr_a_e - img_chr_a_s
img_chr_h = img_chr_b_e - img_chr_b_s

w_ration = img_chr_w / img_size[0]
h_ration = img_chr_h / img_size[1]

error = {}  # a_s, a_e, b_s, b_e

# each num_classes
for i in result:
    # each object
    for index, value in enumerate(i):
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

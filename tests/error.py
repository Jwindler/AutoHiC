#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: error.py
@time: 10/26/22 7:47 PM
@function: 
"""

import json
import numpy as np
import pickle


class ERRORS:
    def __init__(self, classes, info_file, img_size=(1110, 1100)):
        self.info_file = info_file
        self.classes = classes
        self.img_size = img_size
        self.errors, self.counter = dict(), dict()
        self.class_list = []

        for class_ in classes:
            self.counter[class_] = 0
            self.errors[class_] = []

    # TODO: 生成错误结构
    def create_structure(self, img_info, detection_result):

        for category, classes in zip(detection_result[0], self.classes):
            for index, error in enumerate(category):
                error = error.tolist()
                temp_dict = dict()

                self.counter[classes] += 1
                temp_dict["id"] = self.counter[classes]
                temp_dict["image_id"] = list(img_info.keys())[0]
                temp_dict["bbox"] = error[0:4]
                temp_dict["score"] = error[4]
                temp_dict["hic_loci"] = self.bbox2hic(error[0:4], img_info)
                self.errors[classes].append(temp_dict)
        return self.errors

    def bbox2hic(self, bbox, img_info):
        img_size = self.img_size
        key = list(img_info.keys())[0]
        # Straw b chromosome
        img_chr_a_s = img_info[key]["chr_A_start"]
        img_chr_a_e = img_info[key]["chr_A_end"]

        # Straw a chromosome
        img_chr_b_s = img_info[key]["chr_B_start"]
        img_chr_b_e = img_info[key]["chr_B_end"]

        img_chr_w = img_chr_a_e - img_chr_a_s
        img_chr_h = img_chr_b_e - img_chr_b_s

        w_ration = img_chr_w / img_size[0]
        h_ration = img_chr_h / img_size[1]

        x, y, w, h = bbox

        a_s = x * w_ration + img_chr_a_s
        a_e = w * w_ration + img_chr_a_s
        b_s = y * h_ration + img_chr_b_s
        b_e = h * h_ration + img_chr_b_s
        hic_loci = [a_s, a_e, b_s, b_e]

        return hic_loci

    # TODO: 过滤错误，根据score
    def filter_error(self, score: float = 0.9):
        filter_errors = self.errors
        for key in filter_errors:
            filter_errors[key] = list(filter(lambda x: x["score"] > score, filter_errors[key]))

        return filter_errors

    # TODO: 去除同类错误相交错误
    def de_same_overlap(self):
        pass

    # TODO: 去除异类相交错误
    def de_diff_overlap(self):
        pass


def main():
    file = "/home/jzj/Jupyter-Docker/buffer/Axis.pkl"

    with open(file, 'rb') as f:  # 打开文件
        result = pickle.load(f)  # 将二进制文件对象转换成 Python 对象

    img_info = {
        "/root/7.png/png/Aa_inv/2500000/4e93744fcaad4c75936af4f2345db586.jpg": {"genome_id": "Aa_inv",
                                                                                "chr_A": "assembly",
                                                                                "chr_A_start": 230700000,
                                                                                "chr_A_end": 326650000,
                                                                                "chr_B": "assembly",
                                                                                "chr_B_start": 248650000,
                                                                                "chr_B_end": 302750000}}
    classes = ("translocation", "inversion", "debris", "chromosome")
    temp = ERRORS(classes, img_info)
    errors = temp.create_structure(img_info, result)


if __name__ == "__main__":
    main()

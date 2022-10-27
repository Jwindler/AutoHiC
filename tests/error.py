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


class ERROR:
    def __init__(self, model_result, info_file, img_size=(1110, 1100)):
        self.model_result = model_result
        self.info_file = info_file

    # TODO: 生成错误结构
    def create_structure(self):
        pass

    # TODO: 过滤错误，根据score
    def filter_error(self):
        pass

    # TODO: 将错误映射到染色体或hic上， 根据处理错误需要的输入
    def gen_errors(self):
        pass

    # TODO: 去除相交错误
    def de_overlap(self):
        pass


def main():
    pass


if __name__ == "__main__":
    main()

"""
errors_dict
    "info_file": str
    "errors": errors

errors{
    chrs: List
        id: int
        image_id: str
        bbox: List
        score: int
    invs: List
    trans: List
    debris: List
}


"""

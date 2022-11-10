#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: test.py
@time: 9/21/22 5:27 PM
@function: 
"""

import json
from error import ERRORS


def inference_detector(model, img):
    pass


def main():
    # Opening JSON file
    f = open('/home/jzj/Downloads/0_raw.json', )

    # load json file
    result_json = json.load(f)

    classes = ("translocation", "inversion", "debris", "chromosome")
    img_info = ""
    temp = ERRORS(classes, img_info)
    # temp.create_structure(img_info, result_json)
    temp.errors = result_json
    filter_score = temp.filter_all_errors()

    temp.de_diff_overlap(filter_score, iou_score=0.9)

    print("Done")


if __name__ == "__main__":
    main()

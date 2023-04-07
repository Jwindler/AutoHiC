#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: cal_error_metrics.py
@time: 4/2/23 3:00 PM
@function: 
"""
import json


def loci_zoom(errors_json_file):
    with open(errors_json_file, "r") as f:
        errors_dict = json.load(f)
    error_full_len = 0

    for error in errors_dict:
        error_full_len += errors_dict[error]["end"] - errors_dict[error]["start"]

    return error_full_len


def main():
    error_json = "/home/jzj/Jupyter-Docker/buffer/ci_autohic/ci_0/debris_error.json"
    print(loci_zoom(error_json))


if __name__ == "__main__":
    main()

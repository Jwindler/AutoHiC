#!/usr/scripts/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: JsonTransform.py
@time: 2022/4/18 下午8:34
@function:
"""

import glob
import os


class TransformJson:
    def __init__(self, json_path="./", save_path="./"):
        self.json_path = json_path
        self.save_path = save_path

    def __call__(self):
        self.execute()

    def execute(self):
        json_files = glob.glob(f'{self.json_path}*.json')
        for json_file in json_files:
            command = "/home/jzj/.local/scripts/labelme_json_to_dataset " + json_file
            os.system(command)

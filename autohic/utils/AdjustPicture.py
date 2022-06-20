#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: AdjustPicture.py
@time: 2022/4/18 下午6:00
@function: 
"""

import os
import glob
import subprocess

class PictureAdjust:
    """
    一键移动数据，生成MaskRCNN需要训练的数据结构
    # /home/jzj/Auto-HiC/HiC-Api/test/png 为训练图片的文件夹
    t = AdjustPicture.PictureAdjust("/home/jzj/Auto-HiC/HiC-Api/test/png")
    t()
    """
    def __init__(self, json_path):
        self.json_path = json_path

    def __call__(self):
        self.execute()

    def execute(self):
        if self.json_path.endswith("/") is False:
            self.json_path += "/"
        temp_path = os.path.abspath(os.path.join(self.json_path, "../.."))

        jsons_folder = os.path.join(temp_path, "json")
        labelme_json = os.path.join(temp_path, "labelme_json")
        cv2_mask = os.path.join(temp_path, "cv2_mask")
        # 创建文件夹
        os.makedirs(jsons_folder)
        os.makedirs(labelme_json)
        os.makedirs(cv2_mask)

        # 移动json文件路径
        json_paths = glob.glob(f'{self.json_path}*.json')
        json_paths.insert(0, "mv")
        json_paths.append(jsons_folder)
        subprocess.run(json_paths)

        # 移动_json文件夹
        _json_paths = glob.glob(f'{self.json_path}*_json')
        _json_paths.insert(0, "mv")
        _json_paths.append(labelme_json)
        subprocess.run(_json_paths)


        # 移动cv2_mask文件
        cv2_mask_paths = glob.glob(f'{labelme_json}/*_json')
        for cv2_mask_path in cv2_mask_paths:
            basename = os.path.basename(cv2_mask_path).rstrip("_json")
            command = "mv " + cv2_mask_path + "/label.png " + cv2_mask + "/" +  basename + ".png"
            os.system(command)
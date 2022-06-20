#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: PixelTransform.py
@time: 2022/4/18 下午3:48
@function: 像素转换
"""


import os
import glob
from PIL import Image


class TransformPixel:
    """
    像素转换脚本

    将指定图片文件或者文件夹下的图片转换为指定像素的图片，仅支持PNG | JPEG格式
    Attributes:
        file_dir: 	图片文件或者图片文件夹
        save_dir: 	结果存放位置，默认为输入文件路径
        pixel:  	指定像素大小，默认(1024, 640)
        pic_suffix: 图片文件后缀，默认为PNG（可选JPEG）

    Usage:
        t = test.TransformPixel(file_dir="./test/", save_dir="/home/jzj/buffer/", pixel=(1024, 1024), pic_suffix="JPEG")
        t()

    """

    def __init__(
            self,
            file_dir="./",
            save_dir="./",
            pixel=(
                1024,
                640),
            pic_suffix="PNG"):
        self.file_dir = file_dir
        self.pixel = pixel
        self.save_dir = save_dir
        self.pic_suffix = pic_suffix

    def __call__(self):
        self.execute()

    def execute(self):
        # 传入为目录
        if os.path.isdir(self.file_dir):
            # 判断目录结尾
            if self.file_dir.endswith("/"):
                pass
            else:
                self.file_dir += "/"
            img_paths = glob.glob(f'{self.file_dir}*{self.pic_suffix.lower()}')
        # 传入为文件
        else:
            img_paths = self.file_dir

        def transform(img_path):
            if not isinstance(img_path, str):
                temp_path = img_path[0]
                save_file = os.path.join(
                    os.path.dirname(temp_path), "modify_pic")
                if self.save_dir != "./":
                    save_file = os.path.join(
                        self.save_dir, "modify_pic")
                os.makedirs(save_file)
                for file in img_path:
                    basename = os.path.split(file)[1]
                    save_paths = save_file + "/" + \
                        basename.split(".")[0] + "_modify." + self.pic_suffix.lower()
                    im = Image.open(file)
                    im = im.resize(self.pixel)
                    print(im.format, im.size, im.mode)
                    im.save(save_paths, self.pic_suffix)
            else:
                save_file = os.path.join(
                    os.path.dirname(img_path), "modify_pic")
                if self.save_dir != "./":
                    save_file = os.path.join(
                        self.save_dir, "modify_pic")
                os.makedirs(save_file)

                basename = os.path.split(img_path)[1]
                save_paths = save_file + "/" + \
                    basename.split(".")[0] + "_modify." + self.pic_suffix.lower()
                im = Image.open(img_path)
                im = im.resize(self.pixel)
                print(im.format, im.size, im.mode)
                im.save(save_paths, self.pic_suffix)

        return transform(img_paths)

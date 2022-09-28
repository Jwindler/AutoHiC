#!/usr/scripts/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: ChannelTransform.py
@time: 2022/4/18 下午6:01
@function: 图片通道数转换
"""

from PIL import Image
import os
import cv2
import glob


class OperateError(ValueError):
    pass


class TransformChannel:
    def __init__(self, file, save):
        self.file = file
        self.save = save

        # 添加 "/"
        if str(self.file).endswith("/") is not True:
            self.file += "/"

        if str(self.save).endswith("/") is not True:
            self.save += "/"


    def __call__(self, operate):
        if operate == 3:
            self.fourtothree()
        elif operate == 1:
            self.threetoone()
        else:
            raise OperateError(operate)


    def fourtothree(self):
        imgs_path = glob.glob(f'{self.file}*.png')
        for img_path in imgs_path:  # 打开图片
            img = Image.open(img_path)

            # 打印出原图格式
            print(img.format, img.size, img.mode)

            # 4通道转化为rgb三通道
            img = img.convert("RGB")
            save_path = self.save + \
                os.path.split(img_path)[1].rstrip(".png") + "_3.png"
            img.save(save_path)

    def threetoone(self):
        imgs_path = glob.glob(f'{self.file}*.png')
        for img_path in imgs_path:
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            save_path = self.save + \
                os.path.split(img_path)[1].rstrip(".png") + "_1.png"
            cv2.imwrite(save_path, img)

def main():
    temp = TransformChannel("/home/jzj/buffer/", "/home/jzj/buffer/")
    temp(3)


if __name__ == "__main__":
    main()

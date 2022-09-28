#!/usr/scripts/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: move_type.py
@time: 6/9/22 3:28 PM
@function: 根据bulk_inference推断的结果，将对应的数据移动到相应类型的文件夹
"""

import os
import shutil


class PngTypeMove:
    def __init__(self, png_path, save_path=None, info_path=None):
        self.png_path = png_path
        self.save_path = save_path
        self.info_path = info_path

    def move_png(self):

        # 添加尾部分隔符
        if not self.png_path.endswith("/"):
            self.png_path += "/"

        # 确定默认信息文件
        if self.info_path is None:
            self.info_path = os.path.join(self.png_path, "info_type.txt")

        # 生成目标文件夹
        if self.save_path is None:
            self.save_path = os.path.join(self.png_path, "type")

            file_name = [
                "1.overall",
                "2.local",
                "3.white",
                "4.boundary",
                "5.translocation"]
            for i in file_name:
                temp_file = os.path.join(self.save_path, i)
                try:
                    os.makedirs(temp_file)
                except FileExistsError:
                    continue

        try:
            with open(self.info_path, "r") as f:
                temp_lines = f.readlines()
                for line in temp_lines:
                    temp_line = line.strip().split("    ")
                    source = temp_line[0]  # 原地址
                    # 目的地
                    destination = temp_line[1]

                    destination = os.path.join(self.save_path, destination)
                    # 移动
                    shutil.move(source, destination)

            print("Done")

        except FileNotFoundError:
            print("文件不存在")


def main():
    png_path = "/home/jzj/Jupyter-Docker/datasets/error_classify/Np-one2one"

    temp = PngTypeMove(png_path)
    temp.move_png()


if __name__ == "__main__":
    main()

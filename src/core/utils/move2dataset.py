#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: move2dataset.py
@time: 6/16/22 10:22 AM
@function: 将推断后分类好的数据集，移动到新数据集中
"""


import os
import shutil
import glob

from src.core.utils.logger import LoggerHandler


class PngTypeMove:
    logger = LoggerHandler()

    def __init__(self, png_path, save_path):
        self.png_path = png_path
        self.save_path = save_path

    def move_png(self):
        self.logger.info("Start to move png...")

        if isinstance(self.png_path, list):  # 如果是列表，则需要遍历
            for one_png_path in self.png_path:
                self.logger.info("Start to move file: {}".format(one_png_path))

                one_png_path = os.path.join(one_png_path, "type")

                for folder in os.listdir(one_png_path):
                    source = os.path.join(one_png_path, folder)  # 原地址
                    destination = os.path.join(self.save_path, folder)  # 目的地
                    src_file_list = glob.glob(source + '/*')
                    for src_file in src_file_list:
                        try:
                            # 移动
                            shutil.move(src_file, destination)
                        except shutil.Error:  # 如果文件已经存在，则修改名称
                            temp = os.path.split(src_file)[-1]  # 取文件名
                            folder_name = one_png_path.split("/")[-2]
                            temp_name = folder_name + "_" + temp
                            destination = os.path.join(destination, temp_name)
                            # 移动
                            shutil.move(src_file, destination)
                self.logger.info("Move file: {} done!".format(one_png_path))
        else:

            one_png_path = os.path.join(self.png_path, "type")
            self.logger.info("Start to move file: {}".format(one_png_path))
            for folder in os.listdir(one_png_path):
                source = os.path.join(one_png_path, folder)  # 原地址
                destination = os.path.join(self.save_path, folder)  # 目的地
                src_file_list = glob.glob(source + '*')
                for src_file in src_file_list:
                    try:
                        # 移动
                        shutil.move(src_file, destination)
                    except shutil.Error:  # 如果文件已经存在，则修改名称
                        temp = os.path.split(src_file)[-1]  # 取文件名
                        folder_name = one_png_path.split("/")[-2]
                        temp_name = folder_name + "_" + temp
                        destination = os.path.join(destination, temp_name)
                        # 移动
                        shutil.move(src_file, destination)

            self.logger.info("Move file: {} done!".format(one_png_path))
        self.logger.info("All Files Done")


def main():
    temp = PngTypeMove(
        [
            "/home/jzj/Jupyter-Docker/datasets/error_classify/GSE71831",
            "/home/jzj/Jupyter-Docker/datasets/error_classify/GSM1551550",
            "/home/jzj/Jupyter-Docker/datasets/error_classify/GSM3734952",
            "/home/jzj/Jupyter-Docker/datasets/error_classify/Ls-0",
            "/home/jzj/Jupyter-Docker/datasets/error_classify/Ls-1",
            "/home/jzj/Jupyter-Docker/datasets/error_classify/Ls-2",
            "/home/jzj/Jupyter-Docker/datasets/error_classify/Np-one2one",
            "/home/jzj/Jupyter-Docker/datasets/error_classify/Hv-test"],
        "/home/jzj/Jupyter-Docker/datasets/error_classify/train-4")
    temp.move_png()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: random_copy_file.py
@time: 10/24/22 4:34 PM
@function: 
"""

import os
import shutil


def copy_file(file_dir, train_dir):
    path_dir = os.listdir(file_dir)
    file_number = len(path_dir)  # 统计文件夹下文件个数
    rate = 0.1  # 抽取比例
    pick_number = int(file_number * rate)  # 按照rate比例从文件夹中取一定数量的文件
    # samples = random.sample(path_dir, pick_number)  # 随机选取picknumber数量的样本
    samples = path_dir[pick_number * 9:]
    for sample in samples:
        # Source path
        source = os.path.join(file_dir, sample)

        # Destination path
        destination = os.path.join(train_dir, sample)

        shutil.copy(source, destination)


def main():
    # 文件的原始路径
    file_dir = '/home/jzj/Data/Test/inv/2.inversion'

    # 移动到新的文件夹路径
    train_dir = '/home/jzj/buffer/10'

    copy_file(file_dir, train_dir)


if __name__ == '__main__':
    main()

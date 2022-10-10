#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: make_asy.py
@time: 10/10/22 10:52 AM
@function: construct data set（构造数据集）
"""
import random
from src.assembly.asy_operate import AssemblyOperate


def random_color(maxcolor: int = 6000) -> int:
    """
    随机生成色阈值
    Args:
        maxcolor: 随机色阈最大值

    Returns:
        色阈最大值

    """

    return random.randrange(maxcolor)


def make_inv(asy_file: str, out_file_path: str, random_p: "0 < float < 1" = 0.6) -> None:
    # 获取原始信息
    asy_operate = AssemblyOperate(asy_file, ratio=None)
    ctgs, ctgs_orders = asy_operate._get_ctgs_orders(asy_file)
    ays_info = asy_operate.get_info()

    order_list = [x for x in range(1, int(ays_info["ctg_number"]) + 1)]

    # 生成随机反转列表
    random_inv_list = random.sample(order_list, int(len(order_list) * random_p))

    with open(out_file_path, "w") as f:

        # 写入ctg信息
        for key, value in ctgs.items():
            f.write(key + " " + value["order"] + " " + value["length"] + "\n")

        # 写入新的ctg顺序
        for ctgs_order in ctgs_orders:
            temp_write_list = []
            for x in ctgs_order:
                # 跟新需要切割的ctg顺序
                if abs(int(x)) in random_inv_list:
                    if int(x) > 0:
                        temp_write_list.append(str(-int(x)))
                    else:  # 反向
                        temp_write_list.append(str(abs(int(x))))
                else:
                    temp_write_list.append(x)
            f.write(" ".join(temp_write_list) + "\n")


def make_tran(asy_file: str, out_file_path: str, random_p: "0 < float < 1" = 0.6) -> None:
    # 获取原始信息
    asy_operate = AssemblyOperate(asy_file, ratio=None)
    ctgs, ctgs_orders = asy_operate._get_ctgs_orders(asy_file)
    ays_info = asy_operate.get_info()

    # 抽样数据集
    order_list = [x for x in range(1, int(ays_info["ctg_number"]) + 1)]

    # 随机抽取易位ctg的序号
    random_inv_list = random.sample(order_list, int(len(order_list) * random_p))

    with open(out_file_path, "w") as f:

        # 写入ctg信息
        for key, value in ctgs.items():
            f.write(key + " " + value["order"] + " " + value["length"] + "\n")

        # 写入新的ctg顺序
        for ctgs_order in ctgs_orders:
            temp_write_list = []
            for x in ctgs_order:
                # 跟新需要切割的ctg顺序
                if abs(int(x)) in random_inv_list:
                    if int(x) > 0:
                        temp_write_list.append(str(-int(x)))
                    else:  # 反向
                        temp_write_list.append(str(abs(int(x))))
                else:
                    temp_write_list.append(x)
            f.write(" ".join(temp_write_list) + "\n")


def make_asy(asy_file: str, out_file_path: str, random_p: "0 < float < 1" = 0.6) -> None:
    print(random_p)


def main():
    make_asy("/home/jzj/buffer/Np.0.assembly", "/home/jzj/buffer/Np_tran.assembly", 0.6)


if __name__ == "__main__":
    main()

#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: make_asy.py
@time: 10/10/22 10:52 AM
@function: construct data set（构造数据集）
"""
import random
from src.assembly.asy_operate import AssemblyOperate


def random_color(maxcolor: int = 6000) -> int:
    """
        get random color threshold
    Args:
        maxcolor: color threshold max value

    Returns:
        random color threshold
    """

    return random.randrange(1, maxcolor)


def make_inv(asy_file: str, out_file_path: str, random_p: "0 < float < 1" = 0.6) -> None:
    """
        generate inversion data set
    Args:
        asy_file: assembly file path
        out_file_path: output file path
        random_p: inversion random probability

    Returns:

    """

    # get original information
    asy_operate = AssemblyOperate(asy_file, ratio=None)
    ctgs, ctgs_orders = asy_operate._get_ctgs_orders(asy_file)
    ays_info = asy_operate.get_info()

    order_list = [x for x in range(1, int(ays_info["ctg_number"]) + 1)]

    # generate random inversion list
    random_inv_list = random.sample(order_list, int(len(order_list) * random_p))

    with open(out_file_path, "w") as f:

        # write ctg information
        for key, value in ctgs.items():
            f.write(key + " " + value["order"] + " " + value["length"] + "\n")

        # write new ctg order
        for ctgs_order in ctgs_orders:
            temp_write_list = []
            for x in ctgs_order:
                # update ctg order which need to be cut
                if abs(int(x)) in random_inv_list:
                    if int(x) > 0:
                        temp_write_list.append(str(-int(x)))
                    else:  # opposite direction
                        temp_write_list.append(str(abs(int(x))))
                else:
                    temp_write_list.append(x)
            f.write(" ".join(temp_write_list) + "\n")


def make_tran(asy_file: str, out_file_path: str, random_p: "0 < float < 1" = 0.6) -> None:
    """
        generate translocation data set
    Args:
        asy_file: assembly file path
        out_file_path: output file path
        random_p: translocation random probability

    Returns:

    """

    # get original information
    asy_operate = AssemblyOperate(asy_file, ratio=None)
    ctgs, ctgs_orders = asy_operate._get_ctgs_orders(asy_file)
    ays_info = asy_operate.get_info()

    # generate ctg order list
    order_list = [x for x in range(1, int(ays_info["ctg_number"]) + 1)]

    # generate random translocation list
    random_list = random.sample(order_list, int(len(order_list) * random_p))

    tran_list = random_list[:int(len(random_list) * 0.5)]
    insert_list = random_list[int(len(random_list) * 0.5):]
    tran_dict = {stocks: prices for stocks, prices in zip(tran_list, insert_list)}

    with open(out_file_path, "w") as f:

        # write ctg information
        for key, value in ctgs.items():
            f.write(key + " " + value["order"] + " " + value["length"] + "\n")

        # write new ctg order
        for ctgs_order in ctgs_orders:
            temp_write_list = []
            for x in ctgs_order:
                # update ctg order which need to be cut
                if abs(int(x)) in tran_dict:
                    temp_write_list.append(x)
                    temp_write_list.append(str(tran_dict[abs(int(x))]))
                elif abs(int(x)) in insert_list:
                    continue
                else:
                    temp_write_list.append(x)
            f.write(" ".join(temp_write_list) + "\n")


def make_double(asy_file: str, out_file_path: str, random_p: "0 < float < 1" = 0.6) -> None:
    """
        generate inversion and translocation data set
    Args:
        asy_file: assembly file path
        out_file_path: output file path
        random_p: inversion and translocation random probability

    Returns:

    """
    make_tran(asy_file, out_file_path, random_p)
    make_inv(out_file_path, out_file_path, random_p)


def main():
    make_inv("/home/jzj/buffer/Np_tran.assembly", "/home/jzj/buffer/Np_double.assembly", 0.6)


if __name__ == "__main__":
    main()

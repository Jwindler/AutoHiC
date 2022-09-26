#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: get_ctg_order.py
@time: 7/24/22 1:11 PM
@function: 根据ctg_name获取ctg的序号,带方向
"""


def get_ctg_order(assembly_path, ctg_name):
    ctg_order = []

    with open(assembly_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith(">"):
                temp_line = line.strip().split(" ")
                if temp_line[0] == ctg_name:
                    temp_result = temp_line[1]
            else:
                for i in line.strip().split(" "):
                    if abs(int(i)) == int(temp_result):
                        return i

    return ctg_order


def main():
    assembly_path = "/tests/Np.0.assembly"
    ctg_name = ">utg20393"
    temp_result = get_ctg_order(assembly_path, ctg_name)
    print(temp_result)


if __name__ == "__main__":
    main()

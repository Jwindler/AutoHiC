#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: asy_operate.py
@time: 8/18/22 4:14 PM
@function:
"""

from collections import OrderedDict
import json


class AssemblyOperate(object):
    def __init__(self, assembly_file_path):
        self.assembly_file_path = assembly_file_path

    def get_info(self) -> json:
        """
        获取assembly文件的信息
        :return: assembly整体信息（json格式）
        """

        ctg_number = 0  # ctg数量
        seqs_length = 0  # 总长度

        # 获取ctg数量和总长度
        with open(self.assembly_file_path, "r") as f:
            for line in f:
                if line.startswith(">"):
                    ctg_number += 1

                    # 获取ctg长度
                    seq_length = line.strip().split()[2]
                    seqs_length += int(seq_length)

        assembly_info = {
            "assembly_file": self.assembly_file_path,
            "ctg_number": ctg_number,
            "seq_length": seqs_length
        }

        return assembly_info

    def get_ctg_info(self, ctg_name=None, ctg_order=None) -> json:
        """
        通过ctg名字 或者 序号，获取assembly文件中指定ctg的信息
        :return: ctg信息（json格式）默认ctg_name
        """
        if ctg_name is None and ctg_order is None:
            raise ValueError("ctg_name or ctg_order must be specified")

        ctgs_infos = {}  # ctg信息
        ctgs_orders = []  # ctg序号

        # 获取基本信息
        with open(self.assembly_file_path, "r") as f:
            for line in f:
                if line.startswith(">"):
                    temp_line = line.strip().split()
                    ctgs_infos[temp_line[1]] = {
                        "ctg_name": temp_line[0],
                        "length": temp_line[2]
                    }
                else:
                    for order in line.strip("\n").split(" "):
                        try:
                            ctgs_orders.append(int(order))
                        except ValueError:  # 如果是空的，则跳过
                            print("Warning: order is not int, please check assembly file")

        # 统计ctg的总长度
        ctg_length = 1

        ctg_by_name = {}  # ctg名字字典
        ctg_by_order = {}  # ctg序号字典

        # 格式化信息
        for ctgs_order in ctgs_orders:
            abs_ctgs_order = abs(ctgs_order)
            ctg_by_name[ctgs_infos[str(abs_ctgs_order)]["ctg_name"]] = {
                "ctg_name": ctgs_infos[str(abs_ctgs_order)]["ctg_name"],
                "ctg_order": ctgs_order,
                "ctg_length": ctgs_infos[str(abs_ctgs_order)]["length"],
                "site": (ctg_length, ctg_length - 1 + int(ctgs_infos[str(abs_ctgs_order)]["length"]))
            }

            ctg_by_order[abs_ctgs_order] = {
                "ctg_name": ctgs_infos[str(abs_ctgs_order)]["ctg_name"],
                "ctg_order": ctgs_order,
                "ctg_length": ctgs_infos[str(abs_ctgs_order)]["length"],
                "site": (ctg_length, ctg_length - 1 + int(ctgs_infos[str(abs_ctgs_order)]["length"]))
            }

            ctg_length += int(ctgs_infos[str(abs_ctgs_order)]["length"])

        if ctg_name is not None:
            if ctg_name.startswith(">") is False:
                ctg_name = ">" + ctg_name

            return ctg_by_name[ctg_name]
        else:
            return ctg_by_order[ctg_order]

    @staticmethod
    def _get_ctgs_orders(assembly_file_path):
        """
        获取assembly 文件中的信息
        :return:
        """
        ctgs = OrderedDict()  # ctgs信息
        ctgs_orders = []  # ctgs序号

        # 获取ctg数量和总长度
        with open(assembly_file_path, "r") as f:
            for line in f:
                if line.startswith(">"):
                    temp_line = line.strip().split()
                    ctgs[temp_line[0]] = {
                        "order": temp_line[1],
                        "length": temp_line[2]
                    }
                else:
                    temp_line = line.strip().split(" ")
                    ctgs_orders.append(temp_line)
        return ctgs, ctgs_orders

    def cut_ctgs(self, cut_ctg, out_file_path):
        """
        切割指定的ctgs
        :param cut_ctg: 需要剪切的ctgs（"ctg_name": cut_site）
        :param out_file_path: 修改后存放路径
        :return: None
        """

        # 获取原始ctgs信息
        ctgs, ctgs_orders = self._get_ctgs_orders(self.assembly_file_path)

        # 声明变量（以防后续提醒）
        cut_ctg_name = None
        cut_ctg_site = None

        # 获取需要剪切的ctg信息
        for key, values in cut_ctg.items():
            cut_ctg_name = key
            cut_ctg_site = values

        # 计算剪切的ctg的新信息
        cut_ctg_info = self.get_ctg_info(ctg_name=cut_ctg_name)

        # 获取cut_ctg的顺序（正:True, 负:False）
        cut_ctg_order = cut_ctg_info["ctg_order"]

        # 计算切割的起始位置和结束位置
        cut_ctg_site1 = cut_ctg_site - cut_ctg_info["site"][0]
        cut_ctg_site2 = cut_ctg_info["site"][1] - cut_ctg_site + 1

        with open(out_file_path, "w") as f:

            # 写入新的ctg信息
            for key, value in ctgs.items():
                if key == cut_ctg_name:
                    # ctg正负 对于切割长度的影响
                    if cut_ctg_order > 0:
                        f.write(key + ":::fragment_1 " + value["order"] + " " + str(cut_ctg_site1) + "\n")
                        temp_order = int(value["order"]) + 1
                        f.write(key + ":::fragment_2" + " " + str(temp_order) + " " + str(cut_ctg_site2) + "\n")
                    else:
                        f.write(key + ":::fragment_1 " + value["order"] + " " + str(cut_ctg_site2) + "\n")
                        temp_order = int(value["order"]) + 1
                        f.write(key + ":::fragment_2" + " " + str(temp_order) + " " + str(cut_ctg_site1) + "\n")
                else:
                    # 一分为二后，后续序号+
                    if int(value["order"]) > abs(cut_ctg_order):
                        temp_order = int(value["order"]) + 1
                        f.write(key + " " + str(temp_order) + " " + value["length"] + "\n")
                    else:
                        f.write(key + " " + value["order"] + " " + value["length"] + "\n")

            # 写入新的ctg顺序
            for ctgs_order in ctgs_orders:
                temp_write_list = []
                for x in ctgs_order:
                    # 跟新需要切割的ctg顺序
                    if int(x) == cut_ctg_order:
                        if cut_ctg_order > 0:
                            temp = cut_ctg_order + 1
                            temp_write_list.append(str(cut_ctg_order))
                            temp_write_list.append(str(temp))
                        else:  # 反向
                            temp = cut_ctg_order - 1
                            temp_write_list.append(str(temp))
                            temp_write_list.append(str(cut_ctg_order))
                    else:  # 其余ctg + 1
                        if abs(int(x)) > abs(cut_ctg_order):
                            if int(x) > 0:
                                temp = int(x) + 1
                                temp_write_list.append(str(temp))
                            else:
                                temp = int(x) - 1
                                temp_write_list.append(str(temp))
                        else:
                            temp_write_list.append(str(x))
                f.write(" ".join(temp_write_list) + "\n")

    def move_ctgs(self, assembly_file_path, move_ctg, insert_ctg, out_file_path, direction="left"):
        """
        移动指定ctgs
        :param assembly_file_path: 原始assembly文件路径
        :param move_ctg: 需要移动的ctgs List
        :param insert_ctg: 需要插入的ctg
        :param out_file_path: 输出路径
        :param direction: 插入方向（left:左插入，right:右插入），默认插入在左边
        :return: out_file_path
        """

        self.assembly_file_path = assembly_file_path

        # 获取ctgs 序号信息
        ctgs, ctgs_orders = AssemblyOperate._get_ctgs_orders(assembly_file_path)

        # 获取需要移动的ctg的order
        move_ctg_orders = []
        for ctg in move_ctg:
            get_ctg_info = self.get_ctg_info(ctg_name=ctg)
            get_ctg_info_order = get_ctg_info["ctg_order"]
            move_ctg_orders.append(str(get_ctg_info_order))

        # 获取需要插入的ctg的order
        insert_ctg_order = self.get_ctg_info(ctg_name=insert_ctg)["ctg_order"]

        # 声明变量， 存储插入位置的index
        insert_ctg_order_index = None

        # 修改ctg顺序
        for move_ctg_order in move_ctg_orders:
            for index in range(len(ctgs_orders)):
                # 删除需要移动的ctg的原始位置
                if move_ctg_order in ctgs_orders[index]:
                    ctgs_orders[index].remove(move_ctg_order)

                # 获取插入位置的index
                if str(insert_ctg_order) in ctgs_orders[index]:
                    insert_ctg_order_index = (index, ctgs_orders[index].index(str(insert_ctg_order)))

        # 插入需要移动的ctg
        if direction == "left":  # 左插入
            move_ctg_orders.reverse()
            for move_ctg_order in move_ctg_orders:
                ctgs_orders[insert_ctg_order_index[0]].insert(insert_ctg_order_index[1], move_ctg_order)
        else:  # 右插入
            move_ctg_orders.reverse()
            for move_ctg_order in move_ctg_orders:
                ctgs_orders[insert_ctg_order_index[0]].insert(insert_ctg_order_index[1] + 1, move_ctg_order)

        # 写入新文件
        with open(out_file_path, "w") as f:
            # 写入新的ctg信息
            for key, value in ctgs.items():
                f.write(key + " " + value["order"] + " " + value["length"] + "\n")

            # 写入新的ctg顺序
            for ctgs_order in ctgs_orders:
                temp_write_list = []
                for x in ctgs_order:
                    temp_write_list.append(str(x))
                f.write(" ".join(temp_write_list) + "\n")

    # TODO: 实现将一个ctg切割为三个ctg，可以调用两次cut_ctgs
    def cut_ctg_to3(self):
        pass


def main():
    # 实例化Assembly类
    temp = AssemblyOperate("/home/jzj/Auto-HiC/HiC-API/tests/Np.0.assembly")

    # 测试获取整体信息
    # print(json.dumps(temp.get_info(), indent=4))

    # 测试获取指定ctg信息
    # assembly_info = temp.get_ctg_info(ctg_name="utg832")
    # assembly_info = temp.get_ctg_info(ctg_order=1335)
    # print(json.dumps(assembly_info, indent=4))

    # 测试切割指定ctg
    # out_file_path = "/home/jzj/buffer/cut_Np.0.assembly"
    # cut_ctgs = {
    #     ">utg832": 990375001}
    # temp.cut_ctgs(cut_ctgs, out_file_path)

    # 测试移动指定ctg
    assembly_file_path = "/home/jzj/buffer/cut_Np.0.assembly"
    out_file_path = "/home/jzj/buffer/move_Np.0.assembly"
    move_ctgs = [">utg832:::fragment_1", ">utg2240", ">utg4279"]
    insert_ctg = ">utg4426"
    temp.move_ctgs(assembly_file_path, move_ctgs, insert_ctg, out_file_path, direction="left")


if __name__ == "__main__":
    main()

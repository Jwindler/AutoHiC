#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: asy_operate.py
@time: 8/18/22 4:14 PM
@function:
"""

import json
from collections import OrderedDict

from src.auto_hic.utils.logger import LoggerHandler


class AssemblyOperate(object):
    # 初始化日志
    logger = LoggerHandler()

    def __init__(self, assembly_file_path, ratio):
        # 初始化assembly文件路径
        self.assembly_file_path = assembly_file_path
        self.ratio = ratio  # assembly与hic的比例

    def get_info(self, new_asy_file=None) -> json:
        """
        获取assembly文件的基本信息
        :param new_asy_file: 新的assembly文件路径
        :return:
        """

        ctg_number = 0  # ctg数量
        seqs_length = 0  # 总长度

        # 传入新的assembly文件路径
        if new_asy_file is not None:
            # 更新文件路径
            self.assembly_file_path = new_asy_file

        # 获取 ctg数量 和 总长度
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

    def get_ctg_info(self, ctg_name=None, ctg_order=None, new_asy_file=None) -> json:
        """
        通过ctg名字 或者 序号，获取assembly文件中指定ctg的信息
        :param ctg_name: ctg名字
        :param ctg_order: ctg序号
        :param new_asy_file: 新的assembly文件路径
        :return: ctg信息（json格式）默认ctg_name
        """

        # 未传入查询字段
        if ctg_name is None and ctg_order is None:
            self.logger.error("未传入查询字段 \n")
            raise ValueError("ctg_name or ctg_order must be specified")

        ctgs_infos = {}  # ctg信息
        ctgs_orders = []  # ctg序号

        # 传入新的assembly文件路径
        if new_asy_file is not None:
            self.assembly_file_path = new_asy_file

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

    def cut_ctgs(self, assembly_file_path, cut_ctg, out_file_path):
        """
        切割指定的ctgs
        :param assembly_file_path: 原始assembly文件路径
        :param cut_ctg: 需要剪切的ctgs（"ctg_name": cut_site）
        :param out_file_path: 修改后存放路径
        :return: None
        """

        # 获取原始ctgs信息
        ctgs, ctgs_orders = self._get_ctgs_orders(assembly_file_path)

        # 声明变量（以防后续提醒）
        cut_ctg_name = None
        cut_ctg_site = None

        # 获取需要剪切的ctg信息
        for key, values in cut_ctg.items():
            cut_ctg_name = key
            cut_ctg_site = values

        # 计算剪切的ctg的新信息
        cut_ctg_info = self.get_ctg_info(ctg_name=cut_ctg_name, new_asy_file=assembly_file_path)

        # 获取cut_ctg的顺序（正:True, 负:False）
        cut_ctg_order = cut_ctg_info["ctg_order"]

        # 计算切割的起始位置和结束位置
        cut_ctg_site1 = cut_ctg_site - cut_ctg_info["site"][0] + 1
        cut_ctg_site2 = cut_ctg_info["site"][1] - cut_ctg_site

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

    def move_ctgs(self, assembly_file_path, error_info, out_file_path):
        """
        对易位错误进行移动
        :param assembly_file_path: 需要调整的assembly文件路径
        :param error_info: 易位错误信息
        :param out_file_path: 保存路径
        :return: None
        """

        self.assembly_file_path = assembly_file_path

        # 获取ctgs 序号信息
        ctgs, ctgs_orders = AssemblyOperate._get_ctgs_orders(assembly_file_path)

        for error in error_info:
            # 需要移动的ctg_name
            move_ctg = list(error_info[error]["move_ctgs"].keys())

            # 获取需要移动的ctg的order
            move_ctg_orders = []
            for ctg in move_ctg:
                get_ctg_info = self.get_ctg_info(ctg_name=ctg, new_asy_file=assembly_file_path)
                get_ctg_info_order = get_ctg_info["ctg_order"]
                move_ctg_orders.append(str(get_ctg_info_order))

            # 获取需要插入的ctg的order
            insert_ctg = list(error_info[error]["insert_site"].keys())[0]
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
            direction = error_info[error]["direction"]  # 插入方向
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

    def find_site_ctgs(self, assembly_file_path, start, end):
        """
        根据start,end 返回该区域所包含的contig
        :param start:    hic file 查询起始坐标
        :param end:      hic file 查询终止坐标
        :param assembly_file_path: assembly文件路径
        :return: 位点内contig信息
        """

        contain_contig = OrderedDict()  # 位点内contig信息

        contig_info = {}  # contig 信息{order: {name, length}}

        contig_order = []  # contig 顺序信息列表

        # 基因组上真实的位置信息
        genome_start = start * self.ratio
        genome_end = end * self.ratio

        self.logger.info("查询真实位点为 ： {0} - {1} \n".format(genome_start, genome_end))

        self.logger.info("该区域包含的contig : ")

        with open(assembly_file_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                # contig :name : order, length
                if line.startswith(">"):
                    each_line = line.strip().split()
                    contig_info[each_line[1].strip(">")] = {
                        "name": each_line[0],
                        "length": each_line[2]
                    }
                # contig 顺序
                else:
                    contig_order.append(line.strip().split())

            # 二维降一维
            contig_order = [order for st in contig_order for order in st]

        # 寻找contig
        temp_len_s = 0  # 记录当前contig的起始位置
        temp_len_e = 0  # 记录当前contig的终止位置

        for i in contig_order:  # 循环contig

            if i.startswith("-"):  # 反向contig
                i = i[1:]
                temp_len_s = temp_len_e
                temp_len_e += int(contig_info[i]["length"])
            else:
                temp_len_s = temp_len_e
                temp_len_e += int(contig_info[i]["length"])

            # 解冗余
            def callback():
                contain_contig[contig_info[i]["name"]] = {
                    "length": contig_info[i]["length"],
                    "start": temp_len_s,
                    "end": temp_len_e
                }
                return temp_len_e

            # 各个contig与查询位点之间的关系（主要有四种，可以参考两条线段之间的关系）
            if temp_len_s <= genome_start:
                if genome_start < temp_len_e < genome_end:
                    callback()
                elif temp_len_e > genome_end:
                    callback()
            elif temp_len_s > genome_start:
                if temp_len_e <= genome_end:
                    callback()
                elif temp_len_s < genome_end < temp_len_e:
                    callback()

        # json格式输出
        contain_contig = json.dumps(
            contain_contig,
            indent=4,
            separators=(
                ',',
                ': '))
        self.logger.info(contain_contig)

        return contain_contig

    def cut_ctg_to_3(self, assembly_file_path, cut_ctg_name, site_1, site_2, out_file_path):
        """
        将contig切割为3个
        :param assembly_file_path:
        :param cut_ctg_name:
        :param site_1:
        :param site_2:
        :param out_file_path:
        :return:
        """
        if cut_ctg_name.startswith(">") is False:
            cut_ctg_name = ">" + cut_ctg_name

        # 获取原始ctgs信息
        ctgs, ctgs_orders = self._get_ctgs_orders(assembly_file_path)

        # 计算剪切的ctg的新信息
        cut_ctg_info = self.get_ctg_info(ctg_name=cut_ctg_name, new_asy_file=assembly_file_path)

        # 获取cut_ctg的顺序（正:True, 负:False）
        cut_ctg_order = cut_ctg_info["ctg_order"]

        # 计算切割的起始位置和结束位置
        cut_ctg_site1 = site_1 - cut_ctg_info["site"][0]
        cut_ctg_site2 = site_2 - site_1 + 1
        cut_ctg_site3 = cut_ctg_info["site"][1] - site_2 + 1

        with open(out_file_path, "w") as f:
            # 写入新的ctg信息
            for key, value in ctgs.items():
                if key == cut_ctg_name:
                    # ctg正负 对于切割长度的影响
                    if cut_ctg_order > 0:
                        f.write(key + ":::fragment_1 " + value["order"] + " " + str(cut_ctg_site1) + "\n")
                        temp_order = int(value["order"]) + 1
                        f.write(key + ":::fragment_2" + " " + str(temp_order) + " " + str(cut_ctg_site2) + "\n")
                        temp_order += 1
                        f.write(key + ":::fragment_3" + " " + str(temp_order) + " " + str(cut_ctg_site3) + "\n")

                    else:
                        f.write(key + ":::fragment_1 " + value["order"] + " " + str(cut_ctg_site3) + "\n")
                        temp_order = int(value["order"]) + 1
                        f.write(key + ":::fragment_2" + " " + str(temp_order) + " " + str(cut_ctg_site2) + "\n")
                        temp_order += 1
                        f.write(key + ":::fragment_3" + " " + str(temp_order) + " " + str(cut_ctg_site1) + "\n")
                else:
                    # 一分为二后，后续序号++
                    if int(value["order"]) > abs(cut_ctg_order):
                        temp_order = int(value["order"]) + 2
                        f.write(key + " " + str(temp_order) + " " + value["length"] + "\n")
                    else:
                        f.write(key + " " + value["order"] + " " + value["length"] + "\n")

            # 写入新的ctg顺序
            for ctgs_order in ctgs_orders:
                temp_write_list = []
                for x in ctgs_order:
                    # 更新新需要切割的ctg顺序
                    if int(x) == cut_ctg_order:
                        if cut_ctg_order > 0:
                            temp = cut_ctg_order + 1
                            temp_write_list.append(str(cut_ctg_order))
                            temp_write_list.append(str(temp))
                            temp += 1
                            temp_write_list.append(str(temp))
                        else:  # 反向
                            temp = cut_ctg_order - 2
                            temp_write_list.append(str(temp))
                            temp += 1
                            temp_write_list.append(str(temp))
                            temp_write_list.append(str(cut_ctg_order))
                    else:  # 其余ctg + 1
                        if abs(int(x)) > abs(cut_ctg_order):
                            if int(x) > 0:
                                temp = int(x) + 2
                                temp_write_list.append(str(temp))
                            else:
                                temp = int(x) - 2
                                temp_write_list.append(str(temp))
                        else:
                            temp_write_list.append(str(x))
                f.write(" ".join(temp_write_list) + "\n")

    def inv_ctg(self, ctg_name, assembly_file_path, out_file_path, ctg_order=None):
        """
        反转ctg
        Args:
            ctg_name: 需要反转的ctg名字
            assembly_file_path: 原始assembly文件路径
            out_file_path: 输出文件路径
            ctg_order: 需要反转的ctg的顺序，如果为None，弃用

        Returns:
            None
        """

        # 获取需要反转的ctg的序号
        inv_ctg_order = self.get_ctg_info(ctg_name=ctg_name, new_asy_file=assembly_file_path)["ctg_order"]

        # 获取assembly_file_path中 ctgs 序号信息
        ctgs, ctgs_orders = AssemblyOperate._get_ctgs_orders(assembly_file_path)

        # 写入新文件
        with open(out_file_path, "w") as f:
            # 写入新的ctg信息
            for key, value in ctgs.items():
                f.write(key + " " + value["order"] + " " + value["length"] + "\n")

            # 写入新的ctg顺序
            for ctgs_order in ctgs_orders:
                temp_write_list = []
                for x in ctgs_order:
                    if int(x) == inv_ctg_order:
                        temp_write_list.append(str(-int(x)))
                    else:
                        temp_write_list.append(str(x))
                f.write(" ".join(temp_write_list) + "\n")


def main():
    # 实例化Assembly类
    temp = AssemblyOperate("/home/jzj/Data/Test/asy_test/random_Np/Np.final.assembly", ratio=2)

    # 测试获取整体信息
    print(json.dumps(temp.get_info(), indent=4))

    # 测试获取指定ctg信息
    assembly_info = temp.get_ctg_info(ctg_name="utg487")
    # assembly_info = temp.get_ctg_info(ctg_order=1335)
    print(json.dumps(assembly_info, indent=4))

    # 测试切割指定ctg
    # out_file_path = "/home/jzj/buffer/cut_Np.0.assembly"
    # cut_ctgs = {
    #     ">utg832": 990375001}
    # temp.cut_ctgs(cut_ctgs, out_file_path)

    # 测试移动指定ctg
    # assembly_file_path = "/home/jzj/buffer/cut_Np.0.assembly"
    # out_file_path = "/home/jzj/buffer/move_Np.0.assembly"
    # move_ctgs = [">utg832:::fragment_1", ">utg2240", ">utg4279"]
    # insert_ctg = ">utg4426"
    # temp.move_ctgs(assembly_file_path, move_ctgs, insert_ctg, out_file_path, direction="left")

    # 测试切割指定ctg为三个ctg
    # assembly_file_path = "/home/jzj/buffer/Np.0.assembly"
    # out_file_path = "/home/jzj/buffer/3_Np.0.assembly"
    # temp.cut_ctg_to_3(assembly_file_path, ">utg206980", 2291795710, 2291807171, out_file_path)

    # 测试反转ctg
    # assembly_file_path = "/home/jzj/Data/Test/asy_test/random_Np/Np.final.assembly"
    # out_file_path = "/home/jzj/buffer/test.assembly"
    # ctg_name = "utg2441"
    # temp.inv_ctg(ctg_name, assembly_file_path, out_file_path)


if __name__ == "__main__":
    main()

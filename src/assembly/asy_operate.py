#!/usr/scripts/env python
# encoding: utf-8

"""
@author: jzj
@contact: jzjlab@163.com
@file: asy_operate.py
@time: 12/01/22 4:14 PM
@function: assembly file operate class
"""
import json
import re
from collections import OrderedDict

from src.core.utils.logger import logger


class AssemblyOperate(object):
    def __init__(self, assembly_file_path, ratio):
        # Initiating assembly file path
        self.assembly_file_path = assembly_file_path
        self.ratio = ratio  # thr ratio between assembly and hic

    def get_info(self, new_asy_file=None) -> dict:
        """
            Get basic information of assembly file
        Args:
            new_asy_file:

        Returns:
            assembly_info: assembly information
        """
        ctg_number = 0  # ctg number
        seqs_length = 0  # sequence total length

        # when new_asy_file is not None
        if new_asy_file is not None:
            # renew assembly file path
            self.assembly_file_path = new_asy_file

        # get ctg number and total length
        with open(self.assembly_file_path, "r") as f:
            for line in f:
                if line.startswith(">"):
                    ctg_number += 1

                    # get ctg length
                    seq_length = line.strip().split()[2]
                    seqs_length += int(seq_length)

        assembly_info = {
            "assembly_file": self.assembly_file_path,
            "ctg_number": ctg_number,
            "seq_length": seqs_length
        }

        return assembly_info

    def get_ctg_info(self, ctg_name=None, ctg_order=None, new_asy_file=None) -> dict:
        """
            Get ctg information by ctg name or ctg order
        Args:
            ctg_name: ctg name
            ctg_order: ctg order
            new_asy_file: new assembly file path

        Returns:
            ctg_info: ctg information
        """

        # No query field was passed in
        if ctg_name is None and ctg_order is None:
            logger.error("o query field ctg name or ctg order \n")
            raise ValueError("ctg name or ctg order must be specified")

        ctgs_infos = {}  # ctg information
        ctgs_orders = []  # ctg order

        # when new_asy_file is not None
        if new_asy_file is not None:
            self.assembly_file_path = new_asy_file

        # get basic information
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
                            print("Warning: order is empty, please check assembly file")

        ctg_length = 1  # Calculated total ctg length

        ctg_by_name = {}  # ctg information dict by name
        ctg_by_order = {}  # ctg information dict by order

        # format ctg information
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
            Get all ctg orders
        Args:
            assembly_file_path: assembly file path

        Returns:
            ctgs_orders: all ctgs and orders
        """
        ctgs = OrderedDict()  # ctgs information
        ctgs_orders = []  # ctgs orders

        # get ctg number and total length
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
            Cut ctg by ctg name
        Args:
            assembly_file_path: assembly file path
            cut_ctg: cut ctg name （ctg_name: cut_site）
            out_file_path: output file path

        Returns:

        """

        # get original ctgs information
        ctgs, ctgs_orders = self._get_ctgs_orders(assembly_file_path)

        # Declare variables (in case of subsequent reminders)
        cut_ctg_name, cut_ctg_site = None, None

        # get cut ctg information
        for key, values in cut_ctg.items():
            cut_ctg_name = key
            cut_ctg_site = values

        # calculated new information of cut ctg
        cut_ctg_info = self.get_ctg_info(ctg_name=cut_ctg_name, new_asy_file=assembly_file_path)

        # get cut_ctg order (True: positive, False: negative)
        cut_ctg_order = cut_ctg_info["ctg_order"]

        # calculated cut start and end site
        cut_ctg_site1 = cut_ctg_site - cut_ctg_info["site"][0]
        cut_ctg_site2 = cut_ctg_info["site"][1] - cut_ctg_site + 1

        with open(out_file_path, "w") as f:
            # write new ctg information
            for key, value in ctgs.items():
                if key == cut_ctg_name:
                    # when ctg order is positive
                    if int(cut_ctg_order) > 0:
                        f.write(key + ":::fragment_1 " + value["order"] + " " + str(cut_ctg_site1) + "\n")
                        temp_order = int(value["order"]) + 1
                        f.write(key + ":::fragment_2" + " " + str(temp_order) + " " + str(cut_ctg_site2) + "\n")
                    else:
                        f.write(key + ":::fragment_1 " + value["order"] + " " + str(cut_ctg_site2) + "\n")
                        temp_order = int(value["order"]) + 1
                        f.write(key + ":::fragment_2" + " " + str(temp_order) + " " + str(cut_ctg_site1) + "\n")
                else:
                    # cut ctg divides into two and then increase back ctg order
                    if int(value["order"]) > abs(int(cut_ctg_order)):
                        temp_order = int(value["order"]) + 1
                        f.write(key + " " + str(temp_order) + " " + value["length"] + "\n")
                    else:
                        f.write(key + " " + value["order"] + " " + value["length"] + "\n")

            # write new ctg order information
            for ctgs_order in ctgs_orders:
                temp_write_list = []
                for x in ctgs_order:
                    # update cut ctg order
                    if int(x) == int(cut_ctg_order):
                        if cut_ctg_order > 0:  # when ctg order is positive
                            temp = cut_ctg_order + 1
                            temp_write_list.append(str(cut_ctg_order))
                            temp_write_list.append(str(temp))
                        else:  # when ctg order is negative
                            temp = cut_ctg_order - 1
                            temp_write_list.append(str(temp))
                            temp_write_list.append(str(cut_ctg_order))
                    else:  # the rest ctg order + 1
                        if abs(int(x)) > abs(int(cut_ctg_order)):
                            if int(x) > 0:
                                temp = int(x) + 1
                                temp_write_list.append(str(temp))
                            else:
                                temp = int(x) - 1
                                temp_write_list.append(str(temp))
                        else:
                            temp_write_list.append(str(x))
                f.write(" ".join(temp_write_list) + "\n")

    def recut_ctgs(self, assembly_file_path, cut_ctg, out_file_path):
        """
            Recut ctg
        Args:
            assembly_file_path: assembly file path
            cut_ctg: cut ctg name （ctg_name: cut_site）
            out_file_path: output file path

        Returns:
            None
        """
        # get original ctgs information
        ctgs, ctgs_orders = self._get_ctgs_orders(assembly_file_path)

        # Declare variables (in case of subsequent reminders)
        cut_ctg_name, cut_ctg_site = None, None

        # get cut ctg information
        for key, values in cut_ctg.items():
            cut_ctg_name = key  # get cut ctg name
            cut_ctg_site = values  # get cut ctg site

        # get recut ctg name head
        cut_ctg_name_head = re.search(r"(.*_)(\d+)", cut_ctg_name).group(1)
        # get recut ctg name fragment order(fragment_X)
        cut_ctg_name_order = re.search(r"(.*_)(\d+)", cut_ctg_name).group(2)

        # get recut ctg information
        cut_ctg_info = self.get_ctg_info(ctg_name=cut_ctg_name, new_asy_file=assembly_file_path)

        # get recut ctg order (True: positive, False: negative)
        cut_ctg_order = cut_ctg_info["ctg_order"]

        # calculated recut start and end site
        cut_ctg_site1 = cut_ctg_site - cut_ctg_info["site"][0]
        cut_ctg_site2 = cut_ctg_info["site"][1] - cut_ctg_site + 1

        with open(out_file_path, "w") as f:
            # write new ctg order information
            for key, value in ctgs.items():
                if key.startswith(cut_ctg_name_head):
                    head = re.search(r"(.*_)(\d+)", key).group(1)
                    order = re.search(r"(.*_)(\d+)", key).group(2)

                    # Direct writing of the previous ctg
                    if int(order) < int(cut_ctg_name_order):
                        f.write(key + " " + value["order"] + " " + value["length"] + "\n")

                    # if ctg is recut ctg
                    elif order == cut_ctg_name_order:
                        temp_order = int(value["order"]) + 1
                        # when ctg order is positive
                        if int(cut_ctg_order) > 0:
                            if key.endswith("debris"):
                                f.write(head + order + ":::debris " + value["order"] + " " + str(cut_ctg_site1) + "\n")

                                f.write(head + str(int(order) + 1) + ":::debris " + str(temp_order) + " " + str(
                                    cut_ctg_site2) + "\n")
                            else:
                                f.write(head + order + " " + value["order"] + " " + str(cut_ctg_site1) + "\n")

                                f.write(head + str(int(order) + 1) + " " + str(temp_order) + " " + str(
                                    cut_ctg_site2) + "\n")
                        else:
                            if key.endswith("debris"):
                                f.write(head + order + ":::debris " + value["order"] + " " + str(cut_ctg_site2) + "\n")

                                f.write(head + str(int(order) + 1) + ":::debris " + str(temp_order) + " " + str(
                                    cut_ctg_site1) + "\n")
                            else:
                                f.write(head + order + " " + value["order"] + " " + str(cut_ctg_site2) + "\n")

                                f.write(head + str(int(order) + 1) + " " + str(temp_order) + " " + str(
                                    cut_ctg_site1) + "\n")

                    else:  # the rest ctg order + 1
                        temp_order = int(value["order"]) + 1
                        if key.endswith("debris"):
                            f.write(head + str(int(order) + 1) + ":::debris " + str(temp_order) + " " + value[
                                "length"] + "\n")
                        else:
                            f.write(
                                head + str(int(order) + 1) + " " + str(temp_order) + " " + value["length"] + "\n")
                else:
                    # cut ctg divides into two and then increase back ctg order
                    if int(value["order"]) > abs(int(cut_ctg_order)):
                        temp_order = int(value["order"]) + 1
                        f.write(key + " " + str(temp_order) + " " + value["length"] + "\n")
                    else:
                        f.write(key + " " + value["order"] + " " + value["length"] + "\n")

            # write new ctg order information
            for ctgs_order in ctgs_orders:
                temp_write_list = []
                for x in ctgs_order:
                    # update recut ctg order
                    if int(x) == cut_ctg_order:
                        if cut_ctg_order > 0:
                            temp = cut_ctg_order + 1
                            temp_write_list.append(str(cut_ctg_order))
                            temp_write_list.append(str(temp))
                        else:  # when recut ctg order is negative
                            temp = cut_ctg_order - 1
                            temp_write_list.append(str(temp))
                            temp_write_list.append(str(cut_ctg_order))
                    else:  # the rest ctg order + 1
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
            move translocation ctgs
        Args:
            assembly_file_path: assembly file path
            error_info: error information
            out_file_path: output file path

        Returns:
            None
        """

        self.assembly_file_path = assembly_file_path

        # get ctgs information
        ctgs, ctgs_orders = AssemblyOperate._get_ctgs_orders(assembly_file_path)

        for error in error_info:
            # get move ctg name information
            move_ctg = list(error_info[error]["move_ctgs"].keys())

            # get move ctg order information
            move_ctg_orders = []
            for ctg in move_ctg:
                get_ctg_info = self.get_ctg_info(ctg_name=ctg, new_asy_file=assembly_file_path)
                get_ctg_info_order = get_ctg_info["ctg_order"]
                move_ctg_orders.append(str(get_ctg_info_order))

            # get insert ctg order information
            insert_ctg = list(error_info[error]["insert_site"].keys())[0]
            insert_ctg_order = self.get_ctg_info(ctg_name=insert_ctg)["ctg_order"]

            # insert ctg order index
            insert_ctg_order_index = None

            # update ctg order
            for move_ctg_order in move_ctg_orders:
                for index in range(len(ctgs_orders)):
                    # delete the original position of the move ctg
                    if move_ctg_order in ctgs_orders[index]:
                        ctgs_orders[index].remove(move_ctg_order)

                    # get insert ctg order index
                    if str(insert_ctg_order) in ctgs_orders[index]:
                        insert_ctg_order_index = (index, ctgs_orders[index].index(str(insert_ctg_order)))

            # get move ctg
            direction = error_info[error]["direction"]  # insert direction
            if direction == "left":  # insert left
                move_ctg_orders.reverse()
                for move_ctg_order in move_ctg_orders:
                    ctgs_orders[insert_ctg_order_index[0]].insert(insert_ctg_order_index[1], move_ctg_order)
            else:  # insert right
                move_ctg_orders.reverse()
                for move_ctg_order in move_ctg_orders:
                    ctgs_orders[insert_ctg_order_index[0]].insert(insert_ctg_order_index[1] + 1, move_ctg_order)

            # update assembly file
            with open(out_file_path, "w") as f:
                # write new ctg information
                for key, value in ctgs.items():
                    f.write(key + " " + value["order"] + " " + value["length"] + "\n")

                # write new ctg order information
                for ctgs_order in ctgs_orders:
                    temp_write_list = []
                    for x in ctgs_order:
                        temp_write_list.append(str(x))
                    f.write(" ".join(temp_write_list) + "\n")

    def find_site_ctgs(self, assembly_file_path, start, end):
        """
            Find site coordinate interval ctgs
        Args:
            assembly_file_path: assembly file path
            start: start coordinate
            end: end coordinate

        Returns:
            site_ctgs: site coordinate interval ctgs
        """

        contain_contig = OrderedDict()  # site coordinate interval ctgs

        contig_info = {}  # ctg information {order: {name, length}}

        contig_order = []  # ctg order list

        # get the real position information on the genome
        genome_start = start * self.ratio
        genome_end = end * self.ratio

        logger.info("查询真实位点为 ： {0} - {1} \n".format(genome_start, genome_end))

        logger.info("该区域包含的contig : ")

        with open(assembly_file_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                # ctg :name : order, length
                if line.startswith(">"):
                    each_line = line.strip().split()
                    contig_info[each_line[1].strip(">")] = {
                        "name": each_line[0],
                        "length": each_line[2]
                    }
                # ctg order
                else:
                    contig_order.append(line.strip().split())

            # Two-dimensional reduction to one-dimensional
            contig_order = [order for st in contig_order for order in st]

        # 寻找contig
        temp_len_s = 0  # record the start position of the current ctg
        temp_len_e = 0  # record the end position of the current ctg

        for i in contig_order:  # loop ctgs

            if i.startswith("-"):  # when ctg is reverse(Negative)
                i = i[1:]
                temp_len_s = temp_len_e + 1
                temp_len_e += int(contig_info[i]["length"])
            else:
                temp_len_s = temp_len_e + 1
                temp_len_e += int(contig_info[i]["length"])

            # Decoupling
            def callback():
                contain_contig[contig_info[i]["name"]] = {
                    "length": contig_info[i]["length"],
                    "start": temp_len_s,
                    "end": temp_len_e
                }
                return temp_len_e

            # each ctg relationship with the query site (refer to the relationship between two line segments)
            if temp_len_s < genome_start:
                if genome_start < temp_len_e:
                    callback()
            elif temp_len_s >= genome_start:
                if temp_len_e < genome_end:
                    callback()
                elif temp_len_s < genome_end:
                    callback()

        # reformatted output to json
        contain_contig = json.dumps(
            contain_contig,
            indent=4,
            separators=(
                ',',
                ': '))
        logger.info(contain_contig)

        return contain_contig

    def cut_ctg_to_3(self, assembly_file_path, cut_ctg_name, site_1, site_2, out_file_path):
        """
            Cut ctg to 3 parts
        Args:
            assembly_file_path: assembly file path
            cut_ctg_name: cut ctg name
            site_1: cut site 1
            site_2: cut site 2
            out_file_path: output file path

        Returns:
            None
        """

        if cut_ctg_name.startswith(">") is False:
            cut_ctg_name = ">" + cut_ctg_name

        # get original ctgs information
        ctgs, ctgs_orders = self._get_ctgs_orders(assembly_file_path)

        # get new information of cut ctg
        cut_ctg_info = self.get_ctg_info(ctg_name=cut_ctg_name, new_asy_file=assembly_file_path)

        #  get cut ctg order (positive: True, negative: False)
        cut_ctg_order = cut_ctg_info["ctg_order"]

        # calculate the start and end position of the cut
        cut_ctg_site1 = site_1 - cut_ctg_info["site"][0]
        cut_ctg_site2 = site_2 - site_1 + 1
        cut_ctg_site3 = cut_ctg_info["site"][1] - site_2

        with open(out_file_path, "w") as f:
            # write new ctg information
            for key, value in ctgs.items():
                if key == cut_ctg_name:
                    # when ctg order is positive
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
                    # update other ctg information
                    if int(value["order"]) > abs(cut_ctg_order):
                        temp_order = int(value["order"]) + 2
                        f.write(key + " " + str(temp_order) + " " + value["length"] + "\n")
                    else:
                        f.write(key + " " + value["order"] + " " + value["length"] + "\n")

            # write new ctg order
            for ctgs_order in ctgs_orders:
                temp_write_list = []
                for x in ctgs_order:
                    # update ctg order
                    if int(x) == cut_ctg_order:
                        if cut_ctg_order > 0:
                            temp = cut_ctg_order + 1
                            temp_write_list.append(str(cut_ctg_order))
                            temp_write_list.append(str(temp))
                            temp += 1
                            temp_write_list.append(str(temp))
                        else:  # when ctg order is negative
                            temp = cut_ctg_order - 2
                            temp_write_list.append(str(temp))
                            temp += 1
                            temp_write_list.append(str(temp))
                            temp_write_list.append(str(cut_ctg_order))
                    else:  # other ctg order + 1
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

    def recut_ctg_to_3(self, assembly_file_path, cut_ctg_name, site_1, site_2, out_file_path):
        """
            Recut ctg to 3 parts
        Args:
            assembly_file_path: assembly file path
            cut_ctg_name: cut ctg name
            site_1: cut site 1
            site_2: cut site 2
            out_file_path: output file path

        Returns:
            None
        """
        if cut_ctg_name.startswith(">") is False:
            cut_ctg_name = ">" + cut_ctg_name

        # get original ctgs information
        ctgs, ctgs_orders = self._get_ctgs_orders(assembly_file_path)

        # get recut ctg head information
        cut_ctg_name_head = re.search(r"(.*_)(\d+)", cut_ctg_name).group(1)
        # get recut ctg order information（fragment_X）
        cut_ctg_name_order = re.search(r"(.*_)(\d+)", cut_ctg_name).group(2)

        # calculate the new information of the cut ctg
        cut_ctg_info = self.get_ctg_info(ctg_name=cut_ctg_name, new_asy_file=assembly_file_path)

        # get cut ctg order (positive: True, negative: False)
        cut_ctg_order = cut_ctg_info["ctg_order"]

        # calculate the start and end position of the cut
        cut_ctg_site1 = site_1 - cut_ctg_info["site"][0]
        cut_ctg_site2 = site_2 - site_1 + 1
        cut_ctg_site3 = cut_ctg_info["site"][1] - site_2

        with open(out_file_path, "w") as f:
            # write new ctg information
            for key, value in ctgs.items():
                if key.startswith(cut_ctg_name_head):
                    head = re.search(r"(.*_)(\d+)", key).group(1)
                    order = re.search(r"(.*_)(\d+)", key).group(2)

                    # directly write the front ctg information
                    if int(order) < int(cut_ctg_name_order):
                        f.write(key + " " + value["order"] + " " + value["length"] + "\n")

                    # recut ctg
                    elif int(order) == int(cut_ctg_name_order):
                        temp_order = int(value["order"]) + 1
                        # judge the order direction of the cut ctg
                        if int(cut_ctg_order) > 0:
                            if key.endswith("debris"):
                                f.write(head + order + ":::debris " + value["order"] + " " + str(cut_ctg_site1) + "\n")
                                f.write(head + str(int(order) + 1) + ":::debris " + str(temp_order) + " " + str(
                                    cut_ctg_site2) + "\n")
                                temp_order += 1
                                f.write(head + str(int(order) + 2) + ":::debris " + str(temp_order) + " " + str(
                                    cut_ctg_site3) + "\n")
                            else:
                                f.write(head + order + " " + value["order"] + " " + str(cut_ctg_site1) + "\n")
                                f.write(head + str(int(order) + 1) + " " + str(temp_order) + " " + str(
                                    cut_ctg_site2) + "\n")
                                temp_order += 1
                                f.write(head + str(int(order) + 2) + " " + str(temp_order) + " " + str(
                                    cut_ctg_site3) + "\n")

                        else:
                            if key.endswith("debris"):
                                f.write(head + order + ":::debris " + value["order"] + " " + str(cut_ctg_site3) + "\n")
                                f.write(head + str(int(order) + 1) + ":::debris " + str(temp_order) + " " + str(
                                    cut_ctg_site2) + "\n")
                                temp_order += 1
                                f.write(head + str(int(order) + 2) + ":::debris " + str(temp_order) + " " + str(
                                    cut_ctg_site1) + "\n")
                            else:
                                f.write(head + order + " " + value["order"] + " " + str(cut_ctg_site3) + "\n")
                                f.write(head + str(int(order) + 1) + " " + str(temp_order) + " " + str(
                                    cut_ctg_site2) + "\n")
                                temp_order += 1
                                f.write(head + str(int(order) + 2) + " " + str(temp_order) + " " + str(
                                    cut_ctg_site1) + "\n")
                    # write the back ctg information and update the order + 2
                    else:
                        temp_order = int(value["order"]) + 2
                        if key.endswith("debris"):
                            f.write(head + str(int(order) + 2) + ":::debris " + str(temp_order) + " " + value[
                                "length"] + "\n")
                        else:
                            f.write(
                                head + str(int(order) + 2) + " " + str(temp_order) + " " + value["length"] + "\n")
                else:
                    # update the order + 2
                    if int(value["order"]) > abs(int(cut_ctg_order)):
                        temp_order = int(value["order"]) + 2
                        f.write(key + " " + str(temp_order) + " " + value["length"] + "\n")
                    else:
                        f.write(key + " " + value["order"] + " " + value["length"] + "\n")

            # write new ctg order information
            for ctgs_order in ctgs_orders:
                temp_write_list = []
                for x in ctgs_order:
                    # update the new order of the cut ctg
                    if int(x) == cut_ctg_order:
                        if cut_ctg_order > 0:
                            temp = cut_ctg_order + 1
                            temp_write_list.append(str(cut_ctg_order))
                            temp_write_list.append(str(temp))
                            temp += 1
                            temp_write_list.append(str(temp))
                        else:  # when the cut ctg is negative
                            temp = cut_ctg_order - 2
                            temp_write_list.append(str(temp))
                            temp += 1
                            temp_write_list.append(str(temp))
                            temp_write_list.append(str(cut_ctg_order))
                    else:  # other ctg order + 2
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

    def inv_ctg(self, ctg_name, assembly_file_path, out_file_path, _ctg_order=None):
        """
            Invert the order of the ctg
        Args:
            ctg_name: the name of the ctg
            assembly_file_path: the path of the assembly file
            out_file_path: the path of the output file
            _ctg_order: the order of the ctg

        Returns:
            None
        """

        # get the order of the invert ctg
        inv_ctg_order = self.get_ctg_info(ctg_name=ctg_name, new_asy_file=assembly_file_path)["ctg_order"]

        # get the ctgs order information in assembly_file_path
        ctgs, ctgs_orders = AssemblyOperate._get_ctgs_orders(assembly_file_path)

        # update assembly file
        with open(out_file_path, "w") as f:
            # write the new ctg information
            for key, value in ctgs.items():
                f.write(key + " " + value["order"] + " " + value["length"] + "\n")

            # write new ctg order information
            for ctgs_order in ctgs_orders:
                temp_write_list = []
                for x in ctgs_order:
                    if int(x) == inv_ctg_order:
                        temp_write_list.append(str(-int(x)))
                    else:
                        temp_write_list.append(str(x))
                f.write(" ".join(temp_write_list) + "\n")

    def move_deb_to_end(self, assembly_file_path, move_ctgs, out_file_path):
        """
            Move the debris ctg to the end of the assembly file
        Args:
            assembly_file_path: the path of the assembly file
            move_ctgs: the list of the debris ctg
            out_file_path: the path of the output file

        Returns:
            None
        """
        deb_ctgs_order = []

        for i in move_ctgs:
            for j in move_ctgs[i]["deb_ctgs"]:
                temp = self.get_ctg_info(ctg_name=j, new_asy_file=assembly_file_path)
                deb_ctgs_order.append(str(temp["ctg_order"]))

        # get the ctgs order information in assembly_file_path
        ctgs, ctgs_orders = AssemblyOperate._get_ctgs_orders(assembly_file_path)

        # update order and write to new file
        with open(out_file_path, "w") as f:
            # write the new ctg information
            for key, value in ctgs.items():
                f.write(key + " " + value["order"] + " " + value["length"] + "\n")

            # write new ctg order information
            for ctgs_order in ctgs_orders:
                temp_write_list = []
                for x in ctgs_order:
                    if str(x) in deb_ctgs_order:
                        continue
                    else:
                        temp_write_list.append(str(x))
                f.write(" ".join(temp_write_list) + "\n")
            f.write(" ".join(deb_ctgs_order) + "\n")

    @staticmethod
    def remove_asy_blank(raw_asy, new_asy=None):
        if new_asy is None:
            new_asy = raw_asy.split(".")[0] + "_corrected.assembly"
        open(new_asy, 'w').write(''.join(l for l in open(raw_asy) if l.strip()))

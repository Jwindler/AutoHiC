#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: tran_adjust.py
@time: 10/7/22 10:27 AM
@function: translocation adjust
"""
import json
import re
from collections import OrderedDict

from src.assembly.asy_operate import AssemblyOperate
from src.assembly.search_right_site_V2 import search_right_site_v2
from src.core.utils.get_ratio import get_ratio
from src.core.utils.logger import logger


def adjust_translocation(error_queue, hic_file, assembly_file, modified_assembly_file, move_flag=True):
    """
        translocation adjust
    Args:
        error_queue: error queue
        hic_file: hic file path
        assembly_file: assembly file path
        modified_assembly_file: modified assembly file path
        move_flag: move ctg or not

    Returns:

    """

    logger.info("Start adjust translocation \n")

    # get ratio of hic file and assembly file
    ratio = get_ratio(hic_file, assembly_file)

    # class AssemblyOperate class
    asy_operate = AssemblyOperate(assembly_file, ratio)

    # error modify information record
    error_mdy_info = OrderedDict()

    flag = True  # flag to judge whether the file is modified
    cut_ctg_name_site = {}  # cut ctg name and site

    # loop error queue
    for error in error_queue:
        if flag:
            flag = False
        else:
            assembly_file = modified_assembly_file

        logger.info("开始计算 {0} 的调整信息：".format(error))

        # find ctgs in error region
        error_contain_ctgs = asy_operate.find_site_ctgs(assembly_file, error_queue[error]["start"],
                                                        error_queue[error]["end"])

        error_contain_ctgs = json.loads(error_contain_ctgs)  # str to dict
        error_contain_ctgs = list(error_contain_ctgs.items())  # dict to list

        logger.info("开始切割易位错误的边界ctgs：")

        # cut ctg in translocation error region
        if len(error_contain_ctgs) >= 2:  # ctg number >= 2

            # cut first ctg
            first_ctg = error_contain_ctgs[0]

            cut_ctg_name_site[first_ctg[0]] = error_queue[error]["start"] * ratio

            # {ctg_name: "cut_site"}
            if "fragment" in first_ctg[0] or "debris" in first_ctg[0]:  # check whether the ctg is already cut
                asy_operate.recut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)
            else:
                asy_operate.cut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)

            # cut last ctg
            last_ctg = error_contain_ctgs[-1]

            cut_ctg_name_site.clear()  # clear dict( a bug here, no error because the next function has processed it)
            cut_ctg_name_site[last_ctg[0]] = error_queue[error]["end"] * ratio

            if "fragment" in last_ctg[0] or "debris" in last_ctg[0]:  # check whether the ctg is already cut
                try:
                    first_ctg_name_head = re.search(r"(.*_)(\d+)", first_ctg[0]).group(1)
                    last_ctg_name_head = re.search(r"(.*_)(\d+)", last_ctg[0]).group(1)
                    first_ctg_name_order = re.search(r"(.*_)(\d+)", first_ctg[0]).group(2)
                    last_ctg_name_order = re.search(r"(.*_)(\d+)", last_ctg[0]).group(2)

                    # ctgs are synonymous and in the same direction
                    if first_ctg_name_head == last_ctg_name_head and int(first_ctg_name_order) < int(
                            last_ctg_name_order):
                        renew_last_ctg_name = last_ctg_name_head + str(int(last_ctg_name_order) + 1)
                        cut_ctg_name_site.clear()  # clear dict
                        cut_ctg_name_site[renew_last_ctg_name] = error_queue[error]["end"] * ratio
                except AttributeError:
                    pass
                asy_operate.recut_ctgs(modified_assembly_file, cut_ctg_name_site, modified_assembly_file)
            else:
                asy_operate.cut_ctgs(modified_assembly_file, cut_ctg_name_site, modified_assembly_file)

        else:  # ctg number = 1
            _ctg = error_contain_ctgs[0]  # ctg_name

            _ctg_info = asy_operate.get_ctg_info(ctg_name=_ctg[0], new_asy_file=assembly_file)  # get ctg info

            cut_ctg_site_start = error_queue[error]["start"] * ratio  # error real start site
            cut_ctg_site_end = error_queue[error]["end"] * ratio  # error real end site

            # check ctg position
            if _ctg_info["site"][0] == cut_ctg_site_start:  # left boundary overlap, cut it directly
                cut_ctg_name_site[_ctg[0]] = cut_ctg_site_end

                # cut a ctg to two ctgs
                if "fragment" in _ctg[0] or "debris" in _ctg[0]:  # check whether the ctg is already cut
                    asy_operate.recut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)
                else:
                    asy_operate.cut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)

            elif _ctg_info["site"][1] == cut_ctg_site_end:  # right boundary overlap, cut it directly
                cut_ctg_name_site[_ctg[0]] = cut_ctg_site_start

                # cut a ctg to two ctgs
                if "fragment" in _ctg[0] or "debris" in _ctg[0]:  # check whether the ctg is already cut
                    asy_operate.recut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)
                else:
                    asy_operate.cut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)

            else:  # no boundary situation, cut it into three ctgs
                if "fragment" in _ctg[0] or "debris" in _ctg[0]:  # check whether the ctg is already cut
                    asy_operate.recut_ctg_to_3(assembly_file, _ctg[0], cut_ctg_site_start,
                                               cut_ctg_site_end, modified_assembly_file)
                else:
                    asy_operate.cut_ctg_to_3(assembly_file, _ctg[0], cut_ctg_site_start,
                                             cut_ctg_site_end, modified_assembly_file)

        logger.info("易位错误的边界ctgs切割完成 \n")

    logger.info("重新查询易位错误区间包含的ctgs")
    for error in error_queue:
        logger.info("开始计算 {0} 的插入信息：".format(error))
        new_error_contain_ctgs = asy_operate.find_site_ctgs(modified_assembly_file, error_queue[error]["start"],
                                                            error_queue[error]["end"])

        new_error_contain_ctgs = json.loads(new_error_contain_ctgs)  # str to dict

        logger.info("需要移动的ctgs: %s \n", new_error_contain_ctgs)

        logger.info("开始查询 {0} 易位错误的插入位点：".format(error))

        # get insert ctg site
        error_site = (error_queue[error]["start"], error_queue[error]["end"])
        temp_result, insert_left = search_right_site_v2(hic_file, assembly_file, ratio, error_site)
        error_mdy_info[error] = {
            "move_ctgs": new_error_contain_ctgs,
            "insert_site": temp_result,
            "direction": insert_left
        }

        logger.info("易位错误的插入位点查询完成 \n")

    if move_flag:
        logger.info("开始对所有易位错误进行调整：")

        # move ctgs
        asy_operate.move_ctgs(modified_assembly_file, error_mdy_info, modified_assembly_file)
        logger.info("所有易位错误调整完成 \n")

    logger.info("所有易位错误的调整信息： %s \n", error_mdy_info)
    logger.info("All Done! \n")


def main():
    # error queue, start and end are based on hic file, not assembly file
    error_queue = {
        "error_1": {
            "start": 250081212,
            "end": 254212374
        }
        # "error_2": {
        #     "start": 453010131,
        #     "end": 455241282
        # }
    }

    # hic file path
    hic_file = "/home/jzj/Data/Test/raw_data/Aa/Aa.2.hic"

    # assembly file path
    assembly_file = "/home/jzj/Data/Test/raw_data/Aa/Aa.2.assembly"

    # modified assembly file path
    modified_assembly_file = "/home/jzj/buffer/test.assembly"

    adjust_translocation(error_queue, hic_file, assembly_file, modified_assembly_file)


if __name__ == "__main__":
    main()

#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: inv_adjust.py
@time: 10/7/22 10:27 AM
@function: inversion adjust
"""
import re
import json
from collections import OrderedDict

from src.assembly.asy_operate import AssemblyOperate
from src.core.utils.get_ratio import get_ratio
from src.core.utils.logger import logger


def adjust_inversion(error_queue, hic_file, assembly_file, modified_assembly_file, move_flag=True):
    logger.info("Start adjust inversion \n")

    # get ratio between chromosome length and hic file length
    ratio = get_ratio(hic_file, assembly_file)

    # initialize AssemblyOperate class
    asy_operate = AssemblyOperate(assembly_file, ratio)

    cut_ctg_name_site = {}  # save cut chromosome name and site

    error_inv_info = OrderedDict()  # inversion info

    # flag = True  # 用于文件修改判断
    # if flag:  # 第一次修改assembly文件
    #     flag = False
    # else:
    #     assembly_file = modified_assembly_file

    # iterate error queue
    for error in error_queue:

        logger.info("开始计算 {0} 的调整信息：".format(error))

        # search ctg in debris site
        error_contain_ctgs = asy_operate.find_site_ctgs(assembly_file, error_queue[error]["start"],
                                                        error_queue[error]["end"])
        error_contain_ctgs = json.loads(error_contain_ctgs)  # convert string to dict
        error_contain_ctgs = list(error_contain_ctgs.items())  # convert dict to list

        logger.info("开始切割反转错误的边界ctgs：")

        # cut ctg in inversion site
        if len(error_contain_ctgs) >= 2:  # ctg in debris site >= 2

            # cut first ctg
            first_ctg = error_contain_ctgs[0]
            cut_ctg_name_site[first_ctg[0]] = error_queue[error]["start"] * ratio

            # {ctg_name: "cut_site"}
            if "fragment" in first_ctg[0] or "debris" in first_ctg[0]:  # check if second cut
                asy_operate.recut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)
            else:
                asy_operate.cut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)

            # cut last ctg
            last_ctg = error_contain_ctgs[-1]

            cut_ctg_name_site.clear()  # clear dict
            cut_ctg_name_site[last_ctg[0]] = error_queue[error]["end"] * ratio

            if "fragment" in last_ctg[0] or "debris" in last_ctg[0]:  # check if second cut
                try:
                    first_ctg_name_head = re.search(r"(.*_)(\d+)", first_ctg[0]).group(1)
                    last_ctg_name_head = re.search(r"(.*_)(\d+)", last_ctg[0]).group(1)
                    first_ctg_name_order = re.search(r"(.*_)(\d+)", first_ctg[0]).group(2)
                    last_ctg_name_order = re.search(r"(.*_)(\d+)", last_ctg[0]).group(2)
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

        else:  # only one ctg in debris site
            _ctg = error_contain_ctgs[0]  # ctg_name

            _ctg_info = asy_operate.get_ctg_info(ctg_name=_ctg[0], new_asy_file=assembly_file)  # get ctg info

            cut_ctg_site_start = error_queue[error]["start"] * ratio  # error start site in assembly file
            cut_ctg_site_end = error_queue[error]["end"] * ratio  # error end site in assembly file

            # check ctg position
            if _ctg_info["site"][0] == cut_ctg_site_start:  # left boundary coincide
                cut_ctg_name_site[_ctg[0]] = cut_ctg_site_end

                # cut one ctg to two ctgs
                if "fragment" in _ctg[0] or "debris" in _ctg[0]:  # check if second cut
                    asy_operate.recut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)
                else:
                    asy_operate.cut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)

            elif _ctg_info["site"][1] == cut_ctg_site_end:  # right boundary coincide
                cut_ctg_name_site[_ctg[0]] = cut_ctg_site_start

                # cut one ctg to two ctgs
                if "fragment" in _ctg[0] or "debris" in _ctg[0]:  # check if second cut
                    asy_operate.recut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)
                else:
                    asy_operate.cut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)

            else:  # no boundary, one cut three

                # cut one ctg to three ctgs
                if "fragment" in _ctg[0] or "debris" in _ctg[0]:  # check if second cut
                    asy_operate.recut_ctg_to_3(assembly_file, _ctg[0], cut_ctg_site_start,
                                               cut_ctg_site_end, modified_assembly_file)
                else:
                    asy_operate.cut_ctg_to_3(assembly_file, _ctg[0], cut_ctg_site_start,
                                             cut_ctg_site_end, modified_assembly_file)

        logger.info("反转错误的边界ctgs切割完成 \n")

        logger.info("重新查询反转错误区间包含的ctgs")
        new_error_contain_ctgs = asy_operate.find_site_ctgs(modified_assembly_file, error_queue[error]["start"],
                                                            error_queue[error]["end"])

        new_error_contain_ctgs = json.loads(new_error_contain_ctgs)  # convert str to dict

        logger.info("需要翻转的ctgs: %s \n", new_error_contain_ctgs)

        error_inv_info[error] = {
            "inv_ctgs": list(new_error_contain_ctgs.keys())
        }

    if move_flag:
        logger.info("开始对所有反转错误进行调整：")

        # start move ctgs
        for error in error_inv_info:
            for inv_ctg in error_inv_info[error]["inv_ctgs"]:
                asy_operate.inv_ctg(inv_ctg, modified_assembly_file, modified_assembly_file)

        logger.info("所有反转错误调整完成 \n")

    logger.info("所有反转错误的调整信息： %s \n", error_inv_info)
    logger.info("All Done! \n")


def main():
    # 错误队列，其中的start和end是基于hic文件上的位置，没有转换为基因组上的位置
    error_queue = {
        "error_1": {
            "start": 268689492,
            "end": 274981070
        },
        "error_2": {
            "start": 280560061,
            "end": 284239273
        }
    }

    # hic文件路径
    hic_file = "/home/jzj/Data/Test/Np-Self/Np.final.hic"

    # assembly文件路径
    assembly_file = "/home/jzj/Data/Test/Np-Self/Np.final.assembly"

    # 修改后assembly文件路径
    modified_assembly_file = "/home/jzj/buffer/test.assembly"

    adjust_inversion(error_queue, hic_file, assembly_file, modified_assembly_file)


if __name__ == "__main__":
    main()

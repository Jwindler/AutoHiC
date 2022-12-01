#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: tran_adjust.py
@time: 10/7/22 10:27 AM
@function: 易位错误调整流程整合
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
    易位错误调整
    :param error_queue: 易位错误队列
    :param hic_file:  hic文件路径
    :param assembly_file:  assembly文件路径
    :param modified_assembly_file:  修改后assembly文件保存路径
    :return: None
    """
    logger.info("Start adjust translocation \n")

    # 获取染色体长度比例
    ratio = get_ratio(hic_file, assembly_file)

    # 实例化AssemblyOperate类
    asy_operate = AssemblyOperate(assembly_file, ratio)

    # 错误修改信息记录
    error_mdy_info = OrderedDict()

    flag = True  # 用于文件修改判断
    cut_ctg_name_site = {}  # 存放切割的染色体名和位置

    # 循环易位错误队列
    for error in error_queue:
        if flag:
            flag = False
        else:
            assembly_file = modified_assembly_file

        logger.info("开始计算 {0} 的调整信息：".format(error))

        # 查找易位错误区间中包含的ctgs
        # 第一次查找旧文件，第二次查找新文件

        error_contain_ctgs = asy_operate.find_site_ctgs(assembly_file, error_queue[error]["start"],
                                                        error_queue[error]["end"])

        error_contain_ctgs = json.loads(error_contain_ctgs)  # 将字符串转换为字典
        error_contain_ctgs = list(error_contain_ctgs.items())  # 将字典转换为列表

        logger.info("开始切割易位错误的边界ctgs：")

        # 对易位错误区间中包含的ctgs进行切割,判断情况
        if len(error_contain_ctgs) >= 2:  # 易位错误区间内包含两个或两个以上的ctgs

            # 切割第一个ctg
            first_ctg = error_contain_ctgs[0]

            cut_ctg_name_site[first_ctg[0]] = error_queue[error]["start"] * ratio

            # {ctg_name: "cut_site"}
            if "fragment" in first_ctg[0] or "debris" in first_ctg[0]:  # 是否二次切割
                asy_operate.recut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)
            else:
                asy_operate.cut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)

            # 切割最后一个ctg
            last_ctg = error_contain_ctgs[-1]

            cut_ctg_name_site.clear()  # 清空字典(此处是一个BUG，没有报错是因为后一个函数做了处理)
            cut_ctg_name_site[last_ctg[0]] = error_queue[error]["end"] * ratio

            if "fragment" in last_ctg[0] or "debris" in last_ctg[0]:  # 是否二次切割
                try:
                    first_ctg_name_head = re.search(r"(.*_)(\d+)", first_ctg[0]).group(1)
                    last_ctg_name_head = re.search(r"(.*_)(\d+)", last_ctg[0]).group(1)
                    first_ctg_name_order = re.search(r"(.*_)(\d+)", first_ctg[0]).group(2)
                    last_ctg_name_order = re.search(r"(.*_)(\d+)", last_ctg[0]).group(2)

                    # 包含的错误是同源，并且正向，后一个需要加一
                    if first_ctg_name_head == last_ctg_name_head and int(first_ctg_name_order) < int(
                            last_ctg_name_order):
                        renew_last_ctg_name = last_ctg_name_head + str(int(last_ctg_name_order) + 1)
                        cut_ctg_name_site.clear()  # 清空字典(此处是一个BUG，没有报错是因为后一个函数做了处理)
                        cut_ctg_name_site[renew_last_ctg_name] = error_queue[error]["end"] * ratio
                except AttributeError:
                    pass
                asy_operate.recut_ctgs(modified_assembly_file, cut_ctg_name_site, modified_assembly_file)
            else:
                asy_operate.cut_ctgs(modified_assembly_file, cut_ctg_name_site, modified_assembly_file)

        else:  # 易位错误区间内只有一个ctg
            _ctg = error_contain_ctgs[0]  # ctg_name

            _ctg_info = asy_operate.get_ctg_info(ctg_name=_ctg[0], new_asy_file=assembly_file)  # 获取ctg信息

            cut_ctg_site_start = error_queue[error]["start"] * ratio  # 错误真实起始位置
            cut_ctg_site_end = error_queue[error]["end"] * ratio  # 错误真实终止位置

            # 判断该ctg的位置情况
            if _ctg_info["site"][0] == cut_ctg_site_start:  # 左边界重合，一切二即可
                cut_ctg_name_site[_ctg[0]] = cut_ctg_site_end

                # 将一个ctg切割为二个ctg
                if "fragment" in _ctg[0] or "debris" in _ctg[0]:  # 是否二次切割
                    asy_operate.recut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)
                else:
                    asy_operate.cut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)

            elif _ctg_info["site"][1] == cut_ctg_site_end:  # 右边界重合，一切二即可
                cut_ctg_name_site[_ctg[0]] = cut_ctg_site_start

                # 将一个ctg切割为二个ctg
                if "fragment" in _ctg[0] or "debris" in _ctg[0]:  # 是否二次切割
                    asy_operate.recut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)
                else:
                    asy_operate.cut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)

            else:  # 不存在边界情况，一切三
                # 将一个ctg切割为三个ctg
                if "fragment" in _ctg[0] or "debris" in _ctg[0]:  # 是否二次切割
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

        new_error_contain_ctgs = json.loads(new_error_contain_ctgs)  # 将字符串转换为字典

        logger.info("需要移动的ctgs: %s \n", new_error_contain_ctgs)

        logger.info("开始查询 {0} 易位错误的插入位点：".format(error))
        # 依次获取错误的插入ctg位点
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

        # 开始移动记录的ctgs
        asy_operate.move_ctgs(modified_assembly_file, error_mdy_info, modified_assembly_file)
        logger.info("所有易位错误调整完成 \n")

    logger.info("所有易位错误的调整信息： %s \n", error_mdy_info)
    logger.info("All Done! \n")


def main():
    # 错误队列，其中的start和end是基于hic文件上的位置，没有转换为基因组上的位置
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

    # hic文件路径
    hic_file = "/home/jzj/Data/Test/raw_data/Aa/Aa.2.hic"

    # assembly文件路径
    assembly_file = "/home/jzj/Data/Test/raw_data/Aa/Aa.2.assembly"

    # 修改后assembly文件路径
    modified_assembly_file = "/home/jzj/buffer/test.assembly"

    adjust_translocation(error_queue, hic_file, assembly_file, modified_assembly_file)


if __name__ == "__main__":
    main()

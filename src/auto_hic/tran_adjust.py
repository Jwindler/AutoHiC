#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: tran_adjust.py
@time: 8/23/22 8:13 PM
@function: 易位错误调整流程整合
"""
import json
from collections import OrderedDict

from src.assembly.asy_operate import AssemblyOperate
from src.assembly.search_right_site_V2 import search_right_site_v2
from src.auto_hic.utils.get_ratio import get_ratio
from src.auto_hic.utils.logger import LoggerHandler

# 初始化日志
logger = LoggerHandler()


def adjust_translocation(error_queue, hic_file, assembly_file, modified_assembly_file):
    """
    易位错误调整
    :param error_queue: 易位错误队列
    :param hic_file:  hic文件路径
    :param assembly_file:  assembly文件路径
    :param modified_assembly_file:  修改后assembly文件保存路径
    :return: None
    """
    logger.info("Start \n")

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
        logger.info("开始计算 {0} 的调整信息：".format(error))

        # 查找易位错误区间中包含的ctgs
        error_contain_ctgs = asy_operate.find_site_ctgs(assembly_file, error_queue[error]["start"],
                                                        error_queue[error]["end"])
        error_contain_ctgs = json.loads(error_contain_ctgs)  # 将字符串转换为字典
        error_contain_ctgs = list(error_contain_ctgs.items())  # 将字典转换为列表

        logger.info("开始切割易位错误的边界ctgs：")

        # 对易位错误区间中包含的ctgs进行切割,判断情况
        if len(error_contain_ctgs) >= 2:  # 易位错误区间内包含两个或两个以上的ctgs

            # 切割第一个ctg
            first_ctg = error_contain_ctgs[0]

            if flag:  # 第一次修改assembly文件

                # {ctg_name: "cut_site"}
                cut_ctg_name_site[first_ctg[0]] = error_queue[error]["start"] * ratio
                asy_operate.cut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)
                flag = False  # 标记为已经第一次修改过
            else:
                cut_ctg_name_site[first_ctg[0]] = error_queue[error]["start"] * ratio
                asy_operate.cut_ctgs(modified_assembly_file, cut_ctg_name_site, modified_assembly_file)

            # 切割最后一个ctg
            last_ctg = error_contain_ctgs[-1]
            cut_ctg_name_site[last_ctg[0]] = error_queue[error]["end"] * ratio
            asy_operate.cut_ctgs(modified_assembly_file, cut_ctg_name_site, modified_assembly_file)

        else:  # 易位错误区间内只有一个ctg
            if flag:  # 第一次修改文件
                _ctg = error_contain_ctgs[0]

                # 将一个ctg切割为三个ctg
                asy_operate.cut_ctg_to_3(modified_assembly_file, _ctg[0], error_queue[error]["start"],
                                         error_queue[error]["end"], modified_assembly_file)
                flag = False  # 标记为已经第一次修改过

        logger.info("易位错误的边界ctgs切割完成 \n")

        logger.info("重新查询易位错误区间包含的ctgs")
        new_error_contain_ctgs = asy_operate.find_site_ctgs(modified_assembly_file, error_queue[error]["start"],
                                                            error_queue[error]["end"])

        new_error_contain_ctgs = json.loads(new_error_contain_ctgs)  # 将字符串转换为字典

        logger.info("需要移动的ctgs: %s \n", new_error_contain_ctgs)

        logger.info("开始查询易位错误的插入位点：")
        # 依次获取错误的插入ctg位点
        error_site = (error_queue[error]["start"], error_queue[error]["end"])
        temp_result, insert_left = search_right_site_v2(hic_file, assembly_file, ratio, error_site)
        error_mdy_info[error] = {
            "move_ctgs": new_error_contain_ctgs,
            "insert_site": temp_result,
            "direction": insert_left
        }
        logger.info("易位错误的插入位点查询完成 \n")

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
            "start": 495140001,
            "end": 499424992
        },
        "error_2": {
            "start": 453010131,
            "end": 455241282
        }
    }

    # hic文件路径
    hic_file = "/home/jzj/Auto-HiC/Test/Np-Self/Np.0.hic"

    # assembly文件路径
    assembly_file = "/home/jzj/Auto-HiC/Test/asy_test/Np.0.assembly"

    # 修改后assembly文件路径
    modified_assembly_file = "/home/jzj/Downloads/2_ctg.assembly"

    adjust_translocation(error_queue, hic_file, assembly_file, modified_assembly_file)


if __name__ == "__main__":
    main()

#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: dynamic_modify_assembly.py
@time: 7/21/22 3:23 PM
@function: 根据易位的错误队列，动态修改assembly文件,并整合流程
"""

import json
from collections import OrderedDict

from assembly.tools.cut_ctg import insert_site
from assembly.tools.cut_ctg_to3 import cut_ctg_to_three
from assembly.tools.find_site_ctgs import find_site_ctgs
from assembly.tools.move_ctgs import move_ctgs_toback
from autohic.utils.logger import LoggerHandler
from assembly.tools.search_right_site_V2 import search_right_site_v2

# 初始化日志
logger = LoggerHandler()


def adjust_errors(error_queue, hic_file, ratio, assembly_file, modified_assembly_file):
    # 错误插入位点记录
    error_insert_site = OrderedDict()

    # 插入 left or right
    insert_left = None

    flag = True  # 用于文件修改判断

    for error in error_queue:
        logger.info("正在修改 {0} ".format(error))
        # 对错误进行ctg 切割
        # 查找错误区间中包含的ctgs
        error_contain_ctgs = find_site_ctgs(error_queue[error]["start"], error_queue[error]["end"], ratio,
                                            assembly_file)
        error_contain_ctgs = json.loads(error_contain_ctgs)  # 将字符串转换为字典
        error_contain_ctgs = list(error_contain_ctgs.items())  # 将字典转换为列表

        # 对错误区间中包含的ctgs进行切割,判断情况
        if len(error_contain_ctgs) >= 2:
            # 切割第一个ctg
            first_ctg = error_contain_ctgs[0]

            if flag:  # 第一次修改文件
                insert_site(assembly_file, first_ctg[0], error_queue[error]["start"] * ratio, modified_assembly_file)
                flag = False
            else:
                insert_site(modified_assembly_file, first_ctg[0], error_queue[error]["start"] * ratio,
                            modified_assembly_file)

            # 切割最后一个ctg
            last_ctg = error_contain_ctgs[-1]
            insert_site(modified_assembly_file, last_ctg[0], error_queue[error]["end"] * ratio, modified_assembly_file)

        else:  # 只有一个ctg
            if flag:  # 第一次修改文件
                _ctg = error_contain_ctgs[0]

                # 将一个ctg切割为三个ctg
                cut_ctg_to_three(modified_assembly_file, _ctg[0], error_queue[error]["start"],
                                 error_queue[error]["end"],
                                 modified_assembly_file)
                flag = False

        logger.info("切割完成")
        new_error_contain_ctgs = find_site_ctgs(error_queue[error]["start"], error_queue[error]["end"], ratio,
                                                modified_assembly_file)
        new_error_contain_ctgs = json.loads(new_error_contain_ctgs)  # 将字符串转换为字典

        logger.info("需要移动的ctgs: %s", new_error_contain_ctgs)

        logger.info("查询插入位点")
        # 依次获取错误的插入ctg位点
        error_site = (error_queue[error]["start"], error_queue[error]["end"])
        temp_result, insert_left = search_right_site_v2(hic_file, assembly_file, ratio, error_site)
        error_insert_site[error] = {
            "move_ctgs": new_error_contain_ctgs,
            "insert_site": temp_result
        }
    logger.info("错误插入位点记录:%s", error_insert_site)

    move_ctgs_toback(modified_assembly_file, error_insert_site)

    logger.info("RESULT： %s", error_insert_site)
    logger.info("修改完成")


def main():
    # 错误队列，其中的start和end是基于hic文件上的位置，没有转换为基因组上的位置
    error_queue = {
        "error_1": {
            "start": 495140001,
            "end": 499424992
        }
    }

    # hic文件路径
    hic_file = "/home/jzj/Auto-HiC/Test/Np-Self/Np.0.hic"

    ratio = 2  # 染色体长度比例

    # assembly文件路径
    assembly_file = "/home/jzj/buffer/Np.0.assembly"

    # 修改后assembly文件路径
    modified_assembly_file = "/home/jzj/Downloads/modified_test.assembly"

    adjust_errors(error_queue, hic_file, ratio, assembly_file, modified_assembly_file)


if __name__ == "__main__":
    main()

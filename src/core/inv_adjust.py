#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: inv_adjust.py
@time: 9/6/22 2:53 PM
@function: 反转调整流程整合
"""

import json
from collections import OrderedDict

from src.assembly.asy_operate import AssemblyOperate
from src.core.utils.get_ratio import get_ratio
from src.core.utils.logger import LoggerHandler

# 初始化日志
logger = LoggerHandler()


def adjust_inversion(error_queue, hic_file, assembly_file, modified_assembly_file):
    logger.info("Start adjust inversion \n")

    # 获取染色体长度比例
    ratio = get_ratio(hic_file, assembly_file)

    # 实例化AssemblyOperate类
    asy_operate = AssemblyOperate(assembly_file, ratio)

    flag = True  # 用于文件修改判断
    cut_ctg_name_site = {}  # 存放切割的染色体名和位置

    error_inv_info = OrderedDict()  # 错误 和 需要调整的反转信息

    # 循环反转错误队列
    for error in error_queue:
        logger.info("开始计算 {0} 的调整信息：".format(error))

        # 查找反转错误区间中包含的ctgs
        error_contain_ctgs = asy_operate.find_site_ctgs(assembly_file, error_queue[error]["start"],
                                                        error_queue[error]["end"])
        error_contain_ctgs = json.loads(error_contain_ctgs)  # 将字符串转换为字典
        error_contain_ctgs = list(error_contain_ctgs.items())  # 将字典转换为列表

        logger.info("开始切割反转错误的边界ctgs：")

        # 对反转错误区间中包含的ctgs进行切割,判断情况
        if len(error_contain_ctgs) >= 2:  # 反转错误区间内包含两个或两个以上的ctgs

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

        else:  # 反转错误区间内只有一个ctg
            _ctg = error_contain_ctgs[0]  # ctg_name

            _ctg_info = asy_operate.get_ctg_info(ctg_name=_ctg[0], new_asy_file=assembly_file)  # 获取ctg信息

            cut_ctg_site_start = error_queue[error]["start"] * ratio  # 错误真实起始位置
            cut_ctg_site_end = error_queue[error]["end"] * ratio  # 错误真实终止位置

            # 判断该ctg的位置情况
            if _ctg_info["site"][0] == cut_ctg_site_start:  # 左边界重合，一切二即可
                cut_ctg_name_site[_ctg[0]] = cut_ctg_site_end
                if flag:  # 第一次修改文件

                    # 将一个ctg切割为二个ctg
                    asy_operate.cut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)
                    flag = False  # 标记为已经第一次修改过

                else:
                    # 将一个ctg切割为二个ctg
                    asy_operate.cut_ctgs(modified_assembly_file, cut_ctg_name_site, modified_assembly_file)

            elif _ctg_info["site"][1] == cut_ctg_site_end:  # 右边界重合，一切二即可
                cut_ctg_name_site[_ctg[0]] = cut_ctg_site_start
                if flag:  # 第一次修改文件
                    # 将一个ctg切割为二个ctg
                    asy_operate.cut_ctgs(assembly_file, cut_ctg_name_site, modified_assembly_file)
                    flag = False  # 标记为已经第一次修改过

                else:
                    # 将一个ctg切割为二个ctg
                    asy_operate.cut_ctgs(modified_assembly_file, cut_ctg_name_site, modified_assembly_file)

            else:  # 不存在边界情况，一切三
                if flag:  # 第一次修改文件
                    # 将一个ctg切割为三个ctg
                    asy_operate.cut_ctg_to_3(assembly_file, _ctg[0], cut_ctg_site_start,
                                             cut_ctg_site_end, modified_assembly_file)
                    flag = False  # 标记为已经第一次修改过

                else:
                    # 将一个ctg切割为三个ctg
                    asy_operate.cut_ctg_to_3(modified_assembly_file, _ctg[0], cut_ctg_site_start,
                                             cut_ctg_site_end, modified_assembly_file)
        logger.info("反转错误的边界ctgs切割完成 \n")

        logger.info("重新查询反转错误区间包含的ctgs")
        new_error_contain_ctgs = asy_operate.find_site_ctgs(modified_assembly_file, error_queue[error]["start"],
                                                            error_queue[error]["end"])

        new_error_contain_ctgs = json.loads(new_error_contain_ctgs)  # 将字符串转换为字典

        logger.info("需要翻转的ctgs: %s \n", new_error_contain_ctgs)

        error_inv_info[error] = {
            "inv_ctgs": list(new_error_contain_ctgs.keys())
        }

    logger.info("开始对所有反转错误进行调整：")

    # 开始翻转记录的ctgs
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
    hic_file = "/home/jzj/Data/Test/asy_test/random_Np/Np.final.hic"

    # assembly文件路径
    assembly_file = "/home/jzj/Data/Test/asy_test/random_Np/Np.final.assembly"

    # 修改后assembly文件路径
    modified_assembly_file = "/home/jzj/buffer/test.assembly"

    adjust_inversion(error_queue, hic_file, assembly_file, modified_assembly_file)


if __name__ == "__main__":
    main()

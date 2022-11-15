#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: inv_adjust.py
@time: 10/7/22 10:27 AM
@function: 反转调整流程整合
"""
import re
import json
from collections import OrderedDict

from src.assembly.asy_operate import AssemblyOperate
from src.core.utils.get_ratio import get_ratio
from src.core.utils.logger import logger


def adjust_inversion(error_queue, hic_file, assembly_file, modified_assembly_file):
    logger.info("Start adjust inversion \n")

    # 获取染色体长度比例
    ratio = get_ratio(hic_file, assembly_file)

    # 实例化AssemblyOperate类
    asy_operate = AssemblyOperate(assembly_file, ratio)

    cut_ctg_name_site = {}  # 存放切割的染色体名和位置

    error_inv_info = OrderedDict()  # 错误 和 需要调整的反转信息

    # flag = True  # 用于文件修改判断
    # if flag:  # 第一次修改assembly文件
    #     flag = False
    # else:
    #     assembly_file = modified_assembly_file

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

        else:  # 反转错误区间内只有一个ctg
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
    # for error in error_inv_info:
    #     for inv_ctg in error_inv_info[error]["inv_ctgs"]:
    #         asy_operate.inv_ctg(inv_ctg, modified_assembly_file, modified_assembly_file)

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

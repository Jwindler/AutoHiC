#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: deb_adjust.py
@time: 10/7/22 10:27 AM
@function:
"""
import re
import json
from collections import OrderedDict

from src.assembly.asy_operate import AssemblyOperate
from src.core.utils.get_ratio import get_ratio
from src.core.utils.logger import logger


def adjust_debris(error_queue, hic_file, assembly_file, modified_assembly_file):
    logger.info("Start adjust debris \n")

    # 获取染色体长度比例
    ratio = get_ratio(hic_file, assembly_file)

    # 实例化AssemblyOperate类
    asy_operate = AssemblyOperate(assembly_file, ratio)

    cut_ctg_name_site = {}  # 存放切割的染色体名和位置

    error_deb_info = OrderedDict()  # 错误 和 需要调整的冗余信息

    # flag = True  # 用于文件修改判断
    # if flag:  # 第一次修改assembly文件
    #     flag = False
    # else:
    #     assembly_file = modified_assembly_file

    # 循环冗余错误队列
    for error in error_queue:

        logger.info("开始计算 {0} 的调整信息：".format(error))

        # 查找冗余错误区间中包含的ctgs
        error_contain_ctgs = asy_operate.find_site_ctgs(assembly_file, error_queue[error]["start"],
                                                        error_queue[error]["end"])
        error_contain_ctgs = json.loads(error_contain_ctgs)  # 将字符串转换为字典
        error_contain_ctgs = list(error_contain_ctgs.items())  # 将字典转换为列表

        logger.info("开始切割冗余错误的边界ctgs：")

        # 对冗余错误区间中包含的ctgs进行切割,判断情况
        if len(error_contain_ctgs) >= 2:  # 冗余错误区间内包含两个或两个以上的ctgs

            # 切割第一个ctg
            first_ctg = error_contain_ctgs[0]
            cut_ctg_name_site[first_ctg[0]] = error_queue[error]["start"] * ratio

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

        else:  # 冗余错误区间内只有一个ctg
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

        logger.info("冗余错误的边界ctgs切割完成 \n")

        logger.info("重新查询冗余错误区间包含的ctgs")
        new_error_contain_ctgs = asy_operate.find_site_ctgs(modified_assembly_file, error_queue[error]["start"],
                                                            error_queue[error]["end"])

        new_error_contain_ctgs = json.loads(new_error_contain_ctgs)  # 将字符串转换为字典

        logger.info("需要移动冗余的ctgs: %s \n", new_error_contain_ctgs)

        error_deb_info[error] = {
            "deb_ctgs": list(new_error_contain_ctgs.keys())
        }

    logger.info("开始对所有冗余错误进行调整：")

    # 开始翻转记录的ctgs
    # for error in error_deb_info:
    #     asy_operate.move_deb_to_end(modified_assembly_file, error_deb_info[error]["deb_ctgs"], modified_assembly_file)

    logger.info("所有冗余错误调整完成 \n")

    logger.info("所有冗余错误的调整信息： %s \n", error_deb_info)
    logger.info("All Done! \n")


def main():
    # 错误队列，其中的start和end是基于hic文件上的位置，没有转换为基因组上的位置
    error_queue = {
        "error_1": {
            "start": 163482501,
            "end": 163820001
        }
        # "error_2": {
        #     "start": 280560061,
        #     "end": 284239273
        # }
    }

    # hic文件路径
    hic_file = "/home/jzj/Data/Test/Np-Self/Np.0.hic"

    # assembly文件路径
    assembly_file = "/home/jzj/Data/Test/Np-Self/Np.0.assembly"

    # 修改后assembly文件路径
    modified_assembly_file = "/home/jzj/buffer/test.assembly"

    adjust_debris(error_queue, hic_file, assembly_file, modified_assembly_file)


if __name__ == "__main__":
    main()

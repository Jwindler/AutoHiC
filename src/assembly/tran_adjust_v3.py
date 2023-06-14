#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: tran_adjust_v3.py.py
@time: 3/29/23 10:58 AM
@function: update translocation adjust and add black list
"""

import json
from collections import OrderedDict

from src.assembly.asy_operate import AssemblyOperate
from src.common.search_right_site_v8 import search_right_site_v8
from src.utils.get_cfg import get_ratio
from src.utils.logger import logger


def adjust_translocation(errors_queue, hic_file, modified_assembly_file, black_list_output, black_list=None):
    """
    Translocation adjust
    Args:
        errors_queue: error queue
        hic_file: hic file path
        modified_assembly_file: modified assembly file path
        black_list_output: black list output path
        black_list: the black list of ctg name

    Returns:
        translocation error information queue
    """

    logger.info("Start adjust translocation errors:\n")

    # get ratio of hic file and assembly file
    ratio = get_ratio(hic_file, modified_assembly_file)

    # class AssemblyOperate class
    asy_operate = AssemblyOperate(modified_assembly_file, ratio)

    # error modify information record
    error_tran_info = OrderedDict()

    black_list_set = None
    if black_list is not None:
        with open(black_list, "r") as outfile:
            black_list = outfile.readlines()
            black_list = [sub.replace('\n', '') for sub in black_list]
        black_list_set = set(black_list)

    # loop error queue
    for error in errors_queue:
        logger.info("Start calculate {0} insert information：\n".format(error))
        new_error_contains_ctg = asy_operate.find_site_ctg_s(modified_assembly_file, errors_queue[error]["start"],
                                                             errors_queue[error]["end"])

        new_error_contains_ctg = json.loads(new_error_contains_ctg)  # str to dict

        if black_list is not None:
            # error in black list
            error_set = set(new_error_contains_ctg)
            if error_set & black_list_set:
                logger.info("Error {0} in black list, skip\n".format(error))
                continue

        logger.info("Needs to be moved ctg: %s\n", new_error_contains_ctg)

        logger.info("Search {0} translocation error insert location：".format(error))

        # 插入位置如果没有找到，则跳过这个错误
        try:
            # get insert ctg site
            error_site = (errors_queue[error]["start"], errors_queue[error]["end"])
            temp_result, insert_left = search_right_site_v8(hic_file, modified_assembly_file, ratio, error_site,
                                                            modified_assembly_file)
        except Exception as e:
            logger.info("Error {0} insert location search failed, skip\n".format(error))
            continue
        new_error_contains_ctg = asy_operate.find_site_ctg_s(modified_assembly_file, errors_queue[error]["start"],
                                                             errors_queue[error]["end"])

        new_error_contains_ctg = json.loads(new_error_contains_ctg)  # str to dict

        error_tran_info[error] = {
            "moves_ctg": new_error_contains_ctg,
            "insert_site": temp_result,
            "direction": insert_left
        }

    logger.info("Translocation errors insert location search done\n")

    # write error information to blacklist
    with open(black_list_output, "a") as outfile:
        for index in error_tran_info:
            outfile.write("\n".join(list(error_tran_info[index]['moves_ctg'].keys())) + "\n")
    return error_tran_info


def main():
    pass


if __name__ == "__main__":
    main()

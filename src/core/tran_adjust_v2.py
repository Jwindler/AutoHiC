#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: tran_adjust_v2.py
@time: 3/2/23 3:16 PM
@function: 
"""

import json
from collections import OrderedDict

from src.assembly.asy_operate import AssemblyOperate
from src.core.utils.get_cfg import get_ratio
from src.core.utils.logger import logger
from core.search_right_site_v8 import search_right_site_v8


def adjust_translocation(errors_queue, hic_file, modified_assembly_file):
    """
    Translocation adjust
    Args:
        errors_queue: error queue
        hic_file: hic file path
        modified_assembly_file: modified assembly file path

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

    # loop error queue
    for error in errors_queue:
        logger.info("Start calculate {0} insert information：\n".format(error))
        new_error_contains_ctg = asy_operate.find_site_ctg_s(modified_assembly_file, errors_queue[error]["start"],
                                                             errors_queue[error]["end"])

        new_error_contains_ctg = json.loads(new_error_contains_ctg)  # str to dict

        logger.info("Needs to be moved ctg: %s\n", new_error_contains_ctg)

        logger.info("Search {0} translocation error insert location：".format(error))

        # get insert ctg site
        error_site = (errors_queue[error]["start"], errors_queue[error]["end"])
        temp_result, insert_left = search_right_site_v8(hic_file, modified_assembly_file, ratio, error_site,
                                                        modified_assembly_file)
        error_tran_info[error] = {
            "moves_ctg": new_error_contains_ctg,
            "insert_site": temp_result,
            "direction": insert_left
        }

        logger.info("Translocation errors insert location search done\n")
    return error_tran_info


def main():
    pass


if __name__ == "__main__":
    main()

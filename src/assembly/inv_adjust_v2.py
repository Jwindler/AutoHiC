#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: inv_adjust_v2.py
@time: 3/2/23 2:43 PM
@function: 
"""

import json
from collections import OrderedDict

from src.assembly.asy_operate import AssemblyOperate
from src.utils.get_cfg import get_ratio
from src.utils.logger import logger


def adjust_inversion(errors_queue, hic_file, modified_assembly_file, black_list_output, black_list=None):
    """
    Inversion adjust
    Args:
        errors_queue:
        hic_file:
        modified_assembly_file:
        black_list_output: black list output path
        black_list: the black list of ctg name

    Returns:
        inversion error information queue
    """
    logger.info("Start adjust inversion errors:\n")

    # get ratio between chromosome length and hic file length
    ratio = get_ratio(hic_file, modified_assembly_file)

    # initialize AssemblyOperate class
    asy_operate = AssemblyOperate(modified_assembly_file, ratio)

    error_inv_info = OrderedDict()  # inversion info

    black_list_set = None
    if black_list is not None:
        with open(black_list, "r") as outfile:
            black_list = outfile.readlines()
            black_list = [sub.replace('\n', '') for sub in black_list]
        black_list_set = set(black_list)

    # iterate error queue
    for error in errors_queue:
        logger.info("Re-search {0} inversion location ctg information:\n".format(error))
        new_error_contains_ctg = asy_operate.find_site_ctg_s(modified_assembly_file, errors_queue[error]["start"],
                                                             errors_queue[error]["end"])

        new_error_contains_ctg = json.loads(new_error_contains_ctg)  # convert str to dict

        if black_list is not None:
            # error in black list
            error_set = set(new_error_contains_ctg)
            if error_set & black_list_set:
                logger.info("Error {0} in black list, skip\n".format(error))
                continue

        logger.info("Needs to be moved ctg: %s\n", new_error_contains_ctg)

        error_inv_info[error] = {
            "inv_ctg": list(new_error_contains_ctg.keys())
        }

    # write error information to blacklist
    with open(black_list_output, "a") as outfile:
        for index in error_inv_info:
            outfile.write("\n".join(list(error_inv_info[index]['moves_ctg'].keys())) + "\n")

    return error_inv_info


def main():
    pass


if __name__ == "__main__":
    main()

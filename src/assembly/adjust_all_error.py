#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: adjust_all_error.py
@time: 3/2/23 3:20 PM
@function: 
"""

import json
import os
import shutil
from src.assembly.asy_operate import AssemblyOperate
from src.assembly.cut_errors_ctg import cut_errors_ctg
from src.assembly.deb_adjust_v3 import adjust_debris
from src.assembly.inv_adjust_v2 import adjust_inversion
from src.assembly.tran_adjust_v3 import adjust_translocation
from src.utils.get_cfg import get_ratio
from src.utils.logger import logger


def adjust_all_error(hic_file_path, asy_file_path, divided_error, modified_asy_file,
                     tran_flag, inv_flag, deb_flag, black_list=None):
    """
        adjust all error
    Args:
        hic_file_path: hic file path
        asy_file_path: assembly file path
        divided_error: divided error path
        modified_asy_file: modified assembly file path
        black_list: black list
        tran_flag: whether to adjust translocation
        inv_flag: whether to adjust inversion
        deb_flag: whether to adjust debris

    Returns:
        None
    """
    tran_black_num = 0
    inv_black_num = 0

    # translocation rectify
    if os.path.exists(os.path.join(divided_error, "translocation_error.json")) and tran_flag:
        with open(os.path.join(divided_error, "translocation_error.json"), "r") as outfile:
            translocation_queue = outfile.read()
            translocation_queue = json.loads(translocation_queue)

        cut_errors_ctg(translocation_queue, hic_file_path, asy_file_path, modified_asy_file)
        asy_file_path = modified_asy_file
        logger.info("Translocation rectify done\n")
    else:
        logger.info("No translocation error\n")

    # inversion rectify
    if os.path.exists(os.path.join(divided_error, "inversion_error.json")) and inv_flag:
        with open(os.path.join(divided_error, "inversion_error.json"), "r") as outfile:
            inversion_queue = outfile.read()
            inversion_queue = json.loads(inversion_queue)

        cut_errors_ctg(inversion_queue, hic_file_path, asy_file_path, modified_asy_file)
        asy_file_path = modified_asy_file
        logger.info("Inversion rectify done")
    else:
        logger.info("No inversion error")

    # debris rectify
    if os.path.exists(os.path.join(divided_error, "debris_error.json")) and deb_flag:
        with open(os.path.join(divided_error, "debris_error.json"), "r") as outfile:
            debris_queue = outfile.read()
            debris_queue = json.loads(debris_queue)

        cut_errors_ctg(debris_queue, hic_file_path, asy_file_path, modified_asy_file)
        logger.info("Debris rectify done")
    else:
        logger.info("No debris error")

    # if not detect error, return old assembly file
    if os.path.exists(modified_asy_file) is False:
        shutil.copy(asy_file_path, modified_asy_file)

    # Define error info
    error_tran_info, error_inv_info, error_deb_info = None, None, None

    # black_list_output
    black_list_output = os.path.join(os.path.dirname(modified_asy_file), "black_list.txt")

    # move translocation ctg
    if os.path.exists(os.path.join(divided_error, "translocation_error.json")) and tran_flag:
        tran_black_num, error_tran_info = adjust_translocation(translocation_queue, hic_file_path, modified_asy_file,
                                                               black_list_output=black_list_output,
                                                               black_list=black_list)
    # move inversion ctg
    if os.path.exists(os.path.join(divided_error, "inversion_error.json")) and inv_flag:
        inv_black_num, error_inv_info = adjust_inversion(inversion_queue, hic_file_path, modified_asy_file,
                                                         black_list_output=black_list_output, black_list=black_list)

    # move debris ctg
    if os.path.exists(os.path.join(divided_error, "debris_error.json")) and deb_flag:
        error_deb_info = adjust_debris(debris_queue, hic_file_path, modified_asy_file)

    # get ratio of hic file and assembly file
    ratio = get_ratio(hic_file_path, modified_asy_file)

    # class AssemblyOperate class
    asy_operate = AssemblyOperate(modified_asy_file, ratio)

    if os.path.exists(os.path.join(divided_error, "translocation_error.json")) and tran_flag:
        logger.info("Start moving translocation ctg\n")
        asy_operate.moves_ctg(modified_asy_file, error_tran_info, modified_asy_file)
        logger.info("Moving translocation ctg done\n")

    if os.path.exists(os.path.join(divided_error, "inversion_error.json")) and inv_flag:
        logger.info("Start moving inversion ctg\n")
        asy_operate.inv_ctg_s(modified_asy_file, error_inv_info, modified_asy_file)
        logger.info("Moving inversion ctg done\n")

    if os.path.exists(os.path.join(divided_error, "debris_error.json")) and deb_flag:
        logger.info("Start moving debris ctg\n")
        asy_operate.move_deb_to_end(modified_asy_file, error_deb_info, modified_asy_file)
        logger.info("Moving debris ctg done\n")

    return [tran_black_num, inv_black_num, tran_black_num + inv_black_num]


def main():
    pass


if __name__ == "__main__":
    main()

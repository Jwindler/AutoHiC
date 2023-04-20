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

from src.assembly.asy_operate import AssemblyOperate
from src.core.utils.get_cfg import get_ratio
from src.core.utils.logger import logger
from assembly.cut_errors_ctg import cut_errors_ctg
from core.deb_adjust_v3 import adjust_debris
from core.inv_adjust_v2 import adjust_inversion
from core.tran_adjust_v3 import adjust_translocation


def adjust_all_error(hic_file_path, assembly_file_path, divided_error, modified_assembly_file, black_list=None):
    # translocation rectify
    if os.path.exists(os.path.join(divided_error, "translocation_error.json")):
        with open(os.path.join(divided_error, "translocation_error.json"), "r") as outfile:
            translocation_queue = outfile.read()
            translocation_queue = json.loads(translocation_queue)

        cut_errors_ctg(translocation_queue, hic_file_path, assembly_file_path, modified_assembly_file)
        assembly_file_path = modified_assembly_file
        logger.info("translocation rectify done")
    else:
        logger.info("no translocation error")

    # inversion rectify
    if os.path.exists(os.path.join(divided_error, "inversion_error.json")):
        with open(os.path.join(divided_error, "inversion_error.json"), "r") as outfile:
            inversion_queue = outfile.read()
            inversion_queue = json.loads(inversion_queue)

        cut_errors_ctg(inversion_queue, hic_file_path, assembly_file_path, modified_assembly_file)
        assembly_file_path = modified_assembly_file
        logger.info("inversion rectify done")
    else:
        logger.info("no inversion error")

    # debris rectify
    if os.path.exists(os.path.join(divided_error, "debris_error.json")):
        with open(os.path.join(divided_error, "debris_error.json"), "r") as outfile:
            debris_queue = outfile.read()
            debris_queue = json.loads(debris_queue)

        cut_errors_ctg(debris_queue, hic_file_path, assembly_file_path, modified_assembly_file)
        logger.info("debris rectify done")
    else:
        logger.info("no debris error")

    # Define error info
    error_tran_info, error_inv_info, error_deb_info = None, None, None

    # move translocation ctg
    if os.path.exists(os.path.join(divided_error, "translocation_error.json")):
        black_list_output = os.path.join(divided_error, "black_list.txt")
        error_tran_info = adjust_translocation(translocation_queue, hic_file_path, modified_assembly_file,
                                               black_list_output=black_list_output, black_list=black_list)

    # move inversion ctg
    if os.path.exists(os.path.join(divided_error, "inversion_error.json")):
        error_inv_info = adjust_inversion(inversion_queue, hic_file_path, modified_assembly_file)

    # move debris ctg
    if os.path.exists(os.path.join(divided_error, "debris_error.json")):
        error_deb_info = adjust_debris(debris_queue, hic_file_path, modified_assembly_file, black_list=black_list)

    # get ratio of hic file and assembly file
    ratio = get_ratio(hic_file_path, modified_assembly_file)

    # class AssemblyOperate class
    asy_operate = AssemblyOperate(modified_assembly_file, ratio)

    if os.path.exists(os.path.join(divided_error, "translocation_error.json")):
        logger.info("Start moving translocation ctg\n")
        asy_operate.moves_ctg(modified_assembly_file, error_tran_info, modified_assembly_file)
        logger.info("Moving translocation ctg done\n")

    if os.path.exists(os.path.join(divided_error, "inversion_error.json")):
        logger.info("Start moving inversion ctg\n")
        asy_operate.inv_ctg_s(modified_assembly_file, error_inv_info, modified_assembly_file)
        logger.info("Moving inversion ctg done\n")

    if os.path.exists(os.path.join(divided_error, "debris_error.json")):
        logger.info("Start moving debris ctg\n")
        asy_operate.move_deb_to_end(modified_assembly_file, error_deb_info, modified_assembly_file)
        logger.info("Moving debris ctg done\n")


def main():
    hic_file_path = "/home/jzj/Jupyter-Docker/buffer/silkworm_5/silkworm.5.hic"
    assembly_file_path = "/home/jzj/Jupyter-Docker/buffer/silkworm_5/silkworm.5.assembly"

    divided_error = "/home/jzj/Jupyter-Docker/buffer/silkworm_5"

    # 输出文件路径
    modified_assembly_file = "/home/jzj/Jupyter-Docker/buffer/silkworm_6/test.assembly"
    black_list = None

    adjust_all_error(hic_file_path, assembly_file_path, divided_error, modified_assembly_file, black_list)


if __name__ == "__main__":
    main()

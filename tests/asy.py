#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: asy.py
@time: 2/23/23 3:38 PM
@function: 
"""

import json
import os

from src.assembly.asy_operate import AssemblyOperate
from src.core.deb_adjust import adjust_debris
from src.core.inv_adjust import adjust_inversion
from src.core.tran_adjust import adjust_translocation
from src.core.utils.get_ratio import get_ratio

hic_asy_path = "/home/jzj/Jupyter-Docker/buffer/01_ci/ci_2"
hic_file_path = os.path.join(hic_asy_path, "ci.2.hic")

assembly_file_path = os.path.join(hic_asy_path, "ci.2.assembly")

divided_error = "/home/jzj/Jupyter-Docker/buffer/01_ci/ci_2/test_all"

# 输出文件路径
modified_assembly_file = os.path.join(divided_error, "test_all.assembly")

# define variable
error_deb_info = None
error_tran_info = None
error_inv_info = None

# translocation rectify
if os.path.exists(os.path.join(divided_error, "translocation_error.json")):
    with open(os.path.join(divided_error, "translocation_error.json"), "r") as outfile:
        translocation_queue = outfile.read()
        translocation_queue = json.loads(translocation_queue)

    error_tran_info = adjust_translocation(translocation_queue, hic_file_path, assembly_file_path,
                                           modified_assembly_file)

    print("translocation rectify done")
else:
    print("no translocation error")

# inversion rectify
if os.path.exists(os.path.join(divided_error, "inversion_error.json")):
    with open(os.path.join(divided_error, "inversion_error.json"), "r") as outfile:
        inversion_queue = outfile.read()
        inversion_queue = json.loads(inversion_queue)

    error_inv_info = adjust_inversion(inversion_queue, hic_file_path, modified_assembly_file, modified_assembly_file)

    print("inversion rectify done")
else:
    print("no inversion error")

# debris rectify
if os.path.exists(os.path.join(divided_error, "debris_error.json")):
    with open(os.path.join(divided_error, "debris_error.json"), "r") as outfile:
        debris_queue = outfile.read()
        debris_queue = json.loads(debris_queue)

    error_deb_info = adjust_debris(debris_queue, hic_file_path, modified_assembly_file, modified_assembly_file)

    print("debris rectify done")
else:
    print("no debris error")

# get ratio of hic file and assembly file
ratio = get_ratio(hic_file_path, assembly_file_path)

# class AssemblyOperate class
asy_operate = AssemblyOperate(modified_assembly_file, ratio)

# move ctg
# translocation
asy_operate.moves_ctg(modified_assembly_file, error_tran_info, modified_assembly_file)

# inversion
asy_operate.ins_ctg(modified_assembly_file, error_inv_info, modified_assembly_file)

# debris
asy_operate.move_deb_to_end(modified_assembly_file, error_deb_info, modified_assembly_file)

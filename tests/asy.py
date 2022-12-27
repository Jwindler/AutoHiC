#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: asy.py
@time: 11/11/22 3:38 PM
@function: 
"""
import os
import json
from src.core.deb_adjust import adjust_debris
from src.core.inv_adjust import adjust_inversion
from src.core.tran_adjust import adjust_translocation

# 初始化日志

hic_asy_path = "/home/jzj/Downloads"
hic_file_path = os.path.join(hic_asy_path, "cs.final.hic")
assembly_file_path = os.path.join(hic_asy_path, "cs.final.assembly")

divided_error = "/home/jzj/Jupyter-Docker/buffer/result"

modified_assembly_file = os.path.join(divided_error, "only_tran_adjusted.assembly")
# modified_assembly_file = os.path.join(divided_error, "no_move_only_tran_adjusted.assembly")

# rectify all category errors

if os.path.exists(os.path.join(divided_error, "translocation_error.json")):
    with open(os.path.join(divided_error, "translocation_error.json"), "r") as outfile:
        translocation_queue = outfile.read()
        translocation_queue = json.loads(translocation_queue)

    # translocation rectify
    # adjust_translocation(translocation_queue, hic_file_path, assembly_file_path, modified_assembly_file, move_flag=False)
    adjust_translocation(translocation_queue, hic_file_path, assembly_file_path, modified_assembly_file)

    print("translocation rectify done")

# if os.path.exists(os.path.join(divided_error, "inversion_error.json")):
#     with open(os.path.join(divided_error, "inversion_error.json"), "r") as outfile:
#         inversion_queue = outfile.read()
#         inversion_queue = json.loads(inversion_queue)
#
#     # inversion rectify
#     adjust_inversion(inversion_queue, hic_file_path, modified_assembly_file, modified_assembly_file)
#
#     print("inversion rectify done")
#
# if os.path.exists(os.path.join(divided_error, "debris_error.json")):
#     with open(os.path.join(divided_error, "debris_error.json"), "r") as outfile:
#         debris_queue = outfile.read()
#         debris_queue = json.loads(debris_queue)
#
#     # debris rectify
#     # adjust_debris(debris_queue, hic_file_path, modified_assembly_file, modified_assembly_file)  # no move
#     adjust_debris(debris_queue, hic_file_path, modified_assembly_file, modified_assembly_file, move_flag=True)  # move

#    print("debris rectify done")

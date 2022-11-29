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


hic_file = "/home/jzj/Data/Test/asy_test/double/Np/Np.final.hic"
assembly_file = "/home/jzj/Data/Test/asy_test/double/Np/Np.final.assembly"
modified_assembly_file = "/home/jzj/Jupyter-Docker/Download/result/Np_double/2_score_0.9/adjusted.assembly"

divided_error = "/home/jzj/Jupyter-Docker/Download/result/Np_double/2_score_0.9"

with open(os.path.join(divided_error, "translocation_error.json"), "r") as outfile:
    translocation_queue = outfile.read()
    translocation_queue = json.loads(translocation_queue)

with open(os.path.join(divided_error, "inversion_error.json"), "r") as outfile:
    inversion_queue = outfile.read()
    inversion_queue = json.loads(inversion_queue)
#
with open(os.path.join(divided_error, "debris_error.json"), "r") as outfile:
    debris_queue = outfile.read()
    debris_queue = json.loads(debris_queue)

# rectify all category errors
# translocation rectify
# adjust_translocation(translocation_queue, hic_file, assembly_file, modified_assembly_file, move_flag=False)
adjust_translocation(translocation_queue, hic_file, assembly_file, modified_assembly_file)

print("translocation rectify done")

# inversion rectify
adjust_inversion(inversion_queue, hic_file, modified_assembly_file, modified_assembly_file)

print("inversion rectify done")
#
# debris rectify
# adjust_debris(debris_queue, hic_file, modified_assembly_file, modified_assembly_file)
adjust_debris(debris_queue, hic_file, modified_assembly_file, modified_assembly_file, move_flag=True)

print("debris rectify done")

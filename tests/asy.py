#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: asy.py
@time: 11/11/22 3:38 PM
@function: 
"""
import json
from src.core.deb_adjust import adjust_debris
from src.core.inv_adjust import adjust_inversion
from src.core.tran_adjust import adjust_translocation

hic_file = "/home/jzj/Data/Test/raw_data/Np/Np.0.hic"
assembly_file = "/home/jzj/Data/Test/raw_data/Np/Np.0.assembly"
modified_assembly_file = "/home/jzj/Jupyter-Docker/Download/test.assembly"

with open("/home/jzj/Jupyter-Docker/Download/tran_error.json", "r") as outfile:
    translocation_queue = outfile.read()
    translocation_queue = json.loads(translocation_queue)

with open("/home/jzj/Jupyter-Docker/Download/inv_error.json", "r") as outfile:
    inversion_queue = outfile.read()
    inversion_queue = json.loads(inversion_queue)

with open("/home/jzj/Jupyter-Docker/Download/deb_error.json", "r") as outfile:
    debris_queue = outfile.read()
    debris_queue = json.loads(debris_queue)

# rectify all category errors
# translocation rectify
adjust_translocation(translocation_queue, hic_file, assembly_file, modified_assembly_file)

# inversion rectify
adjust_inversion(inversion_queue, hic_file, assembly_file, modified_assembly_file)

# debris rectify
adjust_debris(debris_queue, hic_file, assembly_file, modified_assembly_file)

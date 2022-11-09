#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: derrors.py
@time: 11/08/22 7:22 PM
@function: 整合纠错全部流程
"""

import json

from src.core.deb_adjust import adjust_debris
from src.core.inv_adjust import adjust_inversion
from src.core.tran_adjust import adjust_translocation
from tests.error import ERRORS
from tests.test import inference_detector


def gen_errors(model, classes, info_file, epoch_flag=None):
    infos = []  # save generated jpgs info

    # read info file
    with open(info_file, "r") as f:
        for line in f.readlines():
            info = json.loads(line)
            infos.append(info)

    # instantiating ERRORS class
    instance_class = ERRORS(classes, info_file)

    for info in infos:  # loop all images
        # inference
        detection_result = inference_detector(model, list(info.keys())[0])

        # create error structure
        instance_class.create_structure(info, detection_result)

    # filter errors with score
    filtered_errors = instance_class.filter_all_errors(score=0.9, filter_cls=classes)

    # remove all category duplicate errors
    filtered_errors = instance_class.de_diff_overlap(filtered_errors, iou_score=0.9)

    return filtered_errors


def rectify_flow(filtered_errors, hic_file, assembly_file, modified_assembly_file):
    # rectify all category errors
    # translocation rectify
    adjust_translocation(filtered_errors["translocation"], hic_file, assembly_file, modified_assembly_file)

    # inversion rectify
    adjust_inversion(filtered_errors["inversion"], hic_file, assembly_file, modified_assembly_file)

    # debris rectify
    adjust_debris(filtered_errors["debris"], hic_file, assembly_file, modified_assembly_file)


def main():
    model = None
    classes = ("translocation", "inversion", "debris", "chromosome")
    info_file = "/home/jovyan/Download/Np/info.txt"
    hic_file = "/home/jovyan/Download/Np/chr1_1.hic"
    assembly_file = "/home/jovyan/Download/Np/chr1_1.fa"
    modified_assembly_file = "/home/jovyan/Download/Np/chr1_1_modified.fa"
    filtered_errors = gen_errors(model, classes, info_file, epoch_flag=None)
    rectify_flow(filtered_errors, hic_file, assembly_file, modified_assembly_file)


if __name__ == "__main__":
    main()

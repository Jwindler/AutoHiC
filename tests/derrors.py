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


def gen_errors(model, classes, info_file, epoch_flag=0):
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

        # FIXME: 个人主机上 内存可能不够， 服务区上可以没有显卡
        # create error structure
        instance_class.create_structure(info, detection_result, epoch_flag)

    # filter errors with score
    filtered_errors = instance_class.filter_all_errors(score=0.9, filter_cls=classes)

    # remove all category duplicate errors
    filtered_errors = instance_class.de_diff_overlap(filtered_errors, iou_score=0.9)

    return filtered_errors


def rectify_flow(filtered_errors, hic_file, assembly_file, modified_assembly_file):
    translocation_queue, inversion_queue, debris_queue = dict(), dict(), dict()

    # rectify all category errors
    # translocation rectify
    for tran_error in filtered_errors["translocation"]:
        translocation_queue[tran_error["id"]] = {
            "start": tran_error["hic_loci"][0],
            "end": tran_error["hic_loci"][1],
        }
    adjust_translocation(translocation_queue, hic_file, assembly_file, modified_assembly_file)

    # inversion rectify
    for inv_error in filtered_errors["inversion"]:
        inversion_queue[inv_error["id"]] = {
            "start": inv_error["hic_loci"][0],
            "end": inv_error["hic_loci"][1],
        }
    adjust_inversion(inversion_queue, hic_file, assembly_file, modified_assembly_file)

    # debris rectify
    for deb_error in filtered_errors["debris"]:
        debris_queue[deb_error["id"]] = {
            "start": deb_error["hic_loci"][0],
            "end": deb_error["hic_loci"][1],
        }
    adjust_debris(debris_queue, hic_file, assembly_file, modified_assembly_file)


def main():
    model = None
    classes = ("translocation", "inversion", "debris", "chromosome")
    info_file = "/home/jovyan/Download/Np/info.txt"
    hic_file = "/home/jovyan/Download/Np/chr1_1.hic"
    assembly_file = "/home/jovyan/Download/Np/chr1_1.fa"
    modified_assembly_file = "/home/jovyan/Download/Np/chr1_1_modified.fa"
    filtered_errors = gen_errors(model, classes, info_file, epoch_flag=0)
    rectify_flow(filtered_errors, hic_file, assembly_file, modified_assembly_file)


if __name__ == "__main__":
    main()

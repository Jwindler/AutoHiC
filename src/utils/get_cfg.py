#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: get_cfg.py
@time: 2/14/23 8:52 PM
@function: get hic file real length
"""

import json
import math
import os
import subprocess

import hicstraw
import numpy as np

from src.assembly.asy_operate import AssemblyOperate
from src.report.gen_report import image_to_base64
from src.utils.logger import logger


def get_ratio(hic, asy_file) -> int:
    """
        get the ratio of the actual length of the chromosome and the length of the chromosome in the assembly file
    Args:
        hic: hic file path
        asy_file: assembly file path

    Returns:
        ratio: assembly length / hic length
    """

    # class Assembly class
    temp = AssemblyOperate(asy_file, ratio=None)

    # get the length of the chromosome in the assembly file
    asy_length = temp.get_info().get("seq_length", "")

    hic_length = 0

    # get hic object
    hic = hicstraw.HiCFile(hic)
    for chrom in hic.getChromosomes():
        hic_length = chrom.length

    logger.info("Ratio(assembly length / hic length) is %s\n", asy_length / hic_length)

    return asy_length / hic_length


def get_hic_len(hic_file) -> int:
    """
        get hic file length
    Args:
        hic_file: hic file path

    Returns:
        hic file length
    """
    # get hic object
    hic_object = hicstraw.HiCFile(hic_file)

    hic_len = None  # hic_object length
    for chrom in hic_object.getChromosomes():
        hic_len = chrom.length
    logger.info("Hic file full length is %s\n" % hic_len)
    return hic_len


def get_hic_real_len(hic_file, asy_file) -> int:
    """
        get hic file real length
    Args:
        hic_file: hic file path
        asy_file: assembly file path

    Returns:
        hic file real length
    """

    # get ratio: asy_length / hic_length
    ratio = get_ratio(hic_file, asy_file)

    all_seqs_len = 0  # sequence total length
    real_seqs_len = 0  # real sequence total length

    ctg_dict = {}  # ctg number and length

    # get ctg dict and total length
    with open(asy_file, "r") as f:
        for line in f:
            if line.startswith(">"):
                # get ctg dict and length
                ctg_len = line.strip().split()[2]
                ctg_dict[int(line.strip().split()[1])] = ctg_len
                all_seqs_len += int(ctg_len)
            else:
                # calculate real sequence length
                for ctg in line.strip().split():
                    real_seqs_len += int(ctg_dict[abs(int(ctg))])
                break
    logger.info("Hic file real len: %s\n", round(real_seqs_len / ratio))
    return round(real_seqs_len / ratio)


def increment(resolution):
    """
        get resolution increment
    Args:
        resolution: hic resolution

    Returns:
        resolution increment
    """

    dim_increase = {
        "increase": resolution * 400,
        "range": resolution * 700
    }

    return dim_increase


def get_max_hic_len(resolution):
    """
        get resolution increment
    Args:
        resolution: hic resolution

    Returns:
        resolution max length
    """

    return resolution * 1400


def get_max_color(hic_file, resolution):
    """
        get max color
    Args:
        hic_file: hic file path
        resolution: hic resolution

    Returns:
        max color
    """
    full_len_matrix = get_full_len_matrix(hic_file, resolution)

    if resolution <= 1000:
        return 1
    maxcolor = (np.percentile(full_len_matrix, 95))
    if maxcolor < 1:
        maxcolor = 1
    return maxcolor


def get_max_color_v2(hic_file, resolution):
    """
        get max color
    Args:
        hic_file: hic file path
        resolution: hic resolution

    Returns:
        max color
    """
    if resolution <= 2000:
        return 1
    elif resolution <= 12500:
        return 3
    else:
        # get hic object
        hic_object = hicstraw.HiCFile(hic_file)

        matrix_zoom_data = hic_object.getMatrixZoomData(
            'assembly', 'assembly', "observed", "KR", "BP", resolution)
        start = 0
        end = resolution * 700
        matrix_data = matrix_zoom_data.getRecordsAsMatrix(start, end, start, end)
        return np.percentile(matrix_data, 95)


def get_full_len_matrix(hic_file, resolution, assembly_file=None):
    """
        get full length matrix
    Args:
        hic_file: hic file path
        resolution: hic resolution
        assembly_file: assembly file path

    Returns:
        full length matrix
    """
    # get hic object
    hic_object = hicstraw.HiCFile(hic_file)

    hic_len = None  # hic_object length
    if assembly_file is None:
        for chrom in hic_object.getChromosomes():
            hic_len = chrom.length
    else:
        hic_len = get_hic_real_len(hic_file, assembly_file)

    # get resolution max len
    res_max_len = get_max_hic_len(resolution)

    # cut full length block number
    len_block_num = math.ceil(hic_len / res_max_len)
    # each block length
    each_block_len = math.ceil(hic_len / len_block_num)
    each_block_res_number = round(each_block_len / resolution)
    iter_len = []
    for i in range(len_block_num):
        iter_len.append(each_block_res_number * i * resolution)
    iter_len.append(hic_len)

    # according to fit_resolution, get matrix_zoom_data
    matrix_zoom_data = hic_object.getMatrixZoomData(
        'assembly', 'assembly', "observed", "KR", "BP", resolution)

    full_len_matrix = None
    for i in range(len(iter_len) - 1):  # loop full length each block
        temp_matrix = None
        for j in range(len(iter_len) - 1):
            # logger.debug(
            #     "Start_A: {}, End_A: {}, Start_B: {}, End_B: {}".format(iter_len[j], iter_len[j + 1] - 1, iter_len[i],
            #                                                             iter_len[i + 1] - 1))
            matrix_data = matrix_zoom_data.getRecordsAsMatrix(iter_len[j], iter_len[j + 1] - 1,
                                                              iter_len[i], iter_len[i + 1] - 1)
            if temp_matrix is None:
                # 稀疏矩阵
                if matrix_data.shape == (1, 1):
                    matrix_data = np.zeros((each_block_res_number, each_block_res_number))
                temp_matrix = matrix_data
            elif matrix_data.shape == (1, 1):
                temp_matrix = np.zeros((each_block_res_number, each_block_res_number))
            else:
                temp_matrix = np.vstack((temp_matrix, matrix_data))

        if full_len_matrix is None:
            full_len_matrix = temp_matrix
        else:
            full_len_matrix = np.hstack((full_len_matrix, temp_matrix))
    return full_len_matrix


def get_cfg(cfg_dir, cfg_key=None):
    """
        get config
    Args:
        cfg_dir: config file path
        cfg_key: config key

    Returns:
        config dict
    """
    config = {}
    with open(cfg_dir, 'r') as f:
        for line in f:
            if line.startswith('#') or line.startswith('\n'):
                continue
            try:
                key = line.strip().split('=')[0]
                value = line.strip().split('=')[1]
                if value == '':
                    print("Please check you ", key, " parameter")
                    return
                config[key] = value
            except IndexError:
                print("Please check you config file")
                continue
    if cfg_key is not None:
        try:
            return config[cfg_key]
        except KeyError:
            raise KeyError("Please check you config file")
    else:
        return config


def write_no_error_infer_json(error_json):
    """

    Args:
        error_json:

    Returns:

    """

    with open(error_json, "w") as f:
        temp_json = {}
        json.dump(temp_json, f)


def write_no_error_json(error_json):
    """
        write no error json
    Args:
        error_json: error json file

    Returns:
        None
    """
    with open(error_json, "w") as f:
        temp_json = {
            "Raw error number": {
                "translocation": 0,
                "inversion": 0,
                "debris": 0
            },
            "Score filtered error number": {
                "translocation": 0,
                "inversion": 0,
                "debris": 0
            },
            "Length filtered error number": {
                "translocation": 0,
                "inversion": 0,
                "debris": 0
            },
            "Length removed error number": {
                "translocation": 0,
                "inversion": 0,
                "debris": 0
            },
            "Overlap filtered error number": {
                "debris": 0,
                "inversion": 0,
                "translocation": 0
            },
            "Chromosome real length filtered error number": {
                "translocation": {
                    "normal": 0,
                    "abnormal": 0
                },
                "inversion": {
                    "normal": 0,
                    "abnormal": 0
                },
                "debris": {
                    "normal": 0,
                    "abnormal": 0
                }
            }
        }
        json.dump(temp_json, f)


def get_error_sum(error_json) -> int:
    """
        calculate translocation and inversion error number
    Args:
        error_json: error json file

    Returns:
        error number
    """
    with open(error_json, "r") as f:
        error_count = json.loads(f.read())

    final_count = error_count["Chromosome real length filtered error number"]
    tran_inv_sum = final_count["translocation"]["normal"] + final_count["inversion"]["normal"]
    return tran_inv_sum


def get_each_error(error_json) -> list:
    """
        calculate each error number
    Args:
        error_json: error json file

    Returns:
        each error number list
    """
    with open(error_json, "r") as f:
        error_count = json.loads(f.read())

    final_count = error_count["Chromosome real length filtered error number"]
    error_sum = final_count["translocation"]["normal"] + final_count["inversion"]["normal"] + final_count["debris"][
        "normal"]
    each_error_num = [final_count["translocation"]["normal"], final_count["inversion"]["normal"],
                      final_count["debris"]["normal"], error_sum]
    return each_error_num


def subprocess_popen(statement, cwd=None):
    """
        subprocess popen
    Args:
        statement: command
        cwd: current work dir

    Returns:
        command result
    """
    p = subprocess.Popen(statement, shell=True, stdout=subprocess.PIPE, cwd=cwd)
    while p.poll() is None:
        if p.wait() != 0:
            print("Command execution failed, please check the device connection status")
            return False
        else:
            re = p.stdout.readlines()
            result = []
            for i in range(len(re)):
                res = re[i].decode('utf-8').strip('\r\n')
                result.append(res)
            return result


def calculate_genome_size(file_path):
    """
    Calculate genome size from fasta file
    Args:
        file_path: fasta file path

    Returns:
        genome size
    """
    genome_size = 0
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('>'):
                continue  # Skip header lines
            genome_size += len(line.strip())
    return genome_size


def cal_anchor_rate(ctg, scaffold):
    """
        Calculate anchor rate
    Args:
        ctg: ctg genome file
        scaffold: scaffold genome file

    Returns:
        anchor rate
    """
    ctg_len = calculate_genome_size(ctg)
    scaffold_len = calculate_genome_size(scaffold)
    return scaffold_len / ctg_len


def get_error_len(errors_json_file):
    """
        Get error length from error json file
    Args:
        errors_json_file: error json file

    Returns:
        error length
    """
    if os.path.exists(errors_json_file):
        with open(errors_json_file, "r") as f:
            errors_dict = json.load(f)
        error_full_len = 0

        for error in errors_dict:
            error_full_len += errors_dict[error]["end"] - errors_dict[error]["start"]
    else:
        error_full_len = 0
    return error_full_len


def get_error_pairs(errors_json_path):
    """
        Get error pairs from error json file
    Args:
        errors_json_path: error json file path: chr_len_filtered_errors.json

    Returns:
        inversion_pairs, translocation_pairs, debris_pairs
    """
    inversion_pairs, translocation_pairs, debris_pairs = [], [], []

    with open(os.path.join(errors_json_path, "infer_result/infer_result.json")) as f:
        data = json.load(f)

    tran_error_counter = 0
    inv_error_counter = 0
    deb_error_counter = 0
    for error_type, errors in data.items():
        for error in errors:
            temp_error_dict = {
                "image": image_to_base64(error["infer_image"]),
                "start": error["hic_loci"][0],
                "end": error["hic_loci"][1]}
            if error_type == "inversion":
                if inv_error_counter > 4:
                    break
                inversion_pairs.append(temp_error_dict)
                inv_error_counter += 1
            elif error_type == "translocation":
                if tran_error_counter > 4:
                    break
                translocation_pairs.append(temp_error_dict)
                tran_error_counter += 1
            elif error_type == "debris":
                if deb_error_counter > 4:
                    break
                debris_pairs.append(temp_error_dict)
                deb_error_counter += 1
    return translocation_pairs, inversion_pairs, debris_pairs


def main():
    pass


if __name__ == "__main__":
    main()

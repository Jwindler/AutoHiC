#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: get_chr_data.py
@time: 3/6/23 5:20 PM
@function: 
"""
import json
import math
import os
from collections import OrderedDict

import torch
from PIL import Image
from mmdet.apis import init_detector, inference_detector

from src.assembly.asy_operate import AssemblyOperate
from src.utils.get_cfg import get_cfg, get_hic_real_len, get_ratio
from src.utils.logger import logger


def bbox2hic(bbox, hic_len, img_size):
    # hic len
    img_chr_w = img_chr_h = hic_len

    w_ration = img_chr_w / img_size[0]
    h_ration = img_chr_h / img_size[1]

    x, y, w, h = bbox

    a_s = x * w_ration
    a_e = w * w_ration
    b_s = y * h_ration
    b_e = h * h_ration

    hic_loci = list(map(lambda temp: int(temp), [a_s, a_e, b_s, b_e]))

    return hic_loci


def create_structure(detection_result, hic_len, img_size):
    """

    Args:
        detection_result:
        hic_len:
        img_size:

    Returns:

    """
    chr_dict = dict()

    for index, error in enumerate(detection_result):
        chr_dict[index] = {
            "bbox": error[0:4].tolist(),
            "score": error[4],
            "hic_loci": bbox2hic(error[0:4], hic_len, img_size=img_size)
        }

    return chr_dict


def get_chr_data(detection_result, hic_len, img_size):
    """

    Args:
        detection_result:
        hic_len:
        img_size:

    Returns:

    """
    chr_dict = dict()

    for index, error in enumerate(detection_result):
        chr_dict[index] = {
            "bbox": error[0:4].tolist(),
            "score": error[4],
            "hic_loci": bbox2hic(error[0:4], hic_len, img_size=img_size)
        }

    return chr_dict


def score_filter(chr_dict, score_threshold):
    """

    Args:
        chr_dict:
        score_threshold:

    Returns:

    """
    chr_dict = dict(filter(lambda temp: temp[1]["score"] > score_threshold, chr_dict.items()))

    return chr_dict


def hic_loci2txt(chr_dict, txt_path, hic_len=None, redundant_len=200000):
    """

    Args:
        chr_dict:
        txt_path:
        hic_len:
        redundant_len:

    Returns:

    """

    chr_len_list = []
    for index, value in chr_dict.items():
        chr_len_list.append([value['hic_loci'][0], value['hic_loci'][1]])
    chr_len_list_sorted = sorted(chr_len_list, key=lambda x: x[1])
    for chr_index in range(len(chr_len_list_sorted) - 1):
        chr_len_list_sorted[chr_index][1] = (chr_len_list_sorted[chr_index][1] + chr_len_list_sorted[chr_index + 1][
            0]) // 2
        chr_len_list_sorted[chr_index + 1][0] = chr_len_list_sorted[chr_index][1] + 1

    #
    chr_len_list_sorted[0][0] = 0
    if hic_len is not None:
        chr_len_list_sorted[-1][1] = hic_len
    else:
        chr_len_list_sorted[-1][1] = chr_len_list_sorted[-1][1] + redundant_len

    with open(txt_path, "w") as f:
        f.write("Chr\tStart\tEnd\n")
        for index, value in enumerate(chr_len_list_sorted):
            f.write("{0}\t{1}\t{2}\n".format(index + 1, value[0], value[1]))


def hic_loci2excel(chr_dict, excel_path):
    """

    Args:
        chr_dict:
        excel_path:

    Returns:

    """
    import pandas as pd

    df = pd.DataFrame(columns=["chr", "start", "end"])

    for index, value in chr_dict.items():
        df.loc[index] = [index, value["hic_loci"][0], value["hic_loci"][1]]

    df.to_excel(excel_path, index=False)

    return excel_path


def split_list(lst, val):
    return [lst[:lst.index(val)], lst[lst.index(val) + 1:]] if val in lst else [lst]


def divide_chr(chr_len_txt, hic_file, assembly_file, modified_assembly_file):
    chr_len_list = []
    with open(chr_len_txt, 'r') as f:
        for line in f.readlines():
            line_split = line.strip().split("\t")
            if line_split[0] == "Chr":
                continue
            chr_len_list.append(int(line_split[2]))

    # get ratio of hic file and assembly file
    ratio = get_ratio(hic_file, assembly_file)

    # class AssemblyOperate class
    asy_operate = AssemblyOperate(assembly_file, ratio)

    flag = True  # flag to judge whether the file is modified

    # cut chr ctg
    for chr_len in chr_len_list:
        if flag:
            flag = False
        else:
            assembly_file = modified_assembly_file

        # find ctg
        error_contains_ctg = asy_operate.find_site_ctg_s(assembly_file, chr_len, chr_len + 1)

        # json format
        contain_ctg = json.loads(error_contains_ctg)

        # cut final insert location ctg right point
        contain_ctg_second = list(contain_ctg.keys())[0]

        second_cut_ctg = {contain_ctg_second: math.ceil(chr_len * ratio) + 1}

        # 如果刚好边界等，不需要切割
        if contain_ctg[contain_ctg_second]["start"] != chr_len:
            # check whether the ctg is already cut
            if "fragment" in contain_ctg_second or "debris" in contain_ctg_second:
                asy_operate.re_cut_ctg_s(assembly_file, second_cut_ctg, modified_assembly_file)
            else:
                asy_operate.cut_ctg_s(assembly_file, second_cut_ctg, modified_assembly_file)
    logger.info("Cut errors ctg done \n")

    # get chr cut ctg order
    chr_cut_ctg_order = []
    for chr_len in chr_len_list:
        # find ctg
        error_contains_ctg = asy_operate.find_site_ctg_s(modified_assembly_file, chr_len, chr_len + 2)

        # json format
        contain_ctg = json.loads(error_contains_ctg)

        # cut final insert location ctg right point
        contain_ctg_second = list(contain_ctg.keys())[0]

        each_chr_cut_ctg_order = asy_operate.get_ctg_info(ctg_name=contain_ctg_second,
                                                          new_asy_file=modified_assembly_file)
        chr_cut_ctg_order.append(str(each_chr_cut_ctg_order["ctg_order"]))

    # cut chr ctg order
    ctg_s = OrderedDict()  # ctg_s information
    ctg_orders = []  # ctg_s orders

    # get ctg number and total length
    with open(modified_assembly_file, "r") as f:
        for line in f:
            if line.startswith(">"):
                temp_line = line.strip().split()
                ctg_s[temp_line[0]] = {
                    "order": temp_line[1],
                    "length": temp_line[2]
                }
            else:
                temp_line = line.strip().split(" ")
                ctg_orders.append(temp_line)
    one_dim_ctg_orders = [item for sublist in ctg_orders for item in sublist]

    # 切分成二维列表
    def split_chr_list(chars_list, split_chars_list):
        # 定义一个变量来存储当前子列表的起始位置
        start_index = 0

        # 定义一个空列表来存储切分后的二维列表
        result_list = []

        # 遍历 chars_list
        for i in range(len(chars_list)):
            # 如果当前字符是一个指定的切分字符
            if chars_list[i] in split_chars_list:
                # 将 chars_list 从起始位置到当前位置+1切分为一个子列表，并将其添加到 result_list 中
                result_list.append(chars_list[start_index:i])
                # 更新起始位置为当前位置的下一个位置
                start_index = i

        # 如果还有剩余字符，将它们添加到最后一个子列表中
        if start_index < len(chars_list):
            result_list.append(chars_list[start_index:])

        return result_list

    result_orders = split_chr_list(one_dim_ctg_orders, chr_cut_ctg_order)

    # update order and write to new file
    with open(modified_assembly_file, "w") as f:
        # write the new ctg information
        for key, value in ctg_s.items():
            f.write(key + " " + value["order"] + " " + value["length"] + "\n")

        # write new ctg order information
        for ctg_order in result_orders:
            f.write(" ".join(ctg_order) + "\n")

    logger.info("Get ctg_s information done \n")


def split_chr(img_file, asy_file, hic_file, cfg_file):
    # 检查是否有显卡
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    # get cfg
    cfg_data = get_cfg(cfg_file)

    # infer png
    config_file = cfg_data["CHR_MODEL_CFG"]
    checkpoint_file = cfg_data["CHR_PRETRAINED_MODEL"]
    model = init_detector(config_file, checkpoint_file, device=device)
    result = inference_detector(model, img_file)
    #
    hic_len = get_hic_real_len(hic_file, asy_file)
    img_size = Image.open(img_file).size

    chr_data = create_structure(result[0][0], hic_len, img_size)
    score_filtered_chr = score_filter(chr_data, 0.6)

    chr_output = os.path.join(os.path.dirname(img_file), "chr.txt")
    hic_loci2txt(score_filtered_chr, chr_output, redundant_len=200000)

    # split chr
    modified_assembly_file = os.path.join(os.path.dirname(img_file), "chr.assembly")
    divide_chr(chr_output, hic_file, asy_file, modified_assembly_file)

    # get chr number
    with open(chr_output, 'r') as file:
        chr_count = sum(1 for line in file) - 1

    return modified_assembly_file, chr_count


def main():
    chr_len_txt = "/home/jzj/Jupyter-Docker/buffer/br_4/chr/chr.txt"
    hic_file = "/home/jzj/Jupyter-Docker/buffer/br_4/br.4.hic"
    assembly_file = "/home/jzj/Jupyter-Docker/buffer/br_4/br.4.assembly"
    modified_assembly_file = "/home/jzj/Jupyter-Docker/buffer/br_4/chr/test_chr.assembly"
    divide_chr(chr_len_txt, hic_file, assembly_file, modified_assembly_file)


if __name__ == "__main__":
    main()

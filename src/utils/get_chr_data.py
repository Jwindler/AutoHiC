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
    if len(chr_len_list_sorted) == 0:
        chr_len_list_sorted.append([0, hic_len])
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


def divide_chr(chr_len_txt, hic_file, assembly_file, modified_assembly_file, hic_len):
    """Split after inclusive chromosome ends without making empty fragments."""
    chr_len_list = []
    with open(chr_len_txt, "r") as f:
        for line in f:
            fields = line.strip().split("\t")
            if fields and fields[0] != "Chr":
                chr_len_list.append(int(fields[2]))
    if (not chr_len_list or chr_len_list[-1] != hic_len or
            any(end <= 0 for end in chr_len_list) or
            any(a >= b for a, b in zip(chr_len_list, chr_len_list[1:]))):
        raise ValueError("Chromosome ends must increase and finish at the inference span")

    ratio = get_ratio(hic_file, assembly_file)
    if not math.isfinite(ratio) or ratio <= 0:
        raise ValueError("Invalid assembly/map coordinate ratio")
    # AutoHiC uses inclusive ends in map coordinates; cuts start at the next base.
    boundaries = [math.ceil(end * ratio) for end in chr_len_list]
    if len(set(boundaries)) != len(boundaries):
        raise ValueError("Chromosome ends collapse to the same assembly coordinate")
    if os.path.abspath(assembly_file) == os.path.abspath(modified_assembly_file):
        raise ValueError("Use a separate chromosome assembly output")
    with open(assembly_file) as source, open(modified_assembly_file, "w") as output:
        output.write(source.read())
    asy_operate = AssemblyOperate(modified_assembly_file, ratio)

    for boundary in boundaries:
        cut_site = boundary + 1
        ctg_s, ctg_orders = asy_operate._get_ctg_orders(modified_assembly_file)
        by_order = {int(value["order"]): (name, int(value["length"]))
                    for name, value in ctg_s.items()}
        offset = 0
        for order in (value for group in ctg_orders for value in group):
            name, length = by_order[abs(int(order))]
            if length <= 0:
                raise ValueError("Nonpositive input fragment length")
            start, end = offset + 1, offset + length
            offset = end
            # Existing joins and the very last base require regrouping only.
            # The strict lower bound prevents a zero-length left fragment;
            # the upper bound prevents a zero-length right fragment.
            if start < cut_site <= end:
                operation = (asy_operate.re_cut_ctg_s if
                             "fragment" in name or "debris" in name else
                             asy_operate.cut_ctg_s)
                operation(modified_assembly_file, {name: cut_site}, modified_assembly_file)
                break

    ctg_s, ctg_orders = asy_operate._get_ctg_orders(modified_assembly_file)
    lengths = {int(value["order"]): int(value["length"]) for value in ctg_s.values()}
    orders = [value for group in ctg_orders for value in group]
    if (any(length <= 0 for length in lengths.values()) or
            len(orders) != len(set(abs(int(order)) for order in orders)) or
            set(abs(int(order)) for order in orders) != set(lengths)):
        raise ValueError("Invalid chromosome assembly fragments or placements")

    # Regroup by cumulative ends, rather than querying a two-base interval:
    # that query can pick the wrong side of a join or no fragment at EOF.
    boundary_set = set(boundaries)
    groups, current, offset, reached = [], [], 0, set()
    for order in orders:
        current.append(order)
        offset += lengths[abs(int(order))]
        if offset in boundary_set:
            groups.append(current)
            current = []
            reached.add(offset)
    if reached != boundary_set:
        raise ValueError("Chromosome end is outside the assembly or was not split")
    if current:
        groups.append(current)  # retain all unassigned fragments after the model span
    with open(modified_assembly_file, "w") as output:
        for name, value in ctg_s.items():
            output.write(name + " " + value["order"] + " " + value["length"] + "\n")
        for group in groups:
            output.write(" ".join(group) + "\n")
    logger.info("Chromosome boundary cutting and regrouping done\n")


def split_chr(img_file, asy_file, hic_file, cfg_file, device='cpu'):
    """
    Split chromosome from image
    Args:
        img_file: chromosome image file
        asy_file: assembly file
        hic_file: hic file
        cfg_file: config file
        device: device GPU or CPU

    Returns:

    """
    # get cfg
    cfg_data = get_cfg(cfg_file)

    # infer png
    config_file = os.path.join(cfg_data["AutoHiC_DIR"], "src/models/cfgs/chr_model.py")
    checkpoint_file = cfg_data["CHR_PRETRAINED_MODEL"]
    model = init_detector(config_file, checkpoint_file, device=device)
    result = inference_detector(model, img_file)

    hic_len = get_hic_real_len(hic_file, asy_file)

    img_size = Image.open(img_file).size

    chr_data = create_structure(result[0][0], hic_len, img_size)
    score_filtered_chr = score_filter(chr_data, 0.6)

    chr_output = os.path.join(os.path.dirname(img_file), "chr.txt")
    hic_loci2txt(score_filtered_chr, chr_output, hic_len, redundant_len=200000)

    # split chr
    modified_assembly_file = os.path.join(os.path.dirname(img_file), "chr.assembly")
    divide_chr(chr_output, hic_file, asy_file, modified_assembly_file, hic_len)

    # get chr number
    with open(chr_output, 'r') as file:
        chr_count = sum(1 for line in file) - 1

    return modified_assembly_file, chr_count


def main():
    pass


if __name__ == "__main__":
    main()

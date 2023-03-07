#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: get_chr_data.py
@time: 3/6/23 5:20 PM
@function: 
"""


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


def hic_loci2txt(chr_dict, txt_path):
    """

    Args:
        chr_dict:
        txt_path:

    Returns:

    """
    with open(txt_path, "w") as f:
        for index, value in chr_dict.items():
            f.write(
                f"{index}\t{value['hic_loci'][0]}\t"
                f"{value['hic_loci'][1]}\t"
                f"{value['hic_loci'][2]}\t"
                f"{value['hic_loci'][3]}\n")


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


def main():
    pass


if __name__ == "__main__":
    main()

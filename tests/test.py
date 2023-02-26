import json
import os
import uuid

import hicstraw


def bbox2hic(img_size, bbox, img_info):
    # Straw b chromosome
    img_chr_a_s = img_info["chr_A_start"]
    img_chr_a_e = img_info["chr_A_end"]

    # Straw a chromosome
    img_chr_b_s = img_info["chr_B_start"]
    img_chr_b_e = img_info["chr_B_end"]

    img_chr_w = img_chr_a_e - img_chr_a_s
    img_chr_h = img_chr_b_e - img_chr_b_s

    w_ration = img_chr_w / img_size[0]
    h_ration = img_chr_h / img_size[1]

    x, y, w, h = bbox

    a_s = x * w_ration + img_chr_a_s
    a_e = w * w_ration + img_chr_a_s
    b_s = y * h_ration + img_chr_b_s
    b_e = h * h_ration + img_chr_b_s

    hic_loci = list(map(lambda temp: int(temp), [a_s, a_e, b_s, b_e]))

    return hic_loci


def main():
    img_size = (224, 627)

    bbox = [68.710785, 309.68906, 1.2306507e+02, 3.6340259e+02]
    img_info = {
        "chr_A_start": 159895000,
        "chr_A_end": 161005000,
        "chr_B_start": 158690000,
        "chr_B_end": 161820000
    }
    print("HiC_Loci: ", bbox2hic(img_size, bbox, img_info))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: get_hic_real_len.py
@time: 2/14/23 8:52 PM
@function: get hic file real length
"""

import hicstraw

from src.assembly.asy_operate import AssemblyOperate


def get_ratio(hic, asy_file) -> float:
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

    return asy_length / hic_length


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
    return round(real_seqs_len / ratio)


def main():
    hic_file = "/home/jzj/Data/Elements/buffer/10_genomes/03_silkworm/silkworm.1.hic"
    assembly_file = "/home/jzj/Data/Elements/buffer/10_genomes/03_silkworm/silkworm.1.assembly"
    print("hic_real_len: ", get_hic_real_len(hic_file, assembly_file))


if __name__ == "__main__":
    main()

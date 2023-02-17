#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: get_ratio.py
@time: 8/31/22 9:48 AM
@function: get the ratio of the actual length of the chromosome and the length of the chromosome in the assembly file
"""
import hicstraw

from src.assembly.asy_operate import AssemblyOperate


def get_ratio(hic, asy_file) -> int:
    """
        get the ratio of the actual length of the chromosome and the length of the chromosome in the assembly file
    Args:
        hic: hic file path
        asy_file: assembly file path

    Returns:
        ratio: asy/assembly
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


def main():
    hic_file = "/home/jzj/Data/Elements/buffer/10_genomes/05_pb/pb.0.hic"
    assembly_file = "/home/jzj/Data/Elements/buffer/10_genomes/05_pb/pb.0.assembly"

    result = get_ratio(hic_file, assembly_file)
    print(result)


if __name__ == "__main__":
    main()

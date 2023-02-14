#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: split_chr.py
@time: 2/13/23 3:29 PM
@function: 
"""
import hicstraw

import numpy as np


def main():
    hic = hicstraw.HiCFile("/home/jzj/Jupyter-Docker/buffer/03_silkworm/silkworm.0.hic")
    resolutions = hic.getResolutions()
    assembly_len = 0  # define assembly length

    for chrom in hic.getChromosomes():
        if chrom.name == "assembly":
            assembly_len = chrom.length

    matrix_object_chr_max = hic.getMatrixZoomData('assembly', 'assembly', "observed", "KR", "BP", resolutions[0])

    numpy_matrix_chr_max = matrix_object_chr_max.getRecordsAsMatrix(0, assembly_len, 0, assembly_len)

    print(numpy_matrix_chr_max.shape)


if __name__ == "__main__":
    main()

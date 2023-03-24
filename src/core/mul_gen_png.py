#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: mul_gen_png.py
@time: 9/5/22 4:00 PM
@function: multiprocessing generate hic image
"""

import os
from multiprocessing import Pool

from src.core.common.hic_adv_model import GenBaseModel
from src.core.utils.get_cfg import increment
from src.core.utils.logger import logger

info_path = ""  # define


def write_records(records):
    """
        write records to info.txt
    Args:
        records: entries

    Returns:
         None
    """
    with open(info_path, "a+") as f:
        f.writelines(records)


def mul_process(hic_file, genome_id, out_file, methods, process_num, _resolution=None):
    """
        multiprocessing generate hic image
    Args:
        hic_file: hic file path
        genome_id: genome id
        out_file: output file path
        methods: global or diagonal (default: diagonal)
        process_num: process number (default: 10)
        _resolution: specific resolution (default: None)

    Returns:
        None
    """
    logger.info("Multiple Process Initiating ...\n")

    # initialize hic process class
    hic_class = GenBaseModel(hic_file, genome_id, out_file)

    resolutions = hic_class.get_resolutions()  # get resolution list

    logger.info("Number of processes is : %s\n" % process_num)
    pool = Pool(process_num)  # process number

    start = 0
    end = hic_class.get_chr_len()  # get hic file length

    global info_path  # info.txt file path
    info_path = os.path.join(hic_class.genome_folder, "info.txt")
    if _resolution is not None:
        resolutions = [_resolution]

    for resolution in resolutions:
        logger.info("Processing resolution: %s\n" % resolution)

        # create resolution folder
        resolution_folder = os.path.join(hic_class.genome_folder, str(resolution))
        hic_class.create_folder(resolution_folder)

        # get visualization max color
        maxcolor = 1  # 后续生成了

        # range and increment
        site_increase = increment(resolution)

        if methods == "global":  # sliding window method with global
            flag = False  # flag to judge whether the end is reached
            for site_1 in range(start, end, site_increase["increase"]):
                if site_increase["range"] > end:
                    site_increase["range"] = end
                if site_1 + site_increase["range"] > end:
                    site_1 = end - site_increase["range"]
                    flag = True
                for site_2 in range(start, end, site_increase["increase"]):
                    if site_2 + site_increase["range"] > end:
                        site_2 = end - site_increase["range"]
                        pool.apply_async(hic_class.gen_png, args=(
                            resolution, maxcolor, site_1, site_1 + site_increase["range"], site_2,
                            site_2 + site_increase["range"],),
                                         callback=write_records)
                        break
                    pool.apply_async(hic_class.gen_png, args=(
                        resolution, maxcolor, site_1, site_1 + site_increase["range"], site_2,
                        site_2 + site_increase["range"],),
                                     callback=write_records)
                if flag:
                    break
        else:  # sliding window method with diagonal
            for site in range(start, end, site_increase["increase"]):
                if site_increase["range"] > end:
                    site_increase["range"] = end
                site_end = site + site_increase["range"]
                if site_end > end:  # at the end
                    site = end - site_increase["range"]
                    site_end = end
                if site < 0:  # solve white region padding bug
                    site = 0
                pool.apply_async(hic_class.gen_png, args=(
                    resolution, maxcolor, site, site_end, site, site_end,),
                                 callback=write_records)

    pool.close()  # close pool
    pool.join()  # wait for all subprocesses done

    logger.info("Multiple process finished\n")


def main():
    hic_file = "/home/jzj/Data/Test/raw_data/Np/Np.0.hic"
    mul_process(hic_file, "Np", "/home/jzj/Downloads", "diagonal", 10, False)


if __name__ == "__main__":
    main()

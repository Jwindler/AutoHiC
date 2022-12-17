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


def mul_process(hic_file, genome_id, out_file, methods="global", process_num=10, _resolution=None, ran_color=True):
    """
        multiprocessing generate hic image
    Args:
        hic_file: hic file path
        genome_id: genome id
        out_file: output file path
        methods: global or diagonal (default: diagonal)
        process_num: process number (default: 10)
        _resolution: resolution (default: None)
        ran_color: random color (default: True)

    Returns:
        None
    """
    logger.info("Multiple Process Initiating ...")

    # initialize hic process class
    hic_operate = GenBaseModel(hic_file, genome_id, out_file)

    resolutions = hic_operate.get_resolutions()  # get resolution list

    logger.info("threads: %s" % process_num)
    pool = Pool(process_num)  # process number
    start = 0
    end = hic_operate.get_chr_len()  # get genome length

    global info_path  # info.txt file path
    info_path = os.path.join(hic_operate.genome_folder, "info.txt")
    if _resolution is not None:
        resolutions = [_resolution]

    for resolution in resolutions:
        logger.info("Processing resolution: %s" % resolution)

        # create resolution folder
        temp_folder = os.path.join(hic_operate.genome_folder, str(resolution))
        hic_operate.create_folder(temp_folder)

        # range and increment
        temp_increase = hic_operate.increment(resolution)

        if methods == "global":  # sliding window method with global
            flag = False  # flag
            for site_1 in range(start, end, temp_increase["increase"]):
                if site_1 + temp_increase["dim"] > end:
                    site_1 = end - temp_increase["dim"]
                    flag = True
                for site_2 in range(start, end, temp_increase["increase"]):
                    if site_2 + temp_increase["dim"] > end:
                        site_2 = end - temp_increase["dim"]
                        pool.apply_async(hic_operate.gen_png, args=(
                            resolution, site_1, site_1 + temp_increase["dim"], site_2, site_2 + temp_increase["dim"],),
                                         callback=write_records)
                        break
                    pool.apply_async(hic_operate.gen_png, args=(
                        resolution, site_1, site_1 + temp_increase["dim"], site_2, site_2 + temp_increase["dim"],),
                                     callback=write_records)
                if flag:
                    break
        else:  # sliding window method with diagonal
            for site in range(start, end, temp_increase["increase"]):
                if site + temp_increase["dim"] > end:
                    site = end - temp_increase["dim"]
                if ran_color:
                    pool.apply_async(hic_operate.gen_png, args=(
                        resolution, site, site + temp_increase["dim"], site, site + temp_increase["dim"], True,),
                                     callback=write_records)
                else:
                    pool.apply_async(hic_operate.gen_png, args=(
                        resolution, site, site + temp_increase["dim"], site, site + temp_increase["dim"],),
                                     callback=write_records)

    pool.close()  # close pool
    pool.join()  # wait for all subprocesses done

    logger.info("Multiple Process Finished ...")


def main():
    hic_file = "/home/jzj/Data/Test/raw_data/Np/Np.0.hic"
    # mul_process(hic_file, "Np_global", "/home/jzj/Downloads", "global", 10)
    mul_process(hic_file, "Np", "/home/jzj/Downloads", "diagonal", 10)


if __name__ == "__main__":
    main()

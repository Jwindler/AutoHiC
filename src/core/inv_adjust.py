#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: inv_adjust.py
@time: 2/23/23 10:27 AM
@function: inversion adjust
"""
import json
import re
from collections import OrderedDict

from src.assembly.asy_operate import AssemblyOperate
from src.core.utils.get_ratio import get_ratio
from src.core.utils.logger import logger


def adjust_inversion(error_queue, hic_file, assembly_file, modified_assembly_file):
    """
    Inversion adjust
    Args:
        error_queue:
        hic_file:
        assembly_file:
        modified_assembly_file:

    Returns:
        inversion error information queue
    """
    logger.info("Start adjust inversion errors:\n")

    # get ratio between chromosome length and hic file length
    ratio = get_ratio(hic_file, assembly_file)

    # initialize AssemblyOperate class
    asy_operate = AssemblyOperate(assembly_file, ratio)

    cut_ctg_name_site = {}  # save cut chromosome name and site

    error_inv_info = OrderedDict()  # inversion info

    flag = True  # flag to judge whether the file is modified

    # iterate error queue
    for error in error_queue:
        if flag:
            flag = False
        else:
            assembly_file = modified_assembly_file

        logger.info("Start calculate {0} information：\n".format(error))

        # search ctg in debris site
        error_contains_ctg = asy_operate.find_site_ctg_s(assembly_file, error_queue[error]["start"],
                                                         error_queue[error]["end"])
        error_contains_ctg = json.loads(error_contains_ctg)  # convert string to dict
        error_contains_ctg = list(error_contains_ctg.items())  # convert dict to list

        logger.info("Start cut inversion location ctg：\n")

        # cut ctg in inversion site
        if len(error_contains_ctg) >= 2:  # ctg in debris site >= 2

            # cut first ctg
            first_ctg = error_contains_ctg[0]
            cut_ctg_name_site[first_ctg[0]] = round(error_queue[error]["start"] * ratio)

            # {ctg_name: "cut_site"}
            if "fragment" in first_ctg[0] or "debris" in first_ctg[0]:  # check if second cut
                asy_operate.re_cut_ctg_s(assembly_file, cut_ctg_name_site, modified_assembly_file)
            else:
                asy_operate.cut_ctg_s(assembly_file, cut_ctg_name_site, modified_assembly_file)

            # cut last ctg
            last_ctg = error_contains_ctg[-1]

            cut_ctg_name_site.clear()  # clear dict
            cut_ctg_name_site[last_ctg[0]] = round(error_queue[error]["end"] * ratio)

            if "fragment" in last_ctg[0] or "debris" in last_ctg[0]:  # check if second cut
                try:
                    first_ctg_name_head = re.search(r"(.*_)(\d+)", first_ctg[0]).group(1)
                    last_ctg_name_head = re.search(r"(.*_)(\d+)", last_ctg[0]).group(1)
                    first_ctg_name_order = re.search(r"(.*_)(\d+)", first_ctg[0]).group(2)
                    last_ctg_name_order = re.search(r"(.*_)(\d+)", last_ctg[0]).group(2)
                    if first_ctg_name_head == last_ctg_name_head and int(first_ctg_name_order) < int(
                            last_ctg_name_order):
                        renew_last_ctg_name = last_ctg_name_head + str(int(last_ctg_name_order) + 1)
                        cut_ctg_name_site.clear()  # clear dict
                        cut_ctg_name_site[renew_last_ctg_name] = round(error_queue[error]["end"] * ratio)
                except AttributeError:
                    logger.warning(
                        "AttributeError: {0} or {1} is not synonymous ctg\n".format(first_ctg[0], last_ctg[0]))
                asy_operate.re_cut_ctg_s(modified_assembly_file, cut_ctg_name_site, modified_assembly_file)
            else:
                asy_operate.cut_ctg_s(modified_assembly_file, cut_ctg_name_site, modified_assembly_file)

        else:  # only one ctg in debris site
            _ctg = error_contains_ctg[0]  # ctg_name

            _ctg_info = asy_operate.get_ctg_info(ctg_name=_ctg[0], new_asy_file=assembly_file)  # get ctg info

            cut_ctg_site_start = round(error_queue[error]["start"] * ratio)  # error start site in assembly file
            cut_ctg_site_end = round(error_queue[error]["end"] * ratio)  # error end site in assembly file

            # check ctg position
            if _ctg_info["site"][0] == cut_ctg_site_start:  # left boundary coincide
                cut_ctg_name_site[_ctg[0]] = cut_ctg_site_end

                # cut one ctg to two ctg
                if "fragment" in _ctg[0] or "debris" in _ctg[0]:  # check if second cut
                    asy_operate.re_cut_ctg_s(assembly_file, cut_ctg_name_site, modified_assembly_file)
                else:
                    asy_operate.cut_ctg_s(assembly_file, cut_ctg_name_site, modified_assembly_file)

            elif _ctg_info["site"][1] == cut_ctg_site_end:  # right boundary coincide
                cut_ctg_name_site[_ctg[0]] = cut_ctg_site_start

                # cut one ctg to two ctg
                if "fragment" in _ctg[0] or "debris" in _ctg[0]:  # check if second cut
                    asy_operate.re_cut_ctg_s(assembly_file, cut_ctg_name_site, modified_assembly_file)
                else:
                    asy_operate.cut_ctg_s(assembly_file, cut_ctg_name_site, modified_assembly_file)

            else:  # no boundary, one cut three

                # cut one ctg to three ctg
                if "fragment" in _ctg[0] or "debris" in _ctg[0]:  # check if second cut
                    asy_operate.re_cut_ctg_to_3(assembly_file, _ctg[0], cut_ctg_site_start,
                                                cut_ctg_site_end, modified_assembly_file)
                else:
                    asy_operate.cut_ctg_to_3(assembly_file, _ctg[0], cut_ctg_site_start,
                                             cut_ctg_site_end, modified_assembly_file)

        logger.info("Cut inversion location ctg done \n")

        logger.info("Re-search {0} inversion location ctg information:\n".format(error))
        new_error_contains_ctg = asy_operate.find_site_ctg_s(modified_assembly_file, error_queue[error]["start"],
                                                             error_queue[error]["end"])

        new_error_contains_ctg = json.loads(new_error_contains_ctg)  # convert str to dict

        logger.info("Needs to be moved ctg: %s\n", new_error_contains_ctg)

        error_inv_info[error] = {
            "inv_ctg": list(new_error_contains_ctg.keys())
        }
    return error_inv_info


def main():
    # error queue, start and end are based on hic file, not assembly file
    error_queue = {
        "error_1": {
            "start": 268689492,
            "end": 274981070
        },
        "error_2": {
            "start": 280560061,
            "end": 284239273
        }
    }

    # hic file path
    hic_file = "/home/jzj/Data/Test/Np-Self/Np.final.hic"

    # assembly file path
    assembly_file = "/home/jzj/Data/Test/Np-Self/Np.final.assembly"

    # output assembly file path
    modified_assembly_file = "/home/jzj/buffer/test.assembly"

    adjust_inversion(error_queue, hic_file, assembly_file, modified_assembly_file)


if __name__ == "__main__":
    main()

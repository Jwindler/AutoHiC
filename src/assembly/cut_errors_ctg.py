#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: cut_errors_ctg.py
@time: 3/2/23 2:39 PM
@function: 
"""
import json
import re

from src.assembly.asy_operate import AssemblyOperate
from src.core.utils.get_cfg import get_ratio
from src.core.utils.logger import logger


def cut_errors_ctg(errors_queue, hic_file, assembly_file, modified_assembly_file) -> None:
    """
    cut errors ctg
    Args:
        errors_queue: error queue
        hic_file: hic file path
        assembly_file: assembly file path
        modified_assembly_file: modified assembly file path

    Returns:
        None
    """

    logger.info("Start cut errors:\n")

    # get ratio of hic file and assembly file
    ratio = get_ratio(hic_file, assembly_file)

    # class AssemblyOperate class
    asy_operate = AssemblyOperate(assembly_file, ratio)

    flag = True  # flag to judge whether the file is modified

    cut_ctg_name_site = {}  # cut ctg name and site

    # loop error queue
    for error in errors_queue:
        if flag:
            flag = False
        else:
            assembly_file = modified_assembly_file

        logger.info("Start calculate {0} information：\n".format(error))

        # find ctg in error location
        error_contains_ctg = asy_operate.find_site_ctg_s(assembly_file, errors_queue[error]["start"],
                                                         errors_queue[error]["end"])

        error_contains_ctg = json.loads(error_contains_ctg)  # str to dict
        error_contains_ctg = list(error_contains_ctg.items())  # dict to list

        logger.info("Start cut location ctg：\n")

        # cut ctg in translocation error location
        if len(error_contains_ctg) >= 2:  # ctg number >= 2

            # cut first ctg
            first_ctg = error_contains_ctg[0]

            # {ctg_name: "cut_site"}
            cut_ctg_name_site[first_ctg[0]] = round(errors_queue[error]["start"] * ratio)

            # check whether the ctg is already cut
            if "fragment" in first_ctg[0] or "debris" in first_ctg[0]:
                asy_operate.re_cut_ctg_s(assembly_file, cut_ctg_name_site, modified_assembly_file)
            else:
                asy_operate.cut_ctg_s(assembly_file, cut_ctg_name_site, modified_assembly_file)

            # cut last ctg
            last_ctg = error_contains_ctg[-1]

            # clear dict( a bug here, no error because the next function has processed it)
            cut_ctg_name_site.clear()
            cut_ctg_name_site[last_ctg[0]] = round(errors_queue[error]["end"] * ratio)

            # check whether the ctg is already cut
            if "fragment" in last_ctg[0] or "debris" in last_ctg[0]:
                try:
                    first_ctg_name_head = re.search(r"(.*_)(\d+)", first_ctg[0]).group(1)
                    last_ctg_name_head = re.search(r"(.*_)(\d+)", last_ctg[0]).group(1)
                    first_ctg_name_order = re.search(r"(.*_)(\d+)", first_ctg[0]).group(2)
                    last_ctg_name_order = re.search(r"(.*_)(\d+)", last_ctg[0]).group(2)

                    # ctg are synonymous and in the same direction
                    if first_ctg_name_head == last_ctg_name_head and int(first_ctg_name_order) < int(
                            last_ctg_name_order):
                        renew_last_ctg_name = last_ctg_name_head + str(int(last_ctg_name_order) + 1)
                        cut_ctg_name_site.clear()  # clear dict
                        cut_ctg_name_site[renew_last_ctg_name] = round(errors_queue[error]["end"] * ratio)
                except AttributeError:
                    logger.warning(
                        "AttributeError: {0} or {1} is not synonymous ctg\n".format(first_ctg[0], last_ctg[0]))
                asy_operate.re_cut_ctg_s(modified_assembly_file, cut_ctg_name_site, modified_assembly_file)
            else:
                asy_operate.cut_ctg_s(modified_assembly_file, cut_ctg_name_site, modified_assembly_file)

        else:  # ctg number = 1
            _ctg = error_contains_ctg[0]  # ctg_name

            _ctg_info = asy_operate.get_ctg_info(ctg_name=_ctg[0], new_asy_file=assembly_file)  # get ctg info

            cut_ctg_site_start = round(errors_queue[error]["start"] * ratio)  # error real start site
            cut_ctg_site_end = round(errors_queue[error]["end"] * ratio)  # error real end site

            # check ctg position
            if _ctg_info["site"][0] == cut_ctg_site_start:  # left boundary overlap, cut it directly
                cut_ctg_name_site[_ctg[0]] = cut_ctg_site_end

                # cut a ctg to two ctg
                if "fragment" in _ctg[0] or "debris" in _ctg[0]:  # check whether the ctg is already cut
                    asy_operate.re_cut_ctg_s(assembly_file, cut_ctg_name_site, modified_assembly_file)
                else:
                    asy_operate.cut_ctg_s(assembly_file, cut_ctg_name_site, modified_assembly_file)

            elif _ctg_info["site"][1] == cut_ctg_site_end:  # right boundary overlap, cut it directly
                cut_ctg_name_site[_ctg[0]] = cut_ctg_site_start

                # cut a ctg to two ctg
                if "fragment" in _ctg[0] or "debris" in _ctg[0]:  # check whether the ctg is already cut
                    asy_operate.re_cut_ctg_s(assembly_file, cut_ctg_name_site, modified_assembly_file)
                else:
                    asy_operate.cut_ctg_s(assembly_file, cut_ctg_name_site, modified_assembly_file)

            else:  # no boundary situation, cut it into three ctg
                if "fragment" in _ctg[0] or "debris" in _ctg[0]:  # check whether the ctg is already cut
                    asy_operate.re_cut_ctg_to_3(assembly_file, _ctg[0], cut_ctg_site_start,
                                                cut_ctg_site_end, modified_assembly_file)
                else:
                    asy_operate.cut_ctg_to_3(assembly_file, _ctg[0], cut_ctg_site_start,
                                             cut_ctg_site_end, modified_assembly_file)

        logger.info("Cut errors ctg done \n")


def main():
    pass


if __name__ == "__main__":
    main()

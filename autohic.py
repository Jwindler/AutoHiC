#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: autohic.py
@time: 9/27/22 7:28 PM
@function: cli
"""
import os

import typer

from common import mul_process


def hic_file_name():
    pass


def mul_gen_png(hic_file: str = typer.Option(..., "--hic-file", "-hic", help="hic file path"),
                result_name: str = typer.Option("AutoHiC_result", "--result-name", "-n", help="output folder name",
                                                rich_help_panel="Secondary Arguments"),

                out_path: str = typer.Option("./", "--out-path", "-o", help="output file or directory",
                                             rich_help_panel="Secondary Arguments"),

                methods: str = typer.Option("diagonal", "--methods", "-m",
                                            help="mode generate interactive png"
                                                 "should be global or diagonal",
                                            rich_help_panel="Secondary Arguments"),

                process_num: int = typer.Option(10, "--process-num", "-p", help="number of processes",
                                                rich_help_panel="Secondary Arguments")):
    """
    Multiprocess generation of interactive img
    """

    if result_name is None:
        result_name = os.path.basename(hic_file).split(".")[0]
    mul_process(hic_file, result_name, out_path, methods, process_num)


if __name__ == "__main__":
    typer.run(mul_gen_png)

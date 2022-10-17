#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: autohic.py
@time: 9/27/22 7:28 PM
@function: 命令行程序
"""
import os

import typer

from src.core.mul_gen_png import mul_process


def hic_file_name():
    pass


def mul_gen_png(hic_file: str = typer.Option(..., "--hic-file", "-h", help="`.hic` 文件的绝对路径"),
                result_name: str = typer.Option(None, "--result-name", "-n", help="输出结果的文件夹名称",
                                                rich_help_panel="Secondary Arguments"),

                out_path: str = typer.Option("./", "--out-path", "-o", help="输出结果的文件夹路径",
                                             rich_help_panel="Secondary Arguments"),

                methods: str = typer.Option("diagonal", "--methods", "-m",
                                            help="互作图的生成方法，global 全局，diagonal 对角线",
                                            rich_help_panel="Secondary Arguments"),

                process_num: int = typer.Option(10, "--process-num", "-p", help="进程数，默认10",
                                                rich_help_panel="Secondary Arguments")):
    """
    多进程生成互作图片
    """

    if result_name is None:
        result_name = os.path.basename(hic_file).split(".")[0]
    mul_process(hic_file, result_name, out_path, methods, process_num, ran_color=True)


if __name__ == "__main__":
    typer.run(mul_gen_png)

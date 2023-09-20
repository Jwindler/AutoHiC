#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: onehic.py
@time: 6/14/23 5:15 PM
@function: 
"""

import os

import torch
import typer

from src.assembly.adjust_all_error import adjust_all_error
from src.common.error_pd import infer_error
from src.common.mul_gen_png import mul_process
from src.utils import get_cfg


def onehic(hic_file: str = typer.Option(..., "--hic-file", "-hic", help="hic file path"),
           asy_file: str = typer.Option(..., "--asy-file", "-asy", help="assembly file path"),
           autohic: str = typer.Option(..., "--autohic-file", "-autohic", help="autohic path"),
           pretrained_model: str = typer.Option(..., "--pretrain-model", "-p", help="error pretrained model path"),
           out_path: str = typer.Option("./", "--out-path", "-out", help="result output path"),
           threads: int = typer.Option(10, "--threads", "-t", help="threads number"),
           translocation: bool = typer.Option(True, "--translocation", "-tran", help="whether to adjust translocation"),
           inversion: bool = typer.Option(True, "--inversion", "-inv", help="whether to adjust inversion"),
           debris: bool = typer.Option(True, "--debris", "-deb", help="whether to adjust debris"),
           error_min_len: int = typer.Option(15000, "--min-len", "-min", help="error min length"),
           error_max_len: int = typer.Option(20000000, "--max-len", "-max", help="error max length"),
           black_list: str = typer.Option(None, "--black-list", "-b", help="black list path"),
           score: float = typer.Option(0.9, "--scoree", "-s", help="score threshold"),
           iou_score: float = typer.Option(0.8, "--iou-score", "-i", help="iou score threshold")):
    print("Check if the GPU is available")
    # check gpu whether available
    device = ('cuda:0' if torch.cuda.is_available() else 'cpu')
    if device == 'cpu':
        print("GPU is not available, AutoHiC will run on CPU\n")
    else:
        print("GPU is available, AutoHiC will run on GPU\n")

    mdy_asy_file = os.path.join(out_path, "adjusted.assembly")

    mul_process(hic_file, "png", out_path, "dia", threads)
    hic_real_len = get_cfg.get_hic_real_len(hic_file, asy_file)

    # detect hic img
    hic_img_dir = os.path.join(out_path, "png")
    model_cfg = os.path.join(autohic, "src/models/cfgs/error_model.py")
    infer_error(model_cfg, pretrained_model, hic_img_dir, out_path, device=device, score=score,
                error_min_len=error_min_len,
                error_max_len=error_max_len, iou_score=iou_score, chr_len=hic_real_len)

    adjust_all_error(hic_file, asy_file, out_path, mdy_asy_file, black_list=black_list, tran_flag=translocation,
                     inv_flag=inversion, deb_flag=debris)

    print("AutoHiC finished!")


if __name__ == "__main__":
    typer.run(onehic)

#!/usr/scripts/env python
# encoding: utf-8

"""
@author: jzj
@contact: jzjlab@163.com
@file: main.py
@time: 26/5/23 4:00 PM
@function: main program entry
"""

import os

import torch
import typer

from src.common.error_pd import infer_error
from src.common.mul_gen_png import mul_process
from src.common.get_chr_fa import get_auto_hic_genome
from src.report.gen_report import gen_report_cfg
from src.utils import get_cfg
from src.utils.logger import LoggerHandler
from tests.adjust_all_error import adjust_all_error
from tests.get_chr_data import split_chr
from tests.plot_chr import plot_chr_inter, plot_chr
from src.utils.check_genome import split_genome, check_genome

app = typer.Typer()


@app.command(name="autohic")
def whole(cfg_dir: str = typer.Option(..., "--config", "-c", help="autohic config file path")):
    # TODO: 1.子命令增加 log 2. 步骤增加 log

    # get cfg
    cfg_data = get_cfg.get_cfg(cfg_dir)

    score = float(cfg_data["ERROR_FILTER_SCORE"])
    error_min_len = int(cfg_data["ERROR_MIN_LEN"])
    error_max_len = int(cfg_data["ERROR_MAX_LEN"])
    iou_score = float(cfg_data["ERROR_FILTER_IOU_SCORE"])

    top_output_dir = os.path.join(cfg_data["RESULT_DIR"], cfg_data["SPECIES_NAME"])

    model_cfg = cfg_data["MODEL_CFG"]
    pretrained_model = cfg_data["PRETRAINED_MODEL"]

    # report hic error records for report
    hic_error_records = []

    # 检查是否有显卡
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    # initialing logger
    logger_file = os.path.join(top_output_dir, "log.txt")
    LoggerHandler(file=logger_file)

    # Stage 1: run Juicer + 3d-dna
    run_sh_dir = os.path.join(cfg_data["AutoHiC_DIR"], "src/common/run.sh")
    run_sh = "bash " + run_sh_dir + " " + cfg_dir
    # subprocess_popen(run_sh)
    print(run_sh)

    # # Stage 2: select the min error num hic file
    # get hic file
    hic_file_dir = os.path.join(top_output_dir, "hic_results", "3d-dna")
    hic_files = []

    for epoch in range(int(cfg_data["NUMBER_OF_EDIT_ROUNDS"]) + 1):
        filename = cfg_data["GENOME_NAME"] + "." + str(epoch) + ".hic"
        hic_files.append(filename)

    # run autohic
    autohic_results = os.path.join(top_output_dir, "autohic_results")
    adjust_epoch = 0
    error_count_dict = {}
    for hic_file in hic_files:
        adjust_name = hic_file.split(".")[1]

        adjust_path = os.path.join(autohic_results, adjust_name)
        # os.mkdir(adjust_path)

        # 1. gen hic img
        hic_file_path = os.path.join(hic_file_dir, hic_file)
        # mul_process(hic_file_path, "png", adjust_path, "dia", int(cfg_data["N_CPU"]))

        # 2. detect hic img
        # get real chr len
        assembly_file = hic_file_path.replace(".hic", ".assembly")
        hic_real_len = get_cfg.get_hic_real_len(hic_file_path, assembly_file)

        hic_img_dir = os.path.join(adjust_path, "png")
        # infer_error(model_cfg, pretrained_model, hic_img_dir, adjust_path, device=device, score=score,
        #             error_min_len=error_min_len,
        #             error_max_len=error_max_len, iou_score=iou_score, chr_len=hic_real_len)

        # 3. get error sum
        error_summary_json = os.path.join(adjust_path, "error_summary.json")
        error_count_dict[adjust_name] = {
            "error_sum": get_cfg.get_error_sum(error_summary_json),
            "hic_file": hic_file_path,
            "assembly_file": assembly_file,
            "adjust_path": adjust_path
        }

        hic_error_records.append(get_cfg.get_each_error(error_summary_json))
        hic_error_records[adjust_epoch].insert(0, str(adjust_epoch) + ".hic")
        adjust_epoch += 1

    # 选择处理的hic文件，进行处理
    min_hic = min(error_count_dict, key=lambda k: error_count_dict[k]["error_sum"])
    final_adjust_path = error_count_dict[min_hic]["adjust_path"]
    # TODO: 两者错误数目一致

    merged_nodups_path = os.path.join(top_output_dir, "hic_results", "aligned", "merged_nodups.txt")
    adjust_hic_file = error_count_dict[min_hic]["hic_file"]
    adjust_asy_file = error_count_dict[min_hic]["assembly_file"]
    error_sum = error_count_dict[min_hic]["error_sum"]

    # ctg report cfg
    ctg_extra_info = {'species': cfg_data["SPECIES_NAME"],
                      'inversion_len': get_cfg.get_error_len(
                          os.path.join(final_adjust_path, "inversion_error.json")),
                      'debris_len': get_cfg.get_error_len(os.path.join(final_adjust_path, "debris_error.json")),
                      'translocation_len': get_cfg.get_error_len(
                          os.path.join(final_adjust_path, "translocation_error.json"))}
    # generate before adjust whole hic map png

    plot_chr(adjust_hic_file, genome_name="", chr_len_file=None, out_path=final_adjust_path,
             fig_format="png")
    ctg_hic_map = os.path.join(final_adjust_path, "chromosome.png")

    # Check genome length whether > 80 base
    original_genome = cfg_data["REFERENCE_GENOME"]
    if check_genome(original_genome):
        original_genome_base_path = os.path.dirname(original_genome)
        split_genome_path = os.path.join(original_genome_base_path, cfg_data["GENOME_NAME"] + "_lines.fa")
        split_genome(original_genome, split_genome_path)
        original_genome = split_genome_path

    first_flag = True
    while error_sum > 0:
        adjust_name = str(adjust_epoch)
        final_adjust_path = os.path.join(autohic_results, adjust_name)
        # os.mkdir(final_adjust_path)

        if first_flag:
            hic_file_path = error_count_dict[min_hic]["hic_file"]
            assembly_file_path = error_count_dict[min_hic]["assembly_file"]
            divided_error = error_count_dict[min_hic]["adjust_path"]
            first_flag = False
        else:
            hic_file_path = adjust_hic_file
            assembly_file_path = adjust_asy_file
            divided_error = os.path.dirname(adjust_asy_file)
        modified_assembly_file = os.path.join(final_adjust_path, "test.assembly")

        translocation_flag = cfg_data["TRANSLOCATION_ADJUST"]
        inversion_flag = cfg_data["INVERSION_ADJUST"]
        debris_flag = cfg_data["DEBRIS_ADJUST"]
        adjust_all_error(hic_file_path, assembly_file_path, divided_error, modified_assembly_file, black_list=None,
                         tran_flag=translocation_flag, inv_flag=inversion_flag, deb_flag=debris_flag)

        # 运行 3d-dna 第二步
        # 1. cd folder
        run_sh = "cd " + final_adjust_path
        # subprocess_popen(run_sh)
        print(run_sh)

        # 2. run 3d-dna
        run_sh = "bash " + os.path.join(cfg_data["TD_DNA_DIR"],
                                        "run-asm-pipeline-post-review.sh") + " -r " + modified_assembly_file + " " + \
                 original_genome + " " + merged_nodups_path
        # subprocess_popen(run_sh)
        print(run_sh)

        hic_img_dir = os.path.join(final_adjust_path, "png")
        hic_file_path = os.path.join(final_adjust_path, adjust_name, cfg_data["GENOME_NAME"] + ".final.hic")
        assembly_file = hic_file_path.replace(".hic", ".assembly")

        # generate hic img
        mul_process(hic_file_path, "png", final_adjust_path, "dia", int(cfg_data["N_CPU"]))

        # infer error
        hic_real_len = get_cfg.get_hic_real_len(hic_file_path, assembly_file)
        infer_return = infer_error(model_cfg, pretrained_model, hic_img_dir, final_adjust_path, device=device,
                                   score=score,
                                   error_min_len=error_min_len,
                                   error_max_len=error_max_len, iou_score=iou_score, chr_len=hic_real_len)
        if infer_return:  # no detect error
            adjust_hic_file = hic_file_path
            adjust_asy_file = assembly_file
            break

        # get error sum
        error_summary_json = os.path.join(hic_img_dir, "error_summary.json")

        # report record error
        hic_error_records.append(get_cfg.get_each_error(error_summary_json))
        hic_error_records[adjust_epoch].insert(0, str(adjust_epoch) + ".hic")

        error_count_dict[adjust_epoch] = {
            "error_sum": get_cfg.get_error_sum(error_summary_json),
            "hic_file": hic_file_path,
            "assembly_file": assembly_file,
            "adjust_path": hic_img_dir
        }
        error_sum = error_count_dict[adjust_epoch]["error_sum"]
        adjust_hic_file = hic_file_path
        adjust_asy_file = assembly_file
        adjust_epoch += 1

    # final chr result
    chr_adjust_path = os.path.join(autohic_results, "chr")
    os.mkdir(chr_adjust_path)

    # TODO: 是否拆分chr
    # 生成chr png
    plot_chr_inter(adjust_hic_file, adjust_asy_file, chr_adjust_path, fig_format="png")

    # 检测chr png
    img_path = os.path.join(chr_adjust_path, "chromosome.png")

    # infer img
    chr_asy_file, chr_number = split_chr(img_path, adjust_asy_file, adjust_hic_file, cfg_dir)

    # 运行3d-dna 第二步
    run_sh = "cd " + chr_adjust_path
    # subprocess_popen(run_sh)
    print(run_sh)

    # 2. run 3d-dna
    run_sh = "bash " + os.path.join(cfg_data["TD_DNA_DIR"],
                                    "run-asm-pipeline-post-review.sh") + " -r " + chr_asy_file + " " + \
             original_genome + " " + merged_nodups_path
    # subprocess_popen(run_sh)
    print(run_sh)

    # Report stage
    chr_fa_name = cfg_data["GENOME_NAME"] + ".FINAL.fasta"
    chr_fa_path = os.path.join(chr_adjust_path, chr_fa_name)

    # delete last debris seq
    auto_hic_genome_path = os.path.join(chr_adjust_path, cfg_data["GENOME_NAME"] + "_autohic.fasta")
    get_auto_hic_genome(chr_fa_path, chr_number, auto_hic_genome_path)

    quast_output = os.path.join(top_output_dir, "quast_output")
    os.mkdir(quast_output)

    template_path = os.path.join(cfg_data["AutoHiC_DIR"], "src/report")

    ctg_extra_info["num_chr"] = chr_number

    ctg_fa_path = original_genome
    anchor_ratio = get_cfg.cal_anchor_rate(ctg_fa_path, auto_hic_genome_path)
    autohic_extra_info = {'species': cfg_data["SPECIES_NAME"],
                          'num_chr': chr_number,
                          'anchor_ratio': anchor_ratio,
                          'inversion_len': get_cfg.get_error_len(
                              os.path.join(final_adjust_path, "inversion_error.json")),
                          'debris_len': get_cfg.get_error_len(
                              os.path.join(final_adjust_path, "debris_error.json")),
                          'translocation_len': get_cfg.get_error_len(
                              os.path.join(final_adjust_path, "translocation_error.json"))}

    # 跑quast的线程数
    quast_thread = int(cfg_data["N_CPU"])

    # generate after adjust whole hic map png
    chr_hic_name = cfg_data["GENOME_NAME"] + ".final.hic"
    chr_hic_path = os.path.join(chr_adjust_path, chr_hic_name)

    final_chr_txt = os.path.join(chr_adjust_path, "chr.txt")
    plot_chr(chr_hic_path, genome_name="", chr_len_file=final_chr_txt, out_path=chr_adjust_path,
             fig_format="png")

    chr_hic_map = os.path.join(chr_adjust_path, "chromosome.png")

    translocation_pairs, inversion_pairs, debris_pairs = get_cfg.geg_error_pairs(final_adjust_path)

    gen_report_cfg(ctg_fa_path, auto_hic_genome_path, quast_output, ctg_extra_info, autohic_extra_info, quast_thread,
                   ctg_hic_map,
                   chr_hic_map, inversion_pairs, translocation_pairs, debris_pairs, hic_error_records,
                   template_path, report_output=top_output_dir)


def main():
    cfg_file = "/home/jzj/Jupyter-Docker/buffer/AutoHiC_test/cft-autohic.txt"
    whole(cfg_file)


if __name__ == "__main__":
    # app()
    main()

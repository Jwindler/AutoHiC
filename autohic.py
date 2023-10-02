#!/usr/scripts/env python
# encoding: utf-8

"""
@author: jzj
@contact: jzjlab@163.com
@file: autohic.py
@time: 9/6/23 4:00 PM
@function: main program entry
"""

import os
import re
import sys

import torch
import typer

from src.assembly.adjust_all_error import adjust_all_error
from src.common.error_pd import infer_error
from src.common.get_chr_fa import get_auto_hic_genome
from src.common.mul_gen_png import mul_process
from src.report.gen_report import gen_report_cfg
from src.utils import get_cfg
from src.utils.check_genome import split_genome, check_genome
from src.utils.get_chr_data import split_chr
from src.utils.logger import logger
from src.utils.plot_chr import plot_chr_inter, plot_chr


def whole(cfg_dir: str = typer.Option(..., "--config", "-c", help="autohic config file path")):
    # initialing logger
    logger.info("AutoHiC start running ...\n")

    logger.info("Get configuration items\n")
    # get cfg
    cfg_data = get_cfg.get_cfg(cfg_dir)

    score = float(cfg_data["ERROR_FILTER_SCORE"])
    error_min_len = int(cfg_data["ERROR_MIN_LEN"])
    error_max_len = int(cfg_data["ERROR_MAX_LEN"])
    iou_score = float(cfg_data["ERROR_FILTER_IOU_SCORE"])
    genome_name_without_extension, _ = os.path.splitext(os.path.basename(cfg_data["REFERENCE_GENOME"]))

    top_output_dir = os.path.join(cfg_data["RESULT_DIR"], cfg_data["JOB_NAME"])

    model_cfg = os.path.join(cfg_data["AutoHiC_DIR"], "src/models/cfgs/error_model.py")
    pretrained_model = cfg_data["ERROR_PRETRAINED_MODEL"]

    # hic error records for report
    hic_error_records = []
    hic_error_records_epoch = 0

    logger.info("Check if the GPU is available")
    # check gpu whether available
    device = ('cuda:0' if torch.cuda.is_available() else 'cpu')
    if device == 'cpu':
        logger.info("GPU is not available, AutoHiC will run on CPU\n")
    else:
        logger.info("GPU is available, AutoHiC will run on GPU\n")

    # Check to see if the fastq file is correct
    fastq_folder_path = os.path.join(cfg_data["FASTQ_DIR"], "fastq")

    # count the number of fastq files
    fastq_file_count = len(os.listdir(fastq_folder_path))

    if fastq_file_count % 2 == 0:
        logger.info(f"Fastq file number is correct.\n")
    else:
        logger.error(f"Please check the number of fastq files.")
        sys.exit()

    # define the regular expression pattern to match the file name
    pattern = r'_R[12]\.fastq(\.gz)?$'

    # iterate all files in the folder
    for filename in os.listdir(fastq_folder_path):
        if re.search(pattern, filename):
            continue
        else:
            logger.error(f"Please check if the %s filename is configured correctly." % filename)
            sys.exit()

    # Check genome length whether > 80 base
    logger.info("Check genome length whether > 80 base")
    original_genome = cfg_data["REFERENCE_GENOME"]
    if check_genome(original_genome):
        logger.info("Split genome len to 80 base")
        original_genome_base_path = os.path.dirname(original_genome)
        split_genome_path = os.path.join(original_genome_base_path, genome_name_without_extension + "_old.fasta")
        split_genome(original_genome, split_genome_path)

        # exchange file name
        temp_name = os.path.join(original_genome_base_path, genome_name_without_extension + "_temp.fasta")
        os.rename(original_genome, temp_name)
        os.rename(split_genome_path, original_genome)
        os.rename(temp_name, split_genome_path)

        logger.info("Split genome len to 80 base finished\n")
    else:
        logger.info("Genome len < 80 base\n")

    # Stage 1: run Juicer + 3d-dna
    logger.info("Stage 1: Run Juicer and  3d-dna")
    run_sh_dir = os.path.join(cfg_data["AutoHiC_DIR"], "src/common/run.sh")
    run_sh = "bash " + run_sh_dir + " " + cfg_dir
    get_cfg.subprocess_popen(run_sh)
    logger.info("Run Juicer and  3d-dna finished\n")

    # Stage 2: select the min error num hic file
    logger.info("Stage 2: Select the min error number of  hic file\n")

    # get hic file
    hic_file_dir = os.path.join(top_output_dir, "hic_results", "3d-dna")
    hic_files = []
    for epoch in range(int(cfg_data["NUMBER_OF_EDIT_ROUNDS"]) + 1):
        filename = genome_name_without_extension + "." + str(epoch) + ".hic"
        hic_files.append(filename)

    # run autohic
    autohic_results = os.path.join(top_output_dir, "autohic_results")
    adjust_epoch = 0
    error_count_dict = {}
    for hic_file in hic_files:
        adjust_name = hic_file.split(".")[1]
        logger.info("Check the %s file" % adjust_name)
        adjust_path = os.path.join(autohic_results, adjust_name)
        os.mkdir(adjust_path)

        # gen hic img
        hic_file_path = os.path.join(hic_file_dir, hic_file)
        mul_process(hic_file_path, "png", adjust_path, "dia", int(cfg_data["N_CPU"]))

        # get real chr len
        asy_file = hic_file_path.replace(".hic", ".assembly")
        hic_real_len = get_cfg.get_hic_real_len(hic_file_path, asy_file)

        # detect hic img
        hic_img_dir = os.path.join(adjust_path, "png")
        logger.info("Detect the %s file" % adjust_name)
        infer_error_result = infer_error(model_cfg, pretrained_model, hic_img_dir, adjust_path, device=device,
                                         score=score,
                                         error_min_len=error_min_len,
                                         error_max_len=error_max_len, iou_score=iou_score, chr_len=hic_real_len)
        logger.info("Detect the %s file finished\n" % adjust_name)

        # get error sum and error records dict
        error_summary_json = os.path.join(adjust_path, "error_summary.json")

        if infer_error_result:  # no detect error
            get_cfg.write_no_error_json(error_summary_json)
            os.mkdir(os.path.join(adjust_path, "infer_result"))
            get_cfg.write_no_error_infer_json(os.path.join(adjust_path, "infer_result", "infer_result.json"))
            logger.info("No error detected")

        error_count_dict[adjust_name] = {
            "error_sum": get_cfg.get_error_sum(error_summary_json),
            "hic_file": hic_file_path,
            "assembly_file": asy_file,
            "adjust_path": adjust_path
        }

        logger.info("The %s file done\n" % adjust_name)
        adjust_epoch += 1

    # select the min error num of hic file( default: according to the dict key)
    min_hic = min(error_count_dict, key=lambda k: error_count_dict[k]["error_sum"])
    final_adjust_path = error_count_dict[min_hic]["adjust_path"]

    hic_error_records.append(get_cfg.get_each_error(os.path.join(final_adjust_path, "error_summary.json")))
    hic_error_records[hic_error_records_epoch].insert(0, str(hic_error_records_epoch) + ".hic")
    hic_error_records_epoch += 1

    merged_nodups_path = os.path.join(top_output_dir, "hic_results", "juicer", genome_name_without_extension, "aligned",
                                      "merged_nodups.txt")
    adjust_hic_file = error_count_dict[min_hic]["hic_file"]
    adjust_asy_file = error_count_dict[min_hic]["assembly_file"]
    error_sum = error_count_dict[min_hic]["error_sum"]

    # ctg info for report
    ctg_extra_info = {'species': cfg_data["SPECIES_NAME"],
                      'inversion_len': get_cfg.get_error_len(
                          os.path.join(final_adjust_path, "inversion_error.json")),
                      'debris_len': get_cfg.get_error_len(os.path.join(final_adjust_path, "debris_error.json")),
                      'translocation_len': get_cfg.get_error_len(
                          os.path.join(final_adjust_path, "translocation_error.json"))}

    # generate before adjust whole hic map png
    logger.info("Generate before adjust whole hic map png\n")
    plot_chr(adjust_hic_file, genome_name="", chr_len_file=None, out_path=final_adjust_path,
             fig_format="png")
    ctg_hic_map = os.path.join(final_adjust_path, "chromosome.png")

    logger.info("Start iterating to adjust errors\n")
    first_flag = True
    while error_sum > 0:
        adjust_name = str(adjust_epoch)
        final_adjust_path = os.path.join(autohic_results, adjust_name)
        os.mkdir(final_adjust_path)

        if first_flag:
            hic_file_path = error_count_dict[min_hic]["hic_file"]
            asy_file_path = error_count_dict[min_hic]["assembly_file"]
            divided_error = error_count_dict[min_hic]["adjust_path"]
        else:
            hic_file_path = adjust_hic_file
            asy_file_path = adjust_asy_file
            divided_error = os.path.dirname(adjust_asy_file)
        mdy_asy_file = os.path.join(final_adjust_path, "test.assembly")

        translocation_flag = cfg_data["TRANSLOCATION_ADJUST"]
        inversion_flag = cfg_data["INVERSION_ADJUST"]
        debris_flag = cfg_data["DEBRIS_ADJUST"]

        black_list_path = os.path.join(autohic_results, str(int(adjust_epoch) - 1), "black_list.txt")
        if first_flag:
            black_num_list = adjust_all_error(hic_file_path, asy_file_path, divided_error, mdy_asy_file,
                                              black_list=None,
                                              tran_flag=translocation_flag, inv_flag=inversion_flag,
                                              deb_flag=debris_flag)
            first_flag = False
        else:
            black_num_list = adjust_all_error(hic_file_path, asy_file_path, divided_error, mdy_asy_file,
                                              black_list=black_list_path,
                                              tran_flag=translocation_flag, inv_flag=inversion_flag,
                                              deb_flag=debris_flag)

        # run 3d-dna
        adjust_log = os.path.join(top_output_dir, "logs", "epoch_" + adjust_name + ".log")
        run_sh = "bash " + os.path.join(cfg_data["TD_DNA_DIR"],
                                        "run-asm-pipeline-post-review.sh") + " -r " + mdy_asy_file + " " + \
                 original_genome + " " + merged_nodups_path + " > " + adjust_log + " 2>&1"
        get_cfg.subprocess_popen(run_sh, cwd=final_adjust_path)
        # print(run_sh)

        # generate hic img
        hic_img_dir = os.path.join(final_adjust_path, "png")
        hic_file_path = os.path.join(final_adjust_path, genome_name_without_extension + ".final.hic")
        asy_file = hic_file_path.replace(".hic", ".assembly")
        mul_process(hic_file_path, "png", final_adjust_path, "dia", int(cfg_data["N_CPU"]))

        # infer error
        hic_real_len = get_cfg.get_hic_real_len(hic_file_path, asy_file)
        logger.info("Detect the %s file" % adjust_name)
        infer_return = infer_error(model_cfg, pretrained_model, hic_img_dir, final_adjust_path, device=device,
                                   score=score,
                                   error_min_len=error_min_len,
                                   error_max_len=error_max_len, iou_score=iou_score, chr_len=hic_real_len)
        if infer_return:  # no detect error
            adjust_hic_file = hic_file_path
            adjust_asy_file = asy_file
            break
        logger.info("Detect the %s file finished\n" % adjust_name)

        # get error sum
        error_summary_json = os.path.join(final_adjust_path, "error_summary.json")

        # hic error record for report
        each_error_record = get_cfg.get_each_error(error_summary_json)
        adjust_error_record = [each_error_record[0] - black_num_list[0], each_error_record[1] - black_num_list[1],
                               each_error_record[2], each_error_record[3] - black_num_list[2]]
        # DEBUG error count < 0
        for i in range(len(adjust_error_record)):
            if adjust_error_record[i] < 0:
                adjust_error_record[i] = 0
        adjust_error_record[3] = adjust_error_record[0] + adjust_error_record[1] + adjust_error_record[2]
        hic_error_records.append(adjust_error_record)

        hic_error_records[adjust_epoch].insert(0, str(hic_error_records_epoch) + ".hic")
        hic_error_records_epoch += 1

        error_count_dict[adjust_epoch] = {
            "error_sum": get_cfg.get_error_sum(error_summary_json),
            "hic_file": hic_file_path,
            "assembly_file": asy_file,
            "adjust_path": hic_img_dir
        }
        error_sum = error_count_dict[adjust_epoch]["error_sum"] - black_num_list[0] - black_num_list[1]
        adjust_hic_file = hic_file_path
        adjust_asy_file = asy_file
        adjust_epoch += 1
        if adjust_epoch > 5:  # adjust 5 times at most
            logger.info("Adjust 5 times at most, stop adjusting\n")
            break
    logger.info("Iterative tuning error completed\n")

    logger.info("Stage 3: Split chromosome\n")
    chr_adjust_path = os.path.join(autohic_results, "chromosome")
    os.mkdir(chr_adjust_path)

    # generate whole hic map png
    logger.info("Generate adjusted whole hic map png\n")
    plot_chr_inter(adjust_hic_file, adjust_asy_file, chr_adjust_path, fig_format="png")

    # infer chromosome img
    logger.info("Chromosome number detection\n")
    img_path = os.path.join(chr_adjust_path, "chromosome.png")
    chr_asy_file, chr_number = split_chr(img_path, adjust_asy_file, adjust_hic_file, cfg_dir, device=device)

    # run 3d-dna to split chromosome
    chr_adjust_log = os.path.join(top_output_dir, "logs", "chromosome_epoch.log")
    run_sh = "bash " + os.path.join(cfg_data["TD_DNA_DIR"],
                                    "run-asm-pipeline-post-review.sh") + " -r " + chr_asy_file + " " + \
             original_genome + " " + merged_nodups_path + " > " + chr_adjust_log + " 2>&1"
    get_cfg.subprocess_popen(run_sh, cwd=chr_adjust_path)
    logger.info("Chromosome split completed\n")

    # Generate report
    logger.info("Generate genome report\n")
    chr_fa_name = genome_name_without_extension + ".FINAL.fasta"
    chr_fa_path = os.path.join(chr_adjust_path, chr_fa_name)
    if os.path.exists(chr_fa_path) is False:
        chr_fa_name_bak = genome_name_without_extension + "_HiC.fasta"
        chr_fa_path = os.path.join(chr_adjust_path, chr_fa_name_bak)

    # delete last debris seq
    auto_hic_genome_path = os.path.join(chr_adjust_path, genome_name_without_extension + "_autohic.fasta")
    get_auto_hic_genome(chr_fa_path, chr_number, auto_hic_genome_path)

    # link genome
    link_shell = "ln -s " + auto_hic_genome_path + " " + top_output_dir
    get_cfg.subprocess_popen(link_shell)

    # run quast for chromosome-level genome
    quast_output = os.path.join(top_output_dir, "quast_output")
    os.mkdir(quast_output)

    template_path = os.path.join(cfg_data["AutoHiC_DIR"], "src/report")

    ctg_extra_info["num_chr"] = chr_number

    ctg_fa_path = original_genome
    anchor_ratio = get_cfg.cal_anchor_rate(ctg_fa_path, auto_hic_genome_path)
    autohic_extra_info = {'species': cfg_data["SPECIES_NAME"],
                          'num_chr': chr_number,
                          'anchor_ratio': anchor_ratio * 100,
                          'inversion_len': get_cfg.get_error_len(
                              os.path.join(final_adjust_path, "inversion_error.json")),
                          'debris_len': get_cfg.get_error_len(
                              os.path.join(final_adjust_path, "debris_error.json")),
                          'translocation_len': get_cfg.get_error_len(
                              os.path.join(final_adjust_path, "translocation_error.json"))}

    # get quast thread num
    quast_thread = int(cfg_data["N_CPU"])

    # generate after adjust whole hic map png
    chr_hic_name = genome_name_without_extension + ".final.hic"
    chr_hic_path = os.path.join(chr_adjust_path, chr_hic_name)

    final_chr_txt = os.path.join(chr_adjust_path, "chr.txt")
    plot_chr(chr_hic_path, genome_name="", chr_len_file=final_chr_txt, out_path=chr_adjust_path,
             fig_format="png")

    chr_hic_map = os.path.join(chr_adjust_path, "chromosome.png")

    # get adjust error pairs for report
    translocation_pairs, inversion_pairs, debris_pairs = get_cfg.get_error_pairs(
        error_count_dict[min_hic]["adjust_path"])

    # generate report
    gen_report_cfg(ctg_fa_path, auto_hic_genome_path, quast_output, ctg_extra_info, autohic_extra_info, quast_thread,
                   ctg_hic_map,
                   chr_hic_map, inversion_pairs, translocation_pairs, debris_pairs, hic_error_records,
                   template_path, report_output=top_output_dir)
    logger.info("Genome report completed\n")
    logger.info("AutoHiC finished\n")


def main():
    pass


if __name__ == "__main__":
    typer.run(whole)

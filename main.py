import os
import re

import torch
import typer

from src.core.mul_gen_png import mul_process
from src.core.utils.get_cfg import get_hic_real_len, get_cfg, get_error_sum, subprocess_popen
from src.core.utils.logger import LoggerHandler
from tests.adjust_all_error import adjust_all_error
from tests.error_pd import infer_error
from tests.get_chr_data import split_chr
from tests.plot_chr import plot_chr_inter

app = typer.Typer()


@app.command(name="gen")
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


@app.command(name="autohic")
def whole(cfg_dir: str = typer.Option(..., "--config", "-c", help="autohic config file path")):
    # TODO: 增加每一种错误，是否修改的选项

    # run Juicer + 3d-dna
    run_sh = "bash /home/jzj/Jupyter-Docker/buffer/run.sh " + cfg_dir
    subprocess_popen(run_sh)

    # get cfg
    cfg_data = get_cfg(cfg_dir)

    score = cfg_data["ERROR_FILTER_SCORE"]
    error_min_len = cfg_data["ERROR_MIN_LEN"]
    error_max_len = cfg_data["ERROR_MAX_LEN"]
    iou_score = cfg_data["ERROR_FILTER_IOU_SCORE"]

    output_dir = os.path.join(cfg_data["RESULT_DIR"], cfg_data["JOB_NAME"])
    merged_nodups_path = os.path.join(output_dir, "hic_results", "aligned", "merged_nodups.txt")

    model_cfg = cfg_data["MODEL_CFG"]
    pretrained_model = cfg_data["PRETRAINED_MODEL"]

    # 检查是否有显卡
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    # initialing logger
    logger_file = os.path.join(output_dir, "log.txt")
    LoggerHandler(file=logger_file)

    # get hic file
    hic_file_dir = os.path.join(output_dir, "hic_results", "3d-dna")
    hic_pattern = r"[\d\.]*hic"
    hic_files = []
    # 遍历路径下的所有文件和文件夹
    for filename in os.listdir(hic_file_dir):
        # 使用正则表达式匹配文件名
        if re.match(hic_pattern, filename):
            # 打印与模式匹配的文件名
            hic_files.append(filename)

    # run autohic
    autohic_results = os.path.join(output_dir, "autohic_results")
    adjust_count = 0
    error_count_dict = {}
    for hic_file in hic_files:
        adjust_name = hic_file.split(".")[1]

        adjust_path = os.path.join(autohic_results, adjust_name)
        os.mkdir(adjust_path)
        # 1. gen hic img
        hic_file_path = os.path.join(hic_file_dir, hic_file)
        mul_process(hic_file_path, adjust_name, adjust_path, "dia", cfg_data["N_CPU"])

        # 2. detect hic img
        # get real chr len
        assembly_file = hic_file_path.replace(".hic", ".assembly")
        chr_len = get_hic_real_len(hic_file_path, assembly_file)

        hic_img_dir = os.path.join(adjust_path, adjust_name)
        infer_error(model_cfg, pretrained_model, hic_img_dir, adjust_path, device=device, score=score,
                    error_min_len=error_min_len,
                    error_max_len=error_max_len, iou_score=iou_score, chr_len=chr_len)

        # 3. get error sum
        error_summary_json = os.path.join(adjust_path, "error_summary.json")
        error_count_dict[adjust_name] = {
            "error_sum": get_error_sum(error_summary_json),
            "hic_file": hic_file_path,
            "assembly_file": assembly_file,
            "adjust_path": adjust_path
        }
        adjust_count += 1

    # 选择处理的hic文件，进行处理
    min_hic = min(error_count_dict, key=lambda k: error_count_dict[k]["error_sum"])

    final_hic_file = error_count_dict[min_hic]["hic_file"]
    final_assembly_file = error_count_dict[min_hic]["assembly_file"]
    error_sum = error_count_dict[min_hic]["error_sum"]
    while error_sum > 0:
        adjust_name = str(adjust_count)
        adjust_path = os.path.join(autohic_results, adjust_name)
        os.mkdir(adjust_path)

        hic_file_path = error_count_dict[min_hic]["hic_file"]
        assembly_file_path = error_count_dict[min_hic]["assembly_file"]
        divided_error = error_count_dict[min_hic]["adjust_path"]
        modified_assembly_file = os.path.join(adjust_path, "test.assembly")

        adjust_all_error(hic_file_path, assembly_file_path, divided_error, modified_assembly_file, black_list=None)

        # 运行3d-dna 第二步
        # 1. cd folder
        run_sh = "cd " + adjust_path
        subprocess_popen(run_sh)

        # 2. run 3d-dna
        run_sh = "bash " + os.path.join(cfg_data["TD_DNA_DIR"],
                                        "run-asm-pipeline-post-review.sh") + " -r " + modified_assembly_file + " " + \
                 cfg_data["REFERENCE_GENOME"] + " " + merged_nodups_path
        subprocess_popen(run_sh)

        hic_img_dir = os.path.join(adjust_path, adjust_name)
        hic_file_path = os.path.join(adjust_path, adjust_name, cfg_data["GENOME_NAME"] + ".final.hic")
        assembly_file = hic_file_path.replace(".hic", ".assembly")

        # generate hic img
        mul_process(hic_file_path, adjust_count, hic_img_dir, "dia", cfg_data["N_CPU"])

        # infer error
        chr_len = get_hic_real_len(hic_file_path, assembly_file)
        infer_return = infer_error(model_cfg, pretrained_model, hic_img_dir, adjust_path, device=device, score=score,
                                   error_min_len=error_min_len,
                                   error_max_len=error_max_len, iou_score=iou_score, chr_len=chr_len)
        if infer_return:  # no detect error
            break

        # get error sum
        error_summary_json = os.path.join(hic_img_dir, "error_summary.json")

        error_count_dict[adjust_count] = {
            "error_sum": get_error_sum(error_summary_json),
            "hic_file": hic_file_path,
            "assembly_file": assembly_file,
            "adjust_path": hic_img_dir
        }
        error_sum = error_count_dict[adjust_count]["error_sum"]
        final_hic_file = hic_file_path
        final_assembly_file = assembly_file
        adjust_count += 1

    #
    chr_adjust_path = os.path.join(autohic_results, "chr")
    os.mkdir(chr_adjust_path)

    # 生成chr png
    plot_chr_inter(final_hic_file, final_assembly_file, chr_adjust_path, fig_format="png")

    # 检测chr png
    img_path = os.path.join(chr_adjust_path, "chromosome.png")

    # infer img
    chr_asy_file = split_chr(img_path, final_assembly_file, final_hic_file, cfg_dir)

    # 运行3d-dna 第二步
    run_sh = "cd " + chr_adjust_path
    subprocess_popen(run_sh)

    # 2. run 3d-dna
    run_sh = "bash " + os.path.join(cfg_data["TD_DNA_DIR"],
                                    "run-asm-pipeline-post-review.sh") + " -r " + chr_asy_file + " " + \
             cfg_data["REFERENCE_GENOME"] + " " + merged_nodups_path
    subprocess_popen(run_sh)

    # 获取最终数据


if __name__ == "__main__":
    app()

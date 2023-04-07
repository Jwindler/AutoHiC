import typer
import os
import re
from src.core.mul_gen_png import mul_process
import subprocess
from src.core.utils.logger import logger

app = typer.Typer()


def get_cfg(cfg_dir, key=None):
    config = {}
    with open(cfg_dir, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            key, value = line.strip().split('=')
            config[key] = value
    if key:
        try:
            return config[key]
        except KeyError:
            raise KeyError("Please check you config file")
    else:
        return config


def subprocess_popen(statement):
    p = subprocess.Popen(statement, shell=True, stdout=subprocess.PIPE)
    while p.poll() is None:
        if p.wait() != 0:
            print("命令执行失败，请检查设备连接状态")
            return False
        else:
            re = p.stdout.readlines()  # 获取原始执行结果
            result = []
            for i in range(len(re)):  # 由于原始结果需要转换编码，所以循环转为utf8编码并且去除\n换行
                res = re[i].decode('utf-8').strip('\r\n')
                result.append(res)
            return result


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
    # run Juicer + 3d-dna
    run_sh = "bash /home/jzj/Jupyter-Docker/buffer/run.sh " + cfg_dir
    subprocess_popen(run_sh)

    # get cfg
    cfg_data = get_cfg(cfg_dir)

    # mkdir output dir
    detect_img_dir = os.path.join(cfg_data["RESULT_DIR"], "JOB_NAME", "autohic_results", "detect_imgs")
    error_results_dir = os.path.join(cfg_data["RESULT_DIR"], "JOB_NAME", "autohic_results", "error_results")
    final_results_dir = os.path.join(cfg_data["RESULT_DIR"], "JOB_NAME", "autohic_results", "final_results")
    try:
        os.mkdir(detect_img_dir)
        os.mkdir(error_results_dir)
        os.mkdir(final_results_dir)
    except OSError as error:
        logger.error(error)

    # get hic file
    hic_file_dir = os.path.join(cfg_data["RESULT_DIR"], "JOB_NAME", "hic_results", "3d-dna")
    hic_pattern = r"[\w\.]*hic"
    hic_files = []
    # 遍历路径下的所有文件和文件夹
    for filename in os.listdir(hic_file_dir):
        # 使用正则表达式匹配文件名
        if re.match(hic_pattern, filename):
            # 打印与模式匹配的文件名
            hic_files.append(filename)
    # hic_file_name = hic_files[0].split(".")[0]
    # hic_file_num = len(hic_files)

    # run autohic
    hic_img_dir = os.path.join(cfg_data["RESULT_DIR"], "JOB_NAME", "autohic_results")
    for hic_file in hic_files:
        # 1. gen hic img
        mul_process(os.path.join(hic_file_dir, hic_file), hic_file, hic_img_dir, "dia", cfg_data["N_CPU"])

        # 2. detect hic img
        # TODO: 接入检测模型


if __name__ == "__main__":
    app()

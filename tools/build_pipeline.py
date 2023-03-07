#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: subprocess_popen
@contact: jzjlab@163.com
@file: build_pipeline.py
@time: 11/24/22 2:54 PM
@function: acquire juicer pipeline and check environment
"""

import subprocess

from src.core.utils.logger import logger


def subprocess_popen(statement):
    """
        execute linux command and return result
    Args:
        statement: linux command

    Returns:
        result of command
    """
    # Execute the command
    p = subprocess.Popen(statement, shell=True, stdout=subprocess.PIPE)
    while p.poll() is None:
        if p.wait() != 0:
            logger.error("execute command error，please check your command")
            return False
        else:
            re = p.stdout.readlines()  # get result
            result = []
            # decode and remove \n
            for i in range(len(re)):
                res = re[i].decode('utf-8').strip('\r\n')
                result.append(res)
            return result


def download_juicer(install_path=None, juicer_file_url=None, juicer_file_name=None):
    """
        download juicer pipeline
    Args:
        install_path: path to install
        juicer_file_url: juicer file url
        juicer_file_name: juicer file name

    Returns:
        juicer file path
    """
    logger.info("download juicer pipeline")

    if install_path is None:
        install_path = subprocess_popen("pwd")[0]
    if juicer_file_url is None:
        juicer_file_url = "https://github.com/aidenlab/juicer/archive/refs/tags/1.6.tar.gz"

    if install_path.endswith("/") is not True:
        install_path = install_path + "/"

    # create juicer directory
    for file_iter in ["references", "restriction_sites"]:
        subprocess_popen(' '.join(["mkdir", install_path + file_iter]))

    # download juicer
    subprocess_popen(' '.join(["wget -c", "-P", install_path, juicer_file_url]))

    if juicer_file_name is None:
        juicer_file_name = "juicer-1.6.tar.gz"
    subprocess_popen(' '.join(["tar", "-zxvf", install_path + juicer_file_name, "-C", install_path]))  #

    subprocess_popen(' '.join(["mv", install_path + "juicer-1.6", install_path + "juicer"]))  # rename

    subprocess_popen(" ".join(
        ["ln -s", install_path + "juicer/" + "CPU", install_path + "juicer/scripts"]))  # generate symbolic link
    # download juicer_tools.jar
    subprocess_popen(" ".join(["wget -c", "-P", install_path + "juicer/scripts/common/",
                               "https://hicfiles.tc4ga.com/public/juicer/juicer_tools.1.9.9_jcuda.0.8.jar"]))
    # generate symbolic link
    subprocess_popen(" ".join(["ln -s", install_path + "juicer/scripts/common/juicer_tools.1.9.9_jcuda.0.8.jar",
                               install_path + "juicer/scripts/common/juicer_tools.jar"]))

    logger.info("download juicer pipeline successfully")
    return install_path


def download_3d_dna(install_path=None, d3dna_file_url=None):
    """
        download 3d-dna
    Args:
        install_path: install path
        d3dna_file_url:

    Returns:

    """
    logger.info("download 3d-dna")
    if install_path is None:
        install_path = subprocess_popen("pwd")[0]
    if d3dna_file_url is None:
        d3dna_file_url = "https://github.com/theaidenlab/3d-dna.git"
    if install_path.endswith("/") is not True:
        install_path = install_path + "/"

    # download 3d-dna
    subprocess_popen(' '.join(["git clone", d3dna_file_url, install_path + "3d-dna"]))

    logger.info("download 3d-dna successfully")
    return install_path + "3d-dna"


def main():
    temp = download_juicer(install_path="/home/jzj/Downloads/test")
    print(temp)


if __name__ == "__main__":
    main()

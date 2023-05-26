#!/usr/bin/env python3
# encoding: utf-8

"""
@author: lyj
@contact: jzjlab@163.com
@file: gen_report.py
@time: 5/18/23 10:58 AM
@function:
"""

import base64
import datetime
import os

from jinja2 import FileSystemLoader, Environment

from src.report import read_data


def image_to_base64(image_path):
    """
        将图片转为 Base64流
    Args:
        image_path: 图片路径

    Returns:

    """
    with open(image_path, "rb") as file:
        base64_data = base64.b64encode(file.read())  # base64编码
    return 'data:image/png;base64,' + base64_data.decode('ascii')


def report(data, output_path, template_path):
    """
        generate report
    Args:
        data: data dict
        output_path: report output path
        template_path: report template path

    Returns:
        None
    """
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template("report_template.html")
    with open(os.path.join(output_path, "result.html"), 'w+') as report_file:
        html_content = template.render(
            report_title="AutoHiC Report",
            report_date=datetime.datetime.now().strftime('%c'),
            summaries=data['summaries'],
            adjust=data['adjust'],
            errors=data['errors'],
            additional=data['additional'],
            chromosome_image=data['chromosome_image'],
        )
        report_file.write(html_content)


def gen_report_cfg(scf_path, chr_path, quast_output, ctg_extra_info, autohic_extra_info, quast_thread, before_adjust,
                   after_adjust, inv_pairs, tran_pairs, deb_pairs, hic_records, template_path, report_output):
    ctg_output_path = os.path.join(quast_output, "contig")
    chr_output_path = os.path.join(quast_output, "chromosome")
    os.mkdir(ctg_output_path)
    os.mkdir(chr_output_path)

    # 从read.py获取数据
    summary_data, bef_anchor_data, err_ratio, chr_len_gc, chr_fig_path = read_data.gen_chr_png(scf_path, chr_path,
                                                                                               ctg_output_path,
                                                                                               chr_output_path,
                                                                                               ctg_extra_info,
                                                                                               autohic_extra_info,
                                                                                               quast_thread,
                                                                                               num_one_line=24)
    data = {
        "report_title": 'AutoHiC Report',
        "summaries": summary_data,
        "adjust": [image_to_base64(before_adjust), image_to_base64(after_adjust)],
        "errors": [
            {
                "name": 'Translocation',
                "pairs": tran_pairs,
            },
            {
                "name": 'Inversion',
                "pairs": inv_pairs,
            },
            {
                "name": 'Debris',
                "pairs": deb_pairs,
            },
        ],
        "additional": [
            {
                "name": 'Before correcting',
                "table_data": bef_anchor_data,
            },
            {
                "name": 'Error ratio',
                "table_header": ['Error type', 'Error ratio(%)'],
                "table_data": err_ratio,
            },
            {
                "name": 'Number of error corrections',
                "table_header": ['Error type', 'Translocation', 'Inversion', 'Debris', 'Total'],
                "table_data": hic_records,
            },
            {
                "name": 'Chromosome length',
                "table_header": ['Molecule', 'Length(bp)', 'GC(%)'],
                "table_data": chr_len_gc,
            },
        ],
        "chromosome_image": image_to_base64(chr_fig_path).replace('png', 'svg+xml'),
    }

    report(data, report_output, template_path)


def main():
    # 文件路径
    ctg_path = '/home/jzj/Jupyter-Docker/buffer/AutoHiC_test/data/reference/hd.fa'
    chr_path = '/home/jzj/Jupyter-Docker/buffer/AutoHiC_test/autohic_results/chr/hd.FINAL.fasta'
    quast_output = '/home/jzj/Jupyter-Docker/buffer/AutoHiC_test/autohic_results/quast'

    template_path = "/home/jzj/HiC-OpenCV/src/report"

    # jzj提供的info
    ctg_extra_info = {'species': 'spider',
                      'num_chr': 23,
                      'inversion_len': 1111,
                      'debris_len': 1111,
                      'translocation_len': 1111, }

    autohic_extra_info = {'species': 'spider',
                          'num_chr': 23,
                          'anchor_ratio': 93,
                          'inversion_len': 1111,
                          'debris_len': 1111,
                          'translocation_len': 1111, }

    # 跑quast的线程数
    quast_thread = 2  # 从配置文件获取

    before_adjust_png_path = "/home/jzj/buffer/image_test.png"
    after_adjust_png_path = "/home/jzj/buffer/image_test.png"

    image_demo = "/home/jzj/buffer/image_test.png"

    inversion_pairs = [
        [{"image": image_to_base64(image_demo), "start": 22, "end": 333},
         {"image": image_to_base64(image_demo), "start": 222, "end": 33223}],
        [{"image": image_to_base64(image_demo), "start": 22, "end": 333},
         {"image": image_to_base64(image_demo), "start": 222, "end": 33223}],
        [{"image": image_to_base64(image_demo), "start": 22, "end": 333},
         {"image": image_to_base64(image_demo), "start": 222, "end": 33223}],
        [{"image": image_to_base64(image_demo), "start": 22, "end": 333},
         {"image": image_to_base64(image_demo), "start": 222, "end": 33223}],
        [{"image": image_to_base64(image_demo), "start": 22, "end": 333},
         {"image": image_to_base64(image_demo), "start": 222, "end": 33223}],
    ]

    translocation_pairs = [
        [{"image": image_to_base64(image_demo), "start": 22, "end": 333},
         {"image": image_to_base64(image_demo), "start": 222, "end": 33223}],
        [{"image": image_to_base64(image_demo), "start": 22, "end": 333},
         {"image": image_to_base64(image_demo), "start": 222, "end": 33223}],
        [{"image": image_to_base64(image_demo), "start": 22, "end": 333},
         {"image": image_to_base64(image_demo), "start": 222, "end": 33223}],
        [{"image": image_to_base64(image_demo), "start": 22, "end": 333},
         {"image": image_to_base64(image_demo), "start": 222, "end": 33223}],
        [{"image": image_to_base64(image_demo), "start": 22, "end": 333},
         {"image": image_to_base64(image_demo), "start": 222, "end": 33223}],
    ]
    debris_pairs = [
        [{"image": image_to_base64(image_demo), "start": 22, "end": 333},
         {"image": image_to_base64(image_demo), "start": 222, "end": 33223}],
        [{"image": image_to_base64(image_demo), "start": 22, "end": 333},
         {"image": image_to_base64(image_demo), "start": 222, "end": 33223}],
        [{"image": image_to_base64(image_demo), "start": 22, "end": 333},
         {"image": image_to_base64(image_demo), "start": 222, "end": 33223}],
        [{"image": image_to_base64(image_demo), "start": 22, "end": 333},
         {"image": image_to_base64(image_demo), "start": 222, "end": 33223}],
        [{"image": image_to_base64(image_demo), "start": 22, "end": 333},
         {"image": image_to_base64(image_demo), "start": 222, "end": 33223}],
    ]

    hic_error_records = [
        ['0.hic', '3', '2', '1', '6'],
        ['0.hic', '3', '2', '1', '6'],
        ['0.hic', '3', '2', '1', '6'],
        ['0.hic', '3', '2', '1', '6'],
        ['0.hic', '3', '2', '1', '6'],
    ]

    report_output = "/home/jzj/Jupyter-Docker/buffer"

    gen_report_cfg(ctg_path, chr_path, quast_output, ctg_extra_info, autohic_extra_info, quast_thread,
                   before_adjust_png_path,
                   after_adjust_png_path, inversion_pairs, translocation_pairs, debris_pairs, hic_error_records,
                   template_path, report_output)


if __name__ == '__main__':
    main()

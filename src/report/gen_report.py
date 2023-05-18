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
    :param image_path: 图片路径
    :return:
    """
    with open(image_path, "rb") as file:
        base64_data = base64.b64encode(file.read())  # base64编码
    return 'data:image/png;base64,' + base64_data.decode('ascii')


def report(data, output_path, template_path):
    env = Environment(loader=FileSystemLoader('./'))
    template = env.get_template(template_path)
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


def gen_report_cfg(scf_path, chr_path, output_path, extra_info, quast_thread):
    pass


def main():
    # 文件路径
    scf_path = '/home/pzx/PycharmProjects/pythonProject_hic/Html/07.read_data/seqkit_test/ci_contig.fa'
    chr_path = '/home/pzx/PycharmProjects/pythonProject_hic/Html/07.read_data/seqkit_test/cp_autohic.fa'
    output_path = '/home/pzx/PycharmProjects/pythonProject_hic/Html/07.read_data/quast_result'
    # FIXME: 两个quast在同一个文件夹下会冲突吗？

    # jzj提供的info
    extra_info = {'species': 'spider',
                  'num_chr': 23,
                  'anchor_ratio': 93,
                  'inversion_len': 1111,
                  'debris_len': 1111,
                  'translocation_len': 1111, }

    # 跑quast的线程数
    quast_thread = 6

    # 从read.py获取数据
    summary_data, bef_anchor_data, err_ratio, chr_len_gc, chr_fig_path = read_data.gen_chr_png(scf_path, chr_path,
                                                                                               output_path,
                                                                                               extra_info,
                                                                                               quast_thread,
                                                                                               num_one_line=28)

    image_demo = './images/image_test.png'
    before_adjust_png_path = ""
    after_adjust_png_path = ""
    data = {
        "report_title": 'AutoHiC Report',
        "summaries": summary_data,
        "adjust": [image_to_base64(before_adjust_png_path), image_to_base64(after_adjust_png_path)],
        "errors": [
            {
                "name": 'Inversion',
                "pairs": [
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
                ],
            },
            {
                "name": 'Translocation',
                "pairs": [
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
                ],
            },
            {
                "name": 'Chimeric_join',
                "pairs": [
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
                ],
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
                "table_header": ['Error type', 'Inversion', 'Translocation', 'Debris', 'Total'],
                "table_data": [
                    ['0.hic', '3', '2', '1', '6'],
                    ['0.hic', '3', '2', '1', '6'],
                    ['0.hic', '3', '2', '1', '6'],
                    ['0.hic', '3', '2', '1', '6'],
                    ['0.hic', '3', '2', '1', '6'],
                ],
            },
            {
                "name": 'Chromosome length',
                "table_header": ['Molecule', 'Length(bp)', 'GC(%)'],
                "table_data": chr_len_gc,
            },
        ],
        "chromosome_image": image_to_base64(chr_fig_path).replace('png', 'svg+xml'),
    }
    template_path = "./template.html"
    report(data, output_path, template_path)


if __name__ == '__main__':
    main()

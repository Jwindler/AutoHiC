#!/usr/bin/env python3
# encoding: utf-8

"""
@author: pzx
@contact: jzjlab@163.com
@file: read_data.py
@time: 5/18/23 10:58 AM
@function:
"""
import os

import pandas as pd

from src.core.utils.get_cfg import subprocess_popen
from src.report import gen_chr_fig


def run_quast(input_path, output_path, extra_info, quast_thread):
    """
    用于scf.fa或chr.fa跑quast,然后读取数据,配成所需的数据格式
    Args:
        input_path: 需要跑quast的genome.fa的路径
        output_path: quast结果输出路径
        extra_info: 需要额外提供的数据，比如染色体数目，错误长度等
        quast_thread: 跑quast的最大线程数

    Returns:
        html中table_summary和table_error_ratio的所需数据格式
    """

    # 跑quast
    statement = 'python quast.py ' + '\x20' + input_path + ' -o ' + output_path + ' -t ' + str(
        quast_thread) + ' --large'
    subprocess_popen(statement)

    # extra_info
    num_chr = extra_info['num_chr']
    total_err_len = extra_info['inversion_len'] + extra_info['debris_len'] + extra_info['translocation_len']

    # 读取quast结果
    sum_data = pd.read_csv(os.path.join(output_path, "report.tsv"), sep='\t', index_col=0, header=0)

    # 　计算CC_ratio
    num_contig = int(sum_data.loc['# contigs', :][0])  # 读取contig数目
    cc_ratio = '%.2f' % (num_contig / num_chr)

    # 计算Structural_errors_ratio
    total_length = int(sum_data.loc['Total length', :][0])
    structural_err_ratio = '%.8f' % (total_err_len / total_length)
    inv_err_ratio = '%.8f' % (extra_info['inversion_len'] / total_length)
    tran_err_ratio = '%.8f' % (extra_info['translocation_len'] / total_length)
    deb_err_ratio = '%.8f' % (extra_info['debris_len'] / total_length)

    # 生成所需数据格式
    err_ratio = [['Total error ratio', structural_err_ratio],
                 ['Inversion error ratio', inv_err_ratio],
                 ['Translocation error ratio', tran_err_ratio],
                 ['Debris error ratio', deb_err_ratio]
                 ]

    summary_data = [['Species', extra_info['species']],
                    ['Assembly size (bp)', int(sum_data.loc['Total length', :][0])],
                    ['Scaffold N50 (bp)', int(sum_data.loc['N50', :][0])],
                    ['Scaffold_N90 (bp)', int(sum_data.loc['N90', :][0])],
                    ['CC ratio (%)', cc_ratio],
                    ['Structural errors ratio (%)', structural_err_ratio],
                    ['Number of chromosomes', num_chr],
                    ['HiC Anchor rate (%)', extra_info['anchor_ratio']],
                    ['Number of scaffolds', int(sum_data.loc['# contigs', :][0])],
                    ['Longest scaffold (bp)', int(sum_data.loc['Largest contig', :][0])],
                    ['Scaffold L50', int(sum_data.loc['L50', :][0])],
                    ['Scaffold L90', int(sum_data.loc['L90', :][0])],
                    ['GC (%)', sum_data.loc['GC (%)', :][0]]
                    ]

    return summary_data, err_ratio


# 计算每条染色体长度和gc含量
def readfasta(input_path, quast_path):
    """
    根据chr.fa计算每条chr的长度和gc含量
    :param input_path: chr.fa的路径
    :param quast_path: chr.fa跑quast后的结果路径
    :return:　每条染色体的长度和gc含量 组成的所需数据格式
    """
    # 读取quast结果
    sum_data = pd.read_csv(quast_path + '/report.tsv', sep='\t', index_col=0, header=0)
    # scf.fa或chr.fa的总长度
    total_length = int(sum_data.loc['Total length', :][0])
    total_gc = sum_data.loc['GC (%)', :][0]
    # 读取fasta序列
    f = open(input_path, 'r')
    lines = f.readlines()
    f.close()

    seq = []
    index = []
    seqplast = ""
    numlines = 0
    for i in lines:
        if '>' in i:  # 判断是序列行还是说明行
            index.append(i.replace("\n", '').replace(">", "").split()[0])
            seq.append(seqplast)  # 将序列添加到ｓｅｑ中
            seqplast = ""  # 每次清空，不然所有序列连在一起
            numlines += 1
        else:
            seqplast = seqplast + i.replace("\n", "")  # 把分行的序列拼接成一个字符串
            numlines += 1
        if numlines == len(lines):  # 将最后一轮的序列添加进去
            seq.append(seqplast)
    seq = seq[1:]

    # 　计算每条chr的长度和gc含量
    chr_len_gc = [['All', total_length, total_gc]]
    chr_len = {}
    for i in seq:
        gc = '%.2f' % (float(i.count('G') + i.count("g") + i.count('C') + i.count('c')) / len(i) * 100)
        sin_len_gc = ['Chromosome ' + str(seq.index(i) + 1), len(i), gc]
        sin_len = len(i)
        chr_len_gc.append(sin_len_gc)
        chr_len['Chr ' + str(seq.index(i) + 1)] = sin_len
        # chr_len[index[seq.index(i)]] = sin_len

    return chr_len_gc, chr_len


# 生成染色体图片
def gen_chr_png(scf_path, chr_path, output_path, extra_info, quast_thread, num_one_line):
    """
        将需要进行计算的数据配成所需的格式
    Args:
        scf_path: 需要跑quast的scf.fa的路径,x/x.fa
        chr_path: 需要跑quast的chr.fa的路径,x/x.fa
        output_path: quast结果输出路径
        extra_info: 需要额外提供的数据，比如染色体数目，错误长度等
        quast_thread: 跑quast的最大线程数
        num_one_line: 染色体图片中每行显示的染色体数目

    Returns:
        table_summary、table_error_ratio、table_bef_anchor、table_chr_len_gc的数据和染色体图片路径
    """

    # 为表格summary,err_ratio跑quast并读取数据
    summary_data, err_ratio = run_quast(chr_path, output_path, extra_info, quast_thread)

    # 为表格Before anchoring 跑quast并读取数据
    bef_anchor_data, _ = run_quast(scf_path, output_path, extra_info, quast_thread)

    # 计算染色体长度、gc含量
    chr_len_gc, chr_len = readfasta(chr_path, output_path)

    # 染色体图片的路径
    chr_fig_path = gen_chr_fig.gen_chr_png(chr_len, output_path, num_one_line)

    return summary_data, bef_anchor_data, err_ratio, chr_len_gc, chr_fig_path

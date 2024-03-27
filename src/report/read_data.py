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

from src.report import gen_chr_fig
from src.utils import get_cfg


def run_quast(input_path, output_path, extra_info, quast_thread, ctg_flag=False):
    statement = 'quast.py ' + input_path + ' -o ' + output_path + ' -t ' + str(quast_thread) + ' --large'
    get_cfg.subprocess_popen(statement)
    # print(statement)

    num_chr = extra_info['num_chr']
    total_err_len = extra_info['inversion_len'] + extra_info['translocation_len']

    sum_data = pd.read_csv(os.path.join(output_path, "report.tsv"), sep='\t', index_col=0, header=0)

    num_contig = int(sum_data.loc['# contigs', :][0])
    cc_ratio = int(num_contig / num_chr)

    total_length = int(sum_data.loc['Total length', :][0])
    if (total_err_len / total_length) == 0:
        structural_err_ratio = '0'
    else:
        structural_err_ratio = '%.8f' % (total_err_len / total_length)
    inv_err_ratio = '%.8f' % (extra_info['inversion_len'] / total_length)
    tran_err_ratio = '%.8f' % (extra_info['translocation_len'] / total_length)

    err_ratio = [['Total error ratio', structural_err_ratio],
                 ['Inversion error ratio', inv_err_ratio],
                 ['Translocation error ratio', tran_err_ratio]
                 ]
    if ctg_flag:
        summary_data = [['Species', extra_info['species']],
                        ['Assembly size (bp)', int(sum_data.loc['Total length', :][0])],
                        ['Scaffold N50 (bp)', int(sum_data.loc['N50', :][0])],
                        ['Scaffold N90 (bp)', int(sum_data.loc['N90', :][0])],
                        ['CC ratio', cc_ratio],
                        ['Structural errors ratio (%)', structural_err_ratio],
                        # ['Number of chromosomes', num_chr],
                        ['Number of scaffolds', int(sum_data.loc['# contigs', :][0])],
                        ['Longest scaffold (bp)', int(sum_data.loc['Largest contig', :][0])],
                        ['Scaffold L50', int(sum_data.loc['L50', :][0])],
                        ['Scaffold L90', int(sum_data.loc['L90', :][0])],
                        ['GC (%)', sum_data.loc['GC (%)', :][0]]
                        ]
    else:
        summary_data = [['Species', extra_info['species']],
                        ['Assembly size (bp)', int(sum_data.loc['Total length', :][0])],
                        ['Scaffold N50 (bp)', int(sum_data.loc['N50', :][0])],
                        ['Scaffold N90 (bp)', int(sum_data.loc['N90', :][0])],
                        ['CC ratio', cc_ratio],
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


def readfasta(input_path, quast_path):
    sum_data = pd.read_csv(os.path.join(quast_path, "report.tsv"), sep='\t', index_col=0, header=0)

    # scf.fa或chr.fa的总长度
    total_length = int(sum_data.loc['Total length', :][0])
    total_gc = sum_data.loc['GC (%)', :][0]


    with open(input_path, 'r') as f:
        lines = f.readlines()

    seq, index = [], []
    seqplast = ""
    numlines = 0
    for i in lines:
        if '>' in i:
            index.append(i.replace("\n", '').replace(">", "").split()[0])
            seq.append(seqplast)
            seqplast = ""
            numlines += 1
        else:
            seqplast = seqplast + i.replace("\n", "")
            numlines += 1
        if numlines == len(lines):
            seq.append(seqplast)
    seq = seq[1:]

    chr_len_gc = [['All', total_length, total_gc]]
    chr_len = {}
    for i in seq:
        gc = '%.2f' % (float(i.count('G') + i.count("g") + i.count('C') + i.count('c')) / len(i) * 100)
        sin_len_gc = ['Chromosome ' + str(seq.index(i) + 1), len(i), gc]
        sin_len = len(i)
        chr_len_gc.append(sin_len_gc)
        chr_len['Chr ' + str(seq.index(i) + 1)] = sin_len

    return chr_len_gc, chr_len


def gen_chr_png(scf_path, chr_path, scf_output_path, chr_output_path, ctg_extra_info, autohic_extra_info, quast_thread,
                num_one_line):

    summary_data, _ = run_quast(chr_path, chr_output_path, autohic_extra_info, quast_thread)

    bef_anchor_data, err_ratio = run_quast(scf_path, scf_output_path, ctg_extra_info, quast_thread, ctg_flag=True)

    chr_len_gc, chr_len = readfasta(chr_path, chr_output_path)

    chr_fig_path = gen_chr_fig.gen_chr_png(chr_len, chr_output_path, num_one_line)

    return summary_data, bef_anchor_data, err_ratio, chr_len_gc, chr_fig_path

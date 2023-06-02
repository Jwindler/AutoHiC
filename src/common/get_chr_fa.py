#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: get_chr_fa.py
@time: 6/2/23 10:28 AM
@function: 
"""

from Bio import SeqIO


def extract_sequences_from_genome(genome_file, id_list, output_file):
    """
        get sequences from genome file by id list
    Args:
        genome_file: genome file path
        id_list: id list
        output_file: output file path

    Returns:
        genome file with sequences in id list
    """
    sequences = []

    # 逐个读取基因组文件中的序列
    for record in SeqIO.parse(genome_file, "fasta"):
        # 检查序列的ID是否在指定的ID列表中
        if record.id in id_list:
            sequences.append(record)

    # 将提取的序列写入输出文件
    SeqIO.write(sequences, output_file, "fasta")


def get_genome_ids(genome_file):
    """
        get genome seq ids
    Args:
        genome_file: genome file path

    Returns:
        genome seq ids
    """
    ids = []

    # 逐个读取基因组文件中的序列
    for record in SeqIO.parse(genome_file, "fasta"):
        ids.append(record.id)

    return ids


def get_auto_hic_genome(genome_file, chr_number, output_file):
    """
        get auto hic genome
    Args:
        genome_file: genome file path
        chr_number: chromosome number
        output_file: output file path

    Returns:
        auto hic genome
    """
    seq_ids = get_genome_ids(genome_file)
    chr_seq_ids = seq_ids[:chr_number]
    extract_sequences_from_genome(genome_file, chr_seq_ids, output_file)


def main():
    # 示例用法
    genome_file = "/home/jzj/Jupyter-Docker/buffer/genomes_test/02_br/br_4/chr/br_chr.fasta"
    chr_number = 11
    output_file = "/home/jzj/Jupyter-Docker/buffer/output.fasta"

    get_auto_hic_genome(genome_file, chr_number, output_file)


if __name__ == '__main__':
    main()

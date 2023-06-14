#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: check_genome.py
@time: 6/5/23 3:19 PM
@function: 
"""

from Bio import SeqIO


def split_genome(input_file, output_file, split_len=80):
    """
        Split genome into specify per line
    Args:
        input_file: input genome file
        output_file: output genome file
        split_len: split length

    Returns:
        Split genome file
    """

    # read genome file
    records = SeqIO.parse(input_file, "fasta")

    with open(output_file, "w") as output_handle:
        for record in records:
            # get sequence name and sequence
            seq_name = record.id
            sequence = record.seq

            # split sequence
            split_sequence = [sequence[i:i + split_len] for i in range(0, len(sequence), split_len)]
            output_handle.write(f">{seq_name}\n")
            for i, seq in enumerate(split_sequence):
                output_handle.write(f"{seq}\n")


def check_genome(input_file, base_len=80):
    """
        Check genome file first line length
    Args:
        input_file: input genome file
        base_len: compare length

    Returns:
        True or False
    """
    with open(input_file, "r") as f:
        for line in f:
            if line.startswith(">"):
                continue
            else:
                temp_line = line.strip()
                print(len(temp_line))
                if len(temp_line) > base_len:
                    return True
                else:
                    return False


def main():
    pass


if __name__ == "__main__":
    main()

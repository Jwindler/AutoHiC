#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: error_json2xlsx.py
@time: 2/24/23 10:34 AM
@function: 
"""

import os
import json
import pandas as pd


def error2xlsx(error_file_path, output_path):
    with open(error_file_path, "r") as outfile:
        errors_queue = json.loads(outfile.read())

    columns = ['Error_type', 'ID', 'Resolution', 'Start', 'End']
    error_type_list = []
    error_id_list = []
    error_resolution_list = []
    error_start_list = []
    error_end_list = []
    for error_type, error_infos in errors_queue.items():
        for error_id in error_infos:
            error_type_list.append(error_type)
            error_id_list.append(error_id["id"])
            error_resolution_list.append(error_id['resolution'])
            error_start_list.append(error_id['hic_loci'][0])
            error_end_list.append(error_id['hic_loci'][1])
    df = pd.DataFrame(
        list(zip(error_type_list, error_id_list, error_resolution_list, error_start_list, error_end_list)),
        columns=columns)

    # Write DataFrame to Excel file
    df.to_excel(output_path)


def main():
    error_path = "/home/jzj/Jupyter-Docker/buffer/curated/curated_2"

    error_file = os.path.join(error_path, "overlap_filtered_errors.json")
    output_path = os.path.join(error_path, "errors.xlsx")

    error2xlsx(error_file, output_path)


if __name__ == "__main__":
    main()

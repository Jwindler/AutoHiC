#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: error_json2xlsx.py
@time: 2/24/23 10:34 AM
@function: 
"""
import json

import pandas as pd


def error2xlsx(error_file_path, output_path):
    """
    Convert error json file to xlsx file
    Args:
        error_file_path: error json file path
        output_path: output xlsx file path

    Returns:
        None
    """
    with open(error_file_path, "r") as outfile:
        errors_queue = json.loads(outfile.read())

    columns = ['Error_type', 'ID', 'Resolution', 'A_Start', 'A_End', 'B_Start', 'B_End']
    error_type_list = []
    error_id_list = []
    error_resolution_list = []
    error_a_start_list = []
    error_b_start_list = []
    error_a_end_list = []
    error_b_end_list = []
    for error_type, error_infos in errors_queue.items():
        for error_id in error_infos:
            error_type_list.append(error_type)
            error_id_list.append(error_id["id"])
            error_resolution_list.append(error_id['resolution'])
            error_a_start_list.append(error_id['hic_loci'][0])
            error_b_start_list.append(error_id['hic_loci'][2])
            error_a_end_list.append(error_id['hic_loci'][1])
            error_b_end_list.append(error_id['hic_loci'][3])
    df = pd.DataFrame(
        list(zip(error_type_list, error_id_list, error_resolution_list, error_a_start_list, error_a_end_list,
                 error_b_start_list, error_b_end_list)),
        columns=columns)

    # Write DataFrame to Excel file
    df.to_excel(output_path)


def excel2json(excel_path, json_path):
    """
    Convert excel file to json file
    Args:
        excel_path: excel file path
        json_path: json file path

    Returns:
        None
    """
    dataframe1 = pd.read_excel(excel_path, header=0)
    id_list = dataframe1["ID"].values
    real_start = dataframe1["Real_Start"].values
    real_end = dataframe1["Real_End"].values
    errors = {}
    for error_id, real_s, real_e in zip(id_list, real_start, real_end):
        errors[str(error_id)] = {
            "start": int(real_s),
            "end": int(real_e)
        }

    with open(json_path, "w") as outfile:
        json.dump(errors, outfile)


def main():
    pass


if __name__ == "__main__":
    main()

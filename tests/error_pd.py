#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: error_pd.py
@time: 4/18/23 8:48 PM
@function: construct error pd
"""

import json
import os
from collections import defaultdict
import pandas as pd


# FIXME: update logger when to use > 后续整合实现

class ERRORS:
    __slots__ = "filter_dict", "df", "info_file", "classes", "out_path", "img_size"

    def __init__(self, classes, info_file, out_path, img_size):
        self.info_file = info_file
        self.classes = classes
        self.out_path = out_path
        self.img_size = img_size

        # 创建一个空的DataFrame
        self.df = pd.DataFrame()

        # 创建一个记录每次过滤的字典
        self.filter_dict = dict()

    # generate error structure
    def create_structure(self, img_info, detection_result):
        """

        Args:
            img_info:
            detection_result:

        Returns:

        """
        for category, classes in zip(detection_result, self.classes):
            for index, error in enumerate(category):
                error = error.tolist()
                temp_dict = dict()
                temp_dict["image_id"] = list(img_info.keys())[0]
                temp_dict["category"] = classes
                temp_dict["bbox_1"], temp_dict["bbox_2"], temp_dict["bbox_3"], temp_dict["bbox_4"] = error[0:4]
                temp_dict["score"] = round(error[4], 2)
                temp_dict["resolution"] = img_info[list(img_info.keys())[0]]["resolution"]
                temp_dict["hic_loci_1"], temp_dict["hic_loci_2"], temp_dict["hic_loci_3"], temp_dict[
                    "hic_loci_4"] = self.bbox2hic(error[0:4], img_info)

                # 将字典数据添加到DataFrame中
                if error[4] > 0.9:
                    df_new_row = pd.DataFrame(temp_dict, index=[0])
                    self.df = pd.concat([self.df, df_new_row])

        return self.df

    # convert bbox coordinate to hic coordinate
    def bbox2hic(self, bbox, img_info):
        img_size = self.img_size
        key = list(img_info.keys())[0]
        # Straw b chromosome
        img_chr_a_s = img_info[key]["chr_A_start"]
        img_chr_a_e = img_info[key]["chr_A_end"]

        # Straw a chromosome
        img_chr_b_s = img_info[key]["chr_B_start"]
        img_chr_b_e = img_info[key]["chr_B_end"]

        img_chr_w = img_chr_a_e - img_chr_a_s
        img_chr_h = img_chr_b_e - img_chr_b_s

        w_ration = img_chr_w / img_size[0]
        h_ration = img_chr_h / img_size[1]

        x, y, w, h = bbox

        a_s = x * w_ration + img_chr_a_s
        a_e = w * w_ration + img_chr_a_s
        b_s = y * h_ration + img_chr_b_s
        b_e = h * h_ration + img_chr_b_s

        # to int
        hic_loci = list(map(lambda temp: int(temp), [a_s, a_e, b_s, b_e]))

        return hic_loci

    @staticmethod
    def cal_iou(box1, box2):
        x1min, y1min, x1max, y1max = box1[0], box1[2], box1[1], box1[3]
        x2min, y2min, x2max, y2max = box2[0], box2[2], box2[1], box2[3]

        # calculate box area
        s1 = (y1max - y1min + 1.) * (x1max - x1min + 1.)
        s2 = (y2max - y2min + 1.) * (x2max - x2min + 1.)

        # calculate overlap area
        x_min = max(x1min, x2min)
        y_min = max(y1min, y2min)
        x_max = min(x1max, x2max)
        y_max = min(y1max, y2max)

        inter_h = max(y_max - y_min + 1, 0)
        inter_w = max(x_max - x_min + 1, 0)

        intersection = inter_h * inter_w
        union = s1 + s2 - intersection

        # calculate iou
        iou = intersection / union
        return iou

    @staticmethod
    def transform_bbox(detection_bbox):
        """
        transform bbox to [x1, y1, x2, y2]
        :param detection_bbox: [x, y, w, h]
        :return:
        """
        x1 = detection_bbox[0]
        y1 = detection_bbox[1]
        x2 = detection_bbox[0] + detection_bbox[2]
        y2 = detection_bbox[1] + detection_bbox[3]
        return [x1, y1, x2, y2]

    @staticmethod
    def if_include(bbox1, bbox2):
        # default bbox1 is previous bbox
        if bbox2[1] <= bbox1[1] and bbox2[2] >= bbox1[2] and bbox2[3] <= bbox1[3]:
            return True
        else:
            return False

    # filter error according to score
    def filter_all_errors(self, score: float = 0.9, out_path="score_filtered_errors.xlsx", filter_cls=None):
        score_filtered_errors_counter = dict()  # record the number of filtered errors
        all_errors_counter = dict()
        if filter_cls is None:
            filter_cls = self.classes
        filtered_errors = self.df[self.df['score'] > score]

        # save to excel
        filtered_errors.to_excel(os.path.join(self.out_path, out_path), sheet_name='Sheet1', index=False)

        for key in filter_cls:
            score_filtered_errors_counter[key] = filtered_errors[filtered_errors['category'] == key].shape[0]
            all_errors_counter[key] = self.df[self.df['category'] == key].shape[0]

        self.filter_dict["Raw error number"] = all_errors_counter
        self.filter_dict["Score filtered error number"] = score_filtered_errors_counter

        return filtered_errors, score_filtered_errors_counter

    def len_filter(self, errors_df, min_len: int = 50000, max_len: int = 10000000,
                   out_path="len_filtered_errors.xlsx", remove_error_path="len_remove_error.xlsx", filter_cls=None):
        len_filtered_errors_counter = dict()
        len_removed_errors_counter = dict()

        if filter_cls is None:
            filter_cls = self.classes

        filtered_errors = errors_df[
            (errors_df['hic_loci_2'] - errors_df['hic_loci_1'] > min_len) & (errors_df['hic_loci_2'] - errors_df[
                'hic_loci_1'] < max_len)]
        # save to excel
        filtered_errors.to_excel(os.path.join(self.out_path, out_path), sheet_name='Sheet1', index=False)

        len_removed_errors = errors_df[
            (errors_df['hic_loci_2'] - errors_df['hic_loci_1'] < min_len) | (errors_df['hic_loci_2'] - errors_df[
                'hic_loci_1'] > max_len)]

        # save to excel
        len_removed_errors.to_excel(os.path.join(self.out_path, remove_error_path), sheet_name='Sheet1', index=False)

        for key in filter_cls:
            try:
                len_filtered_errors_counter[key] = filtered_errors[filtered_errors['category'] == key].shape[0]
                len_removed_errors_counter[key] = len_removed_errors[len_removed_errors['category'] == key].shape[0]
            except KeyError:
                print(f"KeyError: {key} not in errors_dict")
                continue

        self.filter_dict["Length filtered error number"] = len_filtered_errors_counter
        self.filter_dict["Length removed error number"] = len_removed_errors_counter

        return filtered_errors, len_filtered_errors_counter

    def repeat_filter(self, errors_df, error_space, out_path="repeat_errors.xlsx"):

        # TODO: slecet min length translocation
        # select translocation
        tran_pd = errors_df[errors_df["category"] == "translocation"]
        else__pd = errors_df[errors_df["category"] != "translocation"]

        # sort by hic_loci_1
        df_sorted = tran_pd.sort_values(by=['hic_loci_1'], na_position='first')

        result_pd = None
        repeat_pd = None
        for index in range(len(df_sorted)):
            if result_pd is None:
                result_pd = df_sorted.iloc[0:1]
                continue
            else:
                temp_value_1 = df_sorted.iloc[index:index + 1, 8].values[0]
                temp_value_2 = result_pd.iloc[-1:, 9].values[0]
                temp_value = abs(temp_value_1 - temp_value_2)
                if temp_value < error_space:
                    repeat_pd = pd.concat([repeat_pd, df_sorted[index:index + 1]], axis=0)
                else:
                    result_pd = pd.concat([result_pd, df_sorted[index:index + 1]], axis=0)
        result_pd = pd.concat([result_pd, else__pd], axis=0)

        # save to excel
        repeat_pd.to_excel(os.path.join(self.out_path, out_path), sheet_name='Sheet1', index=False)

        return result_pd

    def pd2json(self, error_df, out_path="len_filtered_errors.json"):
        len_filtered_errors = dict()
        df = error_df.sort_values("category", inplace=False)

        error_class = df['category'].unique()
        for class_ in error_class:
            len_filtered_errors[class_] = []
        id_counter = 0
        for index, row in df.iterrows():
            temp_dict = {
                "id": id_counter,
                "image_id": row["image_id"],
                "category": row["category"],
                "bbox": [row["bbox_1"], row["bbox_2"], row["bbox_3"], row["bbox_4"]],
                "score": row["score"],
                "resolution": row["resolution"],
                "hic_loci": [row["hic_loci_1"], row["hic_loci_2"], row["hic_loci_3"], row["hic_loci_4"]]
            }
            len_filtered_errors[row["category"]].append(temp_dict)
            id_counter += 1
        with open(os.path.join(self.out_path, out_path), "w") as outfile:
            json.dump(len_filtered_errors, outfile)

        return len_filtered_errors

    # filter error according to overlap and iou
    def de_diff_overlap(self, errors_dict: dict, iou_score: float = 0.8, out_path="overlap_filtered_errors.json",
                        remove_error_path="overlap_remove_error.txt"):
        remove_list = list()  # save the key of the errors_dict which has been removed
        ans = []  # store de_overlap errors
        ans_dict = defaultdict()  # store de_overlap errors
        all_errors = []

        # record the number of overlap filtered errors
        overlap_filtered_errors_counter = dict()

        for class_ in errors_dict:  # loop classes
            all_errors += errors_dict[class_]
            overlap_filtered_errors_counter[class_] = 0  # error counter

        # loop errors
        sorted_errors_dict = sorted(all_errors, key=lambda itme: itme["hic_loci"][0], reverse=False)
        temp_compare = None  # first error to compare
        for error in sorted_errors_dict:
            # whether there is overlap
            if ans and error["hic_loci"][0] <= temp_compare["hic_loci"][1]:
                remove_list.append((error, temp_compare))  # save the error which has overlap

                # calculate overlap ratio
                bbox1 = error["hic_loci"]
                bbox2 = temp_compare["hic_loci"]
                counted_score = self.cal_iou(bbox1, bbox2)
                if float(counted_score) > float(iou_score):
                    # judge which one's resolution is higher
                    if int(error["resolution"]) == int(temp_compare["resolution"]):
                        insert_result = max(error, temp_compare, key=lambda item: item["score"])
                    else:
                        # select the error with the highest resolution
                        insert_result = min(error, temp_compare, key=lambda item: item["resolution"])

                    if insert_result == temp_compare:
                        continue
                    else:
                        del ans[-1]
                        ans.append(insert_result)

                else:  # not same error but have overlap
                    error_len_1 = bbox1[1] - bbox1[0]
                    temp_compare_len_2 = bbox2[1] - bbox2[0]
                    if error_len_1 > temp_compare_len_2:
                        del ans[-1]
                        ans.append(error)
            else:  # nought overlap
                ans.append(error)
            temp_compare = ans[-1]

        # regenerate error structure
        for _ in ans:
            # ans_dict[_["category"]] = _
            ans_dict.setdefault(_["category"], []).append(_)

            # count the number of errors
            overlap_filtered_errors_counter[_["category"]] += 1

        # save remove error to file
        with open(os.path.join(self.out_path, remove_error_path), "w") as f:
            f.write(str(remove_list))

        with open(os.path.join(self.out_path, out_path), "w") as outfile:
            json.dump(ans_dict, outfile)

        self.filter_dict["Overlap filtered error number"] = overlap_filtered_errors_counter

        # logger.info("Filter all error category Done")
        print("Filter all error category Done")

        return ans_dict, overlap_filtered_errors_counter

    def chr_len_filter(self, errors_dict: dict, chr_len: int = None,
                       out_path="chr_len_filtered_errors.json",
                       remove_error_path="chr_len_remove_error.txt", filter_cls=None):
        if chr_len is None:
            # TODO: 接入 get_real_chr_len 函数 > 整合中实现
            print("chr_len is None, please input chr_len")
            return

        if filter_cls is None:
            filter_cls = self.classes
        filtered_errors = dict()
        chr_len_removed_errors = dict()
        chr_len_filtered_errors_counter = dict()

        for key in filter_cls:
            try:
                filtered_errors[key] = list(
                    filter(lambda x: x["hic_loci"][1] < chr_len, errors_dict[key]))
                chr_len_removed_errors[key] = list(
                    filter(lambda x: x["hic_loci"][1] > chr_len, errors_dict[key]))

                chr_len_filtered_errors_counter[key] = {
                    "normal": len(filtered_errors[key]),
                    "abnormal": len(chr_len_removed_errors[key])
                }
            except KeyError:
                print(f"KeyError: {key} not in errors_dict")
                continue

        with open(os.path.join(self.out_path, out_path), "w") as outfile:
            json.dump(filtered_errors, outfile)

        with open(os.path.join(self.out_path, remove_error_path), "w") as outfile:
            json.dump(chr_len_removed_errors, outfile)

        self.filter_dict["Chromosome real length filtered error number"] = chr_len_filtered_errors_counter
        with open(os.path.join(self.out_path, "error_summary.json"), "a") as outfile:
            json.dump(self.filter_dict, outfile)

        return filtered_errors, chr_len_filtered_errors_counter

    def loci_zoom(self, errors_dict, threshold=3000, out_path="zoomed_errors.json", filter_cls=None):
        print("zoom threshold: ", threshold)

        if filter_cls is None:
            filter_cls = self.classes
        zoomed_errors = dict()

        for key in filter_cls:
            try:
                zoomed_errors[key] = []
                for error in errors_dict[key]:
                    error["hic_loci"][0] = error["hic_loci"][0] + threshold
                    error["hic_loci"][1] = error["hic_loci"][1] - threshold
                    zoomed_errors[key].append(error)
            except KeyError:
                print(f"KeyError: {key} not in errors_dict")
                continue

        with open(os.path.join(self.out_path, out_path), "w") as outfile:
            json.dump(zoomed_errors, outfile)

        return zoomed_errors

    def divide_error(self, all_filtered_error: dict):
        for _class in self.classes:
            if _class in all_filtered_error.keys() and all_filtered_error[_class]:
                divided_error = dict()
                for tran_error in all_filtered_error[_class]:
                    divided_error[tran_error["id"]] = {  # one key may have multiple values
                        "start": tran_error["hic_loci"][0],
                        "end": tran_error["hic_loci"][1],
                    }
                with open(os.path.join(self.out_path, _class + "_error.json"), "w") as outfile:
                    json.dump(divided_error, outfile)
            else:
                continue
        print("Divide all error category Done")

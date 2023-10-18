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
import random
from collections import defaultdict

import cv2
import pandas as pd
from PIL import Image
from mmdet.apis import init_detector, inference_detector

from src.utils.logger import logger


class ERRORS:
    """
        Infer error class
    """
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

    def zoom_error2excel(self, zoom_error_json_file, output_excel_file="error_summary.xlsx"):
        with open(zoom_error_json_file) as f:
            json_data = json.load(f)

        error_dict = {
            "type": [],
            "start": [],
            "end": [],
            "path": []
        }

        directory = os.path.dirname(zoom_error_json_file)
        for error_type in json_data:
            if len(json_data[error_type]) == 0:
                continue
            for error in json_data[error_type]:
                img_basename = file_name = os.path.basename(error["image_id"])
                error_dict["type"].append(error["category"])
                error_dict["start"].append(error["hic_loci"][0])
                error_dict["end"].append(error["hic_loci"][1])
                error_dict["path"].append(os.path.join(directory, "infer_result", img_basename))

        df = pd.DataFrame(error_dict)

        df.to_excel(output_excel_file, index=False, engine='openpyxl')

    # convert bbox coordinate to hic coordinate
    def bbox2hic(self, bbox, img_info):
        """
            bbox coordinate to hic coordinate
        Args:
            bbox: bbox coordinate
            img_info: hic info

        Returns:
            hic coordinate
        """
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
        """
            calculate iou
        Args:
            box1: bbox1
            box2: bbox2

        Returns:
            iou
        """
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
        Args:
            detection_bbox: bbox

        Returns:
            [x1, y1, x2, y2]
        """
        x1 = detection_bbox[0]
        y1 = detection_bbox[1]
        x2 = detection_bbox[0] + detection_bbox[2]
        y2 = detection_bbox[1] + detection_bbox[3]
        return [x1, y1, x2, y2]

    @staticmethod
    def if_include(bbox1, bbox2):
        """
            if bbox2 include bbox1
        Args:
            bbox1: bbox1
            bbox2: bbox2

        Returns:
            True or False
        """
        # default bbox1 is previous bbox
        if bbox2[1] <= bbox1[1] and bbox2[2] >= bbox1[2] and bbox2[3] <= bbox1[3]:
            return True
        else:
            return False

    # filter error according to score
    def filter_all_errors(self, score: float = 0.9, out_path="score_filtered_errors.xlsx", filter_cls=None):
        """
            filter error according to score
        Args:
            score: score threshold
            out_path: output path
            filter_cls: filter classes

        Returns:
            filtered errors
        """
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
        """
            filter error according to length
        Args:
            errors_df: errors dataframe
            min_len: error min length
            max_len: error max length
            out_path: output path
            remove_error_path: remove error path
            filter_cls: filter classes

        Returns:
            length filtered errors
        """
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
                logger.info(f"KeyError: {key} not in errors_dict")
                continue

        self.filter_dict["Length filtered error number"] = len_filtered_errors_counter
        self.filter_dict["Length removed error number"] = len_removed_errors_counter

        return filtered_errors, len_filtered_errors_counter

    def repeat_filter(self, errors_df, error_space, out_path="repeat_errors.xlsx"):
        """
            filter repeat error
        Args:
            errors_df: errors dataframe
            error_space: error space
            out_path: output path

        Returns:
            repeat filtered errors
        """

        # select min length translocation > dict default
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
        """
            convert dataframe to json
        Args:
            error_df: errors dataframe
            out_path: output path

        Returns:
            json file
        """
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
        """
            filter error according to overlap and iou
        Args:
            errors_dict: errors dict
            iou_score: iou score
            out_path: overlap filtered errors path
            remove_error_path: overlap removed errors path

        Returns:
            overlap filtered errors
        """
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

        logger.info("Filter all error category Done")

        self.zoom_error2excel(os.path.join(self.out_path, out_path), os.path.join(self.out_path, "overlap_filtered_errors.xlsx"))

        return ans_dict, overlap_filtered_errors_counter

    def chr_len_filter(self, errors_dict: dict, chr_len: int = None,
                       out_path="chr_len_filtered_errors.json",
                       remove_error_path="chr_len_remove_error.txt", filter_cls=None):
        """
            filter error according to chr_len
        Args:
            errors_dict: errors dict
            chr_len: chromosome length
            out_path: output path
            remove_error_path: remove error path
            filter_cls: filter class

        Returns:
            chromosome length filtered errors
        """
        if chr_len is None:
            logger.info("chr_len is None, please input chr_len")
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
                logger.info(f"KeyError: {key} not in errors_dict")
                chr_len_filtered_errors_counter[key] = {
                    "normal": 0,
                    "abnormal": 0
                }
                continue

        with open(os.path.join(self.out_path, out_path), "w") as outfile:
            json.dump(filtered_errors, outfile)

        with open(os.path.join(self.out_path, remove_error_path), "w") as outfile:
            json.dump(chr_len_removed_errors, outfile)

        self.filter_dict["Chromosome real length filtered error number"] = chr_len_filtered_errors_counter
        with open(os.path.join(self.out_path, "error_summary.json"), "a") as outfile:
            json.dump(self.filter_dict, outfile)

        self.zoom_error2excel(os.path.join(self.out_path, out_path),
                              os.path.join(self.out_path, "chr_len_filtered_errors.xlsx"))

        return filtered_errors, chr_len_filtered_errors_counter

    def loci_zoom(self, errors_dict, threshold=3000, out_path="zoomed_errors.json", filter_cls=None):
        """
            zoom error loci
        Args:
            errors_dict: errors dict
            threshold: zoom threshold
            out_path: output path
            filter_cls: filter class

        Returns:
            zoomed errors
        """
        logger.info(f"zoom threshold: {threshold}")

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
                logger.info(f"KeyError: {key} not in errors_dict")
                continue

        with open(os.path.join(self.out_path, out_path), "w") as outfile:
            json.dump(zoomed_errors, outfile)

        self.zoom_error2excel(os.path.join(self.out_path, out_path), os.path.join(self.out_path, "error_summary.xlsx"))

        return zoomed_errors

    def divide_error(self, all_filtered_error: dict):
        """
            divide error according to class
        Args:
            all_filtered_error: all filtered error

        Returns:
            divided error
        """
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
        logger.info("Divide all error category Done")


def draw_box_corner(draw_img, bbox, length, corner_color):
    """
        draw box corner
    Args:
        draw_img: image
        bbox: bbox
        length: length
        corner_color: corner color

    Returns:
        None
    """
    # Top Left
    cv2.line(draw_img, (bbox[0], bbox[1]), (bbox[0] + length, bbox[1]), corner_color, thickness=2)
    cv2.line(draw_img, (bbox[0], bbox[1]), (bbox[0], bbox[1] + length), corner_color, thickness=2)
    # Top Right
    cv2.line(draw_img, (bbox[2], bbox[1]), (bbox[2] - length, bbox[1]), corner_color, thickness=2)
    cv2.line(draw_img, (bbox[2], bbox[1]), (bbox[2], bbox[1] + length), corner_color, thickness=2)
    # Bottom Left
    cv2.line(draw_img, (bbox[0], bbox[3]), (bbox[0] + length, bbox[3]), corner_color, thickness=2)
    cv2.line(draw_img, (bbox[0], bbox[3]), (bbox[0], bbox[3] - length), corner_color, thickness=2)
    # Bottom Right
    cv2.line(draw_img, (bbox[2], bbox[3]), (bbox[2] - length, bbox[3]), corner_color, thickness=2)
    cv2.line(draw_img, (bbox[2], bbox[3]), (bbox[2], bbox[3] - length), corner_color, thickness=2)


def draw_label_type(draw_img, bbox, label_color):
    """
        draw label type
    Args:
        draw_img: image
        bbox: bbox
        label_color: label color

    Returns:
        None
    """
    label = str(bbox[-1])
    label_size = cv2.getTextSize(label + '0', cv2.FONT_HERSHEY_TRIPLEX, 0.7, 2)[0]
    if bbox[1] - label_size[1] - 3 < 0:
        cv2.rectangle(draw_img,
                      (bbox[0], bbox[1] + 2),
                      (bbox[0] + label_size[0], bbox[1] + label_size[1] + 3),
                      color=label_color,
                      thickness=-1
                      )
        cv2.putText(draw_img, label,
                    (bbox[0], bbox[1] + label_size[1] + 3),
                    cv2.FONT_HERSHEY_TRIPLEX,
                    0.7,
                    (0, 0, 0),
                    thickness=1
                    )
    else:
        cv2.rectangle(draw_img,
                      (bbox[0], bbox[1] - label_size[1] - 3),
                      (bbox[0] + label_size[0], bbox[1] - 3),
                      color=label_color,
                      thickness=-1
                      )
        cv2.putText(draw_img, label,
                    (bbox[0], bbox[1] - 3),
                    cv2.FONT_HERSHEY_TRIPLEX,
                    0.7,
                    (0, 0, 0),
                    thickness=1
                    )


def test_corner_box(img, bbox, corner_l=20, is_transparent=False, draw_type=False, draw_corner=False,
                    box_color=(255, 0, 255)):
    """
        test corner box
    Args:
        img: image
        bbox: bbox
        corner_l: corner length
        is_transparent: transparent
        draw_type: type
        draw_corner: corner
        box_color: box color

    Returns:
        None
    """
    draw_img = img.copy()
    pt1 = (bbox[0], bbox[1])
    pt2 = (bbox[2], bbox[3])

    out_img = img
    if is_transparent:
        alpha = 0.8
        # alpha = 0.5
        cv2.rectangle(draw_img, pt1, pt2, color=box_color, thickness=-1)
        out_img = cv2.addWeighted(img, alpha, draw_img, 1 - alpha, 0)

    cv2.rectangle(out_img, pt1, pt2, color=box_color, thickness=2)

    if draw_type:
        draw_label_type(out_img, bbox, label_color=box_color)
    if draw_corner:
        draw_box_corner(out_img, bbox, length=corner_l, corner_color=(0, 255, 0))
    return out_img


def bbox2jpg(img_path, bbox, label, out_path):
    """
        bbox to jpg
    Args:
        img_path: image path
        bbox: bbox
        label: label
        out_path: out path

    Returns:
        None
    """
    img = cv2.imread(img_path)

    bbox = [int(x) for x in bbox] + [label]
    box_color = (255, 144, 30)
    out_img = test_corner_box(img, bbox, corner_l=30, is_transparent=True, draw_type=True, draw_corner=True,
                              box_color=box_color)

    cv2.imwrite(out_path, out_img)


def vis_error(error_xlsx, out_dir):
    """
        vis error
    Args:
        error_xlsx: error xlsx
        out_dir: out dir

    Returns:
        None
    """
    df = pd.read_excel(error_xlsx)
    if not os.path.exists(out_dir):  # check if folder is existing
        os.mkdir(out_dir)
    for index, row in df.iterrows():
        img_path = row['image_id']
        bbox = [row['bbox_1'], row['bbox_2'], row['bbox_3'], row['bbox_4']]
        label = row['category']
        basename = str(index + 1) + "_" + os.path.basename(img_path)
        out_path = os.path.join(out_dir, basename)
        bbox2jpg(img_path, bbox, label, out_path)


def json_vis(error_json, out_dir):
    """
        json visulization
    Args:
        error_json: error json
        out_dir: out dir

    Returns:
        None
    """
    with open(error_json, 'r') as f:
        error_dict = json.load(f)
    logger.info("Done loading json file.")
    for key in error_dict.keys():
        for index, error in enumerate(error_dict[key]):
            basename = str(index + 1) + "_" + os.path.basename(error["image_id"])
            out_path = os.path.join(out_dir, basename)
            error_dict[key][index]["infer_image"] = out_path
            bbox2jpg(error["image_id"], error["bbox"], error["category"], out_path)

    with open(os.path.join(out_dir, "infer_result.json"), "a") as outfile:
        json.dump(error_dict, outfile)


def infer_error(model_cfg, pretrained_model, img_path, out_path, device='cuda:0', score=0.9, error_min_len=15000,
                error_max_len=20000000, iou_score=0.8, chr_len=1453515699):
    """
        infer error
    Args:
        model_cfg: model config path
        pretrained_model: pretrained model path
        img_path: image path
        out_path: out path
        device: GPU device or CPU
        score: infer score
        error_min_len: error min length
        error_max_len: error max length
        iou_score: iou score
        chr_len: chromosome length

    Returns:
        None
    """

    # Initializing model
    model = init_detector(model_cfg, pretrained_model, device=device)

    info_file = os.path.join(img_path, "info.txt")
    infos = []
    with open(info_file, "r") as f:
        for line in f.readlines():
            info = json.loads(line)
            infos.append(info)

    classes = ("translocation", "inversion", "debris")

    if not os.path.exists(out_path):  # check if folder is existing
        os.mkdir(out_path)

    # get img size
    img_size = None
    contents = os.listdir(img_path)

    for item in contents:
        item_path = os.path.join(img_path, item)
        if os.path.isdir(item_path):
            random_file = random.choice(os.listdir(item_path))
            img_size = Image.open(os.path.join(item_path, random_file)).size
            print("img size: ", img_size)
            break

    error_class = ERRORS(classes, info_file, out_path, img_size=img_size)

    # for info in infos:
    for info in infos:
        detection_result = inference_detector(model, list(info.keys())[0])

        error_class.create_structure(info, detection_result[0])

    if len(error_class.df) == 0:  # no detect error
        return True

    # score filter
    score_filtered_errors, score_filtered_errors_counter = error_class.filter_all_errors(score=score,
                                                                                         filter_cls=classes)

    # length filter
    len_filtered_errors, len_filtered_errors_counter = error_class.len_filter(score_filtered_errors,
                                                                              min_len=error_min_len,
                                                                              max_len=error_max_len,
                                                                              out_path="len_filtered_errors.xlsx",
                                                                              remove_error_path="len_remove_error.xlsx",
                                                                              filter_cls=None)
    # dataframe to json
    len_filtered_errors_json = error_class.pd2json(len_filtered_errors)

    # overlap filter
    overlap_filtered_errors, overlap_filtered_errors_counter = error_class.de_diff_overlap(len_filtered_errors_json,
                                                                                           iou_score=iou_score)

    # chromosome length filter
    chr_filtered_errors, chr_filtered_errors_counter = error_class.chr_len_filter(overlap_filtered_errors,
                                                                                  chr_len=chr_len)

    # zoom error
    zoom_threshold = 0
    zoomed_error = error_class.loci_zoom(chr_filtered_errors, threshold=zoom_threshold, out_path="zoomed_errors.json",
                                         filter_cls=None)

    # divide error to each json
    error_class.divide_error(zoomed_error)

    # error visulization
    # infer result out_dir
    infer_out_dir = os.path.join(out_path, "infer_result")
    if not os.path.exists(infer_out_dir):  # check if folder is existing
        os.mkdir(infer_out_dir)

    error_json = os.path.join(out_path, "chr_len_filtered_errors.json")
    json_vis(error_json, infer_out_dir)


def main():
    pass


if __name__ == "__main__":
    main()

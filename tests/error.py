#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: error.py
@time: 10/26/22 7:47 PM
@function: assembly error class
"""
import json
import os
# from src.core.utils.logger import logger  # FIXME: update logger when to use
from collections import defaultdict


class ERRORS:
    def __init__(self, classes, info_file, out_path, img_size=(1116, 1116)):
        self.info_file = info_file
        self.classes = classes
        self.out_path = out_path
        self.img_size = img_size  # TODO: 自动获取图片大小
        self.errors, self.counter = dict(), dict()
        self.class_list = []

        for class_ in classes:
            self.counter[class_] = 0
            self.errors[class_] = []

    # generate error structure
    def create_structure(self, img_info, detection_result, epoch_flag=0):
        """

        Args:
            img_info:
            detection_result:
            epoch_flag: detect epoch flag

        Returns:

        """
        for category, classes in zip(detection_result, self.classes):
            if epoch_flag == 0 and classes == "chromosome":
                continue  # skip chromosome when epoch is 0

            for index, error in enumerate(category):
                error = error.tolist()
                temp_dict = dict()
                self.counter[classes] += 1
                temp_dict["id"] = self.counter[classes]
                temp_dict["image_id"] = list(img_info.keys())[0]
                temp_dict["category"] = classes
                temp_dict["bbox"] = error[0:4]
                temp_dict["score"] = error[4]
                temp_dict["resolution"] = img_info[list(img_info.keys())[0]]["resolution"]
                temp_dict["hic_loci"] = self.bbox2hic(error[0:4], img_info)
                self.errors[classes].append(temp_dict)
        return self.errors

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

    # filter error according to score
    def filter_all_errors(self, score: float = 0.9, out_path="score_filtered_errors.json", filter_cls=None):
        score_filtered_errors_counter = dict()  # record the number of filtered errors
        if filter_cls is None:
            filter_cls = self.classes
        filtered_errors = self.errors

        for key in filter_cls:
            filtered_errors[key] = list(filter(lambda x: x["score"] > score, filtered_errors[key]))
            score_filtered_errors_counter[key] = 0  # error counter

        # count the number of errors
        for scored_class in filtered_errors:
            for _ in filtered_errors[scored_class]:
                score_filtered_errors_counter[scored_class] += 1

        with open(os.path.join(self.out_path, out_path), "w") as outfile:
            json.dump(filtered_errors, outfile)

        return filtered_errors, score_filtered_errors_counter

    def score_filter_specific_class(self, errors_dict: dict, score: float = 0.9,
                                    out_path="_score_filter_specific_class.json", filter_cls=None):
        if filter_cls is None:
            raise ValueError("Please specify the class to filter")
        else:
            errors_dict[filter_cls] = list(filter(lambda x: x["score"] > score, errors_dict[filter_cls]))
            with open(os.path.join(self.out_path, filter_cls + out_path), "w") as outfile:
                json.dump(errors_dict[filter_cls], outfile)

        # count the score_filter_specific_class_counter
        score_filter_specific_class_counter = len(errors_dict[filter_cls])

        return errors_dict[filter_cls], score_filter_specific_class_counter

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

        # logger.info("Filter all error category Done")
        print("Filter all error category Done")

        return ans_dict, overlap_filtered_errors_counter

    def len_filter(self, errors_dict: dict, min_len: int = 50000, max_len: int = 10000000,
                   out_path="len_filtered_errors.json", remove_error_path="len_remove_error.txt", filter_cls=None):
        if filter_cls is None:
            filter_cls = self.classes
        filtered_errors = dict()
        len_removed_errors = dict()
        len_filtered_errors_counter = dict()

        for key in filter_cls:
            try:
                filtered_errors[key] = list(
                    filter(lambda x: min_len <= x["hic_loci"][1] - x["hic_loci"][0] <= max_len, errors_dict[key]))
                len_removed_errors[key] = list(
                    filter(lambda x: x["hic_loci"][1] - x["hic_loci"][0] < min_len or x["hic_loci"][1] - x["hic_loci"][
                        0] > max_len, errors_dict[key]))

                len_filtered_errors_counter[key] = {
                    "normal": len(filtered_errors[key]),
                    "abnormal": len(len_removed_errors[key])
                }
            except KeyError:
                print(f"KeyError: {key} not in errors_dict")
                continue

        with open(os.path.join(self.out_path, out_path), "w") as outfile:
            json.dump(filtered_errors, outfile)

        with open(os.path.join(self.out_path, remove_error_path), "w") as outfile:
            json.dump(len_removed_errors, outfile)

        return filtered_errors, len_filtered_errors_counter

    def chr_len_filter(self, errors_dict: dict, chr_len: int = None,
                       out_path="chr_len_filtered_errors.json",
                       remove_error_path="chr_len_remove_error.txt", filter_cls=None):
        if chr_len is None:
            # TODO: 接入 get_real_chr_len 函数
            print("chr_len is None, please input chr_len")
            return

        if filter_cls is None:
            filter_cls = self.classes
        filtered_errors = dict()
        chr_len_removed_errors = dict()
        chr_len_filtered_errors_counter = dict()

        for key in filter_cls:
            filtered_errors[key] = list(
                filter(lambda x: x["hic_loci"][1] < chr_len, errors_dict[key]))
            chr_len_removed_errors[key] = list(
                filter(lambda x: x["hic_loci"][1] > chr_len, errors_dict[key]))

            chr_len_filtered_errors_counter[key] = {
                "normal": len(filtered_errors[key]),
                "abnormal": len(chr_len_removed_errors[key])
            }

        with open(os.path.join(self.out_path, out_path), "w") as outfile:
            json.dump(filtered_errors, outfile)

        with open(os.path.join(self.out_path, remove_error_path), "w") as outfile:
            json.dump(chr_len_removed_errors, outfile)

        return filtered_errors, chr_len_filtered_errors_counter

    def divide_error(self, all_filtered_error: dict):
        for _class in self.classes:
            if _class in all_filtered_error.keys():
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


def main():
    info_file = "/home/jzj/Jupyter-Docker/buffer/silkworm_test/info.txt"

    classes = ("translocation", "inversion", "debris", "chromosome")

    out_path = "/home/jzj/Jupyter-Docker/buffer"

    temp_class = ERRORS(classes, info_file, out_path)

    raw_errors_file = "/home/jzj/Jupyter-Docker/buffer/silkworm_test/raw_errors.json"

    with open(raw_errors_file, "r") as outfile:
        raw_errors = json.load(outfile)

    score_filtered_errors, score_filtered_errors_counter = temp_class.len_filter(raw_errors)

    print(score_filtered_errors_counter)


if __name__ == "__main__":
    main()

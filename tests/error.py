#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: error.py
@time: 10/26/22 7:47 PM
@function: 
"""
import json
from collections import defaultdict


class ERRORS:
    def __init__(self, classes, info_file, img_size=(1110, 1110)):
        self.info_file = info_file
        self.classes = classes
        self.img_size = img_size
        self.errors, self.counter = dict(), dict()
        self.class_list = []

        for class_ in classes:
            self.counter[class_] = 0
            self.errors[class_] = []

    # generate error structure
    def create_structure(self, img_info, detection_result, epoch_flag=0):
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
    def filter_all_errors(self, score: float = 0.9, filter_cls=None):
        if filter_cls is None:
            filter_cls = self.classes
        filtered_errors = self.errors
        for key in filter_cls:
            filtered_errors[key] = list(filter(lambda x: x["score"] > score, filtered_errors[key]))

        return filtered_errors

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
    def de_diff_overlap(self, errors_dict: dict, iou_score: float = 0.8):
        remove_list = list()  # save the key of the errors_dict which has been removed
        ans = []  # store de_overlap errors
        ans_dict = defaultdict()  # store de_overlap errors
        all_errors = []
        for class_ in errors_dict:  # loop classes
            all_errors += errors_dict[class_]
            # loop errors
        sorted_errors_dict = sorted(all_errors, key=lambda itme: itme["hic_loci"][0], reverse=False)
        temp_compare = None  # first error to compare
        for error in sorted_errors_dict:
            # whether there is overlap
            if ans and error["hic_loci"][0] <= temp_compare["hic_loci"][1]:

                # FIXME: save below var to file
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

        print("Filter all error category Done")

        return ans_dict


def main():
    classes = ("translocation", "inversion", "debris", "chromosome")
    info_file = "/home/jzj/Jupyter-Docker/Download/Np/info.txt"
    temp_class = ERRORS(classes, info_file)
    with open("/home/jzj/Jupyter-Docker/Download/score_filtered_errors.json", "r") as f:
        score_filtered_errors = json.load(f)
    temp_class.de_diff_overlap(score_filtered_errors, iou_score=0.9)


if __name__ == "__main__":
    main()

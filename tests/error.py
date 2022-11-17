#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: error.py
@time: 10/26/22 7:47 PM
@function: 
"""

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
        x1min, y1min, x1max, y1max = box1[0], box1[1], box1[2], box1[3]
        x2min, y2min, x2max, y2max = box2[0], box2[1], box2[2], box2[3]

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

    # filter error according to overlap and iou
    def de_diff_overlap(self, errors_dict: dict, iou_score: float = 0.9):
        remove_list = list()  # save the key of the errors_dict which has been removed
        ans = []  # store de_overlap errors
        ans_dict = defaultdict()  # store de_overlap errors
        all_errors = []
        for class_ in errors_dict:  # loop classes
            all_errors += errors_dict[class_]
            # loop errors
        sorted_errors_dict = sorted(all_errors, key=lambda itme: itme["hic_loci"][0], reverse=False)

        for error in sorted_errors_dict:

            # whether there is overlap
            if ans and error["hic_loci"][0] <= ans[-1]["hic_loci"][1]:

                # FIXME: save below var to file
                remove_list.append((error, ans[-1]))  # save the error which has overlap
                # calculate overlap ratio
                bbox1 = self.transform_bbox(error["bbox"])
                bbox2 = self.transform_bbox(ans[-1]["bbox"])
                counted_score = self.cal_iou(bbox1, bbox2)
                if counted_score > iou_score:
                    # judge which one's resolution is higher
                    if error["resolution"] == ans[-1]["resolution"]:
                        ans.append(max(error, ans[-1], key=lambda item: item["score"]))

                    else:
                        # select the error with the highest resolution
                        ans.append(max(error, ans[-1], key=lambda item: item["resolution"]))

                else:  # not same error but have overlap
                    # FIXME: not same error but have overlap
                    # Select the middle position of the two errors
                    error_copy = error

                    ans[-1]["hic_loci"][1] = error_copy["hic_loci"][0] + int(
                        (ans[-1]["hic_loci"][1] - error_copy["hic_loci"][0]) / 2) - 1

                    error_copy["hic_loci"][0] = ans[-1]["hic_loci"][1] + 1

                    ans[-1]["hic_loci"][3] = error_copy["hic_loci"][2] + int(
                        (ans[-1]["hic_loci"][3] - error_copy["hic_loci"][2]) / 2) - 1

                    error_copy["hic_loci"][2] = ans[-1]["hic_loci"][3] + 1

                    ans.append(error_copy)

                    # raise NotImplementedError("Not same error but have overlap, wait to solve")
            else:  # nought overlap
                ans.append(error)

        # regenerate error structure
        for _ in ans:
            # ans_dict[_["category"]] = _
            ans_dict.setdefault(_["category"], []).append(_)

        print("Filter all error category Done")

        return ans_dict


def main():
    pass


if __name__ == "__main__":
    main()

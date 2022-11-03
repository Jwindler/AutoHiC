#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: test.py
@time: 9/21/22 5:27 PM
@function: 
"""

import pickle
from typing import List
from collections import OrderedDict


def cal_iou_xyxy(box1, box2):
    x1min, y1min, x1max, y1max = box1[0], box1[1], box1[2], box1[3]
    x2min, y2min, x2max, y2max = box2[0], box2[1], box2[2], box2[3]

    # calculate box area
    s1 = (y1max - y1min + 1.) * (x1max - x1min + 1.)
    s2 = (y2max - y2min + 1.) * (x2max - x2min + 1.)

    # calculate overlap area
    xmin = max(x1min, x2min)
    ymin = max(y1min, y2min)
    xmax = min(x1max, x2max)
    ymax = min(y1max, y2max)

    inter_h = max(ymax - ymin + 1, 0)
    inter_w = max(xmax - xmin + 1, 0)

    intersection = inter_h * inter_w
    union = s1 + s2 - intersection

    # calculate iou
    iou = intersection / union
    return iou


def de_same_overlap(errors_dict: dict, similarity: float = 0.9):
    de_overlap_dict = dict()
    remove_list = list()  # save the key of the errors_dict which has been removed
    threshold = (similarity, 1 / similarity)
    for class_ in errors_dict:  # loop classes

        # loop errors
        de_overlap_dict[class_] = sorted(errors_dict[class_], key=lambda itme: itme["hic_loci"][0], reverse=False)
        ans = []  # store de_overlap errors
        for error in de_overlap_dict[class_]:

            # whether there is overlap
            if ans and error["hic_loci"][0] <= ans[-1]["hic_loci"][1]:

                # calculate overlap ratio
                len_similarity = (error["hic_loci"][1] - error["hic_loci"][0]) / (
                        ans[-1]["hic_loci"][1] - ans[-1]["hic_loci"][0])
                if threshold[0] < len_similarity < threshold[1]:
                    if error["resolution"] == ans[-1]["resolution"]:  # select the highest score
                        ans.append(max(error, ans[-1], key=lambda item: item["score"]))
                        remove_list.append((error, ans[-1]))
                    else:
                        # select the error with the highest resolution
                        ans.append(max(error, ans[-1], key=lambda item: item["resolution"]))
                        remove_list.append((error, ans[-1]))
                else:  # not same error but have overlap
                    # TODO: 添加处理
                    print(error)
                    print(ans[-1])
                    raise NotImplementedError("Not same error but have overlap, wait to solve")
            else:  # nought overlap
                ans.append(error)

        print("test done")


def main():
    intervals = [[1, 3], [2, 4], [4, 7], [5, 6]]

    with open("/home/jzj/Jupyter-Docker/error-detection/swin/ex.pkl", 'rb') as file:
        object = pickle.loads(file.read())
    # print(merge(intervals))

    classes = ("translocation", "inversion", "debris", "chromosome")
    de_result = de_same_overlap(object)


if __name__ == "__main__":
    main()

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


def de_same_overlap(errors_dict: dict, iou_score: float = 0.9):
    sorted_errors_dict = dict()
    remove_list = list()  # save the key of the errors_dict which has been removed
    ans = []  # store de_overlap errors
    for class_ in errors_dict:  # loop classes

        # loop errors
        sorted_errors_dict[class_] = sorted(errors_dict[class_], key=lambda itme: itme["hic_loci"][0], reverse=False)

        for error in sorted_errors_dict[class_]:

            # whether there is overlap
            if ans and error["hic_loci"][0] <= ans[-1]["hic_loci"][1]:

                # calculate overlap ratio
                bbox1 = transform_bbox(error["bbox"])
                bbox2 = transform_bbox(ans[-1]["bbox"])
                counted_score = cal_iou(bbox1, bbox2)
                if counted_score > iou_score:
                    # judge which one's resolution is higher
                    if error["resolution"] == ans[-1]["resolution"]:
                        ans.append(max(error, ans[-1], key=lambda item: item["score"]))
                        remove_list.append((error, ans[-1]))
                    else:
                        # select the error with the highest resolution
                        ans.append(max(error, ans[-1], key=lambda item: item["resolution"]))
                        remove_list.append((error, ans[-1]))
                else:  # not same error but have overlap
                    # FIXME: not same error but have overlap
                    # Select the middle position of the two errors
                    last_copy = ans[-1]
                    error_copy = error
                    last_copy["hic_loci"][1] = error_copy["hic_loci"][0] + int(
                        (last_copy["hic_loci"][1] - error_copy["hic_loci"][0]) / 2) - 1

                    error_copy["hic_loci"][0] = last_copy["hic_loci"][1] + 1

                    last_copy["hic_loci"][3] = error_copy["hic_loci"][2] + int(
                        (last_copy["hic_loci"][3] - error_copy["hic_loci"][2]) / 2) - 1

                    error_copy["hic_loci"][2] = last_copy["hic_loci"][3] + 1

                    ans.append(last_copy)
                    ans.append(error_copy)
                    remove_list.append((error, ans[-1]))
                    # raise NotImplementedError("Not same error but have overlap, wait to solve")
            else:  # nought overlap
                ans.append(error)

    print("Filter same error category Done")
    return ans


def de_diff_overlap():
    pass


def main():
    with open("/home/jzj/Jupyter-Docker/error-detection/swin/ex.pkl", 'rb') as file:
        error_object = pickle.loads(file.read())

    de_result = de_same_overlap(error_object)
    print(de_result)


if __name__ == "__main__":
    main()

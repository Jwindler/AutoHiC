#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: re_same_errors.py
@time: 2022/11/7 16:09
@function: 
"""


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


def main():
    pass


if __name__ == "__main__":
    main()

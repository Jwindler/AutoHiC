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


def merge(intervals):
    ans = []

    for p in sorted(intervals, key=lambda x: x[0]):

        if ans and p[0] <= ans[-1][1]:

            ans[-1][1] = max(ans[-1][1], p[1])

        else:

            ans.append(p)  # ans+=p, # 另一种写法，其中p加逗号变为tuple，列表可以用+=将tuple加入其中

    return ans


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
                    ans.append(error)
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

#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: test.py
@time: 9/21/22 5:27 PM
@function: 
"""

from typing import List


def eraseoverlapintervals(intervals: List[List[int]]) -> int:
    if not intervals:
        return 0

    intervals.sort()
    n = len(intervals)
    f = [1]

    for i in range(1, n):
        f.append(max((f[j] for j in range(i) if intervals[j][1] <= intervals[i][0]), default=0) + 1)

    return n - max(f)


def main():
    pass


if __name__ == "__main__":
    main()

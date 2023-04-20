#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: bbox2jpg.py
@time: 4/20/23 10:31 AM
@function: 
"""

import cv2
import pandas as pd
import os


def draw_box_corner(draw_img, bbox, length, corner_color):
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
    img = cv2.imread(img_path)

    bbox = [int(x) for x in bbox] + [label]
    box_color = (255, 144, 30)
    out_img = test_corner_box(img, bbox, corner_l=30, is_transparent=True, draw_type=True, draw_corner=True,
                              box_color=box_color)

    cv2.imwrite(out_path, out_img)


def vis_error(error_xlsx, out_dir):
    df = pd.read_excel(error_xlsx)
    if not os.path.exists(out_dir):  # check if folder is exists
        os.mkdir(out_dir)
    for index, row in df.iterrows():
        img_path = row['image_id']
        bbox = [row['bbox_1'], row['bbox_2'], row['bbox_3'], row['bbox_4']]
        label = row['category']
        basename = str(index + 1) + "_" + os.path.basename(img_path)
        out_path = os.path.join(out_dir, basename)
        bbox2jpg(img_path, bbox, label, out_path)


def main():
    error_xlsx = ""
    out_dir = "/home/jzj/Jupyter-Docker/buffer/result/infer_result"
    vis_error(error_xlsx, out_dir)


if __name__ == "__main__":
    main()

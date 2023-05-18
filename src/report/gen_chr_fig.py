#!/usr/bin/env python3
# encoding: utf-8

"""
@author: pzx
@contact: jzjlab@163.com
@file: gen_chr_fig.py
@time: 5/18/23 10:58 AM
@function:
"""

import math
import os


def axis(chr_len_dict):
    """
    根据染色体长度dict生成坐标轴的所有值以及最大值
    Args:
        chr_len_dict: 染色体长度dict

    Returns:
        坐标轴的所有值和最大值

    """

    max_chr_len = max(chr_len_dict.values())
    if max_chr_len / 1000 <= 10:  # 最大长度小于10kb,显示为bp
        max_value = math.ceil(max_chr_len / 100) * 100  # 向上百位取整
        axis_value = [str(int(max_value / 10 * i)) + ' bp' for i in range(11)]
    elif 10 < max_chr_len / 1000 <= 100:  # 最大长度大于10kb,小于１0Mb显示为kp
        max_value = math.ceil(max_chr_len / 1000)  # 向上百位取整
        axis_value = [str(int(max_value / 10 * i)) + ' kp' for i in range(11)]
        max_value *= 1000
    elif 100 < max_chr_len / 1000 <= 1000:
        max_value = math.ceil(231100 / 10000) * 10  # 向上百位取整
        axis_value = [str(int(max_value / 10 * i)) + ' kp' for i in range(11)]
        max_value *= 1000
    elif 1000 < max_chr_len / 1000 <= 10000:
        max_value = math.ceil(max_chr_len / 100000) * 100  # 向上百位取整
        axis_value = [str(int(max_value / 10 * i)) + ' kp' for i in range(11)]
        max_value *= 1000
    else:  # 最大长度大于10Mb,显示为Mb
        max_value = math.ceil(max_chr_len / 1000000)  # 向上百位取整
        axis_value = [str(int(max_value / 10 * i)) + ' Mb' for i in range(11)]
        max_value *= 1000000

    return axis_value, max_value


def axis_loc(axis_value, i):
    """
        根据坐标轴的值生成svg格式的坐标轴,每条坐标轴上十个刻度
    Args:
        axis_value: 坐标轴对应的值
        i: 第几行染色体，该svg图片每行四十条染色体左右

    Returns:
        生成坐标轴的svg图片命令
    """

    y1 = []
    for a in range(11):
        y = ''.join('"{0}"'.format(50 + 18 * a + 300 * i))
        y1.append(y)
    y1.append(''.join('"{0}"'.format(50 + 18 * 10 + 12 + 300 * i)))
    y1.append(''.join('"{0}"'.format(50 + 18 * 10 + 6 + 300 * i)))

    y = []
    for a in range(11):
        y0 = ''.join('"{0}"'.format(50 + 18 * a + 300 * i + 5.5))
        y.append(y0)
    axis1 = '<line x1="19.5" y1=' + y1[0] + ' x2="24.5" y2=' + y1[
        0] + ' style="stroke:black;stroke-width:1"/><text x="26.5" y=' + y[
                0] + ' text-anchor="left"  font-size="11" fill="black" >' + axis_value[0] + '</text>\n'
    axis2 = '<line x1="19.5" y1=' + y1[1] + ' x2="22.75" y2=' + y1[
        1] + ' style="stroke:black;stroke-width:1"/><text x="26.5" y=' + y[
                1] + ' text-anchor="left"  font-size="11" fill="black" >' + axis_value[1] + '</text>\n'
    axis3 = '<line x1="19.5" y1=' + y1[2] + ' x2="22.75" y2=' + y1[
        2] + ' style="stroke:black;stroke-width:1"/><text x="26.5" y=' + y[
                2] + ' text-anchor="left"  font-size="11" fill="black" >' + axis_value[2] + '</text>\n'
    axis4 = '<line x1="19.5" y1=' + y1[3] + ' x2="22.75" y2=' + y1[
        3] + ' style="stroke:black;stroke-width:1"/><text x="26.5" y=' + y[
                3] + ' text-anchor="left"  font-size="11" fill="black" >' + axis_value[3] + '</text>\n'
    axis5 = '<line x1="19.5" y1=' + y1[4] + ' x2="22.75" y2=' + y1[
        4] + ' style="stroke:black;stroke-width:1"/><text x="26.5" y=' + y[
                4] + ' text-anchor="left"  font-size="11" fill="black" >' + axis_value[4] + '</text>\n'
    axis6 = '<line x1="19.5" y1=' + y1[5] + ' x2="25" y2=' + y1[
        5] + ' style="stroke:black;stroke-width:1"/><text x="26.5" y=' + y[
                5] + ' text-anchor="left"  font-size="11" fill="black" >' + axis_value[5] + '</text>\n'
    axis7 = '<line x1="19.5" y1=' + y1[6] + ' x2="22.75" y2=' + y1[
        6] + ' style="stroke:black;stroke-width:1"/><text x="26.5" y=' + y[
                6] + ' text-anchor="left"  font-size="11" fill="black" >' + axis_value[6] + '</text>\n'
    axis8 = '<line x1="19.5" y1=' + y1[7] + ' x2="22.75" y2=' + y1[
        7] + ' style="stroke:black;stroke-width:1"/><text x="26.5" y=' + y[
                7] + ' text-anchor="left"  font-size="11" fill="black" >' + axis_value[7] + '</text>\n'
    axis9 = '<line x1="19.5" y1=' + y1[8] + ' x2="22.75" y2=' + y1[
        8] + ' style="stroke:black;stroke-width:1"/><text x="26.5" y=' + y[
                8] + ' text-anchor="left"  font-size="11" fill="black" >' + axis_value[8] + '</text>\n'
    axis10 = '<line x1="19.5" y1=' + y1[9] + ' x2="22.75" y2=' + y1[
        9] + ' style="stroke:black;stroke-width:1"/><text x="26.5" y=' + y[
                 9] + ' text-anchor="left"  font-size="11" fill="black" >' + axis_value[9] + '</text>\n'
    axis11 = '<line x1="19.5" y1=' + y1[10] + ' x2="25" y2=' + y1[
        10] + ' style="stroke:black;stroke-width:1"/><text x="26.5" y=' + y[
                 10] + ' text-anchor="left"  font-size="11" fill="black" >' + axis_value[10] + '</text>\n'
    axis_y = '<line x1="20" y1=' + y1[0] + ' x2="20" y2=' + y1[
        11] + ' style="stroke:black;stroke-width:1"/><line x1="20" y1=' + y1[11] + ' x2="18.5" y2=' + y1[
                 12] + ' style="stroke:black;stroke-width:1"/><line x1="20" y1=' + y1[11] + ' x2="21.5" y2=' + y1[
                 12] + ' style="stroke:black;stroke-width:1"/>\n'
    axis_all = axis1 + axis2 + axis3 + axis4 + axis5 + axis6 + axis7 + axis8 + axis9 + axis10 + axis11 + axis_y
    return axis_all


def chr_pro(chr_len_dict, chr_num, max_value, i, num_one_line):
    """
    根据染色体长度生成svg格式的染色体
    Args:
        chr_len_dict: 染色体dict，用于查找染色体长度
        chr_num: 染色体数量，不能直接对chr_len_dict进行求个数，因为每轮个数可能不同
        max_value: 坐标轴最大值
        i: 染色体行数
        num_one_line: 一行显示几条chr

    Returns:
        返回一轮染色体的svg字符串
    """

    # 染色体名字的y坐标
    y_name = ''.join('"{0}"'.format(38 + 300 * i))
    # 染色体的y坐标
    y_chr = ''.join('"{0}"'.format(50 + 300 * i))

    chr_line = ''
    x_name = []  # 染色体名字的ｘ坐标
    x_chr = []  # 染色体的ｘ坐标

    # 一条染色体宽度
    w_sin_chr = math.floor(1100 / num_one_line)

    for a in range(chr_num):
        # 染色体名字的ｘ坐标
        x_n = ''.join('"{0}"'.format(100 + w_sin_chr * a))
        x_name.append(x_n)
        # 染色体的ｘ坐标
        chr_value = list(chr_len_dict.values())[a]  # 每条染色体长度

        total_height = 180  # 每条坐标轴的总长度是180px
        height_i = ''.join('"{0}"'.format(chr_value / max_value * total_height))
        x_c = ''.join('"{0}"'.format(95 + w_sin_chr * a))
        x_chr.append(x_c)

        chr_name = '<text x=' + x_name[
            a] + ' y=' + y_name + ' text-anchor="middle" font="Times New Roman" font-size="12" fill="black" >' + \
                   list(chr_len_dict.keys())[a + num_one_line * i] + '</text>\n'
        chr_x = '<rect  width="10" height=' + height_i + ' x=' + x_chr[
            a] + ' y=' + y_chr + ' rx="14" ry="14" style="stroke-width:1;stroke:black;fill:none;"/>\n'
        chromosome = chr_name + chr_x
        chr_line += chromosome
    return chr_line


def chr_all(chr_len_dict, num_one_line):
    """
        最终生成svg图片所有元素的函数
    Args:
        chr_len_dict: 染色体长度
        num_one_line: 一行显示几条chr

    Returns:
        svg图片、图片高度和宽度
    """

    # svg的header
    header = '<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'

    axis_value, max_value = axis(chr_len_dict)  # 获取坐标轴的数值和最大值
    chr_num = len(chr_len_dict)  # 获取染色体数目
    r = chr_num / num_one_line  # 计算有几行染色体
    r_ = math.ceil(chr_num / num_one_line)  # 向上取整
    height = ''.join('"{0}"'.format(300 * r_))  # 获取svg图片高度
    chr_total = ''
    chr_total += header

    # 一条染色体宽度
    w_sin_chr = math.floor(1100 / num_one_line)
    if r <= 1:  # 如果染色体数目只有一行
        # 根据染色体数目改变svg的大小
        width = ''.join('"{0}"'.format(100 + w_sin_chr * chr_num))
        svg_size = '<svg width=' + width + ' height=' + height + ' version="1.1" xmlns="http://www.w3.org/2000/svg">\n'
        axis_all = axis_loc(axis_value, 0)
        chr_line = chr_pro(chr_len_dict=chr_len_dict, chr_num=chr_num, max_value=max_value, i=0,
                           num_one_line=num_one_line)
        chr_total = svg_size + axis_all + chr_line
    elif r > 1 and chr_num % num_one_line == 0:  # 染色体行数大于1，且为整行数
        width = ''.join('"{0}"'.format(1200))
        svg_size = '<svg width=' + width + ' height=' + height + ' version="1.1" xmlns="http://www.w3.org/2000/svg">\n'
        chr_total += svg_size
        for i in range(r_):
            axis_all = axis_loc(axis_value, i=i)
            chr_line = chr_pro(chr_len_dict=chr_len_dict, chr_num=num_one_line, max_value=max_value, i=i,
                               num_one_line=num_one_line)
            chr_total += (axis_all + chr_line)
    else:  # 如果行数大于1，且最后一行染色体数目不是一整行
        r_int = chr_num // num_one_line
        r_add = chr_num % num_one_line
        width = ''.join('"{0}"'.format(1200))
        svg_size = '<svg width=' + width + ' height=' + height + ' version="1.1" xmlns="http://www.w3.org/2000/svg">\n'
        chr_total += svg_size
        for i in range(int(r_int)):
            axis_all = axis_loc(axis_value, i=i)
            chr_line = chr_pro(chr_len_dict=chr_len_dict, chr_num=num_one_line, max_value=max_value, i=i,
                               num_one_line=num_one_line)
            chr_total += (axis_all + chr_line)
        axis_add = axis_loc(axis_value, i=r_int)
        chr_add = chr_pro(chr_len_dict=chr_len_dict, chr_num=r_add, max_value=max_value, i=r_int,
                          num_one_line=num_one_line)
        chr_total += (axis_add + chr_add)
    return chr_total, height, width


def gen_chr_png(chr_len_dict, svg_path, num_one_line):
    """
        根据染色体长度画染色体图片
    Args:
        chr_len_dict: 染色体长度dict，{'chr1': 111, 'chr2': 222,}
        svg_path: 染色体图片的输出路径
        num_one_line: 染色体图片中每行显示的染色体数目

    Returns:
        染色体图片的路径
    """

    chr_fig, height, width = chr_all(chr_len_dict, num_one_line)
    with open(os.path.join(svg_path, "chr.svg"), 'w+', encoding='utf-8') as f:
        f.write(chr_fig + '\n</svg>')
        f.close()

    chr_img_path = os.path.join(svg_path, "chr.svg")

    return chr_img_path

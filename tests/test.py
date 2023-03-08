import numpy as np
from tools.gen_chr_png import get_full_len_matrix

hic_file = "/home/jzj/Jupyter-Docker/HiC-Straw/Np.1.hic"
assembly_file = None
resolution = 1250000

full_len_matrix = get_full_len_matrix(hic_file, assembly_file, resolution)

# 获取数组的上三角部分
upper_tri = np.triu(full_len_matrix)

# 计算上三角部分的平均值
upper_tri_mean = np.mean(upper_tri)

print(upper_tri_mean, "\n")
print(upper_tri_mean * 5, "\n")

maxcolor_95 = (np.percentile(full_len_matrix, 95))
print("95:", maxcolor_95, "\n")
print("95*2:", maxcolor_95 * 2, "\n")

maxcolor_99 = (np.percentile(full_len_matrix, 99))

print("99:", maxcolor_99, "\n")
print("Done!")

import numpy as np
from src.core.utils.get_cfg import get_full_len_matrix
import time

hic_file = "/home/jzj/Jupyter-Docker/HiC-Straw/Np.1.hic"
assembly_file = None
resolution = 1250000
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
full_len_matrix = get_full_len_matrix(hic_file, resolution)

maxcolor_99 = (np.percentile(full_len_matrix, 99))
maxcolor_95 = (np.percentile(full_len_matrix, 95))

print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
print("maxcolor_99:", maxcolor_99, "\n")

print("maxcolor_95:", maxcolor_95, "\n")

print("Done!")

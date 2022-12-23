import hicstraw
import numpy as np

hic = hicstraw.HiCFile("/home/jzj/Downloads/cs/cs.0.hic")

resolutions = hic.getResolutions()
print(resolutions)
for chrom in hic.getChromosomes():
    print(chrom.name, chrom.length)

matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", "NONE", "BP", 1000)

start = 541000000
end = 542400000
numpy_matrix_chr_1 = matrix_object_chr.getRecordsAsMatrix(start, end, start, end)

if np.percentile(numpy_matrix_chr_1, 99.9) == 0:
    print("yes")
# print(np.max(numpy_matrix_chr_1))

print("done")

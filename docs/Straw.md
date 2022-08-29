# Straw

- Python操作`.hic`文件



## Example

- Denpendency

```python
import numpy as np
import hicstraw
```

- 创建HiC对象

```python
hic = hicstraw.HiCFile("HIC001.hic")

# chromosomes
print(hic.getChromosomes())

# query genomeID
print(hic.getGenomeID())

# resolutions
print(hic.getResolutions())
```

- 提取指定矩阵对象
  - specific matrix-type: `observed` (count) or `oe` (observed/expected ratio)
  - chromosome-chromosome pair
  - resolution
  - normalization

```python
# pick the counts from the intrachromosomal region for chr4 with KR normalization at 5kB resolution

mzd = hic.getMatrixZoomData('4', '4', "observed", "KR", "BP", 5000)

# get numpy matrices for specific genomic windows by calling
numpy_matrix = mzd.getRecordsAsMatrix(10000000, 12000000, 10000000, 12000000)
```



## Usage

```python
hic = hicstraw.HiCFile(filepath)
hic.getChromosomes()
hic.getGenomeID()
hic.getResolutions()

mzd = hic.getMatrixZoomData(chrom1, chrom2, data_type, normalization, "BP", resolution)

numpy_matrix = mzd.getRecordsAsMatrix(gr1, gr2, gc1, gc2)
records_list = mzd.getRecords(gr1, gr2, gc1, gc2)
```



`filepath`: path to file (local or URL)
`data_type`: `'observed'` (previous default / "main" data) or `'oe'` (observed/expected)
`normalization`: `NONE`, `VC`, `VC_SQRT`, `KR`, `SCALE`, etc.
`resolution`: typically `2500000`, `1000000`, `500000`, `100000`, `50000`, `25000`, `10000`, `5000`, etc.

`gr1`: start genomic position along rows   **行**
`gr2`: end genomic position along rows
`gc1`: start genomic position along columns  **列**
`gc2`: end genomic position along columns

> 以上信息只能从`.hic`文件中提取，如果原始文件中没有的话，不能从头计算



## Legacy usage

- fetch a list of all the raw contacts on chrX at 100Kb resolution

```python
import hicstraw

result = hicstraw.straw('observed', 'NONE', '/home/jzj/Auto-HiC/HiC-Data/GSM1551550_HIC001.hic', 'X', 'X', 'BP', 1000000)

for i in range(len(result)):
    print("{0}\t{1}\t{2}".format(result[i].binX, result[i].binY, result[i].counts))
```

- To fetch a list of KR normalized contacts for the same region:

```python
result = hicstraw.straw('observed', 'KR', '/home/jzj/Auto-HiC/HiC-Data/GSM1551550_HIC001.hic', 'X', 'X', 'BP', 1000000)

for i in range(len(result)):
    print("{0}\t{1}\t{2}".format(result[i].binX, result[i].binY, result[i].counts))
```

- To query observed/expected KR normalized data

```python
result = hicstraw.straw('oe', 'KR', '/home/jzj/Auto-HiC/HiC-Data/GSM1551550_HIC001.hic', 'X', 'X', 'BP', 1000000)

for i in range(len(result)):
    print("{0}\t{1}\t{2}".format(result[i].binX, result[i].binY, result[i].counts))
```

> 返回信息为 

![image-20220419205858315](https://s2.loli.net/2022/04/19/c2Y7U5nPmTMdZ1G.png)

- Usage

```python
hicstraw.straw(data_type, normalization, file, region_x, region_y, 'BP', resolution)
```


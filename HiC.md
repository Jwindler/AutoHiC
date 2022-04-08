# HiC

- HiC 开发的软件介绍

```http
https://www.4dnucleome.org/software.html
```



- 文件格式介绍

```http
https://zhuanlan.zhihu.com/p/49181257
```



## 原理





## 建库测序

- HiC建库的插入片段长度一般在**300-500bp**





##　辅助组装

![image-20220330162308256](https://s2.loli.net/2022/03/30/lXVk8DqSFvbt2fM.png)

1. 首先，利用染色体内互作概率高于染色体间互作这一特征将contigs分组，每一组将对应一条染色体。
2. 利用染色体内部距离越近互作概率越高这一特征将contigs排序并进一步确定方向。

- 影响因素
  - 基因组片段越大（即N50越大），组装效果越好。
  - 相同N50时，数据量越高，组装效果越好。



##　数据处理

1. 序列比对
2. 数据过滤
3. 数据Binning（将数据分成小单元）
4. 数据校正

​		**仅双端均唯一匹配**到参考序列上的paired reads（valid pairs）才能用于后续分析

![image-20220330162906970](https://s2.loli.net/2022/03/30/DAqXVW2n3vBwMoe.png)



## 互作矩阵

### ContactMap

​		Contact Map 数据是 Reads Pairs 经过划 bin 后转换为矩阵得到的， 所以会有一定程度的信息损失。 Contact Map 从数据结构上来看其实就是一个矩阵， 但在存储形式上可以是稠密的矩阵也可以是稀疏矩阵。 根据划取的 bin 的大小 (binsize) Contact Map 有不同的分辨率 (resolution) 之分，越高的 resolution 意味着 越小的 binsize，从中能观察出更精细的互作结构，但同时占用的存储空间也越大。 所以需要根据测序深度的大小来选取合适的 binsize。

-  Contact Map 存储现有格式

```
文本文件
tab-delimited text
coordinated list
Numpy 矩阵 (.npy)
Dekker Lab HDF5
Cooler
.hic file (Aiden Lab)
BUTLR (Yue lab)
```



### 矩阵构建

1. 将基因组参考序列按照**指定的大小**分配成固定的区块（bins）
2. 将过滤后双端序列两端分别分配到基因组上不同的bins内

- 分辨率 : 指定大小的bin的长度

![image-20220330165314025](https://s2.loli.net/2022/03/31/GD2BXSaOfTlUuic.png)

​		矩阵内的每个值代表其在坐标轴上的bin内存在多少对Hi-C reads，即这两个bins间发生了多少次“互作”



### 矩阵矫正

​		Hi-C数据中由于各种原因会导致其在**基因组不同位置间存在偏差**。因此，在数据处理的最后一步，会对互作矩阵进行校正，使数据在基因组上每个位点的**覆盖度一致**。

​		如图3所示，校正前的矩阵在基因组上的覆盖度存在差异，相比原始矩阵，校正后矩阵的每个点反映了其对应的基因组上两点间的互作概率。通过矩阵的校正，可以**降低数据的噪音**从而凸显出有意义的互作。

![image-20220330165141072](https://s2.loli.net/2022/03/30/MBoCZiQJnrF29VR.png)



- 归一化

​		不同区域GC含量，mapping概率等系统误差都使得原始的交互矩阵不能够有效代表染色质交互信息， 所以需要进行归一化



## .hic



## .assembly

- `>`开头的行为 contigs
- `-`代表反向
- `:::debris`尾部残余

| name                 | number | length   |
| -------------------- | ------ | -------- |
| >utg412:::fragment_1 | 1      | 16185183 |
| >utg412:::fragment_2 | 2      | 25000    |
| >utg412:::fragment_3 | 3      | 48000    |
| utg75:::fragment_1   | 4      | 9575220  |

- 三部分
  - 1. 上方表格内容
    2. 染色体内容
    3. 尾部残余

- 数据操作

```http
https://github.com/aidenlab/straw

# 基于python 
https://github.com/aidenlab/straw/tree/master/pybind11_python
```





## 软件

HICUP

Hi-Corrector (数据格式定义，无用)

Hic-Box（无用）

Hiclib（long time）

distiller

​	.cool 

HiCExplorer
https://hicexplorer.readthedocs.io/en/3.7.2/index.html

cooler

https://cooler.readthedocs.io/en/latest/datamodel.html

TADbit

​	[Welcome to TADbit’s documentation! — TADbit 1.0 documentation (3dgenomes.github.io)](http://3dgenomes.github.io/TADbit/)

- python操作.hic

https://github.com/aidenlab/straw/wiki/Python

https://github.com/aidenlab/



## 可视化

[Hi-C数据可视化](https://xuzhougeng.top/archives/HiC-visualization-in-assembly)

[HiCPlotter](https://github.com/akdemirlab/HiCPlotter)



Juicer使用

​	[HiC 数据处理](https://zhuanlan.zhihu.com/p/341206245)

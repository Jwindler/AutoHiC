# 异位处理记录



![image-20220715102318499](https://s2.loli.net/2022/07/15/Zm7Lr1Q4CtD8ivX.png)



## 步骤

1. 检测到异位，并返回异位位置  > `error_box.py`
2. 查询该位置，所包含的ctg信息   > `find_error_ctgs.py`
3. 对ctg进行切割，更新assembly信息  > `cut_ctg.py`
4. **查找易位需要插入的位置，并修改assembly信息**   > `search_right_site.py`
5. 3D-DNA测试





![image-20220715101207736](https://s2.loli.net/2022/07/15/J6KOMukIWe2iqV4.png)





## *矩阵获取

> Notes!

```python
matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", "KR", "BP", 1250000)
# 上面代码，会根据分辨率，直接在基因组长度上，进行切割，形成一个整体的矩阵

numpy_matrix_chr_1 = matrix_object_chr.getRecordsAsMatrix(453010131, 455241282, 0, 1)
# 这条代码会根据查炸的范围，从整体的矩阵中提取包括这个范围的矩阵
```



​		获取真实矩阵的方案：由于直接用位点查询的矩阵，会存在许多0的问题，因此，需要根据分辨率和位点，进行结合，获取真实矩阵bin的位置。用于后续查找峰值





## *插入位置的确定

​		将上面获取的矩阵，转化为图像的形式，获取峰值，峰值除开原本位置，就是需要插入的位置，利用这个峰值所在的bin，获取插入的区间，再寻找contig，进行整合插入。

​		峰值需要根据多个一维的情况，先删除原本的峰值，再取交集。





## *插入位置精确

- ？ 如何根据最大分辨率获取的bin，获取更精确的插入位点







## find_peaks

```python
from scipy.signal import find_peaks

x = np.arange(0, 917)
y = numpy_matrix_chr_1[2]

# 已导入需要处理的数据(x,y)
plt.plot(x,y)
plt.xlabel('freq/Hz')
plt.ylabel('amp')

peak_id,peak_property = find_peaks(y, height=2000, distance=20)
peak_freq = x[peak_id]
peak_height = peak_property['peak_heights']
print('peak_freq',peak_freq)
print('peak_height',peak_height)

```




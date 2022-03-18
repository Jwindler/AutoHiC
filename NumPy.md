# NumPy



## Ndarray

ndarray 内部由以下内容组成：

- 一个指向数据（内存或内存映射文件中的一块数据）的指针。
- 数据类型或 dtype，描述在数组中的固定大小值的格子。
- 一个表示数组形状（shape）的元组，表示各维度大小的元组。
- 一个跨度元组（stride），其中的整数指的是为了前进到当前维度下一个元素需要"跨过"的字节数。

![image-20220315113138463](https://s2.loli.net/2022/03/15/TzhJ5BwNmPUEGv7.png)

- 创建对象

```python
numpy.array(object, dtype = None, copy = True, order = None, subok = False, ndmin = 0)
```

| object | 数组或嵌套的数列                                          |
| ------ | --------------------------------------------------------- |
| dtype  | 数组元素的数据类型，可选                                  |
| copy   | 对象是否需要复制，可选                                    |
| order  | 创建数组的样式，C为行方向，F为列方向，A为任意方向（默认） |
| subok  | 默认返回一个与基类类型一致的数组                          |
| ndmin  | 指定生成数组的最小维度                                    |

- numpy.dtype对象

```python
numpy.dtype(object, align, copy)
```

- object - 要转换为的数据类型对象
- align - 如果为 true，填充字段使其类似 C 的结构体。
- copy - 复制 dtype 对象 ，如果为 false，则是对内置数据类型对象的引用



## 数组属性

| 属性             | 说明                                                         |
| :--------------- | :----------------------------------------------------------- |
| ndarray.ndim     | 秩，即轴的数量或维度的数量                                   |
| ndarray.shape    | 数组的维度，对于矩阵，n 行 m 列                              |
| ndarray.size     | 数组元素的总个数，相当于 .shape 中 n*m 的值                  |
| ndarray.dtype    | ndarray 对象的元素类型                                       |
| ndarray.itemsize | ndarray 对象中每个元素的大小，以字节为单位                   |
| ndarray.flags    | ndarray 对象的内存信息                                       |
| ndarray.real     | ndarray元素的实部                                            |
| ndarray.imag     | ndarray 元素的虚部                                           |
| ndarray.data     | 包含实际数组元素的缓冲区，由于一般通过数组的索引获取元素，所以通常不需要使用这个属性。 |

> ndarray.reshape 通常返回的是非拷贝副本，即改变返回后数组的元素，原数组对应元素的值也会改变。



## 创建数组

- numpy.empty

| 参数  | 描述                                                         |
| :---- | :----------------------------------------------------------- |
| shape | 数组形状                                                     |
| dtype | 数据类型，可选                                               |
| order | 有"C"和"F"两个选项,分别代表，行优先和列优先，在计算机内存中的存储元素的顺序。 |

```python
# 创建一个指定形状（shape）、数据类型（dtype）且未初始化的数组
numpy.empty(shape, dtype = float, order = 'C')
#  数组元素为随机值，因为它们未初始化。
```

- numpy.zeros

```python
# 创建指定大小的数组，数组元素以 0 来填充：
numpy.zeros(shape, dtype = float, order = 'C')
# 'C' 用于 C 的行数组，或者 'F' 用于 FORTRAN 的列数组
```

- numpy.asarray (同numpy.array)

```python
numpy.asarray(a, dtype = None, order = None)
```

| 参数  | 描述                                                         |
| :---- | :----------------------------------------------------------- |
| a     | 任意形式的输入参数，可以是，列表, 列表的元组, 元组, 元组的元组, 元组的列表，多维数组 |
| dtype | 数据类型，可选                                               |
| order | 可选，有"C"和"F"两个选项,分别代表，行优先和列优先，在计算机内存中的存储元素的顺序。 |

- numpy.frombuffer

numpy.frombuffer 用于实现动态数组。

numpy.frombuffer 接受 buffer 输入参数，以流的形式读入转化成 ndarray 对象。

```python
numpy.frombuffer(buffer, dtype = float, count = -1, offset = 0)
```

> **注意：***buffer 是字符串的时候，Python3 默认 str 是 Unicode 类型，所以要转成 bytestring 在原 str 前加上 b*

| 参数   | 描述                                     |
| :----- | :--------------------------------------- |
| buffer | 可以是任意对象，会以流的形式读入。       |
| dtype  | 返回数组的数据类型，可选                 |
| count  | 读取的数据数量，默认为-1，读取所有数据。 |
| offset | 读取的起始位置，默认为0。                |

- numpy.fromiter

numpy.fromiter 方法从可迭代对象中建立 ndarray 对象，返回一维数组。

```python
numpy.fromiter(iterable, dtype, count=-1)
```

| 参数     | 描述                                   |
| :------- | :------------------------------------- |
| iterable | 可迭代对象                             |
| dtype    | 返回数组的数据类型                     |
| count    | 读取的数据数量，默认为-1，读取所有数据 |

- numpy.arange

numpy 包中的使用 arange 函数创建数值范围并返回 ndarray 对象，函数格式如下：

```python
numpy.arange(start, stop, step, dtype)
# 根据 start 与 stop 指定的范围以及 step 设定的步长，生成一个 ndarray。

x = np.arange(5)  
print (x)
# [0  1  2  3  4]
```

| 参数    | 描述                                                         |
| :------ | :----------------------------------------------------------- |
| `start` | 起始值，默认为`0`                                            |
| `stop`  | 终止值（不包含）                                             |
| `step`  | 步长，默认为`1`                                              |
| `dtype` | 返回`ndarray`的数据类型，如果没有提供，则会使用输入数据的类型。 |

- numpy.linspace

numpy.linspace 函数用于创建一个一维数组，数组是一个等差数列构成的

```python
np.linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=None)
```

参数说明：

| 参数       | 描述                                                         |
| :--------- | :----------------------------------------------------------- |
| `start`    | 序列的起始值                                                 |
| `stop`     | 序列的终止值，如果`endpoint`为`true`，该值包含于数列中       |
| `num`      | 要生成的等步长的样本数量，默认为`50`                         |
| `endpoint` | 该值为 `true` 时，数列中包含`stop`值，反之不包含，默认是True。 |
| `retstep`  | 如果为 True 时，生成的数组中会显示间距，反之不显示。         |
| `dtype`    | `ndarray` 的数据类型                                         |

```python
a = np.linspace(1,10,10)
print(a)
# [ 1.  2.  3.  4.  5.  6.  7.  8.  9. 10.]
```

- numpy.logspace

numpy.logspace 函数用于创建一个于等比数列

```python
np.logspace(start, stop, num=50, endpoint=True, base=10.0, dtype=None)
```

base 参数意思是取对数的时候 log 的下标。

| 参数       | 描述                                                         |
| :--------- | :----------------------------------------------------------- |
| `start`    | 序列的起始值为：base ** start                                |
| `stop`     | 序列的终止值为：base ** stop。如果`endpoint`为`true`，该值包含于数列中 |
| `num`      | 要生成的等步长的样本数量，默认为`50`                         |
| `endpoint` | 该值为 `true` 时，数列中中包含`stop`值，反之不包含，默认是True。 |
| `base`     | 对数 log 的底数。                                            |
| `dtype`    | `ndarray` 的数据类型                                         |



## 切片和索引

​		与 Python 中 list 的切片操作一样

```python
a = np.arange(10)
s = slice(2,7,2)   # 从索引 2 开始到索引 7 停止，间隔为2
# b = a[2:7:2] 
print (a[s])
# [2  4  6]

print (a[...,1])   # 第2列元素
print (a[1,...])   # 第2行元素
print (a[...,1:])  # 第2列及剩下的所有元素
# 逗号前为行，后为列
```



## 高级索引

- 整数数组索引

获取数组中(0,0)，(1,1)和(2,0)位置处的元素

```python
x = np.array([[1,  2],  [3,  4],  [5,  6]]) 
y = x[[0,1,2],  [0,1,0]]  # 第一个位置是行，后面是列
```



- 布尔索引

```python
# 现在我们会打印出大于 5 的元素  
print (x[x >  5])

# 使用了 ~（取补运算符）来过滤 NaN
a[~np.isnan(a)]

# 从数组中过滤掉非复数元素
a[np.iscomplex(a)
```



- 花式索引(利用整数数组进行索引)

```python
# 3，1，0，6 行
x[[4,2,1,7]]

# 倒数即可
x[[-4,-2,-1,-7]]

# 前一个数组与后一个数组组合
x[np.ix_([1,5,7,2],[0,3,1,2])]
```



## 广播

​		广播(Broadcast)是 numpy 对不同形状(shape)的数组进行数值计算的方式， 对数组的算术运算通常在相应的元素上进行。

```python
# 维数 维度长度相同
a = np.array([1,2,3,4]) 
b = np.array([10,20,30,40]) 
c = a * b  # array([ 10,  40,  90, 160])


```

- 数组形状不同

![image-20220317110501650](https://s2.loli.net/2022/03/17/8cwaByVNfngdSkK.png)



## 迭代数组

```python
a = np.arange(6).reshape(2,3)
# 迭代输出元素
for x in np.nditer(a):
    print (x, end=", " )
```

- 控制遍历顺序

- `for x in np.nditer(a, order='F'):`Fortran order，即是列序优先；
- `for x in np.nditer(a.T, order='C'):`C order，即是行序优先；

![image-20220317111230568](https://s2.loli.net/2022/03/17/BG1HfbwuAk7DvaY.png)

- 修改数组中元素的值

实现对数组元素值得修改，必须指定 read-write 或者 write-only 的模式

```python
for x in np.nditer(a, op_flags=['readwrite']): 
    x[...]=2*x 
```

- 外部循环

| 参数            | 描述                                           |
| :-------------- | :--------------------------------------------- |
| `c_index`       | 可以跟踪 C 顺序的索引                          |
| `f_index`       | 可以跟踪 Fortran 顺序的索引                    |
| `multi_index`   | 每次迭代可以跟踪一种索引类型                   |
| `external_loop` | 给出的值是具有多个值的一维数组，而不是零维数组 |

```python
for x in np.nditer(a, flags =  ['external_loop'], order =  'F'): 
    print (x, end=", " )
```

![image-20220317111759884](https://s2.loli.net/2022/03/17/9TtuGZvbhqYC3Sd.png)

- 广播迭代

```python
a = np.arange(0,60,5) 
a = a.reshape(3,4) 

b = np.array([1,  2,  3,  4], dtype =  int)  

for x,y in np.nditer([a,b]):  
    print ("%d:%d"  %  (x,y), end=", " )
```

![image-20220317111945366](/home/jzj/.config/Typora/typora-user-images/image-20220317111945366.png)



## 数组操作（重点）

### 修改数组形状

- numpy.reshape

```python
numpy.reshape(arr, newshape, order='C')
```

- `arr`：要修改形状的数组
- `newshape`：整数或者整数数组，新的形状应当兼容原有形状
- order：'C' -- 按行，'F' -- 按列，'A' -- 原顺序，'k' -- 元素在内存中的出现顺序。

```python
a = np.arange(8)
# 修改为4行2列的矩阵
b = a.reshape(4, 2)
```



- numpy.ndarray.flat : 数组元素迭代器

```python
a = np.arange(9).reshape(3,3) 
for element in a.flat:
    print(element)
```

- numpy.ndarray.flatten 返回一份数组拷贝，对拷贝所做的修改不会影响原始数组

```python
ndarray.flatten(order='C')
# order：'C' -- 按行，'F' -- 按列，'A' -- 原顺序，'K' -- 元素在内存中的出现顺序。
```

- numpy.ravel() 展平的数组元素，顺序通常是"C风格"，返回的是数组视图（view，有点类似 C/C++引用reference的意味），修改会影响原始数组。

```python
numpy.ravel(a, order='C')
# order：'C' -- 按行，'F' -- 按列，'A' -- 原顺序，'K' -- 元素在内存中的出现顺序。
```



### 翻转数组

- numpy.transpose 函数用于对换数组的维度
  - `arr`：要操作的数组
  - `axes`：整数列表，对应维度，通常所有维度都会对换。

```python
numpy.transpose(arr, axes)
```



- numpy.rollaxis 函数向后滚动特定的轴到一个特定位置
  - `arr`：数组
  - `axis`：要向后滚动的轴，其它轴的相对位置不会改变
  - `start`：默认为零，表示完整的滚动。会滚动到特定位置。

```python
numpy.rollaxis(arr, axis, start)
```



- numpy.swapaxes 函数用于交换数组的两个轴
  - `arr`：输入的数组
  - `axis1`：对应第一个轴的整数
  - `axis2`：对应第二个轴的整数

```python
numpy.swapaxes(arr, axis1, axis2)
```



### 修改数组维度

- numpy.broadcast 用于模仿广播的对象，它返回一个对象，该对象封装了将一个数组广播到另一个数组的结果



## 位运算

| 函数          | 描述                   |
| :------------ | :--------------------- |
| `bitwise_and` | 对数组元素执行位与操作 |
| `bitwise_or`  | 对数组元素执行位或操作 |
| `invert`      | 按位取反               |
| `left_shift`  | 向左移动二进制表示的位 |
| `right_shift` | 向右移动二进制表示的位 |

- bitwise_and 函数对数组中整数的二进制形式执行位与运算。

```python
a,b = 13,17
print (bin(a), bin(b))
# 0b1101 0b10001

print (np.bitwise_and(13, 17))
# 1
```



![image-20220318113744868](https://s2.loli.net/2022/03/18/m6dsZMoD83Qf5rv.png)

- bitwise_or()函数对数组中整数的二进制形式执行位或运算

```python
print (np.bitwise_or(13, 17))
# 29
```

![image-20220318113906504](https://s2.loli.net/2022/03/18/FdvLp3j6PSwkUT9.png)

- invert() 函数对数组中整数进行位取反运算，即 0 变成 1，1 变成 0

- left_shift() 函数将数组元素的二进制形式向左移动到指定位置，右侧附加相等数量的 0

```python
np.left_shift(10,2)
# 00001010 > 10
# 00101000 > 40
```

- right_shift() 函数将数组元素的二进制形式向右移动到指定位置，左侧附加相等数量的 0 (同上，取反向)



## 字符串函数

- numpy.char.add() 函数依次对两个数组的元素进行字符串连接

```python
np.char.add(['hello'],[' xyz'])
# ['hello xyz']
```

- numpy.char.multiply() 函数执行多重连接

```python
np.char.multiply('Runoob ',3)
# Runoob Runoob Runoob 
```

- numpy.char.center() 函数用于将字符串居中，并使用指定字符在左侧和右侧进行填充

```python
np.char.center('Runoob', 20,fillchar = '*')
# *******Runoob*******
```

- numpy.char.capitalize() 函数将字符串的第一个字母转换为大写

```python
np.char.capitalize('runoob')
# Runoob
```

- numpy.char.title() 函数将字符串的每个单词的第一个字母转换为大写

```python
np.char.title('i like runoob')
# I Like Runoob
```

- numpy.char.lower() 函数对数组的每个元素转换为小写。它对每个元素调用 str.lower

```python
#操作数组
np.char.lower(['RUNOOB','GOOGLE'])
# ['runoob' 'google']

# 操作字符串
np.char.lower('RUNOOB')
# runoob
```

- numpy.char.upper() 函数对数组的每个元素转换为大写。它对每个元素调用 str.upper

```python
#操作数组
np.char.upper(['runoob','google'])
# ['RUNOOB' 'GOOGLE']

# 操作字符串
np.char.upper('runoob')
# RUNOOB
```

- numpy.char.split() 通过指定分隔符对字符串进行分割，并返回数组。默认情况下，分隔符为空格

```python
np.char.split ('www.runoob.com', sep = '.')
# ['www', 'runoob', 'com']
```

- numpy.char.splitlines() 函数以换行符作为分隔符来分割字符串，并返回数组

```python
np.char.splitlines('i\nlike runoob?')
# ['i', 'like runoob?']
# \n，\r，\r\n 都可用作换行符
```

- numpy.char.strip() 函数用于移除开头或结尾处的特定字符

```python
np.char.strip(['arunooba','admin','java'],'a')
# ['runoob' 'dmin' 'jav']
```

- numpy.char.join() 函数通过指定分隔符来连接数组中的元素或字符串

```python
np.char.join([':','-'],['runoob','google'])
# ['r:u:n:o:o:b' 'g-o-o-g-l-e']
```

- numpy.char.replace() 函数使用新字符串替换字符串中的所有子字符串

```python
np.char.replace ('i like runoob', 'oo', 'cc')
# i like runccb
```

- numpy.char.encode() 函数对数组中的每个元素调用 str.encode 函数

```python
np.char.encode('runoob', 'cp500') 
# b'\x99\xa4\x95\x96\x96\x82'
```

- numpy.char.decode() 函数对编码的元素进行 str.decode() 解码

```python
np.char.decode(a,'cp500')
# runoob
# 接上一个
```








# Pytorch



## 基本概念

### 简介

- 实现模型训练的 5 大要素

![image-20220316172749777](https://s2.loli.net/2022/03/16/OHnCk6elhmLgzda.png)
- 数据：包括数据读取，数据清洗，进行数据划分和数据预处理，比如读取图片如何预处理及数据增强。

- 模型：包括构建模型模块，组织复杂网络，初始化网络参数，定义网络层。


- 损失函数：包括创建损失函数，设置损失函数超参数，根据不同任务选择合适的损失函数。


- 优化器：包括根据梯度使用某种优化器更新参数，管理模型参数，管理多个参数组实现不同学习率，调整学习率。


- 迭代训练：组织上面 4 个模块进行反复训练。包括观察训练效果，绘制 Loss/ Accuracy 曲线，用 TensorBoard 进行可视化分析。

### 张量

​		Tensor 中文为张量。张量的意思是一个多维数组，它是标量、向量、矩阵的高维扩展。

​		RGB 图像可以表示 3 维张量，可以把张量看作多维数组

![image-20220316223420047](https://s2.loli.net/2022/03/16/lvGkNoIDCB2fOpF.png)

#### Tensor 创建的方法

- torch.tensor()

```python
torch.tensor(data, dtype=None, device=None, requires_grad=False, pin_memory=False)
```

- data: 数据，可以是 list，numpy

- dtype: 数据类型，默认与 data 的一致

- device: 所在设备，cuda/cpu

- requires_grad: 是否需要梯度

- pin_memory: 是否存于锁页内存

```python
import pytorch
arr = np.ones((3, 3))
print("ndarray的数据类型：", arr.dtype)

# 创建存放在 GPU 的数据
# t = torch.tensor(arr, device='cuda')

t= torch.tensor(arr)
print(t)
```

- torch.from_numpy(ndarray)

```python
arr = np.array([[1, 2, 3], [4, 5, 6]])
t = torch.from_numpy(arr)
# 利用这个方法创建的 tensor 和原来的 ndarray 共享内存，当修改其中一个数据，另外一个也会被改动
```

- torch.zeros()

```python
torch.zeros(*size, out=None, dtype=None, layout=torch.strided, device=None, requires_grad=False)
```

功能：根据 size 创建全 0 张量

- size: 张量的形状
- out: 输出的张量，如果指定了 out，那么`torch.zeros()`返回的张量和 out 指向的是同一个地址
- layout: 内存中布局形式，有 strided，sparse_coo 等。当是稀疏矩阵时，设置为 sparse_coo 可以减少内存占用。
- device: 所在设备，cuda/cpu
- requires_grad: 是否需要梯度

```python
out_t = torch.tensor([1])
# 这里制定了 out

t = torch.zeros((3, 3), out=out_t)
print(t, '\n', out_t)

# id 是取内存地址。最终 t 和 out_t 是同一个内存地址
print(id(t), id(out_t), id(t) == id(out_t))
```



- torch.zeros_like

```python
torch.zeros_like(input, dtype=None, layout=None, device=None, requires_grad=False, memory_format=torch.preserve_format)
```

功能：根据 input 形状创建全 0 张量

- input: 创建与 input 同形状的全 0 张量
- dtype: 数据类型
- layout: 内存中布局形式，有 strided，sparse_coo 等。当是稀疏矩阵时，设置为 sparse_coo 可以减少内存占用。



- torch.full()，torch.full_like()

```python
torch.full(size, fill_value, out=None, dtype=None, layout=torch.strided, device=None, requires_grad=False)
```

功能：创建自定义数值的张量

- size: 张量的形状，如 (3,3)
- fill_value: 张量中每一个元素的值

```python
# 参数解读如上
orch.full((3, 3), 1)
```



- torch.arange()

```python
torch.arange(start=0, end, step=1, out=None, dtype=None, layout=torch.strided, device=None, requires_grad=False)
```

功能：创建等差的 1 维张量。注意区间为[start, end)。

- start: 数列起始值
- end: 数列结束值，开区间，取不到结束值
- step: 数列公差，默认为 1

```python
t = torch.arange(2, 10, 2)
```



- torch.linspace()

```python
torch.linspace(start, end, steps=100, out=None, dtype=None, layout=torch.strided, device=None, requires_grad=False)
```

功能：创建均分的 1 维张量。数值区间为 [start, end]

- start: 数列起始值
- end: 数列结束值
- steps: 数列长度 (元素个数)

```python
t = torch.linspace(2, 10, 6)
```



- torch.logspace()

```python
torch.logspace(start, end, steps=100, base=10.0, out=None, dtype=None, layout=torch.strided, device=None, requires_grad=False)
```

功能：创建对数均分的 1 维张量。数值区间为 [start, end]，底为 base。

- start: 数列起始值
- end: 数列结束值
- steps: 数列长度 (元素个数)
- base: 对数函数的底，默认为 10



- torch.eye()

```python
torch.eye(n, m=None, out=None, dtype=None, layout=torch.strided, device=None, requires_grad=False)
```

功能：创建单位对角矩阵( 2 维张量)，默认为方阵

- n: 矩阵行数。通常只设置 n，为方阵。
- m: 矩阵列数



### 张量操作与线性回归

- 拼接



## 图片处理与数据加载

### DataLoader & DataSet

![image-20220321112011489](https://s2.loli.net/2022/03/21/ome7HS6CdERzuYt.png)

### Transforms

- 数据增强

将原始数据，进行多种变化，可以增加数据量，还能提升模型的适应能力



## 模型构建

### 模型创建

![img](https://s2.loli.net/2022/03/21/z9GSfgYq7PMjwbd.png)



![img](https://image.zhangxiann.com/20200614114315.png)



- 容器
  - nn.Sequetial：顺序性，各网络层之间严格按照顺序执行，常用于 block 构建，在前向传播时的代码调用变得简洁
  - nn.ModuleList：迭代行，常用于大量重复网络构建，通过 for 循环实现重复构建
  - nn.ModuleDict：索引性，常用于可选择的网络层

### 卷积层

### 池化层、线性层和激活函数层



## 模型训练

### 权值初始化

### 损失函数

​		损失函数是衡量模型输出与真实标签之间的差异

- 损失函数(Loss Function)是计算**一个**样本的模型输出与真实标签的差异
- 代价函数(Cost Function)是计算**整个样本集**的模型输出与真实标签的差异，是所有样本损失函数的平均值
- 目标函数(Objective Function)就是代价函数加上正则项

### 优化器

​		用于管理并更新模型中可学习参数的值，使得模型输出更加接近真实标签。

## 可视化与Hook

### TensorBoard

​		可视化模型训练过程中，参数的变化

### Hook

​		由于 PyTorch 是基于动态图实现的，因此在一次迭代运算结束后，一些中间变量如非叶子节点的梯度和特征图，会被释放掉。在这种情况下想要提取和记录这些中间变量，就需要使用 Hook 函数。




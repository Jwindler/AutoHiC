# Python深度学习



训练神经网络主要围绕以下四个方面。

- 层,多个层组合成网络(或模型)。
- 输入数据和相应的目标。
- 损失函数,即用于学习的反馈信号。
- 优化器,决定学习过程如何进行。

![image-20220318163548408](https://s2.loli.net/2022/03/18/j65Ap7nb92WO4Gt.png)



## 3.Examples

### 二分类

```python
import matplotlib.pyplot as plt
from keras.datasets import imdb
import numpy as np
from keras import models
from keras import layers

# 配置优化器
from keras import losses
from keras import metrics
from tensorflow import optimizers

# 整数序列编码为二进制矩阵


def vectorize_sequences(sequences, dimension=10000):
    # 创建一个序列长度的0矩阵
    results = np.zeros((len(sequences), dimension))
    for i, sequence in enumerate(sequences):
        # 将 results[i] 的指定索引设为 1
        results[i, sequence] = 1
    return results


# 加载数据
# num_words=10000 仅保留训练数据中前 10 000 个最常出现的单词
(train_data, train_labels), (test_data,
                             test_labels) = imdb.load_data(num_words=10000)

# 将单词映射为整数索引的字典
word_index = imdb.get_word_index()

# 键值颠倒,将整数索引映射为单词
reverse_word_index = dict(
    [(value, key) for (key, value) in word_index.items()])

# 将评论解码
decoded_review = ' '.join(
    [reverse_word_index.get(i - 3, '?') for i in train_data[0]]
)

# 将数据向量化
x_train = vectorize_sequences(train_data)
x_test = vectorize_sequences(test_data)

# 标签向量化
y_train = np.asarray(train_labels).astype('float32')
y_test = np.asarray(test_labels).astype('float32')


# 模型定义
model = models.Sequential()
model.add(layers.Dense(16, activation='relu', input_shape=(10000,)))
model.add(layers.Dense(16, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))

# 编译模型
model.compile(
    optimizer='rmsprop',
    loss='binary_crossentropy',
    metrics=['accuracy'])

# 配置优化器
# model.compile(optimizer=optimizers.RMSprop(lr=0.001), oss='binary_crossentropy', etrics=['accuracy'])

# 使用自定义的损失和指标
model.compile(
    optimizer=optimizers.RMSprop(
        lr=0.001),
    loss=losses.binary_crossentropy,
    metrics=[
        metrics.binary_accuracy])


# 留出验证集
x_val = x_train[:10000]
partial_x_train = x_train[10000:]

y_val = y_train[:10000]
partial_y_train = y_train[10000:]


# 训练模型
model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['acc'])

history = model.fit(
    partial_x_train,
    partial_y_train,
    epochs=20,
    batch_size=512,
    validation_data=(
        x_val,
        y_val))

# History 对象有一个成员 history,包含训练过程中的所有数据
history_dict = history.history
print(history_dict.keys())

# 绘制训练损失和验证损失
loss_values = history_dict['loss']
val_loss_values = history_dict['val_loss']

epochs = range(1, len(loss_values) + 1)


plt.plot(epochs, loss_values, 'bo', label='Training loss') # 'bo'表示蓝色圆点
plt.plot(epochs, val_loss_values, 'b', label='Validation loss') # 'b'表示蓝色实线
plt.title('Training and validation loss')
plt.xlabel('Epoches')
plt.ylabel('LOSS')
plt.legend()

plt.show()

# 绘制训练精度和验证精度
# plt.clf()

acc = history_dict['acc']
val_acc = history_dict['val_acc']

plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.show()

# 新的训练模型
model = models.Sequential()
model.add(layers.Dense(16, activation='relu', input_shape=(10000, )))
model.add(layers.Dense(16, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))
                       
model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])

model.fit(x_train, y_train, epochs=4, batch_size=512)
results = model.evaluate(x_test, y_test)

# 用 predict 方法来得到评论为正面的可能性大小
model.predict(x_test)
```



![image-20220319175815745](https://s2.loli.net/2022/03/19/BnDdJKtZ3qyWHhR.png)

- 通常需要对原始数据进行大量**预处理**,以便将其转换为张量输入到神经网络中。单词序
  列可以编码为二进制向量,但也有其他编码方式。
-  带有 relu 激活的 Dense 层堆叠,可以解决很多种问题(包括情感分类)
- 对于**二分类**问题(两个输出类别),网络的最后一层应该是只有一个单元并使用 sigmoid激活的 Dense 层,网络输出应该是 0~1 范围内的标量,表示概率值。
- 对于二分类问题的 sigmoid 标量输出,你应该使用 binary_crossentropy 损失函数。
- 无论你的问题是什么,**rmsprop 优化器**通常都是足够好的选择。这一点你无须担心。
- 随着神经网络在训练数据上的表现越来越好,模型最终会**过拟合**,并在前所未见的数据上得到越来越差的结果。一定要一直**监控模型在训练集之外的数据上的性能**。



### 多分类

- 如果要对 N 个类别的数据点进行分类,网络的最后一层应该是大小为 N 的 Dense 层。
- 对于单标签、多分类问题,网络的最后一层应该使用 softmax 激活,这样可以输出在 N
  个输出类别上的概率分布。
- 这种问题的损失函数几乎总是应该使用分类交叉熵。它将网络输出的概率分布与目标的
  真实分布之间的距离最小化。
- 处理多分类问题的标签有两种方法。
  - 通 过 分 类 编 码( 也 叫 one-hot 编 码 ) 对 标 签 进 行 编 码, 然 后 使 用 categorical_
    crossentropy 作为损失函数。
  - 将标签编码为整数,然后使用 sparse_categorical_crossentropy 损失函数。
- 如果你需要将数据划分到许多类别中,应该避免使用太小的中间层,以免在网络中造成
  信息瓶颈。

> 代码见Jupyter



### 回归问题

- 利用 K 折验证来验证你的方法



![image-20220320160036278](https://s2.loli.net/2022/03/20/feXqFuy6z13n2GK.png)

> Code in JupyterLab

- 回归问题使用的损失函数与分类问题不同。**回归常用的损失函数是均方误差（MSE）**。
- 同样，回归问题使用的评估指标也与分类问题不同。显而易见，精度的概念不适用于回归问题。常见的**回归指标是平均绝对误差（MAE）**。 
- 如果输入数据的特征具有不同的取值范围，应该先进行**预处理**，对每个特征单独进行缩放。 
- 如果可用的数据很少，使用 **K 折验证**可以可靠地评估模型。 
- 如果可用的训练数据很少，最好使用隐藏层较少（通常只有一到两个）的小型网络，以 避免严重的过拟合。

## 小结

- 在将原始数据输入神经网络之前，通常需要对其进行预处理。 
- 如果数据特征具有不同的取值范围，那么需要进行预处理，将每个特征单独缩放。
- 随着训练的进行，神经网络最终会过拟合，并在前所未见的数据上得到更差的结果。
- 如果训练数据不是很多，应该使用只有一两个隐藏层的小型网络，以避免严重的过拟合。 
- 如果数据被分为多个类别，那么中间层过小可能会导致信息瓶颈。
- 回归问题使用的损失函数和评估指标都与分类问题不同。
- 如果要处理的数据很少，K 折验证有助于可靠地评估模型。



## 4.基础

### 4个分支

#### 监督学习

​		给定一组样本（通常由人工标注），它可以学会将输入数据映射到已知目标［也叫标注（annotation）］。

- 序列生成（sequence generation）。给定一张图像，预测描述图像的文字。序列生成有时 可以被重新表示为一系列分类问题，比如反复预测序列中的单词或标记。
- 语法树预测（syntax tree prediction）。给定一个句子，预测其分解生成的语法树。
- **目标检测**（object detection）。给定一张图像，在图中特定目标的周围画一个边界框。这个问题也可以表示为分类问题（给定多个候选边界框，对每个框内的目标进行分类）或 分类与回归联合问题（用向量回归来预测边界框的坐标）。
- **图像分割**（image segmentation）。给定一张图像，在特定物体上画一个像素级的掩模（mask）。

#### 无监督学习

​		降维（dimensionality reduction）和聚类（clustering）都是众所周知的无监督学习方法

#### 自监督学习

​		自监督学习是没有 人工标注的标签的监督学习，标签仍然存在,但它们是从输入数据中生成的,通常是使用启发式算法生成的。

#### 强化学习

​		强化学习中,智能体(agent)接收有关其环境的信息,并学会选择使某种奖励最大化的行动

- 定义

![image-20220320175949683](https://s2.loli.net/2022/03/20/d2Zo857py6jIkli.png)



### 评估机器学习模型

#### 三个集合

​		将数据划分为三个集合:**训练集、验证集和测试集**

- 数据量少

1. 简单的留出验证

​		留出一定比例的数据作为测试集。在剩余的数据上训练模型,然后在测试集上评估模型。

![image-20220320180617299](https://s2.loli.net/2022/03/20/lXNdSZBQMJFh6ka.png)

​		这是最简单的评估方法,但有一个缺点:如果可用的数据很少,那么可能验证集和测试集
包含的样本就太少,从而无法在统计学上代表数据。



2. K折验证

​		K 折验证(K-fold validation)将数据划分为大小相同的 K 个分区。对于每个分区 i ,在剩
余的 K - 1 个分区上训练模型,然后在分区 i 上评估模型。最终分数等于 K 个分数的平均值。

![image-20220320181224949](https://s2.loli.net/2022/03/20/C3KDaocurjOQgAh.png)

3. 带打乱数据的重复K折验证

​		多次使用 K 折验证,在每次将数据划分为 K 个分区之前都先将数据打乱。最终分数是每次 K 折验证分数的平均值。注意,这种方法一共要训练和评估 P×K 个模型(P是重复次数),计算代价很大。

> 一定要确保训练集和验证集之间没有交集



### 数据预处理·特征工程和特征学习

#### 数据预处理

- 向量化

​		神经网络的所有输入和目标都必须是浮点数张量

​		无论处理什么数据(声音、图像还是文本),都必须首先将其转换为**张量**,这一步叫作**数据向量化**

- 值标准化

​		为了让网络的学习变得更容易,输入数据应该具有以下特征。

1. 取值较小:大部分值都应该在 **0~1 范围**内
2. 同质性(homogenous):所有**特征的取值**都应该在大致相同的范围内
3. 将每个特征分别标准化,使其平均值为 0。
4. 将每个特征分别标准化,使其标准差为 1。

- 处理缺失值

​		一般来说,对于神经网络,将缺失值设置为 0 是安全的,只要 0 不是一个有意义的值。网
络能够从数据中学到 0 意味着缺失数据,并且会忽略这个值。

#### 特征工程

​		将数据输入模型之前,利用你自己关于数据和机器学习算法(这里指神经网络)的知识对数据进行硬编码的变换(不是模型学到的),以改善模型的效果。

​		最好一种比较简单的方式将特征特殊处理，便于机器学习

### 过拟合与欠拟合

​		优化(optimization)是指调节模型以在训练数据上得到最佳性能(即机器学习中的学习),而泛化(generalization)是指训练好的模型在前所未见的数据上的性能好坏。

​		降低过拟合的方法叫作正则化

- 减小网络大小

减小模型大小,即减少模型中可学习参数的个数(这由层数和每层的单元个数决定)

- 添加权重正则化
  - L1 正则化(L1 regularization):添加的成本与权重系数的绝对值[权重的 L1 范数(norm)]成正比。
  - L2 正则化(L2 regularization):添加的成本与权重系数的平方(权重的 L2 范数)成正比。神经网络的 L2 正则化也叫权重衰减(weight decay)。不要被不同的名称搞混,权重衰减与 L2 正则化在数学上是完全相同的。
- 添加dropout 正则化

​		对某一层使用 dropout,就是在训练过程中随机将该层的一些输出特征舍弃(设置为 0)

​		dropout 比率(dropout rate)是被设为 0 的特征所占的比例,通常在 0.2~0.5范围内

- 获取更多的训练数据也可以实现防止网络过拟合



### 通用工作流程

- 定义问题，收集数据集
- 选择衡量成功的指标（选择损失函数）
- 确定评估方法
  - 留出验证集。数据量很大时可以采用这种方法
  - K 折交叉验证。如果留出验证的样本量太少,无法保证可靠性,那么应该选择这种方法
  - 重复的 K 折验证。如果可用的数据很少,同时模型评估又需要非常准确,那么应该使用
    这种方法。
- 准备数据
  - 将数据格式化为张量
  - 取值通常应该缩放为较小的值,比如在 [ - 1, 1] 区间或 [0, 1] 区间
  - 如果不同的特征具有不同的取值范围(异质数据),那么应该做数据标准化
  - 你可能需要做特征工程,尤其是对于小数据问题

- 开发比基准更好的模型
  - 最后一层的激活。它对网络输出进行有效的限制。
  - 损失函数。它应该匹配你要解决的问题的类型。
  - 优化配置。你要使用哪种优化器?学习率是多少?大多数情况下,使用 rmsprop 及其
    默认的学习率是稳妥的。

![image-20220320204925164](https://s2.loli.net/2022/03/20/WNpyodVLiFGwXkj.png)

- 扩大模型规模:开发过拟合的模型
  - 添加更多的层
  - 让每一层变得更大
  - 训练更多的轮次

​		**要始终监控训练损失和验证损失,以及你所关心的指标的训练值和验证值。如果你发现模型在验证数据上的性能开始下降,那么就出现了过拟合**。

- 模型正则化与调节超参数
  - 添加 dropout
  - 尝试不同的架构:增加或减少层数
  - 添加 L1 和 / 或 L2 正则化
  - 尝试不同的超参数(比如每层的单元个数或优化器的学习率),以找到最佳配置
  - (可选)反复做特征工程:添加新特征或删除没有信息量的特征



## 5.计算机视觉

​		**卷积神经网络接收形状为 (image_height, image_width, image_channels)的输入张量(不包括批量维度)**

### 卷积

- 卷积神经网络学到的模式具有平移不变性。
- 卷积神经网络在图像右下角学到某个模式之后,它可以在任何地方识别这个模式,比如左上角。、
- 卷积神经网络可以学到模式的空间层次结构

​		**对于包含两个空间轴(高度和宽度)和一个深度轴(也叫通道轴)的 3D 张量,其卷积也叫特征图(feature map)。**

​		对于 RGB 图像,深度轴的维度大小等于 3,因为图像有 3 个颜色通道:红色、绿色和蓝色。对于黑白图像(比如 MNIST 数字图像),深度等于 1(表示灰度等级)。卷积运算从输入特征图中提取图块,并对所有这些图块应用相同的变换,生成输出特征图(outputfeature map)。该输出特征图仍是一个 3D 张量,具有宽度和高度,其深度可以任意取值,因为输出深度是层的参数,深度轴的不同通道不再像 RGB 输入那样代表特定颜色,而是代表过滤器(filter)。

卷积由以下两个关键参数所定义

- 从输入中提取的图块尺寸:这些图块的大小通常是 3×3 或 5×5。
- 输出特征图的深度:卷积所计算的过滤器的数量。

![image-20220320213546111](https://s2.loli.net/2022/03/20/Qjk5DMO6KJL3WZe.png)



> 网络中特征图的深度在逐渐增大(从 32 增大到 128),而特征图的尺寸在逐渐减小(从150×150 减小到 7×7)。这几乎是所有卷积神经网络的模式。

![preview](https://s2.loli.net/2022/03/21/jCYB3O4XLm8gxed.jpg)

### 3.使用预训练的卷积神经网络

​		使用在大数据集上已经训练好的模型

- 特征提取

​		特征提取是使用之前网络学到的表示来从新样本中提取出有趣的特征。然后将这些特征输入一个新的分类器,从头开始训练。

- 模型微调
  1. 在已经训练好的基网络(base network)上添加自定义网络
  2. 冻结基网络
  3. 训练所添加的部分
  4. 解冻基网络的一些层
  5. 联合训练解冻的这些层和添加的部分

### 小节

- **卷积神经网络**是用于计算机视觉任务的最佳机器学习模型。即使在非常小的数据集上也可以从头开始训练一个卷积神经网络,而且得到的结果还不错。
- 在小型数据集上的主要问题是过拟合。在处理图像数据时,**数据增强**是一种降低过拟合的强大方法。
- 利用特征提取,可以很容易将现有的卷积神经网络复用于新的数据集。对于小型图像数据集,这是一种很有价值的方法。
- 作为特征提取的补充,你还可以使用微调,将现有模型之前学到的一些数据表示应用于新问题。这种方法可以进一步提高模型性能。

### 卷积神经网络的可视化

### 小节

- **卷积神经网络**是解决视觉分类问题的最佳工具。
- 卷积神经网络通过学习模块化模式和概念的层次结构来表示视觉世界。
- 卷积神经网络学到的表示很容易可视化,卷积神经网络不是黑盒。
- 视觉**数据增强**来防止过拟合。
- 使用预训练的卷积神经网络进行特征提取与模型微调。
- 将卷积神经网络学到的过滤器**可视化**,也可以将类激活热力图可视化。

# Python深度学习



训练神经网络主要围绕以下四个方面。

- 层,多个层组合成网络(或模型)。
- 输入数据和相应的目标。
- 损失函数,即用于学习的反馈信号。
- 优化器,决定学习过程如何进行。

![image-20220318163548408](https://s2.loli.net/2022/03/18/j65Ap7nb92WO4Gt.png)



## Examples

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


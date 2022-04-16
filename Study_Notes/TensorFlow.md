# TensorFlow 随记



## 训练指标

- 损失函数 - 用于测量模型在训练期间的准确率。您会希望最小化此函数，以便将模型“引导”到正确的方向上。
- 优化器 - 决定模型如何根据其看到的数据和自身的损失函数进行更新。
- 指标 - 用于监控训练和测试步骤。以下示例使用了准确率，即被正确分类的图像的比率。



## 计算图

```python
# 计算图
keras.utils.plot_model(model, "my_first_model.png", show_shapes=True)
```



## 验证集

- 留出验证数据

```python
# 百分之2
model.fit(x_train, y_train, batch_size=64, validation_split=0.2, epochs=1)
```



## tf.data 数据流

```python
# tf.data 数据流
model = get_compiled_model()

# Prepare the training dataset
train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))
train_dataset = train_dataset.shuffle(buffer_size=1024).batch(64)

# Prepare the validation dataset
val_dataset = tf.data.Dataset.from_tensor_slices((x_val, y_val))
val_dataset = val_dataset.batch(64)

model.fit(train_dataset, epochs=1, validation_data=val_dataset)
```

- 从目录加载
  - 目录结构

```bash
data_dir/
├── class_a
│   ├── a_imgae_1.png
│   └── a_imgae_2.png
└── class_b
    ├── b_imgae_1.png
    └── b_imgae_2.png
```

- [image_dataset_from_directory](https://tensorflow.google.cn/api_docs/python/tf/keras/utils/image_dataset_from_directory)

```python
# 参数
tf.keras.preprocessing.image_dataset_from_directory(
    directory,
    labels="inferred", # 标签从目录结构生成
    label_mode="int", # 标签将被编码成整数 可以更改
    class_names=None,
    color_mode="rgb",
    batch_size=32, # 数据批次的大小
    image_size=(256, 256),
    shuffle=True, # 是否打乱数据
    seed=None, # 用于shuffle和转换的可选随机种子
    validation_split=None, # 保留一部分数据用于验证
    subset=None,
    interpolation="bilinear",
    follow_links=False,)

# 实例
batch_size = 32
img_height = 180
img_width = 180

# 加载训练集
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size)

# 加载验证集
val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size)

# 查看类别
class_names = train_ds.class_names
print(class_names)

# 配置数据集
AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
```


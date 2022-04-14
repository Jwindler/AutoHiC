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


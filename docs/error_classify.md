# 错误分类



## 数据集准备



- 数据类型
  - 分两类情况进行训练（1. 有错误;无错误	2.具体错误和正常类型）


| 类型 | 代码 |
| ---- | ---- |
| 全红 | e0   |
| 全白 | e1   |
| 正常 | e2   |
| 易位 | e3   |
| 反转 | e4   |

​		每种错误200-400张图片不等



- 目录结构

```sh
# dir
	error_labels.txt
	training
		training
			e0
			e1
			e2
			e3
			e4
	validation
		validation
			e0
			e1
			e2
			e3
			e4
```





## 网络构建

### EfficientNetV2

https://github.com/WZMIAOMIAO/deep-learning-for-image-processing/tree/master/pytorch_classification/Test11_efficientnetV2



num_classes

epochs

batch-size

lr

lrf

data-path

weights 预训练权重

-freeze-layers 冻结权重

device





图片推断速度 > 13 png/s

模型记录
	模型大小，参数，推断时间，内存占用

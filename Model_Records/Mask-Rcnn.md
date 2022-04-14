# Mask R-CNN

- 学习网站
  - https://blog.csdn.net/nima_zhang_b/article/details/82878771





- 特征金字塔（FPN）

![image-20220328201959116](https://s2.loli.net/2022/03/28/vkMJYHNCGrzh1Bq.png)

上下采样：线性差值 变换特征维度 使得金字塔每层的特征维度一致



- 生成获选框





- RPN

![image-20220328204239169](https://s2.loli.net/2022/03/28/43YPjIzVvZ8hqA5.png)



![image-20220328214144088](https://s2.loli.net/2022/03/28/pRtd18vPk4SoVFJ.png)



## Labelme

​		**标注数据**



- Install

```bash
# on Linux
sudo apt-get install python3-pyqt5
pip3 install labelme

# 导入环境变量
~/.bashrc
export PATH=/home/jzj/.local/bin:$PATH
source .bashrc

# 运行
labelme

# save
png > .json

# 将 json 转换为单通道的 image
labelme_json_to_dataset HiC2.json
```

- **img.png**：原始图像
- **label.png**：标签，uint8
- **label_viz.png**：可视化的带标签图像
- **label_names.txt**：记录了标签的名称

```bash
# 批处理json文件
ls *.json | while read i; do (labelme_json_to_dataset $i);done
```



- 文件处理

```bash
# 生成4个文件夹
# pic 			: 原始图片
# lableme.json  : 生成文件夹
# cv2_mask 		: 掩码图片
# json 			: json 文件
```



## Demo

- GPU 数量
- 图像处理数 （12G 显存 大概处理2张 1024x1024px）
- 类别数

```python
# Number of classes (including background)
NUM_CLASSES = 1 + 80
# 80 改为HiC 需要识别的类型总数
```

- 阈值

```python 
DETECTION_MIN_CONFIDENCE = 0.7
```



## 迁移学习

- 直接训练（收敛快）
- 冻结相关层

```python
for layers in model.layers:
    layer.trainable = False

# 冻结前100层
model.layers[:100].train = False
```



- 残差网络



![image-20220402102926970](https://s2.loli.net/2022/04/02/uNeELHfm1G6xVF5.png)



## 自训练



### 制作数据集

- 创建文件夹

```sh
mkdir png json png_modify labelme_json cv2_mask
```



- 像素转换

​		首先对自己的图片进行像素转换，全部转换为 64 的倍数，比如 1024*768 ，如果不转换为 64 倍数后续**有可能**会出错

```python
import os
import glob
from PIL import Image

# 初始图片放在 pic11文件夹下
img_path = glob.glob("./png") 

# 新建 pic 文件夹，以生成像素转换后的图片
path_save = "./png_modify" 

# 判断目录
if not os.path.exists(path_save):
    os.makedirs(path_save)

files = os.listdir(img_path[0])
# print(img_path)
for file in files:
  name = os.path.join(path_save, file)
  filename = "./png/" + file
  print(filename)
  # with Image.open(file,'rw') as im:
  im = Image.open(filename)
  # 转换倍数
  im.thumbnail((1024,768))
  print(im.format, im.size, im.mode)
  im.save(name,'png')
```



### 特征标注

​		见`labelme.md`

- **labelme_json_to_dataset**

```shell
ls ./json | while read id;do (labelme_json_to_dataset ./json/$id);done
```



- **move_file.sh**

```bash
#!/bin/bash

root_dir="./"
cv2_mask_dir="cv2_mask/"
labelme_json_dir="labelme_json/"
for i in `ls ${root_dir}${labelme_json_dir}`
do
	cp ${root_dir}${labelme_json_dir}${i}/label.png ${root_dir}${cv2_mask_dir}${i}.png 
	
```



- 数据集结果

```bash
.
├── change_pixel.py
├── cv2_mask # 最终复制出的png文件(黑色图像)
├── json # 标定的文件
├── labelme_json # 批量转换后的文件
├── png # 初始图片
└── png_modify # 更改像素后的图片
```

上传至/home/jovyan/Train_test/Mask_RCNN/datasets/hic-datasets

## 训练

见Jupyter：/home/jovyan/Train_test/Mask_RCNN/samples/hic/train.ipynb

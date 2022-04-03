# Mask R-CNN





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
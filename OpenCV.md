# OpenCV

## GUI特性

### 入门

```python
# 导入
import cv2 as cv

# 读取图像
img = cv.imread('messi5.jpg',0)

# 显示图像
cv.imshow('image',img)

# 绑定键盘时间
k = cv.waitKey(0)

if k == 27:         # 等待ESC退出
    cv.destroyAllWindows()
elif k == ord('s'): # 等待关键字，保存和退出
    cv.imwrite('messigray.png',img)
    cv.destroyAllWindows()
```

- Matplotlib

```python
import cv2 as cv
from matplotlib import pyplot as plt

img = cv.imread('./images/Gene_structure.png',0)
plt.imshow(img, cmap = 'gray', interpolation = 'bicubic')
plt.xticks([]), plt.yticks([])  # 隐藏 x 轴和 y 轴上的刻度值
plt.show()
```

### 绘图

### 鼠标时间

```python
import numpy as np
import cv2 as cv

# 鼠标回调函数
def draw_circle(event,x,y,flags,param):
    if event == cv.EVENT_LBUTTONDBLCLK:
        cv.circle(img,(x,y),100,(255,0,0),-1)
        
# 创建一个黑色的图像，一个窗口，并绑定到窗口的功能
img = np.zeros((512,512,3), np.uint8)
cv.namedWindow('image')
cv.setMouseCallback('image',draw_circle)
while(1):
    cv.imshow('image',img)
    if cv.waitKey(20) & 0xFF == 27:
        break
cv.destroyAllWindows()
```



### 轨迹栏

```python
import numpy as np
import cv2 as cv
def nothing(x):
    pass
# 创建一个黑色的图像，一个窗口
img = np.zeros((300,512,3), np.uint8)
cv.namedWindow('image')
# 创建颜色变化的轨迹栏
cv.createTrackbar('R','image',0,255,nothing)
cv.createTrackbar('G','image',0,255,nothing)
cv.createTrackbar('B','image',0,255,nothing)
# 为 ON/OFF 功能创建开关
switch = '0 : OFF \n1 : ON'
cv.createTrackbar(switch, 'image',0,1,nothing)
while(1):
    cv.imshow('image',img)
    k = cv.waitKey(1) & 0xFF
    if k == 27:
        break
    # 得到四条轨迹的当前位置
    r = cv.getTrackbarPos('R','image')
    g = cv.getTrackbarPos('G','image')
    b = cv.getTrackbarPos('B','image')
    s = cv.getTrackbarPos(switch,'image')
    if s == 0:
        img[:] = 0
    else:
        img[:] = [b,g,r]
cv.destroyAllWindows()
```



## 核心操作

### 基本操作

- 访问和修改像素值

```python
import numpy as np
import cv2 as cv

img = cv.imread("./images/hic.png")

# 通过行和列坐标来访问像素值
px = img[100,100]

# 返回一个由蓝色、绿色和红色值组成的数组
# 对于灰度图像，只返回相应的灰度
print(px)

# 修改像素值
img[100, 100] = [255, 255, 255]
print(img[100,100])

# 访问 RED 值
img.item(10, 10, 2)

# 修改 RED 值
img.itemset((10, 10, 2), 100)
img.item(10, 10, 2)
# 100
```

- 访问图像属性

​		图像属性包括**行数，列数和通道数，图像数据类型，像素数**等

```python
# 图像的形状可通过img.shape访问
# 它返回行，列和通道数的元组（如果图像是彩色的
print(img.shape)

# 像素总数
print(img.size)

# 图像数据类型
print(img.dtype)
```

- 图像感兴趣区域ROI

```python
hic = img[238:294, 237:294]
img[180:236, 237:294] = hic

cv.imshow("i", img)
cv.waitKey(0)
cv.destroyAllWindows()
```

- 拆分&合并图像通道

​		有时你需要分别处理图像的B，G，R通道。在这种情况下，你需要将BGR图像拆分为单个通道。在其他情况下，你可能需要将这些单独的频道加入BGR图片。

```python
b,g,r = cv.split(img) 
img = cv.merge((b,g,r))

b = img [:, :, 0]

# 将所有红色像素都设置为零
img[:, :, 2] = 0
```

- 设置边框
  - **src** - 输入图像
  - **top**，**bottom**，**left**，**right** 边界宽度（以相应方向上的像素数为单位）
  - **borderType** - 定义要添加哪种边框的标志。它可以是以下类型：
  - **cv.BORDER_CONSTANT** - 添加恒定的彩色边框。该值应作为下一个参数给出。
  - **cv.BORDER_REFLECT** - 边框将是边框元素的镜像，如下所示： *fedcba | abcdefgh | hgfedcb*
  - **cv.BORDER_REFLECT_101**或 **cv.BORDER_DEFAULT**与上述相同，但略有变化，例如： *gfedcb | abcdefgh | gfedcba*
  - **cv.BORDER_REPLICATE**最后一个元素被复制，像这样： *aaaaaa | abcdefgh | hhhhhhh*
  - **cv.BORDER_WRAP**难以解释，它看起来像这样： *cdefgh | abcdefgh | abcdefg*
  - **value** -边框的颜色，如果边框类型为**cv.BORDER_CONSTANT**

```python
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

BLUE = [255,0,0]
RED = [0, 255, 0]
img1 = cv.imread("./images/hic.png")
replicate = cv.copyMakeBorder(img1,10,10,10,10,cv.BORDER_REPLICATE)
reflect = cv.copyMakeBorder(img1,10,10,10,10,cv.BORDER_REFLECT)
reflect101 = cv.copyMakeBorder(img1,10,10,10,10,cv.BORDER_REFLECT_101)
wrap = cv.copyMakeBorder(img1,10,10,10,10,cv.BORDER_WRAP)
constant= cv.copyMakeBorder(img1,10,10,10,10,cv.BORDER_CONSTANT,value=BLUE)
right = cv.copyMakeBorder(img1,1,1,1,1 , cv.BORDER_CONSTANT, value=RED)
plt.subplot(231),plt.imshow(img1,'gray'),plt.title('ORIGINAL')
plt.subplot(232),plt.imshow(replicate,'gray'),plt.title('REPLICATE')
# plt.subplot(233),plt.imshow(reflect,'gray'),plt.title('REFLECT')
plt.subplot(234),plt.imshow(reflect101,'gray'),plt.title('REFLECT_101')
plt.subplot(235),plt.imshow(wrap,'gray'),plt.title('WRAP')
plt.subplot(236),plt.imshow(constant,'gray'),plt.title('CONSTANT')
plt.subplot(233),plt.imshow(constant,'gray'),plt.title('rigth')
plt.show()
```



### 算法运算

- 加法

​		通过OpenCV函数`cv.add()`或仅通过numpy操作`res = img1 + img2`添加两个图像

​		OpenCV加法和Numpy加法之间有区别。OpenCV加法是饱和运算，而Numpy加法是模运算。

```python
x = np.uint8([250])
y = np.uint8([10])
print( cv.add(x,y) ) # 250+10 = 260 => 255
# [[255]]
rint( x+y )          # 250+10 = 260 % 256 = 4
# [4]
```

- 图像融合



```python
img1 = cv.imread('./images/Gene_structure.png')
img2 = cv.imread('./images/hic.png')
dst = cv.addWeighted(img1,0.7,img2,0.3,0)
cv.imshow('dst',img1)
cv.waitKey(0)
cv.destroyAllWindows()
```

- 按位运算

​		包括按位 `AND`、 `OR`、`NOT` 和 `XOR` 操作

```python
# 加载两张图片
img1 = cv.imread('messi5.jpg')
img2 = cv.imread('opencv-logo-white.png')
# 我想把logo放在左上角，所以我创建了ROI
rows,cols,channels = img2.shape
roi = img1[0:rows, 0:cols ]
# 现在创建logo的掩码，并同时创建其相反掩码
img2gray = cv.cvtColor(img2,cv.COLOR_BGR2GRAY)
ret, mask = cv.threshold(img2gray, 10, 255, cv.THRESH_BINARY)
mask_inv = cv.bitwise_not(mask)
# 现在将ROI中logo的区域涂黑
img1_bg = cv.bitwise_and(roi,roi,mask = mask_inv)
# 仅从logo图像中提取logo区域
img2_fg = cv.bitwise_and(img2,img2,mask = mask)
# 将logo放入ROI并修改主图像
dst = cv.add(img1_bg,img2_fg)
img1[0:rows, 0:cols ] = dst
cv.imshow('res',img1)
cv.waitKey(0)
cv.destroyAllWindows()
```



### 性能衡量和提升技术

- 使用OpenCV衡量性能

​		**cv.getTickCount**函数返回从参考事件（如打开机器的那一刻）到调用此函数那一刻之间的时钟周期数。因此，如果在函数执行之前和之后调用它，则会获得用于执行函数的时钟周期数。

​		**cv.getTickFrequency**函数返回时钟周期的频率或每秒的时钟周期数

```python
e1 = cv.getTickCount()
# 你的执行代码
e2 = cv.getTickCount()
time = (e2 - e1)/ cv.getTickFrequency()
```

- 默认优化

```python
# 检查是否启用了优化
cv.useOptimized()
```


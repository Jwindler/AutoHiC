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



## 图像处理

### 改变颜色空间

- 颜色转换，使用cv函数。

​		cvtColor(input_image, flag)，其中flag决定转换的类型。

对于BGR→灰度转换，我们使用标志cv.COLOR_BGR2GRAY。类似地，对于BGR→HSV，我们使用标志cv.COLOR_BGR2HSV。

```python
import cv2 as cv
img1 = cv.imread('./images/hic.png')

# 灰度转换
img2 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)

# 列出使用标志
[i for i in dir(cv) if i.startswith('COLOR_')]
```

- 对象追踪

```python
# 提取HiC中的红色

# 读取原始图片
frame = cv.imread("./images/hic.png")

# 转换颜色空间 BGR 到 HSV
hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

# 定义HSV中蓝色的范围
lower_blue = np.array([156, 50, 50])
upper_blue = np.array([180, 255, 255])

# 设置HSV的阈值使得只取蓝色
mask = cv.inRange(hsv, lower_blue, upper_blue)

# 将掩膜和图像逐像素相加
res = cv.bitwise_and(frame, frame, mask=mask)

# 展示图片
cv.imshow('frame', frame)
cv.imshow('mask', mask)
cv.imshow('res', res)
cv.waitKey(0)
cv.destroyAllWindows()
```

- HSV值查询

```python
# 颜色对应的BGR值
red = np.uint8([[[255, 0, 0]]])

# 转变为HSV值
hsv_red = cv.cvtColor(red, cv.COLOR_BGR2HSV)
print(hsv_red)
```



### 图像几何变换

- 变换

​		OpenCV提供了两个转换函数**cv.warpAffine**和**cv.warpPerspective**，您可以使用它们进行各种转换。**cv.warpAffine**采用2x3转换矩阵，而**cv.warpPerspective**采用3x3转换矩阵作为输入。

- 缩放

​		缩放只是调整图像的大小。为此，OpenCV带有一个函数**cv.resize()**。图像的大小可以手动指定，也可以指定缩放比例。也可使用不同的插值方法。首选的插值方法是cv.INTER_AREA用于缩小，cv.INTER_CUBIC（慢）和cv.INTER_LINEAR用于缩放。默认情况下，出于所有调整大小的目的，使用的插值方法为cv.INTER_LINEAR。

```python
img = cv.imread("./images/hic.png")

res = cv.resize(img,None,fx=2, fy=2, interpolation = cv.INTER_CUBIC)
# height, width = img.shape[:2]
# res = cv.resize(img,(2*width, 2*height), interpolation = cv.INTER_CUBIC)

cv.imshow("test",res)
cv.waitKey(0)
```

- 平移

![image-20220317104014951](https://s2.loli.net/2022/03/17/5FWkbOshr8qgCpM.png)

```python
# 将其放入np.float32类型的Numpy数组中，并将其传递给cv.warpAffine函数
# 参见下面偏移为(100, 50)的示例

img = cv.imread("./images/hic.png", 0)
rows,cols = img.shape

M = np.float32([[1,0,100],[0,1,50]])

# 第三个参数是输出图像的大小，其形式应为(width，height)
# 记住width =列数，height =行数
dst = cv.warpAffine(img,M,(cols,rows))
cv.imshow('img',dst)
cv.waitKey(0)
cv.destroyAllWindows()
```

- 旋转

![image-20220317104313969](https://s2.loli.net/2022/03/17/cQV8vazLiNAbZuT.png)

```python
# 将图像相对于中心旋转90度而没有任何缩放比例
img = cv.imread("./images/hic.png", 0)
rows,cols = img.shape

# cols-1 和 rows-1 是坐标限制
# 获取旋转矩阵
M = cv.getRotationMatrix2D(((cols-1)/2.0,(rows-1)/2.0),90,1)
# 进行旋转
dst = cv.warpAffine(img,M,(cols,rows))

cv.imshow('img',dst)
cv.waitKey(0)
cv.destroyAllWindows()
```

- 仿射变换

​		在仿射变换中，原始图像中的所有平行线在输出图像中仍将平行。为了找到变换矩阵，我们需要输入图像中的三个点及其在输出图像中的对应位置。然后**cv.getAffineTransform**将创建一个2x3矩阵，该矩阵将传递给**cv.warpAffine**。

![image-20220317105411329](https://s2.loli.net/2022/03/17/CFDAhqK8Te4slPx.png)

```python
img = cv.imread("./images/hic.png", 0)
rows, cols = img.shape

pts1 = np.float32([[50, 50], [200, 50], [50, 200]])
pts2 = np.float32([[10, 100], [200, 50], [100, 250]])

M = cv.getAffineTransform(pts1, pts2)

dst = cv.warpAffine(img, M, (cols, rows))
plt.subplot(121), plt.imshow(img), plt.title('Input')
plt.subplot(122), plt.imshow(dst), plt.title('Output')
plt.show()
```

![image-20220317105842341](https://s2.loli.net/2022/03/17/apDoeHmY4r2cn1O.png)

- 投射变换

​		对于透视变换，您需要3x3变换矩阵。即使在转换后，直线也将保持直线。要找到此变换矩阵，您需要在输入图像上有4个点，在输出图像上需要相应的点。在这四个点中，其中三个不应共线。然后可以通过函数**cv.getPerspectiveTransform**找到变换矩阵。然后将**cv.warpPerspective**应用于此3x3转换矩阵。

```python
pts1 = np.float32([[56,65],[368,52],[28,387],[389,390]])
pts2 = np.float32([[0,0],[300,0],[0,300],[300,300]])
M = cv.getPerspectiveTransform(pts1,pts2)
dst = cv.warpPerspective(img,M,(300,300))
plt.subplot(121),plt.imshow(img),plt.title('Input')
plt.subplot(122),plt.imshow(dst),plt.title('Output')
plt.show()
```

![image-20220317105823790](https://s2.loli.net/2022/03/17/hJTjpB1He4DtlIO.png)

### 图像阈值

比较不同的图像阈值处理

```python

import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
img = cv.imread('./images/hic.png', 0)
ret, thresh1 = cv.threshold(img, 127, 255, cv.THRESH_BINARY)
ret, thresh2 = cv.threshold(img, 127, 255, cv.THRESH_BINARY_INV)
ret, thresh3 = cv.threshold(img, 127, 255, cv.THRESH_TRUNC)
ret, thresh4 = cv.threshold(img, 127, 255, cv.THRESH_TOZERO)
ret, thresh5 = cv.threshold(img, 127, 255, cv.THRESH_TOZERO_INV)
titles = [
    'Original Image',
    'BINARY',
    'BINARY_INV',
    'TRUNC',
    'TOZERO',
    'TOZERO_INV']
images = [img, thresh1, thresh2, thresh3, thresh4, thresh5]
for i in range(6):
    plt.subplot(2, 3, i + 1), plt.imshow(images[i], 'gray')
    plt.title(titles[i])
    plt.xticks([]), plt.yticks([])
plt.show()
```

- 自适应阈值

自动选择周围的阈值进行处理

- Otsu的二值化



### 图像平滑

- 2D卷积（图像过滤）

```python
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
img = cv.imread('./images/hic.png', 0)
kernel = np.ones((5,5),np.float32)/25
dst = cv.filter2D(img,-1,kernel)
plt.subplot(121),plt.imshow(img),plt.title('Original')
plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(dst),plt.title('Averaging')
plt.xticks([]), plt.yticks([])
plt.show()
```

![image-20220318224053231](https://s2.loli.net/2022/03/18/FuqQaehUlH7Ntcp.png)







- 图像模糊（图像平滑）

- 通过将图像与低通滤波器内核进行卷积来实现图像模糊，对于消除噪音很有用

  - 平均

    ```python
    import cv2 as cv
    import numpy as np
    from matplotlib import pyplot as plt
    img = cv.imread('./images/hic.png', 0)
    blur = cv.bilateralFilter(img,9,75,75)
    plt.subplot(121),plt.imshow(img),plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(blur),plt.title('Blurred')
    plt.xticks([]), plt.yticks([])
    plt.show()
    ```

  - 高斯模糊

    ```python
    blur = cv.GaussianBlur(img,(5,5),0)
    ```

  - 中位模糊

    ```python
    median = cv.medianBlur(img,5)
    ```

  - 双边模糊

    ```python
    blur = cv.bilateralFilter(img,9,75,75)
    ```




### 形态转换

- 侵蚀

​		有助于去除小的白色噪声(正如我们在颜色空间章节中看到的)，分离两个连接的对象等。

```python
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
img = cv.imread('./images/hic.png', 0)
kernel = np.ones((5,5),np.uint8)
erosion = cv.erode(img,kernel,iterations = 1)
plt.subplot(121), plt.imshow(img), plt.title('ORIGINAL')
plt.subplot(122), plt.imshow(erosion), plt.title('erosion')
plt.show()
```

![image-20220321110419971](https://s2.loli.net/2022/03/21/joiUHd4wXEkVbIQ.png)

- 扩张

​		增加图像中的白色区域或增加前景对象的大小,在连接对象的损坏部分时也很有用。

```python
dilation = cv.dilate(img,kernel,iterations = 1)
```

![image-20220321110509728](https://s2.loli.net/2022/03/21/OoIQaAB7K4khxyR.png)

- 开运算

​		侵蚀然后扩张,对于消除噪音很有用

```python
opening = cv.morphologyEx(img, cv.MORPH_OPEN, kernel) 
```

- 闭运算

​		先扩张然后再侵蚀，在关闭前景对象内部的小孔或对象上的小黑点时很有用。

```python
closing = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel) 
```

- 形态学梯度

```python
gradient = cv.morphologyEx(img, cv.MORPH_GRADIENT, kernel) 
```

- 顶帽

​		输入图像和图像开运算之差

```python
tophat = cv.morphologyEx(img, cv.MORPH_TOPHAT, kernel) 
```

- 黑帽

​		输入图像和图像闭运算之差

```python
blackhat = cv.morphologyEx(img, cv.MORPH_BLACKHAT, kernel) 
```



### 图像梯度

滤波器

### Canny边缘检测

### 图像金字塔

### 轮廓



## 5.特征检测与描述


























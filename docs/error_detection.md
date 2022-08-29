# 错误检测



## 模型

- COCO 数据集80个类的名称 https://blog.csdn.net/weixin_41466947/article/details/98783700



## 预测框

- Inference_detector > `result = inference_detector(model, img)`

返回的结果：

​    result: 存储模型识别信息

result**详解**：

​    result 的大小，与模型的输出类别有关。

​    例：识别两种类别 ① normal ② abnormal

​    则result里的内容为：

​    <class 'list'>: [array([])], array([])]   #为了便于理解，这里array里内容进行了省略。

​    其中每一个array 与类别相对应。第一个array 对应 normal 第二个 array  对应 abnormal

​    array中则存储位置和得分信息。array[[x,y,w,h,score],[]] 

​    其中array里每一个[]都代表识别到了该种类型。[]包含5个参数，前四个参数代表位置信息，最后一个参数代表检测得分。



![image-20220606215820643](https://s2.loli.net/2022/06/06/fyWw9tcaHdSANso.png)

x：表示预测框**左上角**的x坐标信息；

y：表示预测框左上角的y坐标信息；

w：表示预测框的宽度信息；（减去x）

h：表示预测框的高度信息 ；（减去y）

score： 代表检测得分 。
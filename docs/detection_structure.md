# 推理数据结构

`mmdet.apis.inference_detector` 模型推理后返回数据的数据结构



```sh
result: tuple
	0: list
		0: numpy.ndarray
			[[463.81464   336.5313    873.45123   743.7297      0.9807947]]
		1: ndarray
		2: ndarray
		3: ndarray
	1: list
```



## *bbox

x：表示预测框**左上角**的`x`坐标信息；

y：表示预测框**左上角**的`y`坐标信息；

w：表示预测框的宽度信息；（减去x）

h：表示预测框的高度信息 ；（减去y）

score： 代表检测得分 。



## 0

`result[0]`：存储自己标注的类别的检测结果，按照配置文件中的顺序

结果是一个二维的`numpy.ndarray` （仅限结果长度为1）

```sh
# 降维
# test = result[0][1].flatten()  弃用
test = test.tolist()  # 仅需转为list存储
```





## 1

wait for explore



## *error_dict

```sh
error_dict: tuple
    info: dict
        "info_file": str
        "errors": errors
        
    errors: dict
        chrs: List
            id: int
            image_id: str
            bbox: List
            score: int
        invs: List
        trans: List
        debris: List



```






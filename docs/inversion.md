# INVERSIONS

​		反转错误调整记录

![image-20220906095559071](https://swindler-typora.oss-cn-chengdu.aliyuncs.com/typora_imgs/image-20220906095559071.png)

> **500 < 反转检测分辨率 < 50000（含）以下**



## 数据生成

​		利用反转asy中的ctgs，生成了一批反转数据，仅有70张左右可用的数据，太少，需要增加数据集。存在的问题：需要调整分辨率（图像的color 或者是图像的分辨率），还有就是生成图像的长宽。



- 9.6
  - 目前已经将 Np Hv Ls 三个数据中的所有ctgs全部反转，用于生成反转数据





## 模型训练

### 数据标注

1. 首先利用分类模型，将全部分类，去除无互作的数据，再人工挑选

2. 利用labelme进行反转标注

3. labelme2coco

   

## inv_ctg

​		根据错误检测模型返回的易位区间，对asy进行调整

### 代码逻辑



### 参数设计







## 功能测试

- 两个测试用例

> random_Np/Np.final.hic
>
> random_Np/Np.final.assembly
>
> 268689492 - 274981071  utg563
>
> 280560061 - 284239273  utg487



- 原图

![](https://swindler-typora.oss-cn-chengdu.aliyuncs.com/typora_imgs/image-20220920094219320.png)



- 检测结果

![image-20220920094349636](https://swindler-typora.oss-cn-chengdu.aliyuncs.com/typora_imgs/image-20220920094349636.png)



- 修改结果


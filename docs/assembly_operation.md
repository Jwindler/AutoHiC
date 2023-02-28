# Assembly

​		处理`.assembly`脚本，涉及多种情况： 一个contig内， 包含两个contig

- 4个类别，两种情况

![image-20220523172101669](https://s2.loli.net/2022/05/23/Mavhw3YuCs6QUWI.png)



上面两种属于一类，无需特殊处理

下面两种，需要特殊处理，方法见code





## Situations



### Misjoins

![image-20220607095946211](https://s2.loli.net/2022/06/07/M6AISctkupmQ1lO.png)



需要对Contig进行剪切



### Translocations

![image-20220607100156248](https://s2.loli.net/2022/06/07/i6bfCNHnOkLg9jd.png)



对易位进行位置调整

- 如何确定需要目地位置





### Inversions

![image-20220607100210650](https://s2.loli.net/2022/06/07/HXtypVxKgjzPk32.png)



对颠倒位置进行翻转





### Chr Boundarys

![image-20220607100306054](https://s2.loli.net/2022/06/07/S6hfjEsIqx4uAFd.png)



对染色体边界进行划分





## Scripts

### Translocation Adjust

​		易位调整



### Debris Shear

​		空白片段剪切，并移动到末尾



## Cut ctgs

2022.10.5	考虑二次切割ctg，新增情况



- 流程

1. 判断是否已经切割过

​		条件：ctg_name中包含fragment





## 切割

​	查看分辨率，是否会将序列文件减少长度

​	在不同分辨率下，切一个ctg，查看是否会减少基因组长度

```sh
/home/jzj/Auto-HiC/Test/Np-Self
	Np.0.assembly
	Np.0.review.assembly
```



| File                                                         | 长度          |
| ------------------------------------------------------------ | ------------- |
| 原始Np.fa                                                    | 2,291,903,782 |
|                                                              |               |
| Np_HiC.fasta (Np.Final.fasta)                                | 2,293,182,782 |
| Np.rawchrom.fasta (Np.final.fasta) 与上面的区别就是，上面将ctgs合并为chr了 | 2,291,903,782 |
|                                                              |               |
| cut_with_gap: Np_HiC.fasta (Np.Final.fasta)                  | 2,292,962,282 |
|                                                              |               |
| cut_not_gap: Np_HiC.fasta (Np.Final.fasta)                   | 2,292,962,282 |
|                                                              |               |
| translocation_no_debris(Np.Final.fasta)  自己代码实现        | 2,292,962,282 |
| translocation_with_debris(Np.Final.fasta)  juicebox 操作下   | 2,292,962,282 |



- assembly文件最后的gap 会出现在最后的fasta文件中，以`N`的形式出现。
- 在不同分辨率下切割产生的debris 会出现在最后的序列文件中, 会被切除



> 再特定分辨率进行切割操作，会产生debris，自动移动到最后一行，会对原始数据造成影响。



## 反转

​		反转对于`assembly`文件的改变

![image-20220815215031685](https://s2.loli.net/2022/08/15/oUBbxjGWqmHkwaV.png)



> 反转区域内所包含的ctgs 全部倒序，并且符号取反



### 正

![image-20220829170238457](https://swindler-typora.oss-cn-chengdu.aliyuncs.com/typora_imgs/image-20220829170238457.png)



![image-20220829170651626](https://swindler-typora.oss-cn-chengdu.aliyuncs.com/typora_imgs/image-20220829170651626.png)



​		仅改变正负号



### 负

utg183 ： -4



![image-20220829170606368](https://swindler-typora.oss-cn-chengdu.aliyuncs.com/typora_imgs/image-20220829170606368.png)



​		仅改变正负号

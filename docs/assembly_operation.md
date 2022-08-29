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

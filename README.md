# Auto-HiC

![](https://img.shields.io/badge/release-v0.8.18-blue)![a](https://img.shields.io/badge/license-MIT-brightgreen)




![image-20221027210512819](https://swindler-typora.oss-cn-chengdu.aliyuncs.com/typora_imgs/image-20221027210512819.png)



## Overview





## Citations

If you use this pipline, please cite the following paper:



## Workflow





## Usages

### Install

```sh
git clone https://github.com/Jwindler/AutoHiC.git
```



- conda

```sh
conda create -n autohic python=3.8 -y

conda activate autohic

# CPU
conda install pytorch torchvision cpuonly -c pytorch -y

# GPU
conda install pytorch torchvision -c pytorch -y

cd ./src/model

pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple/
```



### config

- SETTING THE CONFIGURATION FILE

```sh
# 参考
http://nservant.github.io/HiC-Pro/MANUAL.html#setting-the-configuration-file
```



### run

```sh
python autohic.py cft-autohic.txt
```





### results

```sh
# 参考
https://github.com/aidenlab/3d-dna
```







## Contact

**Please free to open an issue, when you encounter any problems.**





## LICENSE

**This software is distributed under The MIT License (MIT).**


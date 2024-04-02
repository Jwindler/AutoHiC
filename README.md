# AutoHiC

![GitHub release (with filter)](https://img.shields.io/github/v/release/Jwindler/AutoHiC)  ![a](https://img.shields.io/badge/license-MIT-brightgreen)  ![Docker Pulls](https://img.shields.io/docker/pulls/jwindler/autohic)  [![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://hub.docker.com/r/jwindler/autohic)  [![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://github.com/Jwindler/AutoHiC/tree/main/example/singularity_autohic.md)



Author: Zijie Jiang

Email: jzjlab@163.com



## Content

- [AutoHiC](#autohic)
  - [Content](#content)
  - [Notes](#notes)
  - [Introduction](#introduction)
  - [Overview of AutoHiC](#overview-of-autohic)
  - [Citations](#citations)
  - [Installation](#installation)
    - [conda](#conda)
    - [Docker](#docker)
    - [Singularity](#singularity)
    - [Pre-trained model download](#pre-trained-model-download)
  - [Usages](#usages)
    - [Data Preparation](#data-preparation)
    - [Configs](#configs)
    - [Run](#run)
    - [Results](#results)
  - [Example](#example)
    - [data](#data)
    - [run](#run-1)
    - [result](#result)
  - [Plot HiC interaction map](#plot-hic-interaction-map)
  - [One Setp AutoHiC (optional)](#one-setp-autohic-optional)
    - [example](#example-1)
  - [Split chromosome (optional)](#split-chromosome-optional)
  - [License](#license)






## Notes

- **Currently AutoHiC has integrated `3d-dna` into the complete process. If you are using `YaHS`, `SALSA`, `Pin_hic` etc, please read this document: [Other tools](https://github.com/Jwindler/AutoHiC/tree/main/example/other_tools.md)**
- **Currently, AutoHiC updates very fast. If you have already cloned `AutoHiC`, please delete the `AutoHiC` folder and clone it again.**
- **Please feel free to [open an issue](https://github.com/Jwindler/AutoHiC/issues) if you encounter any problems. This is very important to help us improve AutoHiC. If you have any questions, you can also email `jzjlab@163.com` to get help.**

​    


## Introduction

 `AutoHiC` is a deep learning tool that uses Hi-C data to support genome assembly. It can automatically correct errors during genome assembly and generate genomes at the chromosome level.

​            

## Overview of AutoHiC

  ![](https://s2.loli.net/2023/08/01/jT5FIS4cXyDfEmB.png)

​       

 

## Citations

**If you used AutoHiC in your research, please cite us:**

```sh
AutoHiC: a deep-learning method for automatic and accurate chromosome-level genome assembly
Zijie Jiang, Zhixiang Peng, Yongjiang Luo, Lingzi Bie, Yi Wang

bioRxiv 2023.08.27.555031; doi: https://doi.org/10.1101/2023.08.27.555031
```





## Installation



### conda

```sh
# clone AutoHiC
git clone https://github.com/Jwindler/AutoHiC.git

# cd AutoHiC
cd AutoHiC

# create AutoHiC env
conda env create -f autohic.yaml

# activate AutoHiC
conda activate autohic

# configuration environment
cd ./src/models/swin

# install dependencies
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

> Note: 
>
> 1.   If `src/straw.cpp:34:10: fatal error: curl/curl.h: No such file or directory` is encountered during installation, enter the following command `sudo apt-get install libcurl-dev libcurl4-openssl-dev libssl-dev` in the terminal or refer: `https://stackoverflow.com/questions/11471690/curl-h-no-such-file-or-directory`.
>
> 2.   Either GPU or CPU can be installed according to the above steps, and the program will automatically identify the running configuration and environment.  
>
> 3.   If you want to use GPU, please install [CUDA-11.3](https://developer.nvidia.com/cuda-11.3.0-download-archive) and [cuDNN-8.2](https://developer.nvidia.com/rdp/cudnn-archive) before.

​    



### Docker

```sh
# pull images
sudo docker pull jwindler/autohic:main

# start container
sudo docker run -it -v $(pwd):/home/autohic jwindler/autohic:main bash

# You need to use mounts (-v) to exchange files between the host filesystem on which your user can write and the container filesystem. ( Default "./" )

# clone AutoHiC
git clone https://github.com/Jwindler/AutoHiC.git

# cd AutoHiC
cd AutoHiC

# activate AutoHiC
conda activate autohic

# configuration environment
cd ./src/models/swin

# install dependencies
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple/
```



### Singularity

Considering that many users run AutoHiC on HPC, the build dependency environment may not be very free, and Docker has root restrictions, we provide a singularity version.  Detailed documentation: [doc](https://github.com/Jwindler/AutoHiC/blob/main/example/singularity_autohic.md#autohic-singularity-version)

  

### Pre-trained model download

**Please select your most convenient download link below, You need to download `error_model.pth`,  `chr_model.pth` , `Juicer` and `3d-dna` for the configuration of subsequent configuration files**

| Google Drive (recommend)                                                                                  | Baidu Netdisk (百度网盘)                                                      | Quark (夸克)                                             |
| --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------- |
| [Pre-trained model](https://drive.google.com/drive/folders/1T9twnImt1CK_NrB9SBb-dg4dBENyhPTN?usp=sharing) | [Pre-trained model](https://pan.baidu.com/s/1CturvBMowVMwpeKYKjsa9w?pwd=v4et) | [Pre-trained model](https://pan.quark.cn/s/709f9e5e005b) |

​    

## Usages

### Data Preparation

- Contig level genome
- Hi-C reads
- directory structure (as below)

```sh
species_name/
├── rawdata
│   └── fastq
│       ├── SRR_X_R1.fastq.gz
│       ├── SRR_X_R2.fastq.gz
└── references
    └── contig.fasta
```

![](https://s2.loli.net/2023/06/12/aZ6ulMrwqcjkXE8.png)

> Notes:
>
> 1. **The directory structure must be consistent with the above image.**
> 2. **Paired-end sequences must end with `X_R1.fastq.gz` and `X_R2.fastq.gz`**  ( also supports uncompressed formats such as : `X_R1.fastq` and `X_R2.fastq` )  

​             

### Configs

Copy and edit the configuration file `cft-autohic.txt` in your local folder. 

`cft-autohic.txt` example files are available in the AutoHiC directory

- Setting the configuration file

| options                | value                                                        |
| :--------------------- | ------------------------------------------------------------ |
| JOB_NAME               | Name of the job                                              |
| AutoHiC_DIR            | Path to AutoHiC  *eg:  /path_to/AutoHiC*                     |
| RESULT_DIR             | Path to AutoHiC result                                       |
| N_CPU                  | Number of CPU allows per job   *Default: 10*                 |
|                        |                                                              |
|                        |                                                              |
| SPECIES_NAME           | Name of the species                                          |
| REFERENCE_GENOME       | Path to reference genome                                     |
|                        |                                                              |
| JUICER_DIR             | Path to Juicer                                               |
| FASTQ_DIR              | Path to HiC reads (Just path to the `rawdata` directory, not fastq folder) |
| ENZYME                 | Restriction enzyme  *eg:  "HindIII" or "MboI"*               |
|                        |                                                              |
| TD_DNA_DIR             | Path to 3d-dna                                               |
| NUMBER_OF_EDIT_ROUNDS  | Specifies number of iterative rounds for misjoin correction   *Default: 2* **Modification is not recommended.** |
|                        |                                                              |
|                        |                                                              |
| ERROR_PRETRAINED_MODEL | Path to error pretrained model  *eg: /path/AutoHiC/src/models/cfgs/error_model.pth* |
| CHR_PRETRAINED_MODEL   | Path to chromosome pretrained model  *eg: /path/AutoHiC/src/models/cfgs/chr_model.pth* |
|                        |                                                              |
| TRANSLOCATION_ADJUST   | Whether to adjust for translocation errors  *Default: True*  |
| INVERSION_ADJUST       | Whether to adjust for inversion errors  *Default: True*      |
| DEBRIS_ADJUST          | Whether to adjust for debris *Default: False*                |
| ERROR_MIN_LEN          | Minimum error length  *Default: 15000*                       |
| ERROR_MAX_LEN          | Maximum error length *Default: 20000000*                     |
| ERROR_FILTER_IOU_SCORE | Overlapping error filtering threshold  *Default: 0.8* **Modification is not recommended.** |
| ERROR_FILTER_SCORE     | Error filtering threshold  *Default: 0.9* **Modification is not recommended.** |



> Notes: 
>
> 1. `PRETRAINED_MODEL` and `CHR_PRETRAINED_MODEL` parameters come from the download path of your pre-trained model before and after               
> 2. `JUICER_DIR` and `TD_DNA_DIR` parameters come from the path you downloaded and decompressed respectively (If you have already installed it in advance, you can configure it directly)

​         

### Run

```sh
# cd AutoHiC directory
# Please modify according to your installation directory
cd /home/AutoHiC  

# run 
nohup python3.9 autohic.py -c cfg-autohic.txt > log.txt 2>&1 &

# nohup: Run the program ignoring pending signals
```

> Notes:  
>
> 1. **Please specify the absolute path of the `cft-autohic.txt`**
> 2. **It is recommended to specify a directory for the `log.txt`, It will record the running information of AutoHiC**
> 3. **Delete the nohup command if you don't want the program to run in the background.**  
> 3. **If you modify the configuration file and re-run AutoHiC, you must manually delete the previously generated result file.**
> 3. If a **warning** (like the image below) appears in the log while you are using it, this is normal and the program is running normally. You just have to wait for the results.

  ![](https://s2.loli.net/2023/11/01/ytS26NTRe1l9JdL.png)

​      

 

### Results

After the AutoHiC operation is completed, the following results will be obtained. 

```sh
species_name/
├── AutoHiC
│   ├── autohic_results
│   │   ├── 0
│   │   ├── 1
│   │   ├── 2
│   │   ├── 3
│   │   ├── 4
│   │   └── chromosome
│   ├── data
│   │   ├── reference
│   │   └── restriction_sites
│   ├── hic_results
│   │   ├── 3d-dna
│   │   └── juicer
│   ├── logs
│   │   ├── 3d-dna.log
│   │   ├── 3_epoch.log
│   │   ├── 4_epoch.log
│   │   ├── bwa_index.log
│   │   ├── chromosome_epoch.log
│   │   └── juicer.log
│   ├── quast_output
│   │   ├── chromosome
│   │   └── contig
│   ├── chromosome_autohic.fasta 
│   └── result.html
├── cfg-autohic.txt
```

**The main output:**

1. fasta file with a "`_autohic`" suffix containing the output scaffolds at the chromosome level.

2. The `result.html` file, which provides detailed information before and after genome correction, where the error occurred, and a heat map of HiC interaction and chromosome length before and after. 

3. Please see this [document](https://github.com/Jwindler/AutoHiC/tree/main/example/detail_result.md "Docs") for detailed results description.    

   

  

## Example 

**If you want to run AutoHiC with sample data, you can choose from the following data.**



### data

Please follow the link provided for the selected species to download the appropriate data and organize it into the required format, can refer to : [Data Preparation](#data-preparation).

| Species                    | Reference genome                                                                      | Hi-C Data                                                                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| *Halictus ligatus*         | [hl.fa](https://drive.google.com/drive/folders/1KDp1FPzC2cxOSirfJpX7yu0oPklexawg)     | [SRR14251351](https://www.ebi.ac.uk/ena/browser/view/SRR14251351)                                                                |
| *Lasioglossum leucozonium* | [ll.fa](https://drive.google.com/drive/folders/1KDp1FPzC2cxOSirfJpX7yu0oPklexawg)     | [SRR14251345](https://www.ebi.ac.uk/ena/browser/view/SRR14251345)                                                                |
| *Schistosoma haematobium*  | [sh.fa](https://drive.google.com/drive/folders/1KDp1FPzC2cxOSirfJpX7yu0oPklexawg)     | [SRR16086854](https://www.ebi.ac.uk/ena/browser/view/SRR16086854)                                                                |
| *Arachis hypogaea*         | [peanut.fa](https://drive.google.com/drive/folders/1KDp1FPzC2cxOSirfJpX7yu0oPklexawg) | [SRR6796709](https://www.ebi.ac.uk/ena/browser/view/SRR6796709); [SRR6832914](https://www.ebi.ac.uk/ena/browser/view/SRR6832914) |

- Reference genome : Sample genome files are available at the `example_genome` file in the pre-trained model download link : [Pre-trained model download](#pre-trained-model-download)
- The default enzyme used for example data is `DpnII`



### run

```sh
cd AutoHiC

nohup python3.9 autohic.py -c cfg-autohic.txt > log.txt 2>&1 &

```

- Please modify the `cfg-autohic.txt` file according to the actual situation, can refer to : [Configs](#configs).



### result

**The main results of AutoHiC are genome and assembly reports at the chromosome level. For a detailed description of the results, please refer to [Results](#results). At the same time, we also upload the assembly report to [Google Drive](https://drive.google.com/drive/folders/1G69pMYtFEmYTUZ6l1q6RgbaJYgj59Mxe) for users to retrieve and view.**

​                       



## Plot HiC interaction map

AutoHiC also provides a script to visualise the HiC interaction matrix separately.

![](https://s2.loli.net/2023/06/13/Brc8zdFhX2ZOUf5.png)

  

```sh
python3.9 visualizer.py -hic example.hic
```

**For detailed commands, please refer to the help documentation (`--help`)**  

   

  

- result

![](https://s2.loli.net/2023/06/13/FKNaZkiCTh9rdfV.png)







## One Setp AutoHiC (optional) 

**If you have already run `Juicer` and `3d-dna`, you can use the following extended script to use `AutoHiC` to help you detect HiC assembly errors and generate adjusted `assembly` files.**

![](https://s2.loli.net/2023/09/20/dgI9O68HeSLXBkN.png)



```sh
# Enter the AutoHiC directory.
cd /home/ubuntu/AutoHic  

# run onehic
python3.9 onehic.py -hic test.hic -asy test.assembly -autohic /home/ubuntu/AutoHic -p pretrained.pth -out ./

# run 3d-dna to get fasta
bash run-asm-pipeline-post-review.sh -r adjusted.assembly genome.fasta merged_nodups.txt 

# Please specify the absolute path of each file
# adjusted.assembly is output from onehic.py
# merged_nodups.txt is output from Juicer
```

> Notes:
>
> 1. `.hic` and `.assembly` : can be obtained from 3d-dna results
> 2. `-autohic` : the parameter represents the path of AutoHiC
> 3. `-p`: the path to the **error pretrained model** you downloaded before  



### example

**If you want to run `onehic.py` with example data, please get the corresponding data from the previously linked [Pre-trained model download](#pre-trained-model-download) `example_onehic` file.**

| Species                 | Hi-C File                                                                                     | Assembly File                                                                                      |
| ----------------------- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| *Mastacembelus armatus* | [Mastacembelus.hic](https://drive.google.com/drive/folders/1y-xbFTYy5gUTCiJKrEvhNEf8oMpRRtDk) | [Mastacembelus.assembly](https://drive.google.com/drive/folders/1y-xbFTYy5gUTCiJKrEvhNEf8oMpRRtDk) |
| *Arachis hypogaea*      | [peanut.hic](https://drive.google.com/drive/folders/1y-xbFTYy5gUTCiJKrEvhNEf8oMpRRtDk)        | [peanut.assembly](https://drive.google.com/drive/folders/1y-xbFTYy5gUTCiJKrEvhNEf8oMpRRtDk)        |



​                     

## Split chromosome (optional) 

If your genome is very complex, the model may not be very accurate in dividing the chromosomes. It is recommended that you import the last adjustment file into Juicxbox to manually split chromosomes.

**The `.hic` and `.assembly` files you need to use can be obtained from the `chromosome` folder under the `autohic_results` directory.**  

 

​    

## License

**AutoHiC Copyright (c) 2022 Wang lab. All rights reserved.**

This software is distributed under the `MIT License` (MIT).  

  

  

# AutoHiC

![](https://img.shields.io/badge/release-v0.9.0-blue)![a](https://img.shields.io/badge/license-MIT-brightgreen)


![image-20221027210512819](https://swindler-typora.oss-cn-chengdu.aliyuncs.com/typora_imgs/image-20221027210512819.png)



## Introduction





## Overview of AutoHiC





## Citations

**If you use this pipline, please cite the following paper:**





## Installation

- conda

```sh
# clone AutoHiC
git clone https://github.com/Jwindler/AutoHiC.git

# create AutoHiC env
conda env create -f autohic.yaml

# activate AutoHiC
conda activate autohic

# configuration environment
cd ./src/models/swin

# install dependencies
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

> Note: Either GPU or CPU can be installed according to the above steps, and the program will automatically identify the running configuration and environment.



### Pre-trained model download

**Please select your most convenient download link below**

- Google Drive (recommend)





- Baidu Netdisk





- 夸克





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

> Example: Arabidopsis thaliana 

![image-20230612213432460](https://s2.loli.net/2023/06/12/aZ6ulMrwqcjkXE8.png)

> Notes:
>
> 1. **The directory structure must be consistent with the above image.**
> 2. **Paired-end sequences must end with `X_R1.fastq.gz` and `X_R2.fastq.gz`**



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
| GENOME_NAME            | Name of the genome                                           |
| SPECIES_NAME           | Name of the species                                          |
| REFERENCE_GENOME       | Path to reference genome                                     |
|                        |                                                              |
| JUICER_DIR             | Path to Juicer                                               |
| FASTQ_DIR              | Path to HiC reads                                            |
| ENZYME                 | Restriction enzyme  *eg:  "HindIII" or "MboI"*               |
|                        |                                                              |
| TD_DNA_DIR             | Path to 3d-dna                                               |
| NUMBER_OF_EDIT_ROUNDS  | Specifies number of iterative rounds for misjoin correction   *Default: 2* |
|                        |                                                              |
| MODEL_CFG              | Path to error model config  *eg: /path/AutoHiC/src/models/cfgs/error_model.py* |
| PRETRAINED_MODEL       | Path to error pretrained model  *eg: /path/AutoHiC/src/models/cfgs/error_model.pth* |
| CHR_MODEL_CFG          | Path to chromosome model config  *eg: /path/AutoHiC/src/models/cfgs/chr_model.py* |
| CHR_PRETRAINED_MODEL   | Path to chromosome pretrained model  *eg: /path/AutoHiC/src/models/cfgs/chr_model.pth* |
| TRANSLOCATION_ADJUST   | Whether to adjust for translocation errors  *Default: True*  |
| INVERSION_ADJUST       | Whether to adjust for inversion errors  *Default: True*      |
| DEBRIS_ADJUST          | Whether to adjust for debris errors  *Default: True*         |
| ERROR_MIN_LEN          | Minimum error length  *Default: 15000*                       |
| ERROR_MAX_LEN          | Maximum error length *Default: 20000000*                     |
| ERROR_FILTER_IOU_SCORE | Overlapping error filtering threshold  *Default: 0.8* **Modification is not recommended.** |
| ERROR_FILTER_SCORE     | Error filtering threshold  *Default: 0.9* **Modification is not recommended.** |



### Run

```sh
# cd AutoHiC directory
cd /home/AutoHiC  # Please modify according to your installation directory

# run 
nohup python autohic.py -c cft-autohic.txt > log.txt 2>&1 &

# nohup: Run the program ignoring pending signals
```

> Notes:  
>
> 1. **Please specify the absolute path of the `cft-autohic.txt`**
>
> 2. **It is recommended to specify a directory for the `log.txt`, It will record the running information of AutoHiC**
> 3. **Delete the nohup command if you don't want the program to run in the background.**



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
├── cft-autohic.txt
```

**The main output:**

1. fasta file with a "`_autohic`" suffix containing the output scaffolds at the chromosome level.

2. The `result.html` file, which provides detailed information before and after genome correction, where the error occurred, and a heat map of HiC interaction and chromosome length before and after. ([example](https://github.com/Jwindler/AutoHiC/example/result_demo.html "Demo"))

3. Please see this [document](https://github.com/Jwindler/AutoHiC/example/detail_result.md "Docs") for detailed results description.



## Plot HiC interaction map

AutoHiC also provides a script to visualise the HiC interaction matrix separately.

![](https://s2.loli.net/2023/06/13/Brc8zdFhX2ZOUf5.png)



```sh
python visualizer.py -hic example.hic
```

**For detailed commands, please refer to the help documentation (`--help`)**



- result ([example](https://github.com/Jwindler/AutoHiC/example/chromosome_demo.svg "Demo"))

![](https://s2.loli.net/2023/06/13/FKNaZkiCTh9rdfV.png)





## Contact

**Please free to open an issue, when you encounter any problems.**



## Split chromosome (optional) 

If your genome is very complex, the model may not be very accurate in dividing the chromosomes. It is recommended that you import the last adjustment file into Juicxbox to manually split chromosomes.

You can download the Juicebox user manual from this link: https://drive.google.com/drive/folders/1T9twnImt1CK_NrB9SBb-dg4dBENyhPTN?usp=sharing

**The `.hic` and `.assembly` files you need to use can be obtained from the `chromosome` folder under the `autohic_results` directory.**



## License

**AutoHiC Copyright (c) 2022 Wang lab. All rights reserved.**

This software is distributed under The `MIT License` (MIT).

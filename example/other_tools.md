# Extending AutoHiC to other assembly software

Currently, the official version of `AutoHiC` only supports `3d-dna` genome assembly. However, it can be extended to any other assembly software by following the steps below. However, the process is currently **under test** and there may be some problems. **I hope if you have any problems during the process, you can open a [issue](https://github.com/Jwindler/AutoHiC/issues/new) or contact me: jzjlab@163.com**



- [Extending AutoHiC to other assembly software](#extending-autohic-to-other-assembly-software)
  - [Install](#install)
    - [conda](#conda)
    - [soft download](#soft-download)
  - [Usage](#usage)
    - [fasta2assembly](#fasta2assembly)
    - [bam2hic](#bam2hic)
    - [onehic](#onehic)
    - [get new fasta](#get-new-fasta)
  - [Notes](#notes)
  - [Citations](#citations)




## Install

Since some other dependencies are needed during use, we recommend using conda to prepare the environment.

### conda

```sh
conda create -n morehic -c bioconda python=3.6 matlock samtools -y

conda activate morehic

```

-   Download the conversion script

```sh
git clone git@github.com:phasegenomics/juicebox_scripts.git

```



### soft download

>   If you cannot clone it, you can get it from the link below. In the Folder `other_tools`, the filename is `juicebox_scripts-master.zip`.

| Google Drive (recommend)                                                                                  | Baidu Netdisk(百度网盘)                                                       | Quark (夸克)                                             |
| --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------- |
| [Pre-trained model](https://drive.google.com/drive/folders/1T9twnImt1CK_NrB9SBb-dg4dBENyhPTN?usp=sharing) | [Pre-trained model](https://pan.baidu.com/s/1CturvBMowVMwpeKYKjsa9w?pwd=v4et) | [Pre-trained model](https://pan.quark.cn/s/709f9e5e005b) |

  

## Usage

Since AutoHiC requires `.hic` and `.assembly` files, we have to generate them first. This process requires the use of `genome files` and `bam files`. These two files come from the custom assembly software you use.



### fasta2assembly

First, generate an X file based on the genome file.

```sh
# fasta 2 apg
python3 juicebox_scripts/juicebox_scripts/makeAgpFromFasta.py test.fasta out.agp

# apg 2 asembly
python3 juicebox_scripts/juicebox_scripts/agp2assembly.py out.agp out.assembly

```

>   The path of `juicebox_scripts` must be replaced according to the actual situation.



### bam2hic

Use the `bam` file to generate the corresponding `.hic` file. This step requires the use of `3d-dna`, which can be obtained from the link above : [soft download](#soft-download)

-   If you have multiple `bam` files, you can use the following command to merge them together

```sh
# merge bam 
samtools merge merged.bam input1.bam input2.bam input3.bam

```



-   get `.hic` file

```sh
# this step sometimes crashes on memory
matlock bam2 juicer out.bam out.links.txt  

sort -k2,2 -k6,6 out.links.txt > out.sorted.links.txt

# creates .hic file
bash 3d-dna/visualize/run-assembly-visualizer.sh out.assembly out.sorted.links.txt 
# The path of 3d-dna must be replaced according to the actual situation.
```



>   The above steps make certain assumptions about the contents of the `bam` file. If an error is reported during the generation of the `out.links.txt  ` file, you can use the following command

```sh
# this BAM file should represent Hi-C reads mapped against starting contigs!
samtools view -h in.bam |sed '/^[^@]/s/^\(.*\)\/[12]\t/\1\t/'|samtools view -Sb -o out.bam

samtools sort -@ 40 -n out.bam -o out.sorted.bam

```



### onehic

Since the current environment used by AutoHiC is incompatible, you have to create a new environment according to the AutoHiC documentation.

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



Now you can use `onehic.py` to adjust the genome based on the acquired `out.assembly` and `out.hic` files.

```sh
# Enter the AutoHiC directory.
cd /home/ubuntu/AutoHic  

# run onehic
python3.9 onehic.py -hic out.hic -asy out.assembly -autohic /home/ubuntu/AutoHic -p pretrained.pth -out ./

```



### get new fasta

```sh
# activate env
conda activate morehic

# get new fasta
python juicebox_assembly_converter.py -a adjusted.assembly -f genome.fasta

```



## Notes

**Since this process is currently in testing, if you have any questions, please feel free to contact me (`jzjlab@163.com`) and I will be happy to help.**



## Citations

**If you used AutoHiC in your research, please cite us:**

```sh
AutoHiC: a deep-learning method for automatic and accurate chromosome-level genome assembly
Zijie Jiang, Zhixiang Peng, Yongjiang Luo, Lingzi Bie, Yi Wang

bioRxiv 2023.08.27.555031; doi: https://doi.org/10.1101/2023.08.27.555031
```


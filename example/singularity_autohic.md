# AutoHiC singularity version

Considering that many users run AutoHiC on large clusters, the build dependency environment may not be very free, and Docker has root restrictions, we provide a singularity version. However, the process is currently under active development and there may be some issues during use. We hope to get your feedback to update the process.



- [AutoHiC singularity version](#autohic-singularity-version)
  - [Usage](#usage)
    - [get image](#get-image)
    - [bulid environment](#bulid-environment)
  - [run](#run)




## Usage

First you need to download the AutoHiC singularity environment.



### get image

You can also retrieve `AutoHiC.sif` files directly from the `other_tools` folder in [Google Drive](https://drive.google.com/drive/folders/1T9twnImt1CK_NrB9SBb-dg4dBENyhPTN).



### bulid environment

```sh
# built container
singularity build your_container.sif AutoHiC.sif

# run container
singularity exec your_container.sif bash

# init conda 
/home/autohic/miniconda3/bin/conda init bash
source ~/.bashrc

# activate AutoHiC
conda activate autohic

# clone AutoHiC
git clone https://github.com/Jwindler/AutoHiC.git

# configuration environment
# install dependencies
cd ~/AutoHiC/src/models/swin
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple/

# return to AutoHiC word folder
cd ~/AutoHiC

# This directory(/home/autohic) contains juicer and 3d-dna.
```



## run

Now you can follow this part of the document to prepare data and configuration files to run AutoHiC: [Usages](https://github.com/Jwindler/AutoHiC#usages)


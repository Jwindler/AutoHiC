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

# enter the working directory
cd /home/autohic
# This directory contains juicer and 3d-dna.

# clone AutoHiC
git clone https://github.com/Jwindler/AutoHiC.git

# activate AutoHiC
conda activate autohic

# configuration environment
cd /home/autohic/AutoHiC/src/models/swin

# install dependencies
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple/

# return to AutoHiC word folder
cd /home/autohic/AutoHiC
```



## run

Now you can follow this part of the document to prepare data and configuration files to run AutoHiC: [Usages](https://github.com/Jwindler/AutoHiC#usages)


#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: IfFolder.py
@time: 2022/4/24 上午10:30
@function: 
"""

import os

class NotAFolder(ValueError):
    pass

def if_folder(folderpath):
    if os.path.isdir(folderpath):
        if not folderpath.endswith("/"): return folderpath + "/"
        else:
            return folderpath
    else:
        print(folderpath, "is not a folder", '\n', "Please check you input")
        raise NotAFolder(folderpath)





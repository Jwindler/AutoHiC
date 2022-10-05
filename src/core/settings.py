#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: settings.py.py
@time: 10/5/22 10:00 AM
@function:
"""

import os

# set the environment variable CONFIG_PATH
current_path = os.path.dirname(os.path.realpath(__file__))
current_path = os.path.abspath(os.path.join(current_path, "../../"))

os.environ.setdefault("PYTHONPATH", current_path)

CONFIG_PATH = os.path.join(current_path, "conf/config.yml")
os.environ.setdefault("CONFIG_PATH", CONFIG_PATH)

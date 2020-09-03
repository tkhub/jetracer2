#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob
import re

files = glob.glob('data/apex/*')
files_num = len(files)

for f in files:
    print(f)
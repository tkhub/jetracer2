#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob
import re

files = glob.glob('data/apex/*')
files_num = len(files)

for f in files:
    #filename = os.path.basename(f)
    initfname = re.sub(r'\d{1,2}_','0_', f)
    os.rename(f, initfname)
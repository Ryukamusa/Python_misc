#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 16:23:47 2017

@author: helio
"""
execfile('/home/helio/Rotinas/Python/AVISO/playxinho.py') #rotina rocheda

import time
import datetime
import sys
import numpy as np

try:
    typ=sys.argv[1]
except:
    typ='coiso'
if typ=='-t':
    mn=int(sys.argv[2])
    sg=int(sys.argv[3])
else:
    mn=60
    sg=0

st=datetime.datetime.now()

while True:
    dif=datetime.datetime.now()-st
    hr=dif.seconds/(mn*60+sg)
    if hr==1:
        for i in np.arange(0,4):
            playxinho()
        break
    else:
        sec=dif.seconds%60
        mint=dif.seconds/60
        prnt='-- %.2i:%.2i --\r'%(mint,sec)
        lenold=len(prnt)
        sys.stdout.write(prnt)
        sys.stdout.flush()
        sys.stdout.write('\b'*lenold)
    time.sleep(1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 15:52:21 2022

@author: clement
"""


import nibabel
#from .blast_ct.blast_ct.console_tool import console_tool_stand_alone
from blast_ct.blast_ct.console_tool import console_tool_stand_alone


def inference(infile, outfolder, ensemble, device):
    print(infile)
    print(outfolder)
    print(ensemble)
    print(device)
    print('Super !')
    splt = infile.split('/')
    fname_ext=splt[-1]
    splt2 = fname_ext.split('.')
    fname = splt2[0]
    segfile = outfolder+'/'+fname+'_seg.nii.gz'
    probfile = outfolder+'/'+fname+'_prob.nii.gz'
    console_tool_stand_alone(infile, segfile, device, probfile, ensemble)

    








if __name__ == "__main__":
    infile='/Volumes/Mac_Data/CQ500/in/CT_PLAIN_THIN_PLAIN_THIN_0_3.nii'
    outfolder='/Volumes/Mac_Data/CQ500/out/'
    ensemble=False
    device='cpu'
    inference(infile, outfolder, ensemble, device)




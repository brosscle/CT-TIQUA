#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 15:52:21 2022

@author: clement
"""


import nibabel as nib
import nibabel.processing
import socket
import os
import shutil

from nipype.interfaces import fsl
import ants


# When executing from the commandline (install with pip)
from .blast_ct.blast_ct.console_tool import console_tool_stand_alone
from .python_scripts.Volume_estimation import Single_Volume_Inference

# When executing this script (from spyder for example)
#from blast_ct.blast_ct.console_tool import console_tool_stand_alone
#from python_scripts.Volume_estimation import Single_Volume_Inference


def inference(infile, outfolder, ensemble, device, remove_tmp_files):
   
    print('Start of the pipeline...')
    print('Summary:')
    print('infile='+infile)
    print('outfolder='+outfolder)
    sep = os.sep
    basename = os.path.basename(infile).split('.')[0]
    tmp_fold = outfolder+sep+'tmp'+sep
    os.makedirs(tmp_fold, exist_ok=True)
    
    fold = sep.join(os.path.realpath(__file__).split(sep)[:-1])
    
    
    #CHECK THAT INPUT IMAGE HAS A QFORMCODE EQUAL TO 1
    print('Start of the quality control...')
    opt={"Sform_code":'scanner', "Qform_code":'scanner'}
    img_h = nib.load(infile)
    sform_code = opt['Sform_code']
    qform_code = opt['Qform_code']
    img_h.set_sform(img_h.get_sform(), code=sform_code)
    img_h.set_qform(img_h.get_qform(), code=qform_code)
    nib.save(img_h, tmp_fold+basename+'_clean.nii.gz')
    print('End of the quality control')
    
    #RESAMPLING
    print('Start of the resampling...')
    im_h = nib.load(tmp_fold+basename+'_clean.nii.gz')
    order = 0
    pixdim=[1,1,1]
    Im_resampled = nibabel.processing.resample_to_output(im_h, pixdim, order = order)
    resampled_file = tmp_fold+basename+'_Resampled.nii'
    nib.save(Im_resampled, resampled_file)
    print('End of the resampling')
    
    
    # #CHECK THAT RESAMPLED IMAGE HAS A QFORMCODE EQUAL TO 1
    
    
    
    #BRAIN EXTRACTION
    print('Start of the brain extraction...')
    matlab_runtime_path = fold+sep+'matlab_scripts'+sep+'RunTime'+sep+'v910'
    App_path = fold+sep+'matlab_scripts'+sep+'App'+sep+'application'+sep+'run_SkullStrip.sh'
    print(matlab_runtime_path)
    outimage = tmp_fold+basename+'_SkullStripped.nii'
    outROI = tmp_fold+basename+'_ROI.nii'
    cmdline = App_path+' ' + matlab_runtime_path + ' ' + resampled_file + ' ' + outimage + ' ' + outROI
    print(cmdline)
    os.system(cmdline)
    print('End of the brain extraction')
    
    
    #CHECK THAT SKULL STRIPPED AND ROI HAVE A QFORMCODE EQUAL TO 1
    
    
    #SEGMENTATION BLAST
    print('Start of the segmentation...')
    segfile = outfolder+sep+basename+'_seg.nii.gz'
    probfile = tmp_fold+sep+basename+'_prob.nii.gz'
    console_tool_stand_alone(resampled_file, segfile, device, probfile, ensemble, tmp_fold)
    print('End of the segmentation')
    
    #CHECK THAT SEGMENTATION HAS A QFORMCODE EQUAL TO 1
    
    # REGISTRATION
    print('Start of the linear registration...')
    Atlas = fold+sep+'data'+sep+'Resliced_Registered_Labels_mod.nii.gz'
    Template = fold+sep+'data'+sep+'TEMPLATE_miplab-ncct_sym_brain.nii.gz'
    flt = fsl.FLIRT()

    flt.inputs.in_file = Template
    flt.inputs.reference = tmp_fold+basename+'_SkullStripped.nii.gz'
    flt.inputs.out_file = tmp_fold+basename+'_Template_FLIRTRegistered.nii.gz'
    flt.inputs.out_matrix_file = tmp_fold+basename+ '_FLIRTRegisteredTemplate_transform-matrix.mat'
    flt.inputs.dof = 7
    flt.inputs.bins = 256
    flt.inputs.cost_func = 'normcorr'
    flt.inputs.interp = 'nearestneighbour'
    flt.inputs.searchr_x = [-180, 180]
    flt.inputs.searchr_y = [-180, 180]
    flt.inputs.searchr_z = [-180, 180]
    flt.run()
    


    applyxfm = fsl.ApplyXFM()
    applyxfm.inputs.in_matrix_file = tmp_fold+basename+ '_FLIRTRegistered_transform-matrix.mat'
    applyxfm.inputs.in_file = Atlas
    applyxfm.inputs.out_file = tmp_fold+basename+'_Altas_FLIRTRegistered.nii.gz'
    applyxfm.inputs.reference = tmp_fold+basename+'_SkullStripped.nii.gz'
    applyxfm.inputs.apply_xfm = True
    applyxfm.inputs.out_matrix_file = tmp_fold+basename+ '_FLIRTRegisteredAtlas_transform-matrix.mat'
    applyxfm.inputs.interp = 'nearestneighbour'
    applyxfm.run()
            
    
    print('End of the linear registration')
    
    
    #CHECK THAT REGISTERED TEMPLATE AND ATLAS HAVE A QFORMCODE EQUAL TO 1
    
    
    
    print('Start of the elastic registration...')
    img_fixed = ants.image_read(tmp_fold+basename+'_SkullStripped.nii.gz')
    img_moving = ants.image_read(tmp_fold+basename+'_Template_FLIRTRegistered.nii.gz')
    outprefix=tmp_fold+basename
    reg = ants.registration(img_fixed, img_moving, outprefix=outprefix)
    reg['warpedmovout'].to_file(tmp_fold+basename+'_Template_ANTSRegistered.nii.gz')
    
    mytx = reg['fwdtransforms']
    im_to_embarque = ants.image_read(tmp_fold+basename+'_Altas_FLIRTRegistered.nii.gz')
    embarqued_im = ants.apply_transforms(img_fixed, im_to_embarque, transformlist=mytx, interpolator='nearestNeighbor')
    embarqued_im.to_file(outfolder+sep+basename+'_Altas_ANTSRegistered.nii.gz')
    print('End of the elastic registration')
    

    #CHECK THAT REGISTERED TEMPLATE AND ATLAS HAVE A QFORMCODE EQUAL TO 1

    print('Start of the volume computation...')
    seg = outfolder+sep+basename+'_seg.nii.gz'
    atlas = outfolder+sep+basename+'_Altas_ANTSRegistered.nii.gz'
    Labels = fold+sep+'data'+sep+'Labels_With_0.csv'
    outcsv = outfolder+sep+basename+'_Volumes.csv'
    Single_Volume_Inference(atlas, seg, Labels, outcsv)
    
    print('End of the volume computation')
    
    if remove_tmp_files:
        print('Removing of the temporary files...')
        shutil.rmtree(tmp_fold)
    
    print('End of the pipeline')






if __name__ == "__main__":
    
    if socket.gethostname() == 'cbrossard-Precision-Tower-7910':
        #computer_path = '/SUMOONE/brossardc/DATA/'
        #computer_path = "/media/cbrossard/ClementBackUp1/SUMO_bis/"
        computer_path = "/data_network/SUMOONE/brossardc/DATA/"
        nb_jobs_max = 10
    elif socket.gethostname() == 'gin-e05-veks':
        computer_path = '/data_network/sumoone/brossardc/DATA/'
        nb_jobs_max = 20
    elif socket.gethostname() == 'gin-e05-banksy':
        computer_path = '/data_network/irmage_pa/brossardc/DATA/'
        nb_jobs_max = 60
    elif socket.gethostname() == 'gin-e05-pratt':
        computer_path = '/data_network/irmage_pa/brossardc/DATA/'
        nb_jobs_max = 100
    elif socket.gethostname() == 'MBP-de-Clement':
        computer_path = '/Volumes/Mac_Data/SUMOONE_Miroir/'
        nb_jobs_max = 2
    elif socket.gethostname() == 'pers-160-138.vpn.u-ga.fr':
        computer_path = '/Volumes/Mac_Data/SUMOONE_Miroir/'
        nb_jobs_max = 2
    elif socket.gethostname() == 'brosscle.vpn.u-ga.fr':
        computer_path = '/Volumes/Mac_Data/SUMOONE_Miroir/'
        nb_jobs_max = 2
    elif socket.gethostname() == 'MacBook-Pro-de-Clement.local':
        computer_path = '/Volumes/Mac_Data/SUMOONE_Miroir/'
        nb_jobs_max = 2
    
    
    # infile='/Volumes/Mac_Data/CQ500/in/CT_PLAIN_THIN_PLAIN_THIN_0_3.nii'
    # outfolder='/Volumes/Mac_Data/CQ500/out/'
    
    infile = computer_path+'CQ500/in/01_CT_PLAIN_THIN_PLAIN_THIN_0_3.nii'
    infile = '/data_network/SUMOONE/brossardc/DATA/Full_Radiomic_TBI/sub-P01/ses-J0/anat/sub-P01_ses-J0_CraneSansIV.nii'
    infile= computer_path+'Full_Radiomic_TBI/sub-P01/ses-J0/anat/sub-P01_ses-J0_CraneSansIV.nii'
    outfolder = computer_path + 'CQ500/out'
    #outfolder = '/home/cbrossard/Bureau/Test_out/'
    
    ensemble=True
    device='cpu'
    device=0
    inference(infile, outfolder, ensemble, device)




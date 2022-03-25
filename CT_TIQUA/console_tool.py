#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 15:52:21 2022

@author: clement
"""

import sys
import os
import argparse
from .main import inference

def path(string):
    if os.path.exists(string):
        return string
    else:
        sys.exit(f'File not found: {string}')


def console_tool():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', metavar='input', type=path, help='Path to input image.', required=True)
    parser.add_argument('--output', metavar='output', type=str, help='Path to output folder.', required=True)
    #matlab_App_path, matlab_runtime_path
    parser.add_argument('--matlab_App_path', metavar='matlab_App_path', type=str, help='Path to the matlab application, ie to the run_SkullStrip.sh file.', required=True)
    parser.add_argument('--matlab_RunTime_path', metavar='matlab_runtime_path', type=str, help='Path to the matlab RunTime, ie to the v910 folder.', required=True)
    parser.add_argument('--ensemble', help='Whether to use all the models (slower but more precise)', type=bool,
                        default=False)
    parser.add_argument('--device', help='GPU device index (int) or \'cpu\' (str)', default='cpu')
    parser.add_argument('--remove_tmp_files', help='Removing temporary files at the end of the pipeline', type=bool, default=True)

    
    parse_args, unknown = parser.parse_known_args()
    if not (parse_args.input[-7:] == '.nii.gz' or parse_args.input[-4:] == '.nii'):
        raise IOError('Input file must be of type .nii or .nii.gz')

    if (parse_args.output[-7:] == '.nii.gz' or parse_args.output[-4:] == '.nii'):
        raise IOError('Output must be a folder, not an image.')

    os.makedirs(parse_args.output+'/tmp/', exist_ok=True)
    inference(parse_args.input, parse_args.output, parse_args.matlab_App_path, parse_args.matlab_RunTime_path, parse_args.ensemble, parse_args.device, parse_args.remove_tmp_files)



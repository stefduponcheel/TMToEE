#!/bin/bash

# list all files
FILES=$(xrdfs maite.iihe.ac.be ls /store/user/sduponch/PhD/TMToEE/BplusToKplusTM/20260509/Skimmed | grep "\.root" | sed 's|^|root://maite.iihe.ac.be/|')

# convert to comma separated for VarParsing
INPUT=$(echo $FILES | tr ' ' ',')

cmsRun TrigObjectPtMatch_cfg.py \
    inputFiles="$INPUT" \
    outputFile="TrigPtMatchBplus.root" \
    maxEvents=-1

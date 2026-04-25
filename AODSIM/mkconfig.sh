#!/bin/bash

step="AODSIM"
mode=$1

cmsDriver.py \
    --python_filename "${step}_${mode}_cfg.py" \
    --eventcontent AODSIM \
    --customise Configuration/DataProcessing/Utils.addMonitoring \
    --datatier AODSIM \
    --filein INPUTFILE \
    --fileout OUTPUTFILE \
    --conditions 124X_mcRun3_2022_realistic_v12 \
    --beamspot Realistic25ns13p6TeVEarly2022Collision \
    --step DIGI,DATAMIX,L1,DIGI2RAW,HLT:2022v12,RAW2DIGI,L1Reco,RECO,RECOSIM \
    --procModifiers premix_stage2,siPixelQualityRawToDigi \
    --datamix PreMix \
    --pileup_input "dbs:/Neutrino_E-10_gun/Run3Summer21PrePremix-Summer22_124X_mcRun3_2022_realistic_v11-v2/PREMIX" \
    --geometry DB:Extended \
    --era Run3 \
    --number -1 \
    --no_exec \
    --mc || exit $? ;

sed -i "6iimport sys" "${step}_${mode}_cfg.py"
sed -i "s|'INPUTFILE'|sys.argv[2]|g" "${step}_${mode}_cfg.py"
sed -i "s|'OUTPUTFILE'|sys.argv[3]|g" "${step}_${mode}_cfg.py"

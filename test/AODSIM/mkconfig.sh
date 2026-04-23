#!/bin/bash

cmsDriver.py \
    --python_filename "AODSIM_cfg.py" \
    --eventcontent AODSIM \
    --customise Configuration/DataProcessing/Utils.addMonitoring \
    --datatier AODSIM \
    --filein file:../GENSIM/etatoTMgamma_GENSIM.root \
    --fileout file:etatoTMgamma_AODSIM.root \
    --conditions 124X_mcRun3_2022_realistic_v12 \
    --beamspot Realistic25ns13p6TeVEarly2022Collision \
    --step DIGI,DATAMIX,L1,DIGI2RAW,HLT:2022v12,RAW2DIGI,L1Reco,RECO,RECOSIM \
    --procModifiers premix_stage2,siPixelQualityRawToDigi \
    --datamix PreMix \
    --pileup_input "dbs:/Neutrino_E-10_gun/Run3Summer21PrePremix-Summer22_124X_mcRun3_2022_realistic_v11-v2/PREMIX" \
    --geometry DB:Extended \
    --era Run3 \
    --number 10 \
    --no_exec \
    --mc

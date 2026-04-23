#!/bin/bash

cmsDriver.py "Configuration/GenProduction/python/etaToTMGamma_fragment_cff.py" \
    --python_filename "etatoTMgamma_GENSIM_cfg.py" \
    --eventcontent RAWSIM \
    --datatier GEN-SIM \
    --fileout file:etatoTMgamma_GENSIM.root \
    --conditions 124X_mcRun3_2022_realistic_v12 \
    --beamspot Realistic25ns13p6TeVEarly2022Collision \
    --step GEN,SIM \
    --geometry DB:Extended \
    --era Run3 \
    --number 10 \
    --no_exec \
    --mc

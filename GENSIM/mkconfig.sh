#!/bin/bash

step="GENSIM"
mode="etaToTMGamma"


ver=20260423
year=2022
outdir="/store/user/sduponch/PhD/TMToEE/${mode}/${ver}/Simulation"

cmsDriver.py "Configuration/GenProduction/python/${mode}_fragment_cff.py" \
    --python_filename "${step}_${mode}_cfg.py" \
    --eventcontent RAWSIM \
    --customise Configuration/DataProcessing/Utils.addMonitoring \
    --datatier GEN-SIM \
    --fileout "output.root" \
    --conditions 124X_mcRun3_2022_realistic_v12 \
    --beamspot Realistic25ns13p6TeVEarly2022Collision \
    --step GEN,SIM \
    --geometry DB:Extended \
    --era Run3 \
    --no_exec \
    --mc || exit $? ;

REQUESTNAME="MC_${mode}_${year}_${ver}"
UNITSPERJOB="500"
TOTALUNITS="50000"
OUTPUTDATASETTAG="${year}"
OUTLFNDIRBASE=${outdir}

sed -e "s%CONFIGFILE%${step}_${mode}_cfg.py%g" \
    -e "s%REQUESTNAME%${REQUESTNAME}%g" \
    -e "s%UNITSPERJOB%${UNITSPERJOB}%g" \
    -e "s%TOTALUNITS%${TOTALUNITS}%g" \
    -e "s%OUTPUTDATASETTAG%${OUTPUTDATASETTAG}%g" \
    -e "s%OUTLFNDIRBASE%${OUTLFNDIRBASE}%g" \
    "crabConfigTemplate.py" > "crabConfig.py"

source /cvmfs/cms.cern.ch/crab3/crab.sh

crab submit -c "crabConfig.py"

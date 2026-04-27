#!/bin/bash

step="MINIAODSIM"
mode=$1

cmsDriver.py \
    --python_filename "${step}_${mode}_cfg.py" \
    --eventcontent MINIAODSIM \
    --customise Configuration/DataProcessing/Utils.addMonitoring \
    --datatier MINIAODSIM \
    --conditions 130X_mcRun3_2022_realistic_v5 \
    --step PAT \
    --geometry DB:Extended \
    --era Run3,run3_miniAOD_12X \
    --filein INPUTFILE \
    --fileout OUTPUTFILE \
    --number -1 \
    --no_exec \
    --mc || exit $? ;

sed -i "6iimport sys" "${step}_${mode}_cfg.py"
sed -i "s|'INPUTFILE'|sys.argv[2]|g" "${step}_${mode}_cfg.py"
sed -i "s|'OUTPUTFILE'|sys.argv[3]|g" "${step}_${mode}_cfg.py"

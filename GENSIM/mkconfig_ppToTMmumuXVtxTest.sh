#!/bin/bash
# DIAGNOSTIC ONLY. See ppToTMmumuXVtxTest_fragment_cff.py.
step="GENSIM"
mode="ppToTMmumuXVtxTest"
lhefile="root://eosuser.cern.ch//eos/user/s/sduponch/PhD/ppToTMeeX/LHE/pp_TT_X_13p6TeV_50kevts.lhe"

cmsDriver.py "Configuration/GenProduction/python/${mode}_fragment_cff.py" \
    --filein "${lhefile}" \
    --python_filename "${step}_${mode}_cfg.py" \
    --eventcontent RAWSIM \
    --customise Configuration/DataProcessing/Utils.addMonitoring \
    --datatier GEN-SIM \
    --fileout "OUTPUTFILE" \
    --conditions 124X_mcRun3_2022_realistic_v12 \
    --beamspot Realistic25ns13p6TeVEarly2022Collision \
    --step GEN,SIM \
    --geometry DB:Extended \
    --era Run3 \
    --no_exec \
    --mc || exit $? ;

sed -i "6iimport sys" "${step}_${mode}_cfg.py"
sed -i "s|'OUTPUTFILE'|sys.argv[4]|g" "${step}_${mode}_cfg.py"

cat >> "${step}_${mode}_cfg.py" << 'EOF'

process.source.skipEvents = cms.untracked.uint32(int(sys.argv[2]))
process.maxEvents.input = cms.untracked.int32(int(sys.argv[3]))
EOF

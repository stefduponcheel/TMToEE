#!/bin/bash
# Generates GENSIM_ppToTMeeX_cfg.py, templated for condor job submission.
# Unlike the CRAB-based mkconfig.sh (other modes generate internally, no fixed
# input), this mode reads a single shared LHE file: every job opens the SAME
# file and skips to its own event range via skipEvents, rather than each job
# getting its own input file.
#
# Runtime usage: cmsRun GENSIM_ppToTMeeX_cfg.py <skipEvents> <maxEvents> <outputFile>

step="GENSIM"
mode="ppToTMeeX"
# Diagnostic swap: was root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/ppToTMeeX/20260806/Generation/LHE/pp_TT_X_13p6TeV_50kevts.lhe
# GEN-SIM condor jobs timed out reaching maite.iihe.ac.be:1094 (network, not auth) -
# testing whether CERN EOS is reachable from the worker node instead.
# eosuser.cern.ch (not eoscms.cern.ch) serves the /eos/user/ namespace.
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

# Per-job event range (condor submission): <cfg> <skipEvents> <maxEvents> <outputFile>
process.source.skipEvents = cms.untracked.uint32(int(sys.argv[2]))
process.maxEvents.input = cms.untracked.int32(int(sys.argv[3]))
EOF

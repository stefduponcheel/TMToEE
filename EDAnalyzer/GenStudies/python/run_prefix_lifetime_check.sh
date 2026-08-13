#!/bin/bash
# One-off diagnostic: GEN-level ntuple from a handful of the OLD (pre-lifetime-fix)
# AODSIM files, still on IIHE at ver=20260807. Used to confirm that the
# LesHouches:setLifetime=2 fix only changed the displaced decay length (tm_Lxyz)
# and not the underlying electron/TM kinematics -- i.e. that the difference in
# trigger firing rates before/after the fix is a RECO-level effect (displaced
# tracks reconstructing/triggering differently), not a change in the generated
# physics itself.

export X509_USER_PROXY="/afs/cern.ch/user/s/sduponch/tmp/x509up"
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_15_0_5/src/
cmsenv

NFILES=${1:-20}
FILELIST=$(mktemp)
for i in $(seq 0 $((NFILES - 1))); do
  echo "root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/ppToTMeeX/20260807/Simulation/AODSIM/2022/output_${i}.root"
done > "$FILELIST"

cmsRun EDAnalyzer/GenStudies/python/GenStudies_ppToTMeeX_cfg.py \
    inputFiles_load="$FILELIST" \
    outputFile=/eos/user/s/sduponch/PhD/ppToTMeeX/Ntuples/2022/ntuple_ppToTMeeX_prefix_check.root

rm -f "$FILELIST"
echo "Done: /eos/user/s/sduponch/PhD/ppToTMeeX/Ntuples/2022/ntuple_ppToTMeeX_prefix_check.root"

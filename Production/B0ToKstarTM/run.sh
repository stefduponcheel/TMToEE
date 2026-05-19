#!/bin/bash
FILELIST=$1
OUTDIR=$2
JOBID=$3

export X509_USER_PROXY="/afs/cern.ch/user/s/sduponch/tmp/x509up"

source /cvmfs/cms.cern.ch/cmsset_default.sh

cd /afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_15_0_5/src/

cmsenv

INPUTFILES=$(paste -sd, "$FILELIST")

LOCALOUT="ntuple_B0_${JOBID}.root"
REMOTEOUT="root://maite.iihe.ac.be/${OUTDIR}/${LOCALOUT}"

cmsRun EDAnalyzer/GenStudies/python/GenStudies_B0_cfg.py \
    inputFiles="$INPUTFILES" \
    outputFile="$LOCALOUT" \
    maxEvents=-1

xrdcp -f "$LOCALOUT" "$REMOTEOUT"

rm -f "$LOCALOUT"

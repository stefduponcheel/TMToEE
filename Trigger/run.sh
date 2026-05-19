#!/bin/bash
MODE=$1
VERSION=$2
YEAR=$3
NFILES=${4:-3000}

export X509_USER_PROXY="/afs/cern.ch/user/s/sduponch/tmp/x509up"
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_15_0_5/src/
cmsenv

tmplog="/afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_15_0_5/src/Trigger/${MODE}/tmp/trigeff.log"

cmsRun /afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_15_0_5/src/EDAnalyzer/GenStudies/python/TrigAnalyzer_cfg.py \
    mode=${MODE} version=${VERSION} year=${YEAR} nFiles=${NFILES} &> $tmplog

#!/bin/bash
set -e

FILELIST=$1
EOSOUT=$2
JOBID=$(($3))
CFG=$4
CMSSW_SRC=$5

export X509_USER_PROXY="/afs/cern.ch/user/s/sduponch/tmp/x509up"

echo "=================================================="
echo "Job ID:      ${JOBID}"
echo "Filelist:    ${FILELIST}"
echo "EOS out:     ${EOSOUT}"
echo "CFG:         ${CFG}"
echo "=================================================="

source /cvmfs/cms.cern.ch/cmsset_default.sh
cd "${CMSSW_SRC}"
cmsenv

# comma-separated input list for inputFiles=
INPUTFILES=$(paste -sd, "${FILELIST}")

# write output locally first, then xrdcp to EOS
LOCALOUT="gentrig_${JOBID}.root"

cmsRun "${CFG}" \
    inputFiles="${INPUTFILES}" \
    outputFile="${LOCALOUT}" \
    maxEvents=-1

echo "cmsRun done, staging out to EOS"
xrdcp -f "${LOCALOUT}" "root://eosuser.cern.ch/${EOSOUT}/gentrig_${JOBID}.root"
rm -f "${LOCALOUT}"

echo "Job ${JOBID} finished successfully"

#!/bin/bash
set -e

MODE=$1
FILELIST=$2
OUTDIR=$3
JOBID=$(($4))
CMSSW_SRC=$5

export X509_USER_PROXY="/afs/cern.ch/user/s/sduponch/tmp/x509up"

outfile="${OUTDIR}/output_${JOBID}.root"
cfg="${CMSSW_SRC}/MINIAODSIM/MINIAODSIM_${MODE}_cfg.py"

source /cvmfs/cms.cern.ch/cmsset_default.sh
cd "${CMSSW_SRC}"
cmsenv

INPUTFILES=$(paste -sd, "${FILELIST}")

# Write locally, then stage out via xrdcp
LOCALOUT="output_${JOBID}.root"

xrdfs maite.iihe.ac.be rm "${outfile}" 2>/dev/null || true

cmsRun "${cfg}" \
    inputFiles="${INPUTFILES}" \
    outputFile="${LOCALOUT}" \
    maxEvents=-1

echo "cmsRun done, staging out to ${outfile}"
xrdcp -f "${LOCALOUT}" "root://maite.iihe.ac.be/${outfile}"
rm -f "${LOCALOUT}"

echo "Job ${JOBID} finished successfully"

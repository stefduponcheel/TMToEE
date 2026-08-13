#!/bin/bash
JOBID=$(($1))
EVENTSPERJOB=$(($2))
OUTDIR=$3
#   voms-proxy-init -voms cms --rfc --valid 168:00
export X509_USER_PROXY="/afs/cern.ch/user/s/sduponch/tmp/x509up"

SKIPEVENTS=$((JOBID * EVENTSPERJOB))
outfile="${OUTDIR}/output_${JOBID}.root"
logfile="${OUTDIR}/log/run_${JOBID}.log"

xrdfs eosuser.cern.ch rm -f $outfile || true
xrdfs eosuser.cern.ch rm -f $logfile || true

echo "Job ID: ${JOBID}"
echo "Skip events: ${SKIPEVENTS}"
echo "Events per job: ${EVENTSPERJOB}"
echo "Output file: ${outfile}"

source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_12_4_14_patch3/src/
cmsenv
voms-proxy-info -all -file $X509_USER_PROXY
echo "Proxy valid"
cmsRun "/afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_12_4_14_patch3/src/GENSIM/GENSIM_ppToTMmumuX_cfg.py" "${SKIPEVENTS}" "${EVENTSPERJOB}" "root://eosuser.cern.ch/${outfile}"

#!/bin/bash
MODE=$1
INDIR=$2
OUTDIR=$3
JOBID=$(($4))

export X509_USER_PROXY="/afs/cern.ch/user/s/sduponch/tmp/x509up"

infile="${INDIR}/output_${JOBID}.root"
outfile="${OUTDIR}/output_${JOBID}.root"
logfile="${OUTDIR}/log/run_${JOBID}.log"

xrdfs eosuser.cern.ch rm -f $outfile || true
xrdfs eosuser.cern.ch rm -f $logfile || true

echo "Input file: ${infile}"
echo "Output file: ${outfile}"
echo "Log file: ${logfile}"

source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_12_4_14_patch3/src/
cmsenv
voms-proxy-info -all -file $X509_USER_PROXY
echo "Proxy valid"
cmsRun "/afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_12_4_14_patch3/src/AODSIM/AODSIM_${MODE}_cfg.py" "root://eosuser.cern.ch/${infile}" "root://eosuser.cern.ch/${outfile}"

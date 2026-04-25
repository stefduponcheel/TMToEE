#!/bin/bash
MODE=$1
INDIR=$2
OUTDIR=$3
JOBID=$(($4))
#   voms-proxy-init -voms cms -rfc --valid 168:00 
export X509_USER_PROXY="/afs/cern.ch/user/s/sduponch/tmp/x509up"

infile="${INDIR}/output_${JOBID}.root"
outfile="${OUTDIR}/output_${JOBID}.root"
logfile="${OUTDIR}/log/run_${JOBID}.log"


xrdfs maite.iihe.ac.be rm -f $outfile || true
xrdfs maite.iihe.ac.be rm -f $logfile || true 

tmplog="/afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_12_4_14_patch3/src/AODSIM/tmp/run_${MODE}_${JOBID}.log" #wrapper stdout

echo "Input file: ${infile}"
echo "Output file: ${outfile}"
echo "Log file: ${logfile}" 

source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_12_4_14_patch3/src/
cmsenv
voms-proxy-info -all -file $X509_USER_PROXY
echo "Proxy valid"
cmsRun "/afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_12_4_14_patch3/src/AODSIM/AODSIM_${MODE}_cfg.py" "root://maite.iihe.ac.be/${infile}" "root://maite.iihe.ac.be/${outfile}" &> ${tmplog}

xrdcp -f ${tmplog} root://maite.iihe.ac.be/${logfile}
#rm -f ${tmplog}


#!/bin/bash
export X509_USER_PROXY="/afs/cern.ch/user/s/sduponch/tmp/x509up"
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_15_0_5/src/
cmsenv
tmplog="/afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_15_0_5/src/Trigger/etaToTMGamma/tmp/trigeff.log" 
cmsRun /afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_15_0_5/src/EDAnalyzer/GenStudies/python/TrigAnalyzer_cfg.py &> $tmplog

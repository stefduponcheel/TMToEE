#!/bin/bash
TRIGEFF_LOG=$1
YEAR=$2
OUTFILE=$3
LIMIT=$4

# condor jobs run a minimal, non-login shell that doesn't source ~/.bashrc,
# so ~/.local/bin (where brilcalc is pip --user installed) isn't on PATH
# by default the way it is in an interactive session.
export PATH="$HOME/.local/bin:$PATH"

cd /afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_15_0_5/src/Prescales/

if [ -n "$LIMIT" ]; then
    python3 compute_trigger_lumi.py "$TRIGEFF_LOG" "$YEAR" "$OUTFILE" --limit "$LIMIT"
else
    python3 compute_trigger_lumi.py "$TRIGEFF_LOG" "$YEAR" "$OUTFILE"
fi

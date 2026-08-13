#!/bin/bash

INPUT_DIR="root://eosuser.cern.ch//eos/user/s/sduponch/PhD/ppToTMeeX/MINIAODSIM/2022"
OUTPUT_DIR="root://eosuser.cern.ch//eos/user/s/sduponch/PhD/ppToTMeeX/Skimmed/2022"

mkdir -p /eos/user/s/sduponch/PhD/ppToTMeeX/Skimmed/2022

for input in /eos/user/s/sduponch/PhD/ppToTMeeX/MINIAODSIM/2022/output_*.root; do

    filename=$(basename "$input")
    index=${filename#output_}
    index=${index%.root}

    full_input="${INPUT_DIR}/${filename}"
    full_output="${OUTPUT_DIR}/skimmed_${index}.root"

    echo "Processing $filename..."
    cmsRun tm_trigger_selector.py "$full_input" "$full_output"

done

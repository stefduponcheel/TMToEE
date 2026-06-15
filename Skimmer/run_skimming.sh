#!/bin/bash

INPUT_DIR="root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/BplusToKplusTM/20260509/Simulation/MINIAODSIM/2022"
OUTPUT_DIR="root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/BplusToKplusTM/20260509/Skimmed"

# create the output dir first via xrdfs
xrdfs maite.iihe.ac.be mkdir -p /store/user/sduponch/PhD/TMToEE/BplusToKplusTM/20260509/Skimmed

for input in $(xrdfs maite.iihe.ac.be ls /store/user/sduponch/PhD/TMToEE/BplusToKplusTM/20260509/Simulation/MINIAODSIM/2022 | grep "output_.*\.root"); do

    filename=$(basename "$input")
    index=${filename#output_}
    index=${index%.root}

    full_input="${INPUT_DIR}/${filename}"
    full_output="${OUTPUT_DIR}/skimmed_${index}.root"

    echo "Processing $filename..."
    cmsRun tm_trigger_selector.py "$full_input" "$full_output"

done

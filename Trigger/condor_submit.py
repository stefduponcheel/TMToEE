import sys
import os
import argparse
import subprocess

MODES = {
    # "etaToTMGamma":     {"version": "20260508", "year": "2022", "nfiles": 1},
    # "B0ToKstarTM":      {"version": "20260509", "year": "2022", "nfiles": 1400},
    # "BplusToKplusTM":   {"version": "20260509", "year": "2022", "nfiles": 1400},
    # "omegaToTMPi0":     {"version": "20260509", "year": "2022", "nfiles": 3000},
    # "DplusToPiplusTM":  {"version": "20260515", "year": "2022", "nfiles": 3000},
    "ppToTMeeX": {"version": "20260810", "year": "2022", "nfiles": 500},
    "ppToTMmumuX": {"version": "20260812", "year": "2022", "nfiles": 500},
}

# Modes whose AODSIM lives on EOS (condor-produced) rather than IIHE
# (CRAB-produced) -- these get routed through a dedicated run script that
# passes storage=eos to TrigAnalyzer_cfg.py.
EOS_MODES = {"ppToTMeeX", "ppToTMmumuX"}


def submit_job(mode):
    if mode not in MODES:
        sys.exit(f"Unknown mode {mode}. Known modes: {list(MODES)}")

    here = os.path.abspath(os.path.dirname(__file__))
    modedir = os.path.join(here, mode)
    tmpdir = os.path.join(modedir, "tmp")
    os.makedirs(tmpdir, exist_ok=True)

    cfg = MODES[mode]
    run_script = "run_ppToTMeeX.sh" if mode in EOS_MODES else "run.sh"

    submit_description = f"""
executable = /bin/bash
arguments  = "{here}/{run_script} {mode} {cfg['version']} {cfg['year']} {cfg['nfiles']}"
log    = {tmpdir}/job.log
output = {tmpdir}/job.out
error  = {tmpdir}/job.err
JobBatchName = TrigEff_{mode}
request_cpus = 1
request_memory = 4G
request_disk = 5G
+JobFlavour = "longlunch"
notify_user = stef.duponcheel@cern.ch
notification = Always
max_retries = 2
should_transfer_files = NO

queue 1
"""
    subprocess.run(["condor_submit"], input=submit_description.encode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "modes", nargs="*", default=list(MODES),
        help=f"modes to submit (default: all). Known: {list(MODES)}",
    )
    args = parser.parse_args()

    for m in args.modes:
        print(f"Submitting trigger analysis job for {m}...")
        submit_job(m)

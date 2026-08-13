import os
import argparse
import subprocess

YEAR = "2022"
TRIGEFF_LOGS = {
    "ppToTMeeX": "/afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_15_0_5/src/Trigger/ppToTMeeX/tmp/trigeff.log",
    "ppToTMmumuX": "/afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_15_0_5/src/Trigger/ppToTMmumuX/tmp/trigeff.log",
}


def submit_job(mode, limit=None):
    if mode not in TRIGEFF_LOGS:
        raise SystemExit(f"Unknown mode {mode!r}. Known: {list(TRIGEFF_LOGS)}")

    here = os.path.abspath(os.path.dirname(__file__))
    # per-mode tmp dir -- sharing one tmp/job.log across modes previously
    # caused confusing commingled condor logs elsewhere in this project.
    tmpdir = os.path.join(here, "tmp", mode)
    os.makedirs(tmpdir, exist_ok=True)

    suffix = "_test" if limit is not None else ""
    outfile = f"{here}/trigger_lumi_{YEAR}_{mode}{suffix}.csv"
    limit_arg = str(limit) if limit is not None else ""

    submit_description = f"""
executable = /bin/bash
arguments  = "{here}/run.sh {TRIGEFF_LOGS[mode]} {YEAR} {outfile} {limit_arg}"
log    = {tmpdir}/job.log
output = {tmpdir}/job.out
error  = {tmpdir}/job.err
JobBatchName = TriggerLumi_{YEAR}_{mode}
request_cpus = 1
request_memory = 2G
request_disk = 100M
+JobFlavour = "tomorrow"
notify_user = stef.duponcheel@cern.ch
notification = Always
max_retries = 1
should_transfer_files = NO

queue 1
"""
    subprocess.run(["condor_submit"], input=submit_description.encode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("modes", nargs="*", default=list(TRIGEFF_LOGS),
                         help=f"modes to submit (default: all). Known: {list(TRIGEFF_LOGS)}")
    parser.add_argument("--limit", type=int, default=None,
                         help="only query this many triggers (smoke test)")
    args = parser.parse_args()

    for mode in args.modes:
        print(f"Submitting trigger luminosity job for {mode}...")
        submit_job(mode, limit=args.limit)

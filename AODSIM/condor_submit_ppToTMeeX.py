import sys
import subprocess
import os
import re
import argparse


def submit_jobs(test=False, jobid=None):
    here = os.path.dirname(os.path.abspath(__file__))

    ver = 20260810  # regenerated with the LesHouches:setLifetime=2 fix
    year = 2022
    mode = "ppToTMeeX"
    # EOS, not IIHE -- worker nodes have shown unreliable connectivity to
    # maite.iihe.ac.be this session, while root://eosuser.cern.ch/ was
    # confirmed reachable from a worker node. Flat layout: our GEN-SIM step
    # writes via condor (skipEvents-templated), not CRAB, so no
    # crab-timestamp/counter subdirectory nesting to walk here.
    base = f"/eos/user/s/sduponch/PhD/ppToTMeeX/GENSIM/{year}"
    outdir = f"/eos/user/s/sduponch/PhD/ppToTMeeX/AODSIM/{year}"

    # Direct POSIX read: this script runs on an EOS-mounted host, not a
    # worker node.
    jobids = sorted(
        int(m.group(1))
        for f in os.listdir(base)
        for m in [re.search(r"output_(\d+)\.root$", f)]
        if m
    )

    print(f"Discovered {len(jobids)} GEN-SIM output files in {base}")

    if jobid is not None:
        jobids = [jobid]
    elif test:
        jobids = jobids[:1]

    os.makedirs("./tmp", exist_ok=True)
    joblist_path = "tmp/joblist.txt"
    with open(joblist_path, "w") as f:
        for jobid in jobids:
            f.write(f"{jobid} {base}\n")
            os.makedirs(f"./tmp/job_{jobid}", exist_ok=True)

    os.makedirs(f"{outdir}/log", exist_ok=True)
    subprocess.run(["./mkconfig.sh", mode])
    scheduler_log = f"condor_logs/HTCondor_{mode}.log"
    if os.path.exists(scheduler_log):
        os.remove(scheduler_log)

    submit_description = f"""
executable = /bin/bash
arguments = "{here}/run_ppToTMeeX.sh {mode} $(indir) {outdir} $(jobid)"
log    = {here}/tmp/job_$(jobid)/job_$(jobid).log
output = {here}/tmp/job_$(jobid)/job_$(jobid).out
error  = {here}/tmp/job_$(jobid)/job_$(jobid).err
JobBatchName = MC_{mode}_AODSIM_{year}_{ver}
request_cpus = 1
request_memory = 8G
request_disk = 10M
+JobFlavour = "longlunch"
max_retries = 2
should_transfer_files = NO

queue jobid, indir from {joblist_path}
"""
    subprocess.run(["condor_submit"], input=submit_description.encode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="submit only 1 job")
    parser.add_argument("--jobid", type=int, default=None, help="resubmit only this single job id")
    args = parser.parse_args()
    print("Submitting jobs to HTCondor...")
    sys.exit(submit_jobs(test=args.test, jobid=args.jobid))

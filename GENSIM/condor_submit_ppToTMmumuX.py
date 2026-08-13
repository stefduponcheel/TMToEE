import sys
import subprocess
import os
import argparse


def submit_jobs(test=False, jobid=None):
    here = os.path.dirname(os.path.abspath(__file__))

    ver = 20260812
    year = 2022
    mode = "ppToTMmumuX"
    outdir = f"/eos/user/s/sduponch/PhD/ppToTMmumuX/GENSIM/{year}"

    # Smoke test: 5 jobs, 1 event each, to confirm each job's skipEvents
    # offset actually lands on a different LHE event before doing the real
    # 500-job x 100-events/job submission.
    events_per_job = 1 if test else 100
    jobids = [jobid] if jobid is not None else (range(5) if test else range(500))

    os.makedirs(f"{outdir}/log", exist_ok=True)
    subprocess.run(["./mkconfig_ppToTMmumuX.sh"])

    os.makedirs("./tmp", exist_ok=True)
    joblist_path = "tmp/joblist.txt"
    with open(joblist_path, "w") as f:
        for j in jobids:
            f.write(f"{j}\n")
            os.makedirs(f"./tmp/job_{j}", exist_ok=True)

    scheduler_log = f"condor_logs/HTCondor_{mode}_GENSIM.log"
    if os.path.exists(scheduler_log):
        os.remove(scheduler_log)

    submit_description = f"""
executable = /bin/bash
arguments = "{here}/run_ppToTMmumuX.sh $(jobid) {events_per_job} {outdir}"
log    = {here}/tmp/job_$(jobid)/job_$(jobid).log
output = {here}/tmp/job_$(jobid)/job_$(jobid).out
error  = {here}/tmp/job_$(jobid)/job_$(jobid).err
JobBatchName = MC_{mode}_GENSIM_{year}_{ver}
request_cpus = 1
request_memory = 3G
request_disk = 10M
+JobFlavour = "longlunch"
max_retries = 2
should_transfer_files = NO

queue jobid from {joblist_path}
"""
    subprocess.run(["condor_submit"], input=submit_description.encode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="submit only 5 jobs, 1 event each")
    parser.add_argument("--jobid", type=int, default=None, help="resubmit only this single job id")
    args = parser.parse_args()
    print("Submitting jobs to HTCondor...")
    sys.exit(submit_jobs(test=args.test, jobid=args.jobid))

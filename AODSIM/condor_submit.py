import sys
import subprocess
import os
import re
import argparse

def submit_jobs(test=False):
    here = os.path.dirname(os.path.abspath(__file__))

    ver = 20260515
    year = 2022
    mode = "DplusToPiplusTM"
    base = f"/store/user/sduponch/PhD/TMToEE/{mode}/{ver}/Simulation/SIM/{year}/260515_134354"
    outdir = f"/store/user/sduponch/PhD/TMToEE/{mode}/{ver}/Simulation/AODSIM/{year}"

    job_to_indir = {}
    result = subprocess.run(
        ["xrdfs", "root://maite.iihe.ac.be", "ls", base],
        capture_output=True, text=True
    )
    subdirs = [line.strip() for line in result.stdout.split("\n") if re.search(r"/\d{4}$", line)]

    for sub in sorted(subdirs):
        result = subprocess.run(
            ["xrdfs", "root://maite.iihe.ac.be", "ls", sub],
            capture_output=True, text=True
        )
        for line in result.stdout.split("\n"):
            m = re.search(r"output_(\d+)\.root$", line)
            if m:
                jobid = int(m.group(1))
                job_to_indir[jobid] = sub

    print(f"Discovered {len(job_to_indir)} input files across {len(subdirs)} subdirs")
    
    jobids = sorted(job_to_indir)
    if test:
        jobids = jobids[:1]

    os.makedirs("./tmp", exist_ok=True)
    joblist_path = "tmp/joblist.txt"
    with open(joblist_path, "w") as f:
        for jobid in sorted(job_to_indir):
            indir = job_to_indir[jobid]
            f.write(f"{jobid} {indir}\n")
            os.makedirs(f"./tmp/job_{jobid}", exist_ok=True)

    subprocess.run(["xrdfs", "root://maite.iihe.ac.be", "mkdir", "-p", f"{outdir}/log"])
    subprocess.run(["./mkconfig.sh", mode])
    scheduler_log = f"condor_logs/HTCondor_{mode}.log"
    if os.path.exists(scheduler_log):
        os.remove(scheduler_log)

    submit_description = f"""
executable = /bin/bash
arguments = "{here}/run.sh {mode} $(indir) {outdir} $(jobid)"
log    = {here}/tmp/job_$(jobid)/job_$(jobid).log
output = {here}/tmp/job_$(jobid)/job_$(jobid).out
error  = {here}/tmp/job_$(jobid)/job_$(jobid).err
JobBatchName = MC_{mode}_AODSIM_{year}_{ver}
request_cpus = 1
request_memory = 8G
request_disk = 10M
+JobFlavour = "longlunch"
max_retries = 0
should_transfer_files = NO

queue jobid, indir from {joblist_path}
"""
    subprocess.run(["condor_submit"], input=submit_description.encode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="submit only 1 job")
    args = parser.parse_args()
    print("Submitting jobs to HTCondor...")
    sys.exit(submit_jobs(test=args.test))

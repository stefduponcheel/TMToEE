import sys
import subprocess
import os
import re

def submit_jobs():
    mode     = "BplusToKplusTM"
    ver_in   = "20260509"            
    ver_out  = "20260509"            
    year     = 2022
    FILES_PER_JOB = 50

    indir_base = f"/store/user/sduponch/PhD/TMToEE/{mode}/{ver_in}/Simulation/AODSIM/{year}"
    outdir     = f"/store/user/sduponch/PhD/TMToEE/{mode}/{ver_out}/Analysis/Ntuples/{year}"

    # Discover files
    all_files = []
    result = subprocess.run(
        ["xrdfs", "root://maite.iihe.ac.be", "ls", indir_base],
        capture_output=True, text=True)

    for line in result.stdout.split("\n"):
        s = line.strip()
        if s.endswith(".root"):
            all_files.append(s)
        elif re.search(r"/\d{4}$", s):
            sub = subprocess.run(
                ["xrdfs", "root://maite.iihe.ac.be", "ls", s],
                capture_output=True, text=True)
            for s2 in sub.stdout.split("\n"):
                if s2.strip().endswith(".root"):
                    all_files.append(s2.strip())

    all_files = sorted(set(all_files))
    n_files = len(all_files)
    print(f"Found {n_files} input files for {mode}")

    if n_files == 0:
        print("ERROR: no input files. Check ver_in and the input dir path.")
        return 1

    # Group into chunks
    chunks = [all_files[i:i + FILES_PER_JOB] for i in range(0, n_files, FILES_PER_JOB)] 
    n_jobs = len(chunks)
    print(f"Submitting {n_jobs} condor jobs ({FILES_PER_JOB} files per job)")

    # Build joblist + per-job file lists
    here = os.path.abspath(os.path.dirname(__file__))
    os.makedirs(os.path.join(here, "tmp"), exist_ok=True)
    joblist_path = os.path.join(here, "tmp/joblist.txt")

    with open(joblist_path, "w") as jl:
        for jobid, chunk in enumerate(chunks, start=1):
            jobdir = os.path.join(here, f"tmp/job_{jobid}")
            os.makedirs(jobdir, exist_ok=True)

            filelist_path = os.path.join(jobdir, "files.txt")
            with open(filelist_path, "w") as fl:
                for f in chunk:
                    fl.write(f"root://maite.iihe.ac.be/{f}\n")

            jl.write(f"{jobid} {filelist_path}\n")

    subprocess.run(["xrdfs", "root://maite.iihe.ac.be", "mkdir", "-p", outdir])

    submit_description = f"""
executable = /bin/bash
arguments = {here}/run.sh $(filelist) {outdir} $(jobid)
log    = {here}/tmp/job_$(jobid)/job_$(jobid).log
output = {here}/tmp/job_$(jobid)/job_$(jobid).out
error  = {here}/tmp/job_$(jobid)/job_$(jobid).err
JobBatchName = GenStudies_{mode}_{year}_{ver_out}
request_cpus = 1
request_memory = 4G
request_disk = 2G
+JobFlavour = "longlunch"
notify_user = stef.duponcheel@cern.ch
notification = Error
max_retries = 0
should_transfer_files = NO

queue jobid, filelist from {joblist_path}
"""
    subprocess.run(["condor_submit"], input=submit_description.encode())


if __name__ == "__main__":
    print("Submitting GenStudies_Bplus jobs...")
    sys.exit(submit_jobs())

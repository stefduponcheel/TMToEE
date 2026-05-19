import sys
import subprocess
import os
import re
import shutil


def submit_jobs():
    # ---- config ----
    mode    = "etaToTMGamma"
    ver_in  = "20260508"
    ver_out = "20260508"
    year    = 2022
    FILES_PER_JOB = 100

    indir_base = f"/store/user/sduponch/PhD/TMToEE/{mode}/{ver_in}/Simulation/AODSIM/{year}"
    outdir     = f"/store/user/sduponch/PhD/TMToEE/{mode}/{ver_out}/Simulation/MINIAODSIM/{year}"

    here = os.path.abspath(os.path.dirname(__file__))
    cmssw_src = "/afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_13_0_13/src"

    # ---- regenerate the cfg via cmsDriver ----
    subprocess.run(["./mkconfig.sh", mode], check=True)

    # ---- discover input files ----
    all_files = []
    result = subprocess.run(
        ["xrdfs", "root://maite.iihe.ac.be", "ls", indir_base],
        capture_output=True, text=True)

    entries = [line.strip() for line in result.stdout.split("\n") if line.strip()]
    direct_files = [e for e in entries if e.endswith(".root")]
    subdirs      = [e for e in entries if not e.endswith(".root")]

    if direct_files:
        all_files.extend(direct_files)

    for sub in subdirs:
        r = subprocess.run(
            ["xrdfs", "root://maite.iihe.ac.be", "ls", sub],
            capture_output=True, text=True)
        for line in r.stdout.split("\n"):
            s = line.strip()
            if s.endswith(".root"):
                all_files.append(s)

    all_files = sorted(set(all_files))
    n_files = len(all_files)
    print(f"Found {n_files} input files for {mode}")

    if n_files == 0:
        print("ERROR: no input files. Check ver_in and the input dir path.")
        return 1

    # ---- chunk into jobs ----
    chunks = [all_files[i:i + FILES_PER_JOB] for i in range(0, n_files, FILES_PER_JOB)]
    n_jobs = len(chunks)
    print(f"Submitting {n_jobs} condor jobs ({FILES_PER_JOB} files per job)")

    # ---- prep tmp dir ----
    tmp_root = os.path.join(here, f"tmp_{mode}_{ver_out}")
    if os.path.exists(tmp_root):
        shutil.rmtree(tmp_root)
    os.makedirs(tmp_root)

    joblist_path = os.path.join(tmp_root, "joblist.txt")
    with open(joblist_path, "w") as jl:
        for jobid, chunk in enumerate(chunks, start=1):
            jobdir = os.path.join(tmp_root, f"job_{jobid}")
            os.makedirs(jobdir)

            filelist_path = os.path.join(jobdir, "files.txt")
            with open(filelist_path, "w") as fl:
                for f in chunk:
                    fl.write(f"root://maite.iihe.ac.be/{f}\n")

            jl.write(f"{jobid} {filelist_path}\n")

    # ---- prep output dir ----
    subprocess.run(["xrdfs", "root://maite.iihe.ac.be", "mkdir", "-p", outdir])
    subprocess.run(["xrdfs", "root://maite.iihe.ac.be", "mkdir", "-p", f"{outdir}/log"])

    # ---- submit ----
    submit_description = f"""
executable = /bin/bash
arguments = {here}/run.sh {mode} $(filelist) {outdir} $(jobid) {cmssw_src}
log    = {tmp_root}/job_$(jobid)/job_$(jobid).log
output = {tmp_root}/job_$(jobid)/job_$(jobid).out
error  = {tmp_root}/job_$(jobid)/job_$(jobid).err
JobBatchName = MINIAODSIM_{mode}_{year}_{ver_out}
request_cpus = 1
request_memory = 8G
request_disk = 5G
+JobFlavour = "longlunch"
notification = Never
max_retries = 0
should_transfer_files = NO

queue jobid, filelist from {joblist_path}
"""
    subprocess.run(["condor_submit"], input=submit_description.encode())
    return 0


if __name__ == "__main__":
    print("Submitting MINIAODSIM jobs to HTCondor...")
    sys.exit(submit_jobs())

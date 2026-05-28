import sys
import subprocess
import os
import shutil


def submit_jobs():
    # ---- config ----
    mode    = "etaToTMGamma"
    ver     = "20260508"
    year    = 2022
    nfirst  = 1
    nlast   = 100
    FILES_PER_JOB = 100   # 100 files / 10 = 10 jobs

    indir  = f"/store/user/sduponch/PhD/TMToEE/{mode}/{ver}/Simulation/MINIAODSIM/{year}"
    # gentrig output (small skim trees) -> EOS
    eosout = f"/eos/user/s/sduponch/TM/gentrig/{mode}/{ver}/{year}"

    here      = os.path.abspath(os.path.dirname(__file__))
    cmssw_src = "/afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_15_0_5/src"
    cfg       = f"{cmssw_src}/EDAnalyzer/Reconstruction/python/TrigObjectOrigin_cfg.py"

    # ---- build the explicit file list (files 1..100) ----
    all_files = [f"root://maite.iihe.ac.be/{indir}/output_{i}.root"
                 for i in range(nfirst, nlast + 1)]
    n_files = len(all_files)
    print(f"Targeting {n_files} files (output_{nfirst}..output_{nlast})")

    # ---- chunk into jobs ----
    chunks = [all_files[i:i + FILES_PER_JOB] for i in range(0, n_files, FILES_PER_JOB)]
    n_jobs = len(chunks)
    print(f"Submitting {n_jobs} condor jobs ({FILES_PER_JOB} files per job)")

    # ---- prep tmp dir (per-submission) ----
    tmp_root = os.path.join(here, f"tmp_gentrig_{mode}_{ver}")
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
                    fl.write(f"{f}\n")

            jl.write(f"{jobid} {filelist_path}\n")

    # ---- prep EOS output dir (via xrootd redirector, more reliable than fuse) ----
    subprocess.run(["eos", "root://eosuser.cern.ch", "mkdir", "-p", eosout])

    # ---- submit ----
    submit_description = f"""
executable = /bin/bash
arguments = {here}/run_gentrig.sh $(filelist) {eosout} $(jobid) {cfg} {cmssw_src}
log    = {tmp_root}/job_$(jobid)/job_$(jobid).log
output = {tmp_root}/job_$(jobid)/job_$(jobid).out
error  = {tmp_root}/job_$(jobid)/job_$(jobid).err
JobBatchName = gentrig_{mode}_{year}_{ver}
request_cpus = 1
request_memory = 2G
request_disk = 2G
+JobFlavour = "longlunch"
notification = Never
max_retries = 2
should_transfer_files = NO

queue jobid, filelist from {joblist_path}
"""
    subprocess.run(["condor_submit"], input=submit_description.encode())
    return 0


if __name__ == "__main__":
    print("Submitting GenTrigMatcher jobs...")
    sys.exit(submit_jobs())

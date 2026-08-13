import sys
import subprocess
import os

def submit_jobs():
    mode = "ppToTMeeX"
    year = 2022
    FILES_PER_JOB = 20

    # Input/output both on EOS, not IIHE -- worker nodes have shown
    # unreliable connectivity to maite.iihe.ac.be this session, while
    # root://eosuser.cern.ch/ was confirmed reachable from a worker node.
    indir  = "/eos/user/s/sduponch/PhD/ppToTMeeX/AODSIM/2022"
    outdir = f"/eos/user/s/sduponch/PhD/ppToTMeeX/Ntuples/{year}"

    # Direct POSIX read: this script runs on an EOS-mounted host, not a
    # worker node.
    all_files = sorted(f for f in os.listdir(indir) if f.endswith(".root"))
    n_files = len(all_files)
    print(f"Found {n_files} input files for {mode}")

    if n_files == 0:
        print("ERROR: no input files. Check indir.")
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
                    fl.write(f"root://eosuser.cern.ch/{indir}/{f}\n")

            jl.write(f"{jobid} {filelist_path}\n")

    os.makedirs(outdir, exist_ok=True)

    submit_description = f"""
executable = /bin/bash
arguments = {here}/run_ppToTMeeX.sh $(filelist) {outdir} $(jobid)
log    = {here}/tmp/job_$(jobid)/job_$(jobid).log
output = {here}/tmp/job_$(jobid)/job_$(jobid).out
error  = {here}/tmp/job_$(jobid)/job_$(jobid).err
JobBatchName = GenStudies_{mode}_{year}
request_cpus = 1
request_memory = 4G
request_disk = 2G
+JobFlavour = "longlunch"
notify_user = stef.duponcheel@cern.ch
notification = Error
max_retries = 2
should_transfer_files = NO

queue jobid, filelist from {joblist_path}
"""
    subprocess.run(["condor_submit"], input=submit_description.encode())


if __name__ == "__main__":
    print("Submitting GenStudies_ppToTMeeX jobs...")
    sys.exit(submit_jobs())

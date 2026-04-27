import sys
import subprocess
import os

def submit_jobs():

    ver = 20260424
    year = 2022
    mode = "etaToTMGamma"
    njobs = 100

    # Input is the AODSIM output from yesterday — produced in 124X but readable from 130X
    indir  = f"/store/user/sduponch/PhD/TMToEE/{mode}/{ver}/Simulation/AODSIM/{year}"
    outdir = f"/store/user/sduponch/PhD/TMToEE/{mode}/{ver}/Simulation/MINIAODSIM/{year}"

    os.makedirs("./tmp", exist_ok=True)
    joblist_path = "tmp/joblist.txt"
    with open(joblist_path, "w") as f:
        for i in range(1, njobs + 1):
            f.write(f"{i}\n")
            os.makedirs(f"./tmp/job_{i}", exist_ok=True)

    subprocess.run(["xrdfs", "root://maite.iihe.ac.be", "mkdir", "-p", f"{outdir}/log"])
    subprocess.run(["./mkconfig.sh", mode])
    scheduler_log = f"condor_logs/HTCondor_{mode}.log"
    if os.path.exists(scheduler_log):
        os.remove(scheduler_log)

    submit_description = f"""
executable = run.sh
arguments = {mode} {indir} {outdir} $(jobid)
log    = /afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_13_0_13/src/MINIAODSIM/tmp/job_$(jobid)/job_$(jobid).log
output = /afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_13_0_13/src/MINIAODSIM/tmp/job_$(jobid)/job_$(jobid).out
error  = /afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_13_0_13/src/MINIAODSIM/tmp/job_$(jobid)/job_$(jobid).err
JobBatchName = MC_{mode}_MINIAODSIM_{year}_{ver}
request_cpus = 1
request_memory = 4G
request_disk = 10M
+JobFlavour = "espresso"
notify_user = stef.duponcheel@cern.ch
notification = Error
max_retries = 0
should_transfer_files = NO

queue jobid from {joblist_path}
"""
    subprocess.run(["condor_submit"], input=submit_description.encode())

if __name__ == "__main__":
    print("Submitting jobs to HTCondor...")
    sys.exit(submit_jobs())

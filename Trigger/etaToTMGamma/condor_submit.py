import sys
import subprocess
import os

def submit_job():
    here = os.path.abspath(os.path.dirname(__file__))
    
    os.makedirs(os.path.join(here, "tmp"), exist_ok= True)

    submit_description = f"""
    executable = /bin/bash
    arguments  = {here}/run.sh
    log    = {here}/tmp/job.log
    output = {here}/tmp/job.out
    error  = {here}/tmp/job.err
    JobBatchName = TrigEff_etaToTMGamma
    request_cpus = 1
    request_memory = 4G
    request_disk = 5G
    +JobFlavour = "tomorrow"
    notify_user = stef.duponcheel@cern.ch
    notification = Always
    max_retries = 0
    should_transfer_files = NO

    queue 1
    """
    subprocess.run(["condor_submit"], input=submit_description.encode())


if __name__ == "__main__":
    print("Submitting trigger analysis job...")
    sys.exit(submit_job())

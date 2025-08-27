#!/usr/env python
# -*- coding: utf-8 -*-
"""Simple SLURM job submission interface."""

import shutil
import os
import subprocess
import time
import sys

from subprocess import Popen, PIPE, STDOUT

import hostlist

class Slurm(object):
    """SLURM Interface class"""

    def __init__(self):
        """Slurm constructor"""
        self.partitions = []
        self.node_lists = {}
        self.verbose = True
        self.job_output_dir = ""

        if not os.path.exists(self.job_output_dir) and self.job_output_dir != "":
            os.makedirs(self.job_output_dir)

    def is_exec_available(self, executable):
        """Check if executable is available"""
        exec_found = shutil.which(executable)
        #if self.verbose:
        #    print("Executable %s is %s" % (executable, "found" if exec_found else "not found"))
        return shutil.which(executable) is not None

    def check_environment(self):
        """Check if SLURM commands are available"""

        self.sbatch_available = self.is_exec_available("sbatch")
        self.squeue_available = self.is_exec_available("squeue")
        self.scancel_available = self.is_exec_available("scancel")
        self.sinfo_available = self.is_exec_available("sinfo")

        return self.sbatch_available and self.squeue_available and self.scancel_available and self.sinfo_available


    def __include_part(self, part, exclude_set):
        include = True

        if len(exclude_set)>0:
            for exclude_pattern in exclude_set:
                if exclude_pattern in part:
                    include = False

        return include

    def query_partitions(self, exclude_set={}):
        """Query partitions in slurm."""
        p = Popen("sinfo", stdout=PIPE, stderr=PIPE,
                  shell=True, universal_newlines=True)
        squeue_output = p.communicate()[0].split("\n")

        self.partitions = []
        self.node_lists = {}

        part_lines = squeue_output[1:]

        for line in part_lines:
            if line != "":
                part_name = line.split()[0].strip()
                node_list = line.split()[5]
                if part_name.find("*") != -1:
                    part_name = part_name[:-1]
                if self.__include_part(part_name, exclude_set):
                    self.partitions.append(part_name)
                    if part_name in self.node_lists:
                        self.node_lists[part_name] = self.node_lists[part_name] + \
                            hostlist.expand_hostlist(node_list)
                    else:
                        self.node_lists[part_name] = hostlist.expand_hostlist(
                            node_list)

        self.partitions = list(set(self.partitions))


    """
    NodeName=eg24 Arch=x86_64 CoresPerSocket=8
       CPUAlloc=0 CPUErr=0 CPUTot=16 CPULoad=0.01
       AvailableFeatures=rack-f1,kepler,mem96GB,gpu8k20
       ActiveFeatures=rack-f1,kepler,mem96GB,gpu8k20
       Gres=gpu:k20:6
       NodeAddr=eg24 NodeHostName=eg24 Version=17.02
       OS=Linux RealMemory=94000 AllocMem=0 FreeMem=94163 Sockets=2 Boards=1
       State=IDLE ThreadsPerCore=1 TmpDisk=0 Weight=1 Owner=N/A MCS_label=N/A
       Partitions=lvis 
       BootTime=2018-02-05T18:02:37 SlurmdStartTime=2018-02-05T18:05:18
       CfgTRES=cpu=16,mem=94000M
       AllocTRES=
       CapWatts=n/a
       CurrentWatts=0 LowestJoules=0 ConsumedJoules=0
       ExtSensorsJoules=n/s ExtSensorsWatts=0 ExtSensorsTemp=n/s
    """

    def query_node(self, node):
        """Query information on node"""
        p = Popen("scontrol show node %s" % node, stdout=PIPE,
                  stderr=PIPE, shell=True, universal_newlines=True)
        scontrol_output = p.communicate()[0].split("\n")

        node_dict = {}

        for line in scontrol_output:
            var_pairs = line.strip().split(" ")
            if len(var_pairs) >= 1:
                for var_pair in var_pairs:
                    if len(var_pair) > 0:
                        if var_pair.find("=") != -1:
                            var_name = var_pair.split("=")[0]
                            var_value = var_pair.split("=")[1]
                            node_dict[var_name] = var_value

        return node_dict

    def query_nodes(self):
        """Query information on node"""
        p = Popen("scontrol show nodes -o", stdout=PIPE,
                  stderr=PIPE, shell=True, universal_newlines=True)
        scontrol_output = p.communicate()[0].split("\n")

        node_dict = {}

        current_node_name = ""

        for line in scontrol_output:
            var_pairs = line.strip().split(" ")
            if len(var_pairs) >= 1:
                for var_pair in var_pairs:
                    if len(var_pair) > 0:
                        if var_pair.find("=") != -1:
                            var_name = var_pair.split("=")[0]
                            var_value = var_pair.split("=")[1]

                            if var_name == "NodeName":
                                current_node_name = var_value
                                node_dict[var_value] = {}
                            else:
                                node_dict[current_node_name][var_name] = var_value

        return node_dict
    
    def query_reservations(self):
        """Query SLURM reservations"""

        """
        ReservationName=lu2023-2-82 StartTime=2023-10-16T14:38:40 EndTime=2040-01-01T00:00:00 Duration=5920-10:21:20
        Nodes=cx[02-03] NodeCnt=2 CoreCnt=96 Features=(null) PartitionName=(null) Flags=IGNORE_JOBS,SPEC_NODES
        TRES=cpu=96
        Users=(null) Groups=(null) Accounts=lu2023-2-82 Licenses=(null) State=ACTIVE BurstBuffer=(null) Watts=n/a
        MaxStartDelay=(null)

        ReservationName=lu2023-2-18 StartTime=2023-11-02T14:26:25 EndTime=2040-01-01T00:00:00 Duration=5903-09:33:35
        Nodes=ca[01-18] NodeCnt=18 CoreCnt=360 Features=(null) PartitionName=(null) Flags=IGNORE_JOBS,SPEC_NODES
        TRES=cpu=360
        Users=(null) Groups=(null) Accounts=lu2023-2-18 Licenses=(null) State=ACTIVE BurstBuffer=(null) Watts=n/a
        MaxStartDelay=(null)

        ReservationName=reimann StartTime=2024-03-21T08:57:04 EndTime=2040-01-01T00:00:00 Duration=5763-15:02:56
        Nodes=ca[19-22] NodeCnt=4 CoreCnt=96 Features=(null) PartitionName=(null) Flags=IGNORE_JOBS,SPEC_NODES
        TRES=cpu=96
        Users=(null) Groups=(null) Accounts=lu2024-2-46 Licenses=(null) State=ACTIVE BurstBuffer=(null) Watts=n/a
        MaxStartDelay=(null)

        ReservationName=RPJM-course StartTime=2024-10-24T09:00:00 EndTime=2024-10-24T16:00:00 Duration=07:00:00
        Nodes=cn[157-158] NodeCnt=2 CoreCnt=96 Features=(null) PartitionName=(null) Flags=IGNORE_JOBS,DAILY,SPEC_NODES
        TRES=cpu=96
        Users=(null) Groups=(null) Accounts=lu2024-7-80 Licenses=(null) State=INACTIVE BurstBuffer=(null) Watts=n/a
        MaxStartDelay=(null)        
        """

        p = Popen("scontrol show res", stdout=PIPE,
                  stderr=PIPE, shell=True, universal_newlines=True)
        scontrol_output = p.communicate()[0].split("\n")

        reservations = []

        for line in scontrol_output:
            if line.find("ReservationName") != -1:
                reservation = {}
                parts = line.split(" ")
                for part in parts:
                    if part.find("=") != -1:
                        key = part.split("=")[0]
                        value = part.split("=")[1]
                        reservation[key] = value

            elif line.find("Nodes") != -1:
                parts = line.split(" ")
                for part in parts:
                    if part.find("=") != -1:
                        key = part.split("=")[0]
                        value = part.split("=")[1]
                        reservation[key] = value

            elif line.find("Users") != -1:
                parts = line.split(" ")
                for part in parts:
                    if part.find("=") != -1:
                        key = part.split("=")[0]
                        value = part.split("=")[1]
                        reservation[key] = value

                reservations.append(reservation)

        return reservations

    def __include_feature(self, feature, exclude_set):
        include = True
        for exclude_pattern in exclude_set:
            if exclude_pattern in feature:
                include = False

        return include

    def query_features(self, part, exclude_set={}):
        """Query features of partition"""

        if self.verbose:
            print(f"Querying {part} for features ...")

        node_info = self.query_nodes()

        feature_list = []

        for node in list(node_info.keys()):
            if "Partitions" in node_info[node]:
                if node_info[node]["Partitions"] == part:
                    features = node_info[node]["ActiveFeatures"].split(",")
                    for feature in features:
                        if self.__include_feature(feature, exclude_set):
                            feature_list.append(feature)

        return list(set(feature_list))

    def query_gres(self, part):
        """Query features of partition"""

        node_list = self.node_lists[part]

        gres_list = []

        for node in node_list:
            node_info = self.query_node(node)

            gres = node_info["Gres"].split(",")
            gres_list.extend(gres)

        return list(set(gres_list))

    def submit(self, job, account=''):
        """Submit job to SLURM"""

        p = Popen("sbatch", stdout=PIPE, stdin=PIPE, stderr=PIPE,
                  shell=True, universal_newlines=True)

        sbatch_stdout, sbatch_stderr = p.communicate(input=job.script)
        sbatch_output = sbatch_stdout.strip()
        sbatch_error = sbatch_stderr.strip()

        # Store error info in job
        job.error_info = sbatch_error if sbatch_error else None

        if sbatch_output.find("Submitted batch") != -1:
            job.id = int(sbatch_output.split()[3])
            return True
        else:
            job.id = -1
            return False

    def job_status(self, job):
        """Query status of job"""
        p = Popen("squeue -j " + str(job.id) + " -t PD,R -h -o '%t;%N;%L;%M;%l'",
                  stdout=PIPE, stderr=PIPE, shell=True, universal_newlines=True)
        
        squeue_output = p.communicate()[0].strip().split(";")

        #print(squeue_output)

        if len(squeue_output) > 1:
            job.status = squeue_output[0]
            job.nodes = squeue_output[1]
            job.timeLeft = squeue_output[2]
            job.timeRunning = squeue_output[3]
            job.timeLimit = squeue_output[4]
        else:
            job.status = ""
            job.nodes = ""
            job.timeLeft = ""
            job.timeRunning = ""
            job.timeLimit = ""

    def cancel_job_with_id(self, jobid):
        """Cancel job"""
        result = subprocess.call("scancel %d" % (jobid), shell=True)
        return result

    def cancel_job(self, job):
        """Cancel job"""
        try:
            result = subprocess.call("scancel %d" % (job.id), shell=True)
            job.id = -1
            job.status = ""
        except:
            return -1

        return result

    def job_output(self, job):
        """Query job output"""

        output_filename = os.path.join(job.output_dir, job.stdout_filename)

        if os.path.exists(output_filename):
            output_file = open(output_filename, "r")
            output = output_file.readlines()
            output_file.close()
            return output
        else:
            print("Couldn't find: "+output_filename)
            return []

    def wait_for_start(self, job):
        """Wait for job to start"""
        self.job_status(job)

        while job.status != "R":
            self.job_status(job)
            time.sleep(1)

    def is_running(self, job):
        self.job_status(job)
        return job.status == "R"

    def has_started(self, job):
        """Query if job has started"""
        self.job_status(job)
        return job.status == "R"

    def is_waiting(self, job):
        """Query if job is in an non-running state"""
        self.job_status(job)
        return job.status != "R"


if __name__ == "__main__":

    import whisper

    job = whisper.WhisperJob()
    job.account = "lu-test"
    job.part = "lu48"
    job.output_dir = "/home/bmjl/Development/job-submitter/output"
    job.setup()

    slurm = Slurm()

    if not slurm.submit(job):
        print("Failed to submit job")
        sys.exit(1)

    print("Job submitted with ID:", job.id)

    slurm.job_status(job)
    
    while job.status!="":
        slurm.job_status(job)
        print(job.status)
        time.sleep(1)

    output = slurm.job_output(job)

    print("Job output:")
    print("\n".join(output))

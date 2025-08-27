#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

whisper_test_template = """#!/bin/bash
#SBATCH -p {part}
{account_line}
#SBATCH -t {walltime} 
#SBATCH -J {jobname}
#SBATCH -o {output_dir}/{jobname}_%j.out
#SBATCH -e {output_dir}/{jobname}_%j.err

hostname 

echo "Loading modules" 

module purge 
module load GCC/12.3.0  OpenMPI/4.1.5 
module load Whisper/1.3.0 

echo 
echo "Starting transcription" && date 

echo whisper {audio_file} --language {language} --task {task} --device {device} --output_format {output_format} --model {model} --model_dir  $WHISPER_MODELS --output_dir {output_dir} --verbose

sleep 10

echo "Transcription ended" && date
"""

whisper_template = """#!/bin/bash 
#SBATCH -p {part}
{account_line}
#SBATCH -t {walltime}
#SBATCH -J {jobname}
#SBATCH -o {output_dir}/{jobname}_%j.out
#SBATCH -e {output_dir}/{jobname}_%j.err

hostname 

echo "Loading modules" 

module purge 
module load GCC/12.3.0  OpenMPI/4.1.5 
module load Whisper/1.3.0 

echo 
echo "Starting transcription" && date 

whisper {audio_file} --language {language} --task {task} --device {device} --output_format {output_format} --model {model} --model_dir  $WHISPER_MODELS --output_dir {output_dir} --verbose True

echo "Transcription ended" && date
"""

class WhisperJob:
    def __init__(self, part="gpua100", walltime="00:15:00", jobname="whisper_transcription", audio_file="audio.mp3", language="en", task="transcribe", device="cuda:0", output_format="txt", model="medium", model_dir="$WHISPER_MODELS", output_dir=".", account=""):
        self.part = part
        self.walltime = walltime
        self.jobname = jobname
        self.audio_file = audio_file
        self.language = language
        self.task = task
        self.device = device
        self.output_format = output_format
        self.model = model
        self.model_dir = model_dir
        self.output_dir = output_dir
        self.account = account
        self.id = 0
        self.dummy_job = True
        self.output = ""

    def check(self):
        if not os.path.exists(self.audio_file):
            raise FileNotFoundError(f"Audio file not found: {self.audio_file}")
        if not os.path.exists(self.output_dir):
            raise FileNotFoundError(f"Output directory not found: {self.output_dir}")

    def setup(self):
        self.output = ""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_script(self):

        account_line = f"#SBATCH -A {self.account}" if self.account else ""

        if self.dummy_job:
            return whisper_test_template.format(
                part=self.part,
                walltime=self.walltime,
                jobname=self.jobname,
                audio_file=self.audio_file,
                language=self.language,
                task=self.task,
                device=self.device,
                output_format=self.output_format,
                model=self.model,
                output_dir=self.output_dir,
                account_line=account_line
            )
        else:
            return whisper_template.format(
                part=self.part,
                walltime=self.walltime,
                jobname=self.jobname,
                audio_file=self.audio_file,
                language=self.language,
                task=self.task,
                device=self.device,
                output_format=self.output_format,
                model=self.model,
                output_dir=self.output_dir,
                account_line=account_line
            )

    def __str__(self):
        return self.generate_script()
    
    @property
    def script(self):
        return self.generate_script()
    
    @property 
    def stdout_filename(self):
        return f"{self.jobname}_{self.id}.out"
    
    @property
    def stderr_filename(self):
        return f"{self.jobname}_{self.id}.err"

if __name__ == "__main__":

    job = WhisperJob()
    print(job)
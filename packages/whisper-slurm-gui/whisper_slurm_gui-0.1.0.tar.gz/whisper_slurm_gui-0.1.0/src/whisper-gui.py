#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Job submission GUI for Whisper ASR jobs."""

whisper_gui_version = "0.1.0"

import sys
import time
import subprocess
import os

from enum import Enum, auto

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal   

os.environ['QT_QPA_PLATFORMTHEME'] = 'gnome'
QIcon.setThemeName('Adwaita')

from ui_loader import load_ui
from whisper import WhisperJob
from lrms_simple import Slurm

class JobStatus(Enum):
    """Enumeration for job status."""
    SUBMITTING = auto()
    SUBMITTED = auto()
    RUNNING = auto()
    FINISHED = auto()
    FAILED = auto()
    CANCELLED = auto()
    UNKNOWN = auto()

class JobSubmitThread(QThread):
    """Thread for submitting jobs to the scheduler."""

    status_update = pyqtSignal(object)  # Will emit JobStatus
    error = pyqtSignal(str)
    submitted = pyqtSignal(str)
    submit_failure = pyqtSignal(int, str)

    def __init__(self, job):
        """Initialize the job submission thread."""
        
        super().__init__()
        self.job = job

        self.slurm = Slurm()
        self.cancel = False
        self.output = []

    def run(self):
        """Run the job submission thread."""

        self.status_update.emit(JobStatus.SUBMITTING)
        if not self.slurm.submit(self.job):
            self.status_update.emit(JobStatus.FAILED)
            self.error.emit("Failed to submit job: \n\n" + str(self.job))
            print("submit_failure -> ", self.job.id, self.job.error_info)
            self.submit_failure.emit(self.job.id, self.job.error_info)
            return

        self.submitted.emit(str(self.job.id))

        self.status_update.emit(JobStatus.SUBMITTED)
        self.slurm.job_status(self.job)

        emit_once = False

        while self.job.status != "" and not self.cancel:
            self.slurm.job_status(self.job)
            if self.job.status == "R" and not emit_once:
                self.status_update.emit(JobStatus.RUNNING)
                emit_once = True
            time.sleep(1)

        self.job.output = self.slurm.job_output(self.job)
        self.status_update.emit(JobStatus.FINISHED)

        if self.cancel:
            self.slurm.cancel_job(self.job)
            self.status_update.emit(JobStatus.CANCELLED)

class WhisperSubmitGUI(QtWidgets.QWidget):
    """Job submitter GUI class for Whisper ASR jobs."""

    def __init__(self):
        """Initialize the job submitter GUI."""
        super().__init__()

        # Load UI

        from ui_loader_utils import get_ui_path
        load_ui(get_ui_path('job-submitter.ui'), self)

        # Create job instance

        self.job = WhisperJob()
        self.job.dummy_job = False

        # Don't create the thread yet

        self.submit_thread = None

        # Update controls with job information

        self.update_controls()

    def update_job(self):
        """Update the job instance with values from the UI."""

        self.job.part = self.part_combo.currentText()
        self.job.walltime = self.walltime_edit.text()
        self.job.jobname = self.jobname_edit.text()
        self.job.audio_file = self.audio_filename_edit.text()
        self.job.language = self.language_combo.currentText()
        self.job.account = self.account_edit.text()
        #self.job.task = self.task_input.text()
        #self.job.device = self.device_input.text()
        self.job.output_format = self.output_format_combo.currentText()
        self.job.model = self.model_combo.currentText()
        #self.job.model_dir = self.model_dir_edit.text()
        self.job.output_dir = self.output_dir_edit.text()

    def update_controls(self):
        """Update the UI controls with the current job information."""

        self.part_combo.setCurrentText(self.job.part)
        self.walltime_edit.setText(self.job.walltime)
        self.jobname_edit.setText(self.job.jobname)
        self.audio_filename_edit.setText(self.job.audio_file)
        self.language_combo.setCurrentText(self.job.language)
        self.account_edit.setText(self.job.account)
        #self.task_input.setText(self.job.task)
        #self.device_input.setText(self.job.device)
        self.output_format_combo.setCurrentText(self.job.output_format)
        self.model_combo.setCurrentText(self.job.model)
        #self.model_dir_edit.setText(self.job.model_dir)
        self.output_dir_edit.setText(self.job.output_dir)
        self.version_label.setText("whisper-gui-" + whisper_gui_version)

    def set_status(self, status):
        """Update the status control with the current job status."""

        # Map status to color and text

        color_map = {
            'SUBMITTING': ('rgb(249, 240, 107)', 'Submit'),
            'SUBMITTED': ('rgb(249, 240, 107)', 'Waiting'),
            'RUNNING': ('rgb(143, 240, 164)', 'Running'),
            'FINISHED': ('rgb(222, 221, 218)', 'Finished'),
            'FAILED': ('rgb(246, 97, 81)', 'Failed'),
            'CANCELLED': ('rgb(222, 221, 218)', 'Cancelled'),
            'UNKNOWN': ('rgb(222, 221, 218)', 'Unknown'),
        }

        # If using enum, get name

        if hasattr(status, 'name'):
            status_name = status.name
        else:
            status_name = str(status)

        # Map status to color and text

        color, text = color_map.get(status_name, ('lightgray', status_name))
        self.status_label.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
        self.status_label.setText(text)

    @pyqtSlot()
    def on_select_audio_file_button_clicked(self):
        """Open a file dialog to select an audio file."""

        options = QtWidgets.QFileDialog.Options()

        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.wav)", options=options)

        if file_name:
            self.audio_filename_edit.setText(file_name)
            self.output_dir_edit.setText(os.path.dirname(file_name))

    @pyqtSlot()
    def on_select_output_dir_button_clicked(self):
        """Open a file dialog to select an output directory."""

        options = QtWidgets.QFileDialog.Options()

        dir_name = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory", "", options=options)

        if dir_name:
            self.output_dir_edit.setText(dir_name)

    @pyqtSlot()
    def on_submit_button_clicked(self):
        """Submit the job for processing."""

        # Update job information from UI

        self.update_job()
        self.job.setup()

        # Validate job information

        try:
            self.job.check()
        except FileNotFoundError as e:
            QMessageBox.information(self, "Job input validation", f"{e}")
            self.log_text.appendPlainText("Error: " + str(e))
            return

        # Create submit thread

        self.submit_thread = JobSubmitThread(self.job)
        self.submit_thread.status_update.connect(self.on_status_update)
        self.submit_thread.error.connect(self.on_error)
        self.submit_thread.submitted.connect(self.on_submitted)
        self.submit_thread.finished.connect(self.on_finished)
        self.submit_thread.submit_failure.connect(self.on_submit_failure)
        self.submit_thread.start()

        # Disable the submit button

        self.submit_button.setEnabled(False)

    @pyqtSlot()
    def on_stop_button_clicked(self):
        """Stop the job if it is running."""

        # We can't stop anything if we haven't created a thread

        if self.submit_thread == None:
            return

        # If we have a thread, we can stop it

        if self.submit_thread.isRunning():
            self.submit_thread.cancel = True
            self.log_text.appendPlainText("Cancelling job...")

        # Enable the submit button again

        self.submit_button.setEnabled(True)

    @pyqtSlot()
    def on_close_button_clicked(self):
        """Close the application."""

        if self.submit_thread == None:
            self.close()

        # If we have a running job, we need to cancel it

        if self.submit_thread.isRunning():
            self.submit_thread.cancel = True
            self.log_text.appendPlainText("Cancelling job...")

        self.close()

    @pyqtSlot(object)
    def on_status_update(self, status):
        """Update the status label and log."""

        status_str = status.name if hasattr(status, 'name') else str(status)
        self.log_text.appendPlainText("Job status updated: " + status_str)
        self.set_status(status)

    @pyqtSlot(str)
    def on_error(self, error):
        """Handle job error."""
        self.log_text.appendPlainText("Job error: " + error)

    @pyqtSlot(str)
    def on_submitted(self, job_id):
        """Handle job submission."""
        self.log_text.appendPlainText("Job submitted with ID: " + job_id)

    @pyqtSlot()
    def on_finished(self):
        """Handle job completion."""
        self.log_text.appendPlainText("Job finished")
        self.log_text.appendPlainText("Job output: \n\n" + '\n'.join(self.submit_thread.output))
        self.submit_button.setEnabled(True)

        if len(self.job.output)>0:
            subprocess.Popen(['xdg-open', self.job.output_dir])

    @pyqtSlot(int, str)
    def on_submit_failure(self, job_id, error_info):
        """Handle job submission failure."""

        # Parse the error output

        human_error_message = ""

        if "default project" in error_info:
            human_error_message = "You are member of multiple projects or you don't have a default project assigned." \
                                  "Please set the project name in the 'Project' field."
        elif "Invalid account" in error_info and "does not exist" in error_info:
            human_error_message = "The combination of project and partition is invalid. Please check the " \
                                  "'Project' and 'Partition' fields."

        QMessageBox.information(self, "Job Submission Failed",
                             f"Job submission failed: {human_error_message}")

        self.log_text.appendPlainText(f"Job submission failed: {human_error_message}")

    @pyqtSlot()
    def on_show_usage_button_clicked(self):
        """Show usage information."""
        subprocess.Popen(['gfxusage'])

def main():

    # Make sure src is in the Python path

    src_dir = os.path.dirname(os.path.abspath(__file__))

    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    # Start the application

    app = QtWidgets.QApplication(sys.argv)
    window = WhisperSubmitGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

"""Scripts for creating and launching BlackDynamite studies"""

import os
import subprocess
import shutil
from BlackDynamite.scripts import createDB, bd_zeo_server
from BlackDynamite import bdparser

################################################################


def create_bd_study(task_manager):
    if not os.path.exists(task_manager.study_dir):
        raise RuntimeError(f"not existing study dir {task_manager.study_dir}")

    # Stop any existing BD server and delete files
    if os.path.exists(task_manager.study_dir):
        subprocess.run(["canYouDigIt", "server", "stop"], cwd=task_manager.study_dir)
        # make a bd command to do the cleaning (to be working in remate also)
        subprocess.run(["git", "clean", "-fxd", task_manager.study_dir])

    os.makedirs(task_manager.bd_dir, exist_ok=True)

    cwd = os.getcwd()
    os.chdir(task_manager.study_dir)
    # TODO: BD seems not to allow to create servers using tcp => fix this in BD
    createDB.main(["--truerun", "--study", task_manager.study])
    bd_zeo_server.main(["--action", "stop"])
    bd_zeo_server.main(
        [
            "--action",
            "start",
            "--host",
            task_manager.host,
            "--study",
            task_manager.study,
        ]
    )
    os.chdir(cwd)


################################################################
def remote_launch(study, study_dir, study_files, host, ssh, local_dir):
    try:
        # Remove previous database
        cmd = f"mkdir -p {study_dir}; "
        cmd += f"cd {study_dir}; "
        cmd += "canYouDigIt server stop; "
        cmd += "rm -rf * .bd"
        ssh.cmd(cmd)
        ssh.copy(study_files, study_dir)
        # Initialize database
        cmd = f"cd {study_dir}; "
        cmd += "canYouDigIt init --truerun; "
        cmd += "canYouDigIt server stop; "
        cmd += f"canYouDigIt server start --host zeo://{host} --study {study}"
        ssh.cmd(cmd)
    except subprocess.CalledProcessError as e:
        print(e.stderr)

    # Assume that we want to access from the current work dir, create jobs/runs etc., we
    # need all files and a dummy .db folder in it
    if local_dir is not None:
        local_study_dir = local_dir + "/" + study
        os.makedirs(local_study_dir + "/.bd", exist_ok=True)
        for f in study_files:
            try:
                shutil.copy(f, local_study_dir)
            except shutil.SameFileError:
                pass


################################################################
def create_bd_studies(
    workflow,
    validated=None,
):
    if validated is None or not validated:
        validated = bdparser.validate_question(
            "Reset and drop content of Kusanagi database", {"yes": False}, False
        )
    if validated is False:
        return

    for name, task_manager in workflow.task_managers.items():
        create_bd_study(task_manager)


################################################################
class SSH:
    def __init__(self, host, user, port=None, profile=""):
        self.host = host
        self.user = user
        self.profile = profile

        self.remote = f"{user}@{host}"

        self.ssh_cmd = ["ssh"]
        self.scp_cmd = ["scp"]
        if port is not None:
            self.ssh_cmd += ["-p", f"{port}"]
            self.scp_cmd += ["-P", f"{port}"]

    def cmd(self, cmd):
        if self.profile == "":
            result = subprocess.run(self.ssh_cmd + [self.remote, cmd])
        else:
            result = subprocess.run(
                self.ssh_cmd + [self.remote, f"source {self.profile}; {cmd}"]
            )
        print(result.stdout)

    def copy(self, files, dest):
        result = subprocess.run(self.scp_cmd + files + [f"{self.remote}:{dest}"])
        print(result.stdout)

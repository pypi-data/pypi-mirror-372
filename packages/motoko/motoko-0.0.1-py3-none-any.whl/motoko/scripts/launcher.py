#!/usr/bin/env python3

from motoko.workflow import Workflow

command = "launcher"
command_help = "Spawn the launcher daemon"


def populate_arg_parser(parser):
    pass


def main(args):
    fullpath = "motoko.yaml"
    wf = Workflow(fullpath)
    wf.start_launcher_daemons()

    # for name, task_manager in wf.task_managers.items():
    #     subprocess.call(
    #         "canYouDigIt launch_daemon --start --detach",
    #         cwd=task_manager.study_dir,
    #         shell=True,
    #     )

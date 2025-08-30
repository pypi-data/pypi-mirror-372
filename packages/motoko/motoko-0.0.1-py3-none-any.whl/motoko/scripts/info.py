#!/usr/bin/env python3

import subprocess
from motoko.workflow import Workflow

command = "info"
command_help = "Get info from sub-studies"


def populate_arg_parser(parser):
    parser.add_argument("--verbose", action="store_true", help="show verbose details")


def main(args):
    fullpath = "motoko.yaml"
    wf = Workflow(fullpath)

    for name, task_manager in wf.task_managers.items():
        print("*" * 30)
        print(f"TaskManager: {name}")
        print("*" * 30)
        if not args.verbose:
            subprocess.call("canYouDigIt info", cwd=task_manager.study_dir, shell=True)

        else:
            subprocess.call(
                "canYouDigIt jobs info", cwd=task_manager.study_dir, shell=True
            )
            subprocess.call(
                "canYouDigIt runs info", cwd=task_manager.study_dir, shell=True
            )
            subprocess.call(
                "canYouDigIt launch_daemon --status",
                cwd=task_manager.study_dir,
                shell=True,
            )

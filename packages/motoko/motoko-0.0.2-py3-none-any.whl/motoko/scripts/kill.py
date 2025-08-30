#!/usr/bin/env python3

import subprocess

from motoko.workflow import Workflow

command = "kill"
command_help = "Kill all the running daemons"


def populate_arg_parser(parser):
    parser.add_argument("--verbose", action="store_true", help="show verbose details")


def main(args):
    fullpath = "motoko.yaml"

    wf = Workflow(fullpath)

    for name, task_manager in wf.task_managers.items():
        print(f"Kill daemons in study: {task_manager.study}")
        cmds = ["canYouDigIt launch_daemon --stop", "canYouDigIt server stop"]
        for cmd in cmds:
            if args.verbose:
                print(f"({task_manager.study}) {cmd}")
            subprocess.call(cmd, cwd=task_manager.study_dir, shell=True)

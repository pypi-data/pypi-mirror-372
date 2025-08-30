#!/usr/bin/env python3

import os
from motoko.workflow import Workflow

command = "create"
command_help = "Create the sub studies of the workflow"


def populate_arg_parser(parser):
    parser.add_argument(
        "--validated",
        action="store_true",
        help="Answer yes to validation questions",
    )
    parser.add_argument(
        "directory",
        type=str,
        default="./",
        help="Directory where the description of the workflow is provided",
    )


def main(args):
    fullpath = os.path.join(args.directory, "motoko.yaml")

    wf = Workflow(fullpath)
    wf.create(args.validated)
    return wf

#!/usr/bin/env python3

import os
import sys
import importlib.util
from BlackDynamite.scripts.launch_daemon import find_pids

from motoko.workflow import Workflow

command = "orchestrator"
command_help = "Start the workflow"


def populate_arg_parser(parser):
    subparsers = parser.add_subparsers(dest="what")
    parser_start = subparsers.add_parser("start", help="start orchestrator daemon")

    parser_start.add_argument(
        "--detach",
        "-d",
        action="store_true",
        help="For starting: run in detach/daemon mode with Zdaemon manager",
    )
    parser_start.add_argument(
        "--wait",
        type=str,
        default=5,
        help="Waiting time between state checks in seconds",
    )

    # Add arguments specific to workflow

    fullpath = "motoko.yaml"
    wf = Workflow(fullpath)

    fname, _ = wf.orchestrator_script.split(".")
    file_path = os.path.join(wf.directory, fname + ".py")
    module_name = "orchestrator"
    print(f"loading {file_path}")
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    parser_function = getattr(module, "populate_arg_parser")
    parser_function(parser_start)

    # parser_stop = subparsers.add_parser("stop", help="stop orchestrator daemon")
    # parser_stat = subparsers.add_parser(
    #     "status", help="get status of detached orchestrator daemon"
    # )


def main(args):
    fullpath = "motoko.yaml"
    wf = Workflow(fullpath)
    wf_root_dir = wf.directory
    wf_conf_dir = os.path.join(wf_root_dir, ".wf")

    conf_fname = os.path.join(wf_conf_dir, "wf.conf")

    if args.what == "start" and not args.detach:
        params = vars(args)
        wf.execute(**params)
        sys.exit(0)

    elif args.what == "start" and args.detach:
        exclude = ["--detach", "-d"]
        argv = sys.argv[3:]
        clargs = " ".join([a for a in argv if a not in exclude])

        prog = f"motoko {command} start {clargs}"

        zdaemon_conf = f"""
<runner>
 program {prog}
 socket-name {wf_conf_dir}/wf.socket
 transcript {wf_conf_dir}/wf.log
 exit-codes 0
</runner>
"""

        os.makedirs(wf_conf_dir, exist_ok=True)
        with open(conf_fname, "w") as f:
            f.write(zdaemon_conf)

        os.system(f"zdaemon -C {conf_fname} start")
        os.system(f"zdaemon -C {conf_fname} status")

    elif args.what == "status":
        print("ZDaemon status:")
        os.system(f"zdaemon -C {conf_fname} status")

        pids = find_pids(wf_root_dir)
        print(f"Running orchestrator pids: {pids}")

    elif args.what == "stop":
        os.system(f"zdaemon -C {conf_fname} stop")
        pids = find_pids(wf_root_dir)
        if pids:
            print(f"Killing: {pids}")
            pids = [str(e) for e in pids]
            os.system(f"kill -9 {' '.join(pids)}")

        # import shutil
        # shutil.rmtree(wf_conf_dir)

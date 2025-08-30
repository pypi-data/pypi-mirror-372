#!/usr/bin/env python
# coding: utf-8

import math
import os
import pytest
import argparse
import subprocess

from motoko.scripts.create_studies import main as create_task_managers

################################################################
test_dir = os.path.dirname(__file__)
workflow_dir = os.path.join(test_dir, "workflow")
# sys.path.append(os.path.join(test_dir, "workflow"))
# from launch import main as main_daemon

################################################################


@pytest.fixture
def workflow():
    args = argparse.Namespace()
    args.directory = workflow_dir
    args.validated = True

    subprocess.call("motoko kill", shell=True, cwd=workflow_dir)
    workflow = create_task_managers(args)
    print("workflow task managers created")
    yield workflow
    # subprocess.call("motoko kill", shell=True, cwd=workflow_dir)


def test_create_db(workflow):
    pass


def test_execute_pipeline(workflow):
    x = [2.1, 3.2]  # input

    print("Launch studies launcher daemons")
    workflow.start_launcher_daemons()
    print("Start the workflow")
    workflow.execute(inputs=x)
    print("commit results")
    workflow.commit()

    val = (
        (0.342 * x[0] + 0.56 - 3.3) ** 2
        + (-2.31 * x[0] + 0.56 - 2.34) ** 2
        + (0.342 * x[1] + 0.56 - 0.148) ** 2
    )

    y1_ref = 0.342 * val
    y2_ref = 0.342 * math.sqrt(val)

    print("y1_ref =", y1_ref)
    print("y2_ref =", y2_ref)

    run_ids = [e for e in workflow.mult.base.runs.keys()]
    print("Runs", run_ids)
    assert max(run_ids) == 4

    y1 = workflow.mult.base.runs[3].y[0]
    y2 = workflow.mult.base.runs[4].y[0]

    print("y1 =", y1)
    print("y2 =", y2)

    assert math.fabs(y1 - y1_ref) < 1e-8
    assert math.fabs(y2 - y2_ref) < 1e-8

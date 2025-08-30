import time

from motoko.workflow import Workflow


def populate_arg_parser(parser):
    parser.add_argument(
        "--inputs",
        "-i",
        type=float,
        nargs=2,
    )


def main(workflow, **params):
    mult_manager = workflow.mult
    mult_manager.createTask(x=params["inputs"], run_params=None)

    while 1:
        if workflow.mult.select(["state != FINISHED"]):
            time.sleep(2)
            continue

        print("mult runs finished", flush=True)

        while workflow.add.select(["state != FINISHED"]):
            time.sleep(2)

        print("add runs finished", flush=True)

        if not workflow.norm.select(["runs.id < 2"]):
            finished_mult_runs = workflow.mult.select(["state = FINISHED"])
            mult_ids = [r["id"] for r, j in finished_mult_runs]
            workflow.norm.createTask(mult_ids=mult_ids)

        while workflow.norm.select(["state != FINISHED", "runs.id < 2"]):
            time.sleep(2)

        print("norm runs finished", flush=True)

        if not workflow.mult.select(["state != FINISHED"]) and not workflow.add.select(
            ["state != FINISHED"]
        ):
            print("test workflow has finished", flush=True)
            break


if __name__ == "__main__":
    workflow = Workflow("motoko.yaml")
    main(workflow)


##### for future: write it like this with the loop being in workflow class
# def spawn_norm_tasks(run, job):
#     workflow.norm.createTask()
#
# wf["add"].action_on_finish(spawn_other_runs)
# wf.execute() => should contain the main infinite loop

#####

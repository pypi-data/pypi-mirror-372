from motoko.workflow import Workflow


def populate_arg_parser(parser):
    parser.add_argument(
        "--inputs",
        "-i",
        type=float,
        nargs=2,
    )


######################################################


def spawn_init_tasks(workflow, **params):
    mult_manager = workflow.mult
    mult_manager.createTask(x=params["inputs"], run_params=None)


######################################################


def spawn_norm_tasks(workflow, **params):
    if not workflow.norm.select(["runs.id < 2"]):
        finished_mult_runs = workflow.mult.select(["state = FINISHED"])
        mult_ids = [r["id"] for r, j in finished_mult_runs]
        workflow.norm.createTask(mult_ids=mult_ids)


######################################################


def finalize(workflow, **params):
    if not workflow.mult.select(["state != FINISHED"]) and not workflow.add.select(
        ["state != FINISHED"]
    ):
        return True


######################################################


def main(workflow, **params):
    workflow.add_init_action(spawn_init_tasks)
    workflow.add_action("add", spawn_norm_tasks)
    workflow.add_action("norm", finalize)


if __name__ == "__main__":
    workflow = Workflow("motoko.yaml")
    main(workflow)

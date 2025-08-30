import os
import math
import BlackDynamite as BD
import numpy as np

from motoko.workflow import Workflow


def doIt(run, job):
    mult_ids = job.mult_ids
    print(mult_ids)
    wf = Workflow(run.workflow)
    mult_runs = [wf.mult.connect().runs[id] for id in mult_ids]
    if len(mult_runs) != 2:
        raise ValueError("number of add runs cannot be larger than 2")

    add_ids = []
    for r in mult_runs:
        add_ids.extend(r.dependencies)

    runs = wf.get_runs(add_ids)
    add_runs = runs["add"]
    print(add_runs)

    if len(add_runs) != 3:
        raise ValueError("number of add runs cannot be larger than 3")

    x = [0.0] * 3
    for i in range(3):
        x[i] = add_runs[i].getScalarQuantity("scalar")[1][0]

    a = [3.3, 2.34, 0.148]
    l1_norm = (x[0] - a[0]) ** 2 + (x[1] - a[1]) ** 2 + (x[2] - a[2]) ** 2
    l2_norm = math.sqrt(l1_norm)

    run.pushVectorQuantity(np.array([l1_norm, l2_norm]), 0, "vector")
    created_mult_runs = wf.mult.createTask(x=[l1_norm, l2_norm])
    run.dependencies = [f"mult.{r['id']}" for r, j in created_mult_runs]


################################################################

run, job = BD.getRunFromScript()
print(run)
print(job)
env_to_remove = []
for k in os.environ.keys():
    if "BLACKDYNAMITE_" in k:
        env_to_remove.append(k)

for k in env_to_remove:
    del os.environ[k]

run.start()
doIt(run, job)
run.finish()

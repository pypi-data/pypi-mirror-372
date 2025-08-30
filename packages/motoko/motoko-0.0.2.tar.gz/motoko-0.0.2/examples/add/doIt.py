import os
import BlackDynamite as BD


def doIt(run, job):
    x = job.x
    y = x + 0.56

    run.pushScalarQuantity(y, 0, "scalar")


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

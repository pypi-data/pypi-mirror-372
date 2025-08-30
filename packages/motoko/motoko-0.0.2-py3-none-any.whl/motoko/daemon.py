import subprocess
import json
import os


def start_daemon(script, inputs):
    cmd = ["python", script.__file__, json.dumps(inputs)]
    print("Execute: ", *cmd)
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        cwd=os.getcwd(),
    )

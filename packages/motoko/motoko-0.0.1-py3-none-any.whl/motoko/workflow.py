#!/usr/bin/env python3
import yaml
import importlib.util
import sys
import os
from motoko.task_manager import TaskManager
from motoko.bd_study import create_bd_studies
import subprocess


class Workflow:
    def __init__(self, filename):
        with open(filename) as f:
            self.config = yaml.load(f, Loader=yaml.SafeLoader)
            self.config_path = os.path.abspath(filename)
            self.directory = os.path.dirname(self.config_path)
        self.task_managers = dict(
            [(e, TaskManager(self, e)) for e in self.config["task_managers"]]
        )

        self.orchestrator_script = self.config["orchestrator"]
        self.orchestrator_function = None

    def create(self, validated=None):
        create_bd_studies(self, validated=validated)

    def start_launcher_daemons(self):
        # Select job management scheme (SLURM, PBS, bash, etc)
        # Default is bash
        clargs = ""
        if "generator" in self.config:
            generator = self.config["generator"]
            clargs += "--generator " + generator
            k = generator.replace("Coat", "_options")
            if k in self.config:
                clargs += " --" + k + " "
                clargs += " ".join(self.config[k])

        for name, task_manager in self.task_managers.items():
            subprocess.call(
                f"canYouDigIt launch_daemon --start -d {clargs}",
                cwd=task_manager.study_dir,
                shell=True,
            )

    def __getattr__(self, name):
        if name in self.task_managers:
            return self.task_managers[name]

        return super().__getattr__(name)

    def get_orchestrator_function(self):
        if self.orchestrator_function is not None:
            return self.orchestrator_function

        fname, func_name = self.orchestrator_script.split(".")
        file_path = os.path.join(self.directory, fname + ".py")
        module_name = "orchestrator"
        print(f"loading {file_path}")
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        self.orchestrator_function = getattr(module, func_name)
        return self.orchestrator_function

    def execute(self, **params):
        func = self.get_orchestrator_function()
        func(self, **params)

    def get_runs(self, run_list):
        requests = {}
        for uri in run_list:
            task_manager_name, _id = uri.split(".")
            _id = int(_id)
            tm = self.__getattr__(task_manager_name)
            if task_manager_name not in requests:
                requests[task_manager_name] = []
            requests[task_manager_name].append(tm.connect().runs[_id])
        return requests

    def commit(self):
        for name, task_manager in self.task_managers.items():
            task_manager.update()

#!/usr/bin/env python3
import yaml
import importlib.util
import sys
import os
import subprocess
import time
from motoko.task_manager import TaskManager
from motoko.bd_study import create_bd_studies


class Workflow:
    ################################################################################

    # TODO: Write Vars class in such a way that it allows for remote access
    class Vars:
        """Driver class for storing and accessing workflow variables, e.g., when performing an
        action upon finishing a task"""

        ################################################
        class DBManager:
            """Manages the database behind Vars"""

            def __init__(self, db_fname, commit_on_exit=True):
                self.db_fname = db_fname
                self.commit_on_exit = commit_on_exit
                self.db = None
                self.conn = None

            def __enter__(self):
                from ZODB import FileStorage, DB

                storage = FileStorage.FileStorage(self.db_fname)
                self.db = DB(storage)
                self.conn = self.db.open()
                return self.conn.root()

            def __exit__(self, exc_type, exc_value, tb):
                if self.commit_on_exit:
                    self.commit()
                self.conn.close()
                self.db.close()

            def commit(self):
                import transaction

                transaction.commit()

        ################################################

        def __init__(self, db_fname):
            self.db_fname = db_fname

        def __setattr__(self, name, value):
            if name != "db_fname":
                with Workflow.Vars.DBManager(self.db_fname) as data:
                    data[name] = value
            else:
                super().__setattr__(name, value)

        def __getattr__(self, name):
            with Workflow.Vars.DBManager(self.db_fname, False) as data:
                if name in data:
                    return data[name]

            return super().__getattr__(name)

        def __delattr__(self, name):
            with Workflow.Vars.DBManager(self.db_fname) as data:
                if name in data:
                    del data[name]
                    return

            super().__delattr__(name)

    ################################################################################

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

        def no_action(wf, **params):
            pass

        self.init_action = no_action
        self.action_on_finish = dict(
            [(name, no_action) for name in self.task_managers.keys()]
        )

        conf_dir = os.path.join(self.directory, ".wf")
        os.makedirs(conf_dir, exist_ok=True)
        db_fname = os.path.join(conf_dir, "wf.db")
        self.vars = self.Vars(db_fname)

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

    def add_init_action(self, func):
        self.init_action = func

    def add_action(self, task_manager_name, func):
        self.action_on_finish[task_manager_name] = func

    def execute(self, **params):
        """Orchestrator function that executes an action upon finishing a task"""

        func = self.get_orchestrator_function()
        func(self, **params)

        try:
            # When needed to restart the workflow, we continue from the last study
            # We reorder the task managers such that the last saved one now becomes first
            stage = self.vars.stage
            tm_names = list(self.task_managers.keys())
            stage_idx = tm_names.index(stage)
            new_order = tm_names[stage_idx:] + tm_names[:stage_idx]
            self.task_managers = dict([(name, self.name) for name in new_order])
        except (AttributeError, ValueError):
            # Run init_action whenever self.vars.stage does not exist yet (AttributeError) or
            # tm_names.index(stage) cannot be found (stage="init" := ValueError)
            self.vars.stage = "init"
            self.init_action(self, **params)

        finish_flag = True
        while finish_flag:
            for name, task_manager in self.task_managers.items():
                self.vars.stage = name
                while task_manager.select(["state != FINISHED"]):
                    time.sleep(2)
                print(f"{name} runs finished", flush=True)

                if self.action_on_finish[name](self, **params):
                    finish_flag = False
                    print("workflow has finished", flush=True)
                    break

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

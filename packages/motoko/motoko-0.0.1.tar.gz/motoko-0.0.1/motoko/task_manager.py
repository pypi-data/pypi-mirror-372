import os
import BlackDynamite as BD
import yaml


class TaskManager:
    def __init__(self, workflow, study):
        self.workflow = workflow
        self.study = study
        self.config = self.workflow.config["task_managers"][self.study]

        if self.config is None:
            self.config = {}
        if "host" in self.config:
            self.host = self.config["host"]
        else:
            self.host = "zeo://" + self.study_dir

        self._base = None
        self.selector = None

        self._default_job_space = {}
        self._default_run_params = {}
        if "job_space" in self.bd_config:
            self._default_job_space = self.bd_config["job_space"]
        if "run_params" in self.bd_config:
            self._default_run_params = self.bd_config["run_params"]

    def connect(self):
        return self.base

    @property
    def base(self):
        if self._base is not None:
            return self._base

        cwd = os.getcwd()
        os.chdir(self.study_dir)
        params = {"study": self.study, "host": self.host}
        self._base = BD.Base(**params)
        print(self._base.schema)
        os.chdir(cwd)

        BD.singleton_base = self._base
        print(f"({self.study}) connected to: {self._base}")
        return self._base

    @property
    def bd_config(self):
        fname = os.path.join(self.study_dir, "bd.yaml")
        with open(fname) as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
        return config

    @property
    def study_dir(self):
        return os.path.join(self.workflow.directory, self.study)

    @property
    def bd_dir(self):
        return os.path.join(self.study_dir, ".bd")

    def _createRun(self, job, run_params):
        myrun = job.base.Run()
        # set the run parameters from the parsed entries
        job.base.prepare(myrun, "run_desc")
        myrun["run_name"] = "test"
        myrun["machine_name"] = "localhost"
        myrun["nproc"] = 1
        myrun["workflow"] = self.workflow.config_path
        myrun.entries.update(run_params)

        cwd = os.getcwd()
        os.chdir(self.study_dir)

        myrun.setExecFile("launch.sh")

        config_files = ["doIt.py"]
        print(self.bd_config)
        if "config_files" in self.bd_config:
            for f in self.bd_config["config_files"]:
                config_files.append(f)
        myrun.addConfigFiles(config_files)
        os.chdir(cwd)

        _id = myrun.attachToJob(job)
        job.base.commit()
        myrun = job.base.runs[_id]
        return myrun

    def _createJob(self, job_input):
        new_job = self.base.Job()
        for k, v in job_input.items():
            new_job[k] = v
        _id = self.base.insert(new_job)
        self.base.commit()
        new_job = self.base.jobs[_id]
        return new_job

    def createTask(self, run_params=None, **kwargs):
        from BlackDynamite.base_zeo import BaseZEO

        BaseZEO.singleton_base = self.base

        if run_params is None:
            run_params = {}

        run_params_ = self._default_run_params
        for k, v in run_params.items():
            if isinstance(v, dict) and k in run_params_:
                run_params_[k].update(v)
            else:
                run_params_[k] = v

        job_space = self._expandJobSpace(**kwargs)
        return self._create_runs_and_jobs(job_space, run_params_)

    def _expandJobSpace(self, **kwargs):
        self.connect()
        desc_job = self.base.get_descriptor("job_desc")
        print(desc_job)
        job_space = self._default_job_space
        job_space.update(kwargs)
        job_space = self.base._createParameterSpace(job_space, entries_desc=desc_job)
        return job_space

    def _create_runs_and_jobs(self, job_space, run_params):
        created = []
        for job_inputs in job_space:
            j = self._createJob(job_inputs)
            r = self._createRun(j, run_params)
            created.append((r, j))
        self.base.commit()
        return created

    # TODO: remove
    # def _create_legacy(self):
    #     self.jobs = []
    #     self.runs = []
    #     for inputs in self.job_space:
    #         j = self.createJob(inputs)
    #         self.jobs.append(j)
    #         r = self.createRun(j)
    #         self.runs.append(r)
    #     self.base.commit()

    def update(self):
        self.connect().commit()

    def select(self, constraints):
        self.update()
        if self.selector is None:
            self.selector = BD.RunSelector(self.base)
        selected_runs = self.selector.selectRuns(constraints, quiet=True)
        return selected_runs

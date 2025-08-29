# -*- coding: utf-8 -*-
from outflow.core.db.database import Databases
from outflow.core.generic.context_manager import ManagedClass
from outflow.core.generic.null_object import NullObject

from .context_manager import PipelineContextManager


class PipelineContext(ManagedClass, context_manager=PipelineContextManager):
    """
    The pipeline context
    """

    def __init__(self):
        self.name = "__pipeline_context__"
        self.force_dry_run = False
        self.args = None
        self.db_untracked = False
        self._databases = None
        self.db_run = None
        self._session = None
        self.backend_name = None
        self.map_uuid = ""
        self.run_uuid = ""
        self.running_slurm_job_ids = []
        self.overwrite_cache: bool = False

        # store each plugin models to allow metadata clear/backup
        self._models = None

    def __getstate__(self):
        """
        This excludes database sessions from the serialization because it is
        not serializable.
        """
        state = self.__dict__.copy()
        state["_databases"] = None
        state["_session"] = None
        return state

    def __setstate__(self, state):
        vars(self).update(state)

    @property
    def dry_run(self):
        args_dry_run = self.args.dry_run if self.args else False
        return self.force_dry_run or args_dry_run

    @property
    def session(self):
        if self.dry_run:
            return NullObject()

        if self._models is None:
            return None

        return self.databases.session

    @property
    def admin_session(self):
        return self.databases.admin_session

    @property
    def databases(self):
        if self.dry_run:
            return NullObject()

        if self._databases is None:
            self._databases = Databases()

        return self._databases

    def resolve(self):
        """
        This method does nothing, it is useful to explicitly initialize the
        lazy object from the pipeline.
        """
        pass

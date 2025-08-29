# -*- coding: utf-8 -*-
import re
import signal
import subprocess
import sys
import time

import cloudpickle
import simple_slurm

from outflow.core.logging import logger
from outflow.core.pipeline import context, settings

from outflow.library.workflows.base_map_workflow import BaseMapWorkflow, SigTerm

from outflow.management.models.mixins import StateEnum

from outflow.management.models.block import Block as BlockModel


def raise_multiple_exceptions(exceptions, message):
    """
    Merge multiple exceptions into one and raise.
    """

    # the MultiException will inherit from each unique exception class in the list
    classes = set()

    for exception in exceptions:
        classes.add(exception.__class__)

    class MultiException(*classes):
        pass

    raise MultiException(message) from Exception(*exceptions)


class SignalHandler:
    term_received = False

    def __init__(self):
        signal.signal(signal.SIGTERM, self.handle_sigterm)

    def handle_sigterm(self, *args):
        self.term_received = True


class SlurmMapWorkflow(BaseMapWorkflow):
    def __init__(self, simultaneous_tasks=None, **kwargs):
        self.sbatch_directives = {}

        sbatch_directive_name = [
            sublist[0] for sublist in simple_slurm.core.read_simple_txt("arguments.txt")
        ]

        for directive in sbatch_directive_name:
            if directive in kwargs:
                self.sbatch_directives.update({directive: kwargs[directive]})
                # remove from kwargs before calling super().__init__()
                del kwargs[directive]

        super().__init__(**kwargs)

        self.simultaneous_tasks = simultaneous_tasks

    def run(self, *, block_db: BlockModel, **map_inputs):
        self.generated_inputs = list(self.generator(**map_inputs))
        results_from_cache = list()

        if self.cache:
            results_from_cache = self.filter_cached()

        self.create_graph_in_db(nb_copies=len(self.generated_inputs))
        self.put_input_values_in_db(self.generated_inputs, block_db)
        context.session.commit()

        self.block_db_id = block_db.id

        run_dir = settings.TEMP_DIR / f"outflow_{context.run_uuid}"
        with open(run_dir / f"map_info_{block_db.uuid}.pickle", "wb") as map_info_file:
            cloudpickle.dump(self, map_info_file)

        # Sbatch slurm array
        nb_slurm_tasks = len(self.generated_inputs)

        results = results_from_cache

        if nb_slurm_tasks == 0:
            return self.reduce(results)

        array_directive = f"0-{nb_slurm_tasks - 1}"

        if self.simultaneous_tasks:
            array_directive += f"%{self.simultaneous_tasks}"

        slurm_out = settings.TEMP_DIR / "slurm_out"

        slurm_out.mkdir(exist_ok=True)

        map_slurm_array = simple_slurm.Slurm(
            array=array_directive,
            job_name=f"outflow_{self.name}_{block_db.uuid}",
            error=(slurm_out / "slurm-%A_%a.err").as_posix(),
            output=(slurm_out / "slurm-%A_%a.out").as_posix(),
            **self.sbatch_directives,
        )

        job_id = map_slurm_array.sbatch(
            f"srun {sys.executable} -m outflow.slurm.remote_runner "
            f"--run-uuid {context.run_uuid} --map-uuid {block_db.uuid} "
            f"--temp-dir {settings.TEMP_DIR.resolve()}",
            verbose=False,
        )

        context.running_slurm_job_ids.append(job_id)

        timeout = 60000  # seconds
        start = time.time()

        slurm_end_states = [
            "BOOT_FAIL",
            "CANCELLED",
            "COMPLETED",
            "DEADLINE",
            "FAILED",
            "NODE_FAIL",
            "OUT_OF_MEMORY",
            "PREEMPTED",
            "TIMEOUT",
        ]

        array_jobs = [f"{str(job_id)}_{i}" for i in range(nb_slurm_tasks)]

        signal_handler = SignalHandler()

        while True:
            time.sleep(1)
            now = time.time()
            states = []

            if signal_handler.term_received:
                raise SigTerm()

            if now - start > timeout:
                raise RuntimeError("timeout on slurm map")

            for job in array_jobs:
                try:
                    output = subprocess.run(
                        ["scontrol", "show", "job", job, "-o"],
                        capture_output=True,
                        text=True,
                        check=True,
                    ).stdout
                    state = re.findall(r"JobState=(\S*)", output)[0]

                except Exception:
                    state = "COMPLETED"

                finally:
                    states.append(state)

            if all([state in slurm_end_states for state in states]):
                break  # job array has ended

        context.session.expire_all()

        all_mapped_tasks = (
            context.session.query(BlockModel)
            .filter(BlockModel.parent == block_db)
            .all()
        )

        try:
            # gether results from all tasks
            for task_id in range(nb_slurm_tasks):
                with open(
                    run_dir / f"map_result_{task_id}_{block_db.uuid}",
                    "rb",
                ) as map_result_file:
                    results.append(cloudpickle.load(map_result_file))
        except FileNotFoundError as fe:
            # if pickle file is not found, raise exception
            logger.error("One or more map output files could not be found")
            raise fe
        finally:
            # check if any task has failed
            map_workflow_failed = any(
                task.state == StateEnum.failed for task in all_mapped_tasks
            )

            # on failure, raise a single exception encapsulating all failures
            if map_workflow_failed:
                error_msg = f"One or more task has failed in mapped workflows of MapWorkflow {self.name}"

                exceptions = [
                    result for result in results if isinstance(result, Exception)
                ]

                if self.raise_exceptions:
                    raise_multiple_exceptions(exceptions, message=error_msg)
                else:
                    logger.warning(error_msg)
                    if exceptions:
                        logger.warning(
                            "The previous exception is directly related to the following exceptions:"
                        )
                        for exception in exceptions:
                            logger.warning(exception)

        context.running_slurm_job_ids.remove(job_id)

        return self.reduce(results)

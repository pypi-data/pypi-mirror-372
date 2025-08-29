# -*- coding: utf-8 -*-
import argparse
import os
import pathlib
import subprocess
import sys

import cloudpickle

from outflow.core.logging import logger
from outflow.core.pipeline import config, context, set_pipeline_state
from outflow.core.pipeline.context_manager import PipelineContextManager
from outflow.library.workflows.base_map_workflow import SigTerm

from outflow.management.models.block import Block
from outflow.slurm.map_workflow import SlurmMapWorkflow


def init_remote(map_uuid, run_uuid, temp_dir):
    sys.path.extend(os.environ["PYTHONPATH"].split(","))

    run_dir = temp_dir / f"outflow_{run_uuid}"
    with open(run_dir / "pipeline_states", "rb") as pipeline_states_file:
        pipeline_states = cloudpickle.load(pipeline_states_file)

    set_pipeline_state(**pipeline_states)

    context.map_uuid = map_uuid
    context.run_uuid = run_uuid

    import logging.handlers

    from outflow.core.logging import set_plugins_loggers_config

    set_plugins_loggers_config()

    logging.config.dictConfig(config["logging"])

    socket_handler = logging.handlers.SocketHandler(
        context.head_address, context.logger_port
    )
    socket_handler.setLevel(logging.DEBUG)
    from outflow.core.logging.stream_handler import AddMessageSourceInfo

    socket_handler.addFilter(AddMessageSourceInfo())

    for logger_name in config["logging"].get("loggers", {}):
        if logger_name == "":
            continue
        _logger = logging.getLogger(logger_name)
        _logger.handlers = [socket_handler]


def remote_run(temp_dir):
    # remote run for slurm backend
    task_id = int(os.environ["SLURM_ARRAY_TASK_ID"])

    filename = f"map_result_{task_id}_{context.map_uuid}"

    run_dir = temp_dir / f"outflow_{context.run_uuid}"

    try:
        with open(
            run_dir / f"map_info_{context.map_uuid}.pickle", "rb"
        ) as map_info_file:
            workflow: SlurmMapWorkflow = cloudpickle.load(map_info_file)

        block_db = context.session.query(Block).filter_by(id=workflow.block_db_id).one()

        result = workflow.run_mapped_workflow(task_id, block_db)

    except SigTerm as e:
        while not len(context.running_slurm_job_ids) == 0:
            slurm_id = context.running_slurm_job_ids.pop()
            logger.debug("cancelling slurm id {id}".format(id=slurm_id))
            subprocess.run(["scancel", str(slurm_id), "-b"])
        result = e

    except Exception as e:
        result = e

    with open(run_dir / filename, "wb") as result_file:
        cloudpickle.dump(result, result_file)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Enter string")
    parser.add_argument(
        "--map-uuid",
        "-m",
        help="Launch outflow in remote run mode with the given map uuid",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--run-uuid", "-r", help="Specify the run ID", type=str, required=True
    )
    parser.add_argument(
        "--temp-dir",
        "-t",
        help="Outflow temp directory used to share pipeline states/tasks",
        type=pathlib.Path,
        required=True,
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    with PipelineContextManager():
        init_remote(args.map_uuid, args.run_uuid, args.temp_dir)
        remote_run(args.temp_dir)


if __name__ == "__main__":
    main()

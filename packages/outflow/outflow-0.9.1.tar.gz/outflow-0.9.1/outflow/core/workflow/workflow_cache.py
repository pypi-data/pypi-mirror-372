# -*- coding: utf-8 -*-
import pickle
from pathlib import Path
from typing import Union

from outflow.core.logging import logger


class WorkflowCache:
    def __init__(
        self, *, workflow: "Workflow", cache_dir: Union[str, Path, None] = None
    ):
        self.workflow = workflow
        self.cache_dir: Path

        if cache_dir is None:
            from outflow.core.pipeline import settings, config

            if config.get("workflow_cache_dir") is not None:
                self.cache_dir = Path(config["workflow_cache_dir"])
            else:
                self.cache_dir = settings.TEMP_DIR / "workflow_cache"
        else:
            self.cache_dir = Path(str(cache_dir))

        self.cache_dir.mkdir(exist_ok=True, parents=True)

    @property
    def path(self) -> Path:
        return self.cache_dir / f"artifact_{self.workflow.hash}"

    def exists(self) -> bool:
        from outflow.core.pipeline import context

        if context.overwrite_cache:
            return False
        else:
            return self.path.exists()

    def read(self) -> dict:
        logger.debug(f"Reading artifact data from {self.path}")

        with open(self.path, "rb") as artifact_file:
            data = pickle.load(artifact_file)

        return data

    def write(self, data: dict):
        logger.debug(f"Writing artifact data to {self.path}")

        with open(self.path, "wb") as artifact_file:
            pickle.dump(data, artifact_file)

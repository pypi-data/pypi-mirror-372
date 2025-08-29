# -*- coding: utf-8 -*-
from contextlib import closing
from pathlib import Path

import hashlib


def compute_checksum(
    filepath: Path, hash_func=hashlib.sha256, buffer_size=128 * 1024
) -> str:
    """
    Compute file checksum
    """
    hash_obj = hash_func()
    buffer = bytearray(buffer_size)
    buffer_view = memoryview(buffer)
    # open the file in binary mode
    # eliminate double buffering (don't use buffered IO)
    with open(filepath, "rb", buffering=0) as f:
        for n in iter(lambda: f.readinto(buffer_view), 0):
            hash_obj.update(buffer_view[:n])
    return hash_obj.hexdigest()


class Product:
    def __init__(self, data, *args, filepath: Path, **kwargs):
        self.data = data
        self.filepath = filepath
        self._hash = None

    @property
    def hash(self) -> str:
        return self._hash

    def open(self, *args, **kwargs):
        return closing(open(str(self.filepath), *args, **kwargs))

    def write(self):
        with self.open(mode="w") as f:
            f.write(self.data)
        self.set_hash()
        return self.data

    def read(self):
        if self.data is None:
            with self.open() as f:
                self.data = f.read()
        return self.data

    def __getstate__(self) -> dict:
        if not self._hash:  # attribute set only by write so this is equivalent
            raise AttributeError(
                "A product must be written to disk before the end of the workflow"
            )
        state = self.__dict__.copy()
        state["data"] = None
        state["filepath"] = str(state["filepath"])
        return state

    def __setstate__(self, state: dict):
        vars(self).update(state)
        self.filepath = Path(self.filepath)

    def set_hash(self) -> None:
        self._hash = compute_checksum(self.filepath)


class HeavyProduct(Product):
    def __init__(self, data, filepath: Path, workflow_hash: str):
        super().__init__(data, filepath=filepath)
        self._hash = workflow_hash

    @property
    def hash(self):
        return self._hash

    def set_hash(self):
        pass

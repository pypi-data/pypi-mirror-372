# -*- coding: utf-8 -*-
import hashlib
import os


def compute_dir_hash(directory, hash_func=hashlib.md5):
    hash_value = hash_func()
    if not os.path.exists(directory):
        return -1

    for root, dirs, files in os.walk(directory):
        for names in files:
            try:
                f1 = open(os.path.join(root, names), "rb")
            except Exception:
                # if the file open() crash for some reason
                f1.close()
                continue

            while True:
                # read file in as little chunks
                buf = f1.read(4096)
                if not buf:
                    break
                hash_value.update(buf)
            f1.close()

    return hash_value.hexdigest()

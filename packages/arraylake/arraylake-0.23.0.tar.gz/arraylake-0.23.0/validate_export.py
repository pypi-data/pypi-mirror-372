#!/usr/bin/env python3

import sys
from difflib import ndiff
from pprint import pformat

import numpy as np
import zarr

from arraylake.client import Client

repo_name = sys.argv[1]
dest_path = sys.argv[2]

repo = Client().get_repo(repo_name)
src = zarr.open_group(repo.store)
dest = zarr.open_group(dest_path)


def diff(label, a, b):
    delta = "".join(ndiff(a.splitlines(keepends=True), b.splitlines(keepends=True)))
    print(f"delta for {label}: " + delta, end="")
    print()


diff("tree()", pformat(src.tree()), pformat(dest.tree()))
diff("info", pformat(src.info), pformat(dest.info))


def validate(src_path):
    diff(src_path, pformat(src[src_path].attrs.asdict()), pformat(dest[src_path].attrs.asdict()))
    try:
        src_mean = np.mean(src[src_path])
        dest_mean = np.mean(dest[src_path])

        print(f"{src_mean} == {dest_mean}: {src_mean == dest_mean}")
    except Exception:
        pass
    print("\n===========")


for key in src.array_keys(recurse=True):
    validate(key)

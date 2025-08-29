#!/usr/bin/env python
import os
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    py_version = sys.version_info[:3]

    os.chdir(Path(__file__).parent)
    os.environ["CUSTOM_COMPILE_COMMAND"] = "requirements/compile.py"
    os.environ["PIP_REQUIRE_VIRTUALENV"] = "0"
    common_args = [
        "-m",
        "piptools",
        "compile",
        "--generate-hashes",
        "--allow-unsafe",
        "--no-emit-index-url",
    ] + sys.argv[1:]

    subprocess.run(
        [
            "python",
            *common_args,
            "-o",
            "py310.txt",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "python",
            *common_args,
            "-o",
            "py311.txt",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "python",
            *common_args,
            "-o",
            "py312.txt",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "python",
            *common_args,
            "-o",
            "py313.txt",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "python",
            *common_args,
            "-o",
            "py314.txt",
        ],
        check=True,
        capture_output=True,
    )

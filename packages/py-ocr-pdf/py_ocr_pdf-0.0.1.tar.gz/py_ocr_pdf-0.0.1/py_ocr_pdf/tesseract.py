"""
Module for extracting text from PDFs using Tesseract OCR and pdftoppm.

This module includes utilities to perform per-page OCR on PDFs by utilising
the `tesseract` command-line tool, along with intermediate PDF to image
conversion.

Functions:
- run: Executes a provided shell command, capturing `stdout` and `stderr`.
- extract: Extracts text from PDF files by processing each page through Tesseract.
- get_run_args: Generates arguments for the `tesseract` command based on given inputs.
"""

import errno
import os
import shutil
import subprocess
from tempfile import mkdtemp

import six


def extract(filename, **kwargs):
    """Extract text from pdfs using tesseract (per-page OCR).
    content = extract(pdf_file).decode("utf-8")
    """
    temp_dir = mkdtemp()
    base = os.path.join(temp_dir, "conv")
    contents = []
    try:
        stdout, _ = run(["pdftoppm", filename, base])

        for page in sorted(os.listdir(temp_dir)):
            page_path = os.path.join(temp_dir, page)

            args = get_run_args(page_path, language=kwargs.get("language"))
            page_content, _ = run(args)
            contents.append(page_content)

        return six.b("").join(contents)
    finally:
        shutil.rmtree(temp_dir)


def get_run_args(page_path, language: str = None):
    """Builds the arguments for the `tesseract` command."""
    args = ["tesseract", page_path, "stdout"]
    if language:
        args = ["tesseract", page_path, "stdout", "-l", language]

    return args


def run(args):
    """Runs the subprocess and returns the stdout and stderr."""
    try:
        pipe = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as e:
        if e.errno == errno.ENOENT:
            raise RuntimeError("sh exitcode 127 triggered in tesseract shell parsing")
        else:
            raise e

    stdout, stderr = pipe.communicate()

    if pipe.returncode != 0:
        raise RuntimeError("pipe is broken during tesseract shell parsing")

    return stdout, stderr

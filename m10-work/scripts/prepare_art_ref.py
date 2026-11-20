"""Import the existing hyphenated offline script without running its entry point."""

import importlib.util
from pathlib import Path


def load_prepare_art():
    spec = importlib.util.spec_from_file_location(
        "m10_prepare_art", Path(__file__).with_name("prepare-art.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

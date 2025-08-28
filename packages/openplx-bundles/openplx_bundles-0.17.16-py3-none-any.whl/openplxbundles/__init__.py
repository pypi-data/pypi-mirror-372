"""
This file will be at root of directory structure with all openplxbundles (with only their .openplx files and directory structure)
"""
import os
import logging

def package_dir():
    return os.path.dirname(os.path.abspath(__file__))

def check_bundle_path(bundle_path_str: str):
    return os.path.exists(f"{bundle_path_str}/Math/config.openplx")

def bundle_path():
    # Use OPENPLX_BUNDLE_PATH if set
    if "OPENPLX_BUNDLE_PATH" in os.environ:
        path = os.environ["OPENPLX_BUNDLE_PATH"]
        assert check_bundle_path(path)
        return path
    logging.info("OPENPLX_BUNDLE_PATH environment not set, searching for alternatives")
    # Check possible paths, in development we should set OPENPLX_BUNDLE_PATH to make sure we use the one we intend
    for path in [
        f"{package_dir()}",                      # package installed via pip, including editable install
    ]:
        if check_bundle_path(path):
            path = os.path.abspath(path)
            logging.info("OPENPLX_BUNDLE_PATH=%s, set environment OPENPLX_BUNDLE_PATH if you expected a different path", path)
            return path
    raise FileNotFoundError("Could not locate directory with OpenPLX bundles, i.e. bundle path")

#/usr/bin/env python

"""
import os
import sys
import subprocess
import pkg_resources


wheels_dir = os.path.join(os.path.dirname(__file__), '../dependencies')


def is_installed(package_name):
    installed = pkg_resources.working_set
    return any(package_name == package.project_name for package in installed)


if not is_installed('SAM-2'):
    for wheel in os.listdir(wheels_dir):
        if wheel.endswith('.whl'):
            wheel_path = os.path.join(wheels_dir, wheel)
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-deps', wheel_path])
"""


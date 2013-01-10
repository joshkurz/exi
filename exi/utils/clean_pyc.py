# -*- coding: utf-8 -*-
import subprocess

def clean_pyc():
    """Removes all *.pyc files from the project folder"""
    clean_command = "find . -name *.pyc -delete".split()
    subprocess.call(clean_command)
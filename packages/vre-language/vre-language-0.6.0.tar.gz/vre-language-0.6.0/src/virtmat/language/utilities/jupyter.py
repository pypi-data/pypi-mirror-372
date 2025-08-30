"""utility functions related to jupyter kernel code"""
import os
import sys


def in_jupyter_notebook():
    """return True if the process is running in a jupyter notebook"""
    jupyter_env_vars = [
        'JPY_PARENT_PID',
        'JUPYTER_RUNTIME_DIR',
        'KERNEL_ID',
        'JPY_SESSION_NAME'
    ]

    if any(var in os.environ for var in jupyter_env_vars):
        return True

    if 'ipykernel' in sys.modules:
        return True

    return False

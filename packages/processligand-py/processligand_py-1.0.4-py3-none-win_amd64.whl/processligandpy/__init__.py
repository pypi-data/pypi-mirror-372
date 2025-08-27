import os
import sys

if 'BABEL_DATADIR' not in os.environ:
    try:
        import importlib.resources
        data_dir = os.path.join(str(importlib.resources.files('processligandpy')), 'share', 'openbabel', '3.1.1')
        if not os.path.isdir(data_dir):
            data_dir = os.path.join(str(importlib.resources.files('processligandpy')), 'bin', 'data')
    except (ImportError, AttributeError):
        import pkg_resources
        data_dir = os.path.join(str(pkg_resources.resource_filename('processligandpy', '')), 'share', 'openbabel',
                                '3.1.1')
        if not os.path.isdir(data_dir):
            data_dir = os.path.join(str(pkg_resources.resource_filename('processligandpy', '')), 'bin', 'data')
    os.environ['BABEL_DATADIR'] = data_dir

from .processligand_wrapper import run_processligand

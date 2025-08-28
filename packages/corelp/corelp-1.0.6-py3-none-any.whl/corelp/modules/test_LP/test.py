#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-25
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : test

"""
This function will launch the testfile for the current file using pytest library.
"""



# %% Libraries
from corelp import debug
from pathlib import Path
import subprocess



# %% Function
def test(file) :
    '''
    This function will launch the testfile for the current file using pytest library.
    
    Parameters
    ----------
    file : str
        __file__ string in the current python file to be tested.

    Returns
    -------
    None

    Examples
    --------
    >>> # %% Test function run
    ... if __name__ == "__main__":
    ...     from corelp import test
    ...     test(__file__)
    '''

    # Get paths
    file = Path(file)
    module_folder = file.parent
    file_name = file.name
    test_name = file_name if file_name.startswith('test_') else "test_" + file_name
    test_file = module_folder / test_name

    # __init__ files
    if file_name == '__init__.py' :
        return None
    
    # Testing
    if test_file.exists() :
        debug_folder = debug(file).absolute()
        subprocess.run(["pytest", test_name, f"--cache-dir={debug_folder}"], cwd=module_folder, check=True) #, stdout=subprocess.PIPE



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)
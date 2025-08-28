#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-28
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : main

"""
This function can decorate the main function of a script.
"""



# %% Libraries
from corelp import print, Section, folder, selfkwargs, kwargsself, icon
import time
from pathlib import Path
import functools
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import types



# %% Function
def main(*, new=False) :
    '''
    This function can decorate the main function of a script.
    User inputs parameters shoud be put in the beginning of the main file, and the decorated function will recognize them.
    Decorated function can change the values of these parameters with keyword arguments when called.
    Section can be created bellow the mainfunction.
    
    Decorator parameter
    -------------------
    new : bool
        True to create a new folder at each call by default.

    Global parameters
    -----------------
    import_path : Path or str or None
        Path where to import script data to process. If None, will manually ask user to select it. If not existent, will be ignored.
    export_path : Path or str or None
        Path where to export script data to process.
        A new folder will be created inside at the call time as name.
        If None, will save in import_path. If not existent, will be ignored.
        If a previous call was already made in this same folder, and new is False, will try to reload data from this last folder.
    
    Examples
    --------
    >>> from corelp import main
    ...
    >>> import_path = None # will be asked via a GUI
    >>> export_path = None # will create inside import_path
    >>> new = False # True to create a new export folder, False to reload precalculated data
    >>> main_string = "Hello from main!" # User input parameter
    ...
    >>> @main(new=True) # if previous new is not defined, new is defined here
    ... def myscript() :
    ...     print(main_string) # By default prints "Hello from main!"
    ...     result = mysection() # Section defined bellow, result can be reloaded from previous run
    ...     return result
    ...
    ... @main.section()
    ... def mysection() :
    ...     print("Hello from section!")
    ...     return True # Will be saved into export_path and can be reuploaded at next run with same inputs
    ...
    >>> # Launch
    >>> if __name__ == "__main__" :
    ...     myscript() # prints "Hello from main!"
    ...     myscript(main_string = "Hello changed!!") # prints "Hello changed!!" and loads section result from first run
    '''



    def decorator(func) :
        name = func.__name__

        # Get globals around function definition
        definition_globals = func.__globals__

        @functools.wraps(func)
        def wrapper(**overrides) -> None :

            # Creates new globals
            exec_globals = definition_globals.copy()
            exec_globals.update(overrides)

            # Creates new function
            new_func = types.FunctionType(
                func.__code__,
                exec_globals,
                name=name,
                argdefs=func.__defaults__,
                closure=func.__closure__,
            )

            # Getting paths
            ipath = exec_globals.get('import_path', "None")
            if ipath is None :
                root = tk.Tk()
                root.title("Select import path")
                root.iconbitmap(default=icon)
                root.withdraw()
                ipath = filedialog.askdirectory(title=f'Select import path for {name}')
                root.destroy()
                if not ipath :
                    print('Searching for import_path was cancelled', style='red')
                    raise ValueError('Searching for import_path was cancelled')
            epath = exec_globals.get('export_path', "None")
            if epath is None :
                epath = ipath
            if ipath != "None" :
                ipath = Path(ipath)
            if epath != "None" :
                epath = Path(epath)

            # Creating new export path
            _name = name.replace('.', '_')
            _new = exec_globals.get("new", new)
            if epath != "None" :
                if _new :
                    epath = folder(epath / (f'{_name}_' + datetime.now().strftime("%Y-%m-%d-%Hh%Mmin%Ss")), warning=False)
                else :
                    #Searching for newest old folder
                    efolder = None
                    _date = None
                    for f in epath.iterdir() :
                        if (not f.is_dir()) or (not f.name.startswith(f'{_name}_')) :
                            continue
                        date_str = f.name.split('_')[-1]
                        date = datetime.strptime(date_str, "%Y-%m-%d-%Hh%Mmin%Ss")
                        if _date is None or date > _date :
                            _date, efolder = date, f
                    epath = efolder if efolder is not None else epath / (f'{_name}_' + datetime.now().strftime("%Y-%m-%d-%Hh%Mmin%Ss"))
                if not epath.exists():
                    os.makedirs(epath) #creates folders until end
                md_file = epath / (name+'_log.md')
                html_file = epath / (name+'_log.html')
            else :
                md_file = None
                html_file = None

            # Updating sections
            wrapper.section.path = epath
            wrapper.section.new = _new

            #Begining prints
            print_status = kwargsself(print)
            print.console = None
            print.file = md_file
            print(f'# BEGIN {name}\n')
            print(f"{time.ctime()}")
            if ipath != "None" :
                print(f'import_path : {ipath}\n')
            if epath != "None" :
                print(f'export_path : {epath}\n')

            #Applying test
            print("---\n")
            print('## Launched script\n')
            tic = time.perf_counter()
            try :
                results = new_func()
            
            # Errors
            except Exception :
                print("# FAILED\n", style="red")
                toc = time.perf_counter()
                print("---\n")
                print(f'\n{name} took {toc-tic:.2f}s')
                print(time.ctime())
                print(f'# END... {name}\n')
                print.error()

            # No error
            else :
                toc = time.perf_counter()
                print("---\n")
                print(f'\n{name} took {toc-tic:.2f}s')
                print(time.ctime())
                print(f'# END {name}\n')

            # End script
            print.export_html(html_file)
            selfkwargs(print, print_status)
            return results

        # Making sections
        section = Section()
        section.new = new
        wrapper.section = section

        return wrapper
    return decorator



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)
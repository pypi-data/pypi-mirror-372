"""Utils to test multiple modules and dependencies"""

import os
import subprocess


def ensure_path(module):
    if isinstance(module, str) and os.path.exists(module):
        return module  # it is a path
    else:  # assume it's a module object, and get the path for it
        path = (
            module.__file__
        )  # TODO: Use other means, since __file__ doesn't work for some packages
        if path.endswith('__init__.py'):  # if path is an __init__.py
            path = os.path.dirname(path)  # ... take the containing folder
        return path


def multiple_pytests_commands(
    *modules_to_test, options: str = '--doctest-modules --quiet --disable-warnings'
):
    template = 'pytest ' + options + ' {path}; '
    for path in map(ensure_path, modules_to_test):
        yield template.format(path=path)


def multiple_pytests_command_str(
    *modules_to_test, options: str = '--doctest-modules --quiet --disable-warnings'
):
    return ''.join(multiple_pytests_commands(*modules_to_test, options=options))


def run_multiple_pytests(
    *modules_to_test,
    options: str = '--doctest-modules --quiet --disable-warnings',
    dry_run=False
):
    for command in multiple_pytests_commands(*modules_to_test, options=options):
        print(command)
        if not dry_run:
            r = subprocess.check_output(command, shell=True)
            if isinstance(r, bytes):
                r = r.decode()
            print(r.strip() + '\n')

"""Tools to contextualize tests

>>> versions()  #doctest: +SKIP
['system',
 '3.8.6',
 '3.8.6/envs/p3',
 '3.8.6/envs/test',
 '3.9.0',
 '3.9.0/envs/p39',
 '3.9.0/envs/test2',
 '* p3 (set by PYENV_VERSION environment variable)',
 'p39',
 'test',
 'test2']

>>> t = versions_available_for_install()   #doctest: +SKIP
>>> print(f"{len(t)=}")   #doctest: +SKIP
len(t)=436
>>> t[:5]   #doctest: +SKIP
['2.1.3', '2.2.3', '2.3.7', '2.4.0', '2.4.1']

See:
https://stackoverflow.com/questions/70177366/context-manager-to-setup-and-tear-down-test-virtual-environments

"""

import subprocess


def syscall(*args, decoder=bytes.decode, split_single_strings=False, post_proc=None):
    if decoder is None:
        decoder = lambda x: x
    if split_single_strings and len(args) == 1 and isinstance(args[0], str):
        single_string = args[0]
        args = single_string.split(' ')
    result = subprocess.run(args, capture_output=True)
    if result.returncode:
        raise RuntimeError(f'Error {result.returncode}: {result.stderr.decode()}')
    else:
        decoded_stdout = decoder(result.stdout)
        if not post_proc:
            return decoded_stdout
        else:
            return post_proc(decoded_stdout)


def lines_string_to_list(lines_string, skip_lines=0, line_split_char='\n'):
    x = list(filter(None, map(str.strip, lines_string.split(line_split_char))))
    return x[skip_lines:]


from functools import partial

print_versions = partial(syscall, 'pyenv', 'versions', post_proc=print)
versions = partial(syscall, 'pyenv', 'versions', post_proc=lines_string_to_list)
versions_available_for_install = partial(
    syscall,
    'pyenv',
    'install',
    '--list',
    post_proc=partial(lines_string_to_list, skip_lines=1),
)
mk_virtual_env = partial(syscall, 'pyenv', 'virtualenv')

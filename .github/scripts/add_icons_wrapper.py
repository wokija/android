#!/usr/bin/env python3

from os import system as execute
from os import name as platform
from os.path import basename

from natsort import natsorted as sorted
from yaml import safe_load as yaml

import requests_parser
from resolve_paths import paths


work_dir = paths['scripts']
delta_dir = paths['root']
target_file = paths['icons']
target_script = work_dir + '/add_icons.py'
requests_file = paths['requests']

null = '>NUL 2>NUL' if platform == 'nt' else '>/dev/null 2>&1'

content = '''\
#
# new_icon_1:
#   - com.example/com.example.MainActivity
#
# new_icon_2:
#   - com.example.1/com.example.MainActivity
#   - com.example.2/com.example.MainActivity
#
# new_icon_2_alt_1: {}
#
'''

requests = requests_parser.read(requests_file)

with open(target_file) as file:
    file_parsed = yaml(file)
    if file_parsed is not None:
        try:
            icons = sorted([(k,v) for k,v in file_parsed.items()])[::-1]

            errors = []
            for icon in icons:
                drawable = icon[0]
                compinfos = ' '.join(icon[1])
                command = f'python {target_script} -P {delta_dir} -aidI -n {drawable}'
                if compinfos: command += f' -c {compinfos}'
                else:
                    if drawable.startswith('google_'): command += f' -C Google'
                    else: command += f' -C Alts'
                status = execute(f'{command} -D {null}')
                if status != 0:
                    print(f'> {drawable}:')
                    execute(f'{command} -D')
                    print(command)
                    print()
                    errors.append(drawable)

            if errors:
                errors.sort()
                print(f'Issues with the next icons: {", ".join(errors)}')
                exit(1)

            for icon in icons:
                drawable = icon[0]
                compinfos = ' '.join(icon[1])
                command = f'python {target_script} -P {delta_dir} -aidI -n {drawable}'

                if compinfos:
                    command += f' -c {compinfos}'
                    if drawable.startswith('google_'): command += f' -C Google'
                    for compinfo in compinfos:
                        if compinfo in requests:
                            requests.pop(compinfo)
                else:
                    if '_alt_' in drawable:
                        command += f' -C Alts'
                print(f'> {drawable}')
                execute(command)
                if not icons[-1][0] == drawable: print()

            with open(target_file, 'w', newline='') as file:
                file.write(content)

            requests_parser.write(requests_file, requests)

        except Exception as error:
            print(error)
            exit(1)
    else:
        print(f'warn: looks like {basename(target_file)} is empty')

#!/usr/bin/env python3

from RunningConfigParser import RunningConfigParser
import os, argparse
import pathlib

#parser = argparse.ArgumentParser(description='Mostra as confirações de vlan')
#parser.add_argument('-v', '--verbosity',
#                    help='Ativa modo verbose',
#                    action='store_true')
#parser.add_argument('filename', type=pathlib.Path,    help = 'running-config file path')

#args = parser.parse_args()
file = 'abl.teste.stack.run'

if os.path.isfile(file):
    sh = RunningConfigParser(file)
    for vlan in sh.get_vlans:
        print(vlan)

    print('\n')
    print(sh.get_full_config())
else:
    print("File {} not found".format(file))

print(sh.parse_system_info())
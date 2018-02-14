"""Export CDL from netCDF files in a folder."""

import os
import subprocess


def ncdump(src):
    dest = src[:-3] + '.cdl'
    shell = os.name == 'nt'  # Use shell=True for commands on Windows
    cmd = ['ncdump']
    cmd.append(os.path.abspath(src))
    cmd.append('>')
    cmd.append(os.path.abspath(dest))
    return str(subprocess.check_output(cmd, shell=shell))
    

def main():
    files = [f for f in os.listdir('.') if f.endswith('.nc')]
    for f in files:
        ncdump(f)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3

import argparse

from pathlib import Path

from edgembar.VBA import read_disang, calc_restraint_energy

from importlib.metadata import version, PackageNotFoundError

def get_package_version(package_name):
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "Unknown"


def calc_boresch_shift():
    parser = argparse.ArgumentParser\
    (description="Calculate the free energy penalty from a set "
     +"of Boresch restraints and write the energy to stdout")
    
    parser.add_argument("disang", help="Input Amber NMR restraint file")

    version = get_package_version("edgembar")

    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format\
                        (version=version))


    
    args = parser.parse_args()

    disang = Path(args.disang)
    if disang.is_file():
        restraints = read_disang(disang)
        dAr = calc_restraint_energy(restraints)
        print(round(dAr, 4), "kcal/mol")
    else:
        raise ValueError(f"Input restraints file does not exist: {disang}")


if __name__ == "__main__":
    calc_boresch_shift()

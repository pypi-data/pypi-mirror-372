#!/usr/bin/env python3
import re
import numpy as np
import math
from pathlib import Path
from .Trial import Trial
import yaml


def flatten_list(nested):
    """
    Recursively flattens a nested list and returns a flat list.
    """
    flat = []
    for item in nested:
        if isinstance(item, list):
            flat.extend(flatten_list(item))
        else:
            flat.append(item)
    return flat


def GetBoreschRstData(self: Trial) -> float:
    fname = Path(self.datadir) / "boresch_vba_rst.yaml"
    data = None

    dAr = None
    kb = 0.0019872  # kcal/mol/K
    T = 298  # K
    pi = math.pi
    V0 = 1660  # Angstroms^3 - Standard State volume for 1M

    k_rst = []
    eq0_rst = []
    if fname.is_file():
        with open(fname, "r") as fh:
            data = yaml.safe_load(fh)

        # Process keys with a helper to ensure both scalar and nested values are flattened.
        # The YAML keys in your file are in lowercase.
        # For Angle:
        if 'Angle' in data:
            angle_data = data['Angle']
            # Flatten r2 and process every number
            if 'r2' in angle_data:
                r2_flat = flatten_list(angle_data['r2'])
                for val in r2_flat:
                    num = float(val)
                    eq0_rst.append(np.sin(num * pi / 180.0))
            # Flatten rk2 and process every number
            if 'rk2' in angle_data:
                rk2_flat = flatten_list(angle_data['rk2'])
                for val in rk2_flat:
                    num = float(val)
                    k_rst.append(num)

        # For Bond:
        if 'Bond' in data:
            bond_data = data['Bond']
            if 'r2' in bond_data:
                r2_flat = flatten_list(bond_data['r2'])
                for val in r2_flat:
                    num = float(val)
                    eq0_rst.append(num ** 2)
            if 'rk2' in bond_data:
                rk2_flat = flatten_list(bond_data['rk2'])
                for val in rk2_flat:
                    num = float(val)
                    k_rst.append(num)
        # For Dihedral:
        if 'Dihedral' in data:
            dihedral_data = data['Dihedral']
            # For Dihedral, it looks like only rk2 is used
            if 'rk2' in dihedral_data:
                rk2_flat = flatten_list(dihedral_data['rk2'])
                for val in rk2_flat:
                    num = float(val)
                    k_rst.append(num)

    dAr = 0
    
    if len(k_rst) > 0:
        kk = np.prod(k_rst)
        rr = np.prod(eq0_rst)

        dAr = -kb * T * np.log(
            ((8 * pi ** 2 * V0) / rr) *
            ((kk ** 0.5) / ((pi * kb * T) ** 3))
        )
    else:
        import sys
        sys.stderr.write(f"WARNING: edgembar.VBA.GetBoreschRstData called, but file not found: {str(fname)}")

    return dAr


def read_disang(filename: Path) -> dict:
    """
    Read an Amber disang file and return its contents as a dictionary.
    """

    result = {
        "Bond": {"r0": [], "k": []},
        "Angle": {"r0": [], "k": []},
        "Dihedral": {"r0": [], "k": []},
    }

    def get_restraint_term(fiter):
        """
        get anchor atoms from the disang file.
        """
        while True:
            line = next(fiter)
            # Normalize whitespace
            entry_str_cleaned = ' '.join(line.split())
            # Extract 'iat' atom list string.
            iat_match = re.search(r"iat\s*=\s*([\d\.,\s-]+)", entry_str_cleaned, re.IGNORECASE)
            if not iat_match:
                continue
            iat_list_str = iat_match.group(1).strip().strip(',')
            try:
                # Split by commas and filter out empty strings that might result from multiple or trailing commas
                iat_values = [int(x.strip()) for x in iat_list_str.split(',') if x.strip()]
            except ValueError:
                raise ValueError(f"Invalid 'iat' values at : {line}")

            natoms = sum(1 for val in iat_values if val > 0)
            term: str
            if natoms == 2:
                term = "Bond"
            elif natoms == 3:
                term = "Angle"
            elif natoms == 4:
                term = "Dihedral"
            else:
                raise ValueError(f"Unsupported number of atoms in 'iat' at : {line}")

            return term

    def get_harmonic_constants(fiter):
        try:
            while True:
                line = next(fiter)
                # Normalize whitespace
                entry_str_cleaned = ' '.join(line.split())
                param_kv_pairs = re.findall(r"([a-zA-Z0-9_]+)\s*=\s*(-?[\d\.]+)", entry_str_cleaned)
                try:
                    current_params = {k.lower(): float(v_str) for k, v_str in param_kv_pairs}
                except ValueError:
                    # No parameters on this line
                    continue
                try:
                    r0_val = current_params["r2"]
                    k_val = current_params["rk2"]
                    break
                except KeyError:
                    # Couldn't find r0 or rk on this line
                    continue
        except StopIteration:
            raise ValueError("Bad restraints file format. No valid harmonic constants found.")

        return r0_val, k_val

    with open(filename, 'r') as f:
        fiter = iter(f)
        while True:
            try:
                term = get_restraint_term(fiter)
                r0, k = get_harmonic_constants(fiter)
                result[term]["r0"].append(r0)
                result[term]["k"].append(k)
            except StopIteration:
                break

    return result


def calc_restraint_energy(data: dict[str, dict[str, float]], equilibrium_position_label: str = "r0",
                          harmonic_constant_label: str = "k") -> float:
    kb = 0.0019872  # kcal/mol/K
    T = 298  # K
    pi = math.pi
    V0 = 1660  # Angstroms^3 - Standard State volume for 1M

    eq0_rst = []
    eq0_rst.extend([float(val) ** 2 for val in data['Bond'][equilibrium_position_label]])
    eq0_rst.extend([np.sin(float(val) * pi / 180.0) for val in data['Angle'][equilibrium_position_label]])
    # Polar coordinates, theta angle doesn't show up in the jacobian

    k_rst = []
    k_rst.extend([float(val) for val in data['Bond'][harmonic_constant_label]])
    k_rst.extend([float(val) for val in data['Angle'][harmonic_constant_label]])
    k_rst.extend([float(val) for val in data['Dihedral'][harmonic_constant_label]])

    kk = np.prod(k_rst)
    rr = np.prod(eq0_rst)

    dAr = -kb * T * np.log(
        ((8 * pi ** 2 * V0) / rr) *
        ((kk ** 0.5) / ((pi * kb * T) ** 3))
    )

    return dAr


def calc_vba_shift(self: Trial, restraints_filename: Path, format: str = "amber") -> float:
    """
    Calculate the VBA shift based on the Boresch disang file.

    Args:
        self: Trial instance containing the data directory.

    Returns:
        The calculated VBA shift.
    """
    supported_restraints_formats = ("amber",)
    if format == "amber":
        restraints = read_disang(restraints_filename)
    else:
        raise ValueError(f"Unsupported restraints format: {format}. Supported formats: {supported_restraints_formats}")

    dAr = calc_restraint_energy(restraints)
    if dAr is None:
        raise ValueError("Failed to retrieve Boresch RST data.")

    if format != "amber":
        # Convert dAr from kcal/mol to kJ/mol
        dAr = dAr * 4.184
    return dAr

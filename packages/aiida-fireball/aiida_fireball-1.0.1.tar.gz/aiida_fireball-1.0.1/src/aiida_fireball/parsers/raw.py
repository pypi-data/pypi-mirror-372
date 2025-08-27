"""Raw parsers for Fireball output files."""

import re


def parse_raw_stdout(stdout):
    """Parse the raw stdout output of a Fireball calculation.

    :param stdout: the stdout content as a string
    :return: the parsed data
    """
    parsed_data = {}

    # Parse the walltime
    match = re.search(r"FIREBALL RUNTIME :\s*(\d+\.\d+)\s*\[sec\]", stdout)
    if match:
        parsed_data["wall_time_seconds"] = float(match.group(1))

    # Parse the total energy
    match = re.search(r"ETOT\s*=\s*([+-]?\d+\.\d+)", stdout)
    if match:
        parsed_data["total_energy"] = float(match.group(1))
        parsed_data["total_energy_units"] = "eV"

    # Parse the Fermi energy
    match = re.search(r"Fermi Level\s*=\s*([+-]?\d+\.\d+)", stdout)
    if match:
        parsed_data["fermi_energy"] = float(match.group(1))
        parsed_data["fermi_energy_units"] = "eV"

    # Parse the number of electrons
    match = re.search(r"qztot\s*=\s*(\d+\.\d+)", stdout)
    if match:
        parsed_data["number_of_electrons"] = float(match.group(1))

    # Parse energy tolerance
    match = re.search(r"energy tolerance\s*=\s*(\d+\.\d+(E[+-]\d+)?)\s*\[eV\]", stdout)
    if match:
        parsed_data["energy_tolerance"] = float(match.group(1))
        parsed_data["energy_tolerance_units"] = "eV"

    # Parse force tolerance
    match = re.search(r"force tolerance\s*=\s*(\d+\.\d+(E[+-]\d+)?)\s*\[eV/A\]", stdout)
    if match:
        parsed_data["force_tolerance"] = float(match.group(1))
        parsed_data["force_tolerance_units"] = "eV/A"

    # Parse sigma tolerance
    match = re.search(r"sigmatol\s*=\s*(\d+\.\d+(E[+-]\d+)?)", stdout)
    if match:
        parsed_data["sigma_tolerance"] = float(match.group(1))

    # Parse beta mixing
    match = re.search(r"bmix\s*=\s*(\d+\.\d+(E[+-]\d+)?)", stdout)
    if match:
        parsed_data["beta_mixing"] = float(match.group(1))

    # Parse the charge state
    match = re.search(r"qstate\s*=\s*(\d+\.\d+(E[+-]\d+)?)", stdout)
    if match:
        parsed_data["charge_state"] = float(match.group(1))

    # Parse charge type
    match = re.search(r"iqout\s*=\s*(\d)", stdout)
    if match:
        charge_types = {1: "Lowdin", 2: "Mulliken", 3: "Natural"}
        parsed_data["charge_type"] = charge_types[int(match.group(1))]

    # Parse the rescal value
    match = re.search(r"rescalar\s*=\s*(\d+\.\d+)", stdout)
    if match:
        parsed_data["rescale_factor"] = float(match.group(1))

    # Parse the quenching mode
    match = re.search(r"iquench\s*=\s*([+-]?\d+)\s*\n", stdout)
    if match:
        quenching_modes = {
            0: "Free dynamics (Newton)",
            -1: "Dynamical quenching",
            -2: "Crude constant temperature MD",
            -3: "Power quenching",
            -4: "Conjugate gradient minimization",
            -5: "Newton-CG minimization (l-bfgs-b)",
        }

        def mode(n):
            if n <= 0:
                return quenching_modes[n]
            else:
                return f"Periodic quenching every {n} steps"

        parsed_data["quenching_mode"] = mode(int(match.group(1)))

    return parsed_data

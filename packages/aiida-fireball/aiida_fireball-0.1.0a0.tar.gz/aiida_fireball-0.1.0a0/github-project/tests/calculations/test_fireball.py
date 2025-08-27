# -*- coding: utf-8 -*-
"""Tests for the `FireballCalculation` class."""

import os
import re

import numpy as np
import pytest
from aiida import orm
from aiida.common import datastructures
import shutil

# from aiida.common.exceptions import InputValidationError
from aiida.plugins import CalculationFactory
from aiida_fireball.calculations.fireball import FireballCalculation


@pytest.fixture(autouse=True)
def add_fireball_entry_point(entry_points):
    """Add the `FireballCalculation` entry point in function scope."""
    entry_points.add(FireballCalculation, "aiida.calculations:fireball.fireball")


def test_calculation():
    """Test the `FireballCalculation` load."""
    calc = CalculationFactory("fireball.fireball")
    assert issubclass(calc, FireballCalculation)


@pytest.mark.parametrize(
    ["symlink_restart", "mesh"],
    [
        (True, True),
        (False, False),
        (False, True),
    ],
)
def test_fireball_default(
    fixture_sandbox,
    generate_calc_job,
    generate_inputs_fireball,
    file_regression,
    symlink_restart: bool,
    generate_kpoints_mesh,
    generate_kpoints,
    mesh: bool,
):
    """Test a default `FireballCalculation`."""
    entry_point_name = "fireball.fireball"

    inputs = generate_inputs_fireball()
    if symlink_restart:
        inputs["settings"] = orm.Dict(dict={"PARENT_FOLDER_SYMLINK": symlink_restart})
    if mesh:
        inputs["kpoints"] = generate_kpoints_mesh((3, 3, 1))
    else:
        inputs["kpoints"] = generate_kpoints(kpts=np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]]))
    calc_info = generate_calc_job(fixture_sandbox, entry_point_name, inputs)

    cmdline_params = []
    remote_symlink_list = [(inputs["fdata_remote"].computer.uuid, os.path.join(inputs["fdata_remote"].get_remote_path(), "*"), "./Fdata/")]

    if symlink_restart:
        remote_symlink_list.extend(
            [
                (
                    inputs["parent_folder"].computer.uuid,
                    os.path.join(inputs["parent_folder"].get_remote_path(), "CHARGES"),
                    "./",
                ),
                (
                    inputs["parent_folder"].computer.uuid,
                    os.path.join(inputs["parent_folder"].get_remote_path(), "*restart*"),
                    "./",
                ),
            ]
        )

    # Check the attributes of the returned `CalcInfo`
    assert isinstance(calc_info, datastructures.CalcInfo)
    assert isinstance(calc_info.codes_info[0], datastructures.CodeInfo)
    assert sorted(calc_info.codes_info[0].cmdline_params) == cmdline_params
    assert sorted(calc_info.remote_symlink_list) == sorted(remote_symlink_list)

    with fixture_sandbox.open("fireball.in") as handle:
        input_written = handle.read()

    # Checks on the files written to the sandbox folder as raw input
    assert sorted(fixture_sandbox.get_content_list()) == sorted(["Fdata", "fireball.in", "aiida.bas", "aiida.lvs", "aiida.kpts"])
    file_regression.check(input_written, encoding="utf-8", extension=".in")

    # Check the content of the bas file
    with fixture_sandbox.open("aiida.bas") as handle:
        bas_written = handle.read()
    file_regression.check(bas_written, encoding="utf-8", extension=".bas")

    # Check the content of the lvs file
    with fixture_sandbox.open("aiida.lvs") as handle:
        lvs_written = handle.read()
    file_regression.check(lvs_written, encoding="utf-8", extension=".lvs")

    # Check the content of the kpts file
    with fixture_sandbox.open("aiida.kpts") as handle:
        kpts_written = handle.read()
    file_regression.check(kpts_written, encoding="utf-8", extension=".kpts")


def test_fireball_fixed_coords(fixture_sandbox, generate_calc_job, generate_inputs_fireball, file_regression):
    """Test a `FireballCalculation` where the `fixed_coords` setting was provided."""
    entry_point_name = "fireball.fireball"

    inputs = generate_inputs_fireball()
    inputs["settings"] = orm.Dict(dict={"FIXED_COORDS": [[True, True, False], [False, True, False]]})
    generate_calc_job(fixture_sandbox, entry_point_name, inputs)

    assert "FRAGMENTS" in fixture_sandbox.get_content_list()

    with fixture_sandbox.open("FRAGMENTS") as handle:
        input_written = handle.read()

    file_regression.check(input_written, encoding="utf-8", extension=".fragments")


@pytest.mark.parametrize(
    ["fixed_coords", "error_message"],
    [
        ([[True, True], [False, True]], "The `fixed_coords` setting must be a list of lists with length 3."),
        (
            [[True, True, 1], [False, True, False]],
            "All elements in the `fixed_coords` setting lists must be either `True` or `False`.",
        ),
        ([[True, True, False]], "Input structure has 2 sites, but fixed_coords has length 1"),
    ],
)
def test_fireball_fixed_coords_validation(fixture_sandbox, generate_calc_job, generate_inputs_fireball, fixed_coords, error_message):
    """Test the validation for the `fixed_coords` setting."""
    entry_point_name = "fireball.fireball"

    inputs = generate_inputs_fireball()
    inputs["settings"] = orm.Dict(dict={"FIXED_COORDS": fixed_coords})

    with pytest.raises(ValueError, match=error_message):
        generate_calc_job(fixture_sandbox, entry_point_name, inputs)


def test_fireball_missing_inputs(fixture_sandbox, generate_calc_job, generate_inputs_fireball):
    """Test a `FireballCalculation` with missing required inputs."""
    entry_point_name = "fireball.fireball"

    inputs = generate_inputs_fireball()
    del inputs["fdata_remote"]
    error_message = "Error occurred validating port 'inputs.fdata_remote': "
    error_message += "required value was not provided for 'fdata_remote'"

    with pytest.raises(
        ValueError,
        match=error_message,
    ):
        generate_calc_job(fixture_sandbox, entry_point_name, inputs)


def test_fireball_blocked_keywords(fixture_sandbox, generate_calc_job, generate_inputs_fireball):
    """Test a `FireballCalculation` with blocked keywords."""
    entry_point_name = "fireball.fireball"

    inputs = generate_inputs_fireball()
    parameters = inputs["parameters"].get_dict()
    parameters.setdefault("OPTION", {})["basisfile"] = "test.bas"
    inputs["parameters"] = orm.Dict(parameters)

    error_message = "Cannot specify the 'basisfile' keyword in the 'OPTION' namelist."

    with pytest.raises(
        ValueError,
        match=error_message,
    ):
        generate_calc_job(fixture_sandbox, entry_point_name, inputs)


def test_fireball_dos_settings_invalid_key(fixture_sandbox, generate_calc_job, generate_inputs_fireball):
    """Test a `FireballCalculation` with DOS settings."""
    entry_point_name = "fireball.fireball"

    inputs = generate_inputs_fireball()
    inputs["settings"] = orm.Dict(dict={"DOS": {"first_atom_index": 1, "last_atom_index": 2, "invalid_key": 1}})

    error_message = "Error occurred validating port 'inputs': \
Invalid key 'invalid_key' in the 'DOS' namelist. Valid keys are: \
['first_atom_index', 'last_atom_index', 'Emin', 'Emax', 'n_energy_steps', 'eta', 'iwrttip', 'Emin_tip', 'Emax_tip']"

    with pytest.raises(ValueError, match=re.escape(error_message)):
        generate_calc_job(fixture_sandbox, entry_point_name, inputs)


@pytest.mark.parametrize(
    ["dos_params", "error_message"],
    [
        (
            {"first_atom_index": 0, "last_atom_index": 2},
            "Invalid value for 'first_atom_index' in the 'DOS' namelist. It must be between 1 and 2",
        ),
        (
            {"first_atom_index": 1, "last_atom_index": 0},
            "Invalid value for 'last_atom_index' in the 'DOS' namelist. It must be between 1 and 2 and greater than 'first_atom_index'",
        ),
        (
            {"first_atom_index": 1, "last_atom_index": 2, "n_energy_steps": 0},
            "Invalid value for 'n_energy_steps' in the 'DOS' namelist. It must be greater than 0",
        ),
        (
            {"first_atom_index": 1, "last_atom_index": 2, "Emin": 0.0, "Emax": -5.0},
            "Invalid values for 'Emin' and 'Emax' in the 'DOS' namelist. 'Emin' must be less than 'Emax'",
        ),
        (
            {"first_atom_index": 1, "last_atom_index": 2, "iwrttip": 2},
            "Invalid value for 'iwrttip' in the 'DOS' namelist. It must be either 0 or 1",
        ),
        (
            {"first_atom_index": 1, "last_atom_index": 2, "iwrttip": 1, "Emin_tip": 0.0, "Emax_tip": -5.0},
            "Invalid values for 'Emin_tip' and 'Emax_tip' in the 'DOS' namelist. 'Emin_tip' must be less than 'Emax_tip'",
        ),
        (
            {"first_atom_index": 1, "last_atom_index": 2, "eta": -0.1},
            "Invalid value for 'eta' in the 'DOS' namelist. It must be greater than 0",
        ),
        (
            {"first_atom_index": 1, "last_atom_index": 2, "eta": 0.0},
            "Invalid value for 'eta' in the 'DOS' namelist. It must be greater than 0",
        ),
    ],
)
def test_fireball_dos_settings_invalid_value(fixture_sandbox, generate_calc_job, generate_inputs_fireball, dos_params, error_message):
    """Test a `FireballCalculation` with DOS settings."""
    entry_point_name = "fireball.fireball"

    inputs = generate_inputs_fireball()
    inputs["settings"] = orm.Dict(dict={"DOS": dos_params})

    with pytest.raises(ValueError, match=re.escape(error_message)):
        generate_calc_job(fixture_sandbox, entry_point_name, inputs)


def test_fireball_dos_settings(
    fixture_sandbox,
    generate_calc_job,
    generate_inputs_fireball,
    generate_calc_job_node,
    fixture_localhost,
    file_regression,
):
    """Test a `FireballCalculation` with DOS settings."""
    entry_point_name = "fireball.fireball"

    node = generate_calc_job_node(entry_point_name, fixture_localhost, test_name="test_fireball_dos_settings")

    inputs = generate_inputs_fireball()
    inputs["parent_folder"] = node.outputs.remote_folder
    inputs["settings"] = orm.Dict(dict={"DOS": {}})

    generate_calc_job(fixture_sandbox, entry_point_name, inputs)

    assert "dos.optional" in fixture_sandbox.get_content_list()

    # Check the content of the dos.optional file
    with fixture_sandbox.open("dos.optional") as handle:
        input_written = handle.read()
    file_regression.check(input_written, encoding="utf-8", extension=".dos")

    # Check the content of the fireball.in file
    with fixture_sandbox.open("fireball.in") as handle:
        input_written = handle.read()
    file_regression.check(input_written, encoding="utf-8", extension=".in")


def test_fireball_transport_generation(
    fixture_sandbox,
    generate_calc_job,
    generate_inputs_fireball,
    generate_calc_job_node,
    fixture_localhost,
):
    """Test la génération des fichiers transport optionnels."""
    entry_point_name = "fireball.fireball"
    node = generate_calc_job_node(entry_point_name, fixture_localhost, test_name="test_fireball_transport")

    inputs = generate_inputs_fireball()
    inputs["parent_folder"] = node.outputs.remote_folder
    inputs["settings"] = orm.Dict(dict={
        "TRANSPORT": {
            "INTERACTION": {
                "ncell1":    0,
                "total_atoms1": 50,
                "ninterval1": 1,
                "intervals1": [(1, 50)],
                "natoms_tip1": 0,
                "atoms1":     list(range(1, 51)),
                "ncell2":    0,
                "total_atoms2": 75,
                "ninterval2": 1,
                "intervals2": [(51, 125)],
                "natoms_tip2": 0,
                "atoms2":     list(range(51, 126)),
            },
            "ETA": {
                "imag_part": 0.1,
                "intervals": [(1, 30)],
            },
            "TRANS": {
                "ieta": True,
                "iwrt_trans": False,
                "ichannel": True,
                "ifithop": 1,
                "Ebottom": -5.0,
                "Etop": 5.0,
                "nsteps": 10,
                "eta": 0.01,
            }
        }
    })

    generate_calc_job(fixture_sandbox, entry_point_name, inputs)

    for fname in ["interaction.optional", "eta.optional", "trans.optional"]:
        assert fname in fixture_sandbox.get_content_list()
        with fixture_sandbox.open(fname) as fsrc, open(fname, "w") as fdst:
            fdst.write(fsrc.read())


def test_fireball_transport_optionals(
    fixture_sandbox,
    generate_calc_job,
    generate_inputs_fireball,
    generate_calc_job_node,
    fixture_localhost,
):
    """Test la génération des fichiers eta.optional, trans.optional et interaction.optional."""
    entry_point_name = "fireball.fireball"
    node = generate_calc_job_node(entry_point_name, fixture_localhost, test_name="test_fireball_transport_optionals")

    inputs = generate_inputs_fireball()
    inputs["parent_folder"] = node.outputs.remote_folder
    inputs["settings"] = orm.Dict(dict={
        "TRANSPORT": {
            "INTERACTION": {
                "ncell1": 0,
                "total_atoms1": 10,
                "ninterval1": 1,
                "intervals1": [(1, 10)],
                "natoms_tip1": 2,
                "atoms1": [2, 3],
                "ncell2": 0,
                "total_atoms2": 8,
                "ninterval2": 1,
                "intervals2": [(11, 18)],
                "natoms_tip2": 3,
                "atoms2": [12, 13, 14],
            },
            "ETA": {
                "imag_part": 0.05,
                "intervals": [(1, 5)],
            },
            "TRANS": {
                "ieta": True,
                "iwrt_trans": False,
                "ichannel": True,
                "ifithop": 1,
                "Ebottom": -2.0,
                "Etop": 2.0,
                "nsteps": 4,
                "eta": 0.02,
            }
        }
    })

    generate_calc_job(fixture_sandbox, entry_point_name, inputs)

    for fname in ["interaction.optional", "eta.optional", "trans.optional"]:
        assert fname in fixture_sandbox.get_content_list()
        with fixture_sandbox.open(fname) as fsrc, open(fname, "w") as fdst:
            fdst.write(fsrc.read())

    with open("eta.optional") as f:
        content = f.read()
        assert "0.05" in content
        assert "1" in content
        assert "1   5" in content


#def test_fireball_bias_optional_generation(
    #fixture_sandbox,
    #generate_calc_job,
   # generate_inputs_fireball,
  #  generate_calc_job_node,
 #   fixture_localhost,
#):
   # """Test la génération du fichier bias.optional."""
    #entry_point_name = "fireball.fireball"
    #node = generate_calc_job_node(entry_point_name, fixture_localhost, test_name="test_fireball_bias_optional")

    #inputs = generate_inputs_fireball()
    #inputs["parent_folder"] = node.outputs.remote_folder
    #inputs["settings"] = orm.Dict(dict={
        #"TRANSPORT": {
          #  "BIAS": {
         #       "bias": -3.0,
        #        "z_top": 11.537758,
       #         "z_bottom": -18.061922,
      #      }
     #   }
    #})

    #generate_calc_job(fixture_sandbox, entry_point_name, inputs)

    #assert "bias.optional" in fixture_sandbox.get_content_list()
    #with fixture_sandbox.open("bias.optional") as fsrc, open("bias.optional", "w") as fdst:
     #   fdst.write(fsrc.read())

    #with open("bias.optional") as f:
    #    content = f.read()
   #     assert "-3.0" in content
  #      assert "11.537758" in content
 #       assert "-18.061922" in content


#def test_fireball_all_transport_optionals(
    #fixture_sandbox,
    #generate_calc_job,
   # generate_inputs_fireball,
  #  generate_calc_job_node,
 #   fixture_localhost,
#):
   # """Test la génération des fichiers eta.optional, trans.optional, interaction.optional et bias.optional."""
    #entry_point_name = "fireball.fireball"
    #node = generate_calc_job_node(entry_point_name, fixture_localhost, test_name="test_fireball_all_transport_optionals")

    #inputs = generate_inputs_fireball()
    #inputs["parent_folder"] = node.outputs.remote_folder
    #inputs["settings"] = orm.Dict(dict={
        #"TRANSPORT": {
         #   "INTERACTION": {
            #    "ncell1": 0,
            #    "total_atoms1": 10,
               # "ninterval1": 1,
              #  "intervals1": [(1, 10)],
                #"natoms_tip1": 2,
               # "atoms1": [2, 3],
              #  "ncell2": 0,
             #   "total_atoms2": 8,
            #    "ninterval2": 1,
         #       "intervals2": [(11, 18)],
          #      "natoms_tip2": 3,
           #     "atoms2": [12, 13, 14],
        #    },
            #"ETA": {
           #     "imag_part": 0.05,
          #      "intervals": [(1, 5)],
         #   },
        #    "TRANS": {
               # "ieta": True,
              #  "iwrt_trans": False,
             #   "ichannel": True,
        #        "ifithop": 1,
         #       "Ebottom": -2.0,
            #    "Etop": 2.0,
           #     "nsteps": 4,
          #      "eta": 0.02,
       #     },
           # "BIAS": {
            #    "bias": -3.0,
             #   "z_top": 11.537758,
            #    "z_bottom": -18.061922,
      #     # }
     #   }
    #})

    #generate_calc_job(fixture_sandbox, entry_point_name, inputs)

    #for fname in ["interaction.optional", "eta.optional", "trans.optional"]:
    #    assert fname in fixture_sandbox.get_content_list()
   #     with fixture_sandbox.open(fname) as fsrc, open(fname, "w") as fdst:
  #          fdst.write(fsrc.read())
 #           fdst.write(fsrc.read())

   # with open("bias.optional") as f:
       # content = f.read()
      #  assert "-3.0" in content
       # assert "11.537758" in content
      #  assert "-18.061922" in content


def test_fireball_transport_eta_trans_interaction_only(
    fixture_sandbox,
    generate_calc_job,
    generate_inputs_fireball,
    generate_calc_job_node,
    fixture_localhost,
):
    """Test la génération des fichiers eta.optional, trans.optional et interaction.optional uniquement."""
    entry_point_name = "fireball.fireball"
    node = generate_calc_job_node(entry_point_name, fixture_localhost, test_name="test_fireball_transport_eta_trans_interaction_only")

    inputs = generate_inputs_fireball()
    inputs["parent_folder"] = node.outputs.remote_folder
    inputs["settings"] = orm.Dict(dict={
        "TRANSPORT": {
            "INTERACTION": {
                "ncell1": 0,
                "total_atoms1": 10,
                "ninterval1": 1,
                "intervals1": [(1, 10)],
                "natoms_tip1": 2,
                "atoms1": [2, 3],
                "ncell2": 0,
                "total_atoms2": 8,
                "ninterval2": 1,
                "intervals2": [(11, 18)],
                "natoms_tip2": 3,
                "atoms2": [12, 13, 14],
            },
            "ETA": {
                "imag_part": 0.05,
                "intervals": [(1, 5)],
            },
            "TRANS": {
                "ieta": True,
                "iwrt_trans": False,
                "ichannel": True,
                "ifithop": 1,
                "Ebottom": -2.0,
                "Etop": 2.0,
                "nsteps": 4,
                "eta": 0.02,
            }
        }
    })

    generate_calc_job(fixture_sandbox, entry_point_name, inputs)

    # Vérifie la présence et copie les fichiers dans le dossier courant
    for fname in ["interaction.optional", "eta.optional", "trans.optional"]:
        assert fname in fixture_sandbox.get_content_list()
        with fixture_sandbox.open(fname) as fsrc, open(fname, "w") as fdst:
            fdst.write(fsrc.read())

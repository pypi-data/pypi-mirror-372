"""WorkChain to relax the structure of a crystal using the Fireball code and the Birch-Murnaghan equation of state."""

import numpy as np
from aiida import orm
from aiida.engine import ToContext, WorkChain, calcfunction
from aiida_fireball.calculations.birch_murnaghan_fit import birch_murnaghan_fit_bayesian
from aiida_fireball.calculations.fireball import FireballCalculation
from aiida_fireball.calculations.structure.tools import scale_structure

# pylint: disable=no-member

__all__ = ("FireballBirchMurnaghanRelaxWorkChain",)


@calcfunction
def extract_volumes_energies(*results_dicts):
    """Extract the volumes and energies from the FireballCalculations' output_parameters."""
    volumes = []
    energies = []
    for result_dict in results_dicts:
        volumes.append(result_dict.get_dict()["volume"])
        energies.append(result_dict.get_dict()["total_energy"])

    return {
        "volumes": orm.List(volumes),
        "energies": orm.List(energies),
    }


class FireballBirchMurnaghanRelaxWorkChain(WorkChain):
    """
    WorkChain to perform a relaxation of a structure using the Fireball code and fit the Birch-Murnaghan equation of state.

    Inputs:
        - structure (orm.StructureData): The input structure.
        - scale_std (orm.Float): The standard deviation to generate the scale factors with a normal law (1.0, scale_std). Default is 0.02.
        - nb_scale (orm.Int): The number of scale factors to generate. Default is 20.
        - prior_means (orm.Dict): The prior means for the pymc bayesian analysis to fit
        the Birch-Murnaghan equation of state [E0, V0, B0, Bp, sigma]. Optional.
        - fireball_code (orm.Code): The code for the Fireball calculation.
        - fireball_options (orm.Dict): The options for the Fireball calculation.
        - fireball_parameters (orm.Dict): The parameters for the Fireball calculation.
        - clean_workdir (orm.Bool): Clean the working directories of all child calculations
        if ``clean_workdir=True`` in the inputs. Default is True.

    Outputs:
        - relaxed_structure (orm.StructureData): The relaxed structure.
        - volumes (orm.List): The volumes used in the fit.
        - energies (orm.List): The energies used in the fit.
        - popt (orm.Dict): The mean optimal parameters of the fit [E0, V0, B0, Bp, sigma].
        - perr (orm.Dict): The standard deviations of the parameters.

    Exit Codes:
        - 401 ERROR_FIREBALL_FAILED: One of the Fireball calculations failed.

    Methods:
        - generate_scale_factors: Generate the list of scale factors.
        - run_fireball_parallel: Run the Fireball calculation for each scaled structure.
        - inspect_all: Verify that all Fireball calculations finished successfully.
        - extract_volumes_energies: Extract the volumes and energies from the Fireball output_parameters.
        - fit_birch_murnaghan: Fit the Birch-Murnaghan equation of state to the volumes and energies.
        - return_results: Return the relaxed structure, the volumes, the energies and the fit results.
        - on_termination: Clean the working directories of all child calculations if ``clean_workdir=True`` in the inputs.
    """

    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input(
            "structure",
            valid_type=orm.StructureData,
            help="The input structure.",
        )
        spec.input(
            "scale_std",
            valid_type=orm.Float,
            default=lambda: orm.Float(0.02),
            help="The standard deviation to generate the scale factors with a normal law (1.0, scale_std).",
        )
        spec.input(
            "nb_scale",
            valid_type=orm.Int,
            default=lambda: orm.Int(20),
            help="The number of scale factors to generate.",
        )
        spec.input(
            "prior_means",
            valid_type=orm.Dict,
            required=False,
            default=lambda: orm.Dict({}),
            help="The prior means for the pymc bayesian analysis to fit \
                the Birch-Murnaghan equation of state [E0, V0, B0, Bp, sigma].",
        )
        spec.input(
            "fireball_code",
            valid_type=orm.Code,
            help="The code for the Fireball calculation.",
        )
        spec.input(
            "fireball_options",
            valid_type=orm.Dict,
            help="The options for the Fireball calculation.",
        )
        spec.input(
            "fireball_parameters",
            valid_type=orm.Dict,
            help="The parameters for the Fireball calculation.",
        )
        spec.input(
            "kpoints_distance",
            valid_type=orm.Float,
            help="The distance between kpoints in the reciprocal space.",
        )
        spec.input(
            "fdata_remote",
            valid_type=orm.RemoteData,
            help="The fdata remote folder.",
        )
        spec.input(
            "clean_workdir",
            valid_type=orm.Bool,
            default=lambda: orm.Bool(True),
            help="Clean the working directories of all child calculations if ``clean_workdir=True`` in the inputs.",
        )
        spec.outline(
            cls.generate_scale_factors,
            cls.run_fireball_parallel,
            cls.inspect_all,
            cls.extract_volumes_energies,
            cls.fit_birch_murnaghan,
            cls.return_results,
            cls.on_termination,
        )
        spec.output(
            "relaxed_structure",
            valid_type=orm.StructureData,
            help="The relaxed structure.",
        )
        spec.output(
            "volumes",
            valid_type=orm.List,
            help="The volumes used in the fit.",
        )
        spec.output(
            "energies",
            valid_type=orm.List,
            help="The energies used in the fit.",
        )
        spec.output(
            "popt",
            valid_type=orm.Dict,
            help="The mean optimal parameters of the fit [E0, V0, B0, Bp, sigma].",
        )
        spec.output(
            "perr",
            valid_type=orm.Dict,
            help="The standard deviations of the parameters.",
        )

        # Exit codes
        spec.exit_code(
            401,
            "ERROR_FIREBALL_FAILED",
            message="One of the Fireball calculations failed",
        )

    def generate_scale_factors(self) -> None:
        """Generate the list of scale factors."""
        scale_std: float = self.inputs.scale_std.value
        nb_scale: int = self.inputs.nb_scale.value
        scale_factors: np.ndarray = np.random.normal(1.0, scale_std, nb_scale)
        self.ctx.scale_factors = scale_factors
        self.report(f"Generated {nb_scale} scale factors")

    def run_fireball_parallel(self) -> ToContext:
        """Run the Fireball calculation for each scaled structure."""
        structure: orm.StructureData = self.inputs.structure
        scale_factors: np.ndarray = self.ctx.scale_factors
        fireball_code: orm.Code = self.inputs.fireball_code
        fireball_options: dict = self.inputs.fireball_options.get_dict()
        fireball_parameters: dict = self.inputs.fireball_parameters.get_dict()
        fireball_fdata_remote: orm.RemoteData = self.inputs.fdata_remote

        kpoints = orm.KpointsData()
        kpoints.set_cell_from_structure(structure)
        kpoints.set_kpoints_mesh_from_density(self.inputs.kpoints_distance.value)

        futures: dict = {}
        for i, scale_factor in enumerate(scale_factors):
            fireball_parameters.setdefault("OPTION", {}).setdefault("rescal", scale_factor)
            builder = FireballCalculation.get_builder()
            builder.code = fireball_code
            builder.structure = structure
            builder.kpoints = kpoints
            builder.fdata_remote = fireball_fdata_remote
            builder.parameters = orm.Dict(dict=fireball_parameters)
            builder.metadata.options = fireball_options
            fireball_calc = self.submit(builder)
            futures[f"fireball_{i}"] = fireball_calc
            self.report(f"launched FireballCalculation<{fireball_calc.pk}> with scale factor {scale_factor}")

        return ToContext(**futures)

    def inspect_all(self):
        """Verify that all Fireball calculations finished successfully."""
        for i in range(self.inputs.nb_scale.value):
            fireball_calc = self.ctx[f"fireball_{i}"]
            if not fireball_calc.is_finished_ok:
                self.report(f"FireballCalculation<{fireball_calc.pk}> failed with exit status {fireball_calc.exit_status}")
                return self.exit_codes.ERROR_FIREBALL_FAILED
        self.report("All Fireball calculations finished successfully")

    def extract_volumes_energies(self):
        """Extract the volumes and energies from the Fireball output_parameters."""
        fireball_calcs = [self.ctx[f"fireball_{i}"] for i in range(self.inputs.nb_scale.value)]
        results_dicts = [fireball.outputs.output_parameters for fireball in fireball_calcs]
        volumes_energies = extract_volumes_energies(*results_dicts)
        self.ctx.volumes = volumes_energies["volumes"]
        self.ctx.energies = volumes_energies["energies"]
        self.report(f"Extracted {len(self.ctx.volumes)} volumes and energies")

    def fit_birch_murnaghan(self):
        """Fit the Birch-Murnaghan equation of state to the volumes and energies."""
        volumes: orm.List = self.ctx.volumes
        energies: orm.List = self.ctx.energies
        fit_results = birch_murnaghan_fit_bayesian(
            volumes=volumes,
            energies=energies,
            prior_means=self.inputs.prior_means,
        )
        self.ctx.fit_results = fit_results
        self.report(f"Fitted Birch-Murnaghan equation of state: {fit_results['popt'].get_dict()}")

    def return_results(self):
        """Return the relaxed structure, the volumes, the energies and the fit results."""
        V0 = self.ctx.fit_results["popt"].get_dict()["V0"]
        V = self.inputs.structure.get_ase().get_volume()
        balance = (V0 / V) ** (1.0 / 3.0)
        relaxed_structure = scale_structure(
            structure=self.inputs.structure,
            scale_factor=orm.Float(balance),
        )
        self.out("relaxed_structure", relaxed_structure)
        self.out("volumes", self.ctx.volumes)
        self.out("energies", self.ctx.energies)
        self.out("popt", self.ctx.fit_results["popt"])
        self.out("perr", self.ctx.fit_results["perr"])

    def on_termination(self):
        """Clean the working directories of all child calculations if ``clean_workdir=True`` in the inputs."""

        if self.inputs.clean_workdir.value is False:
            self.report("remote folders will not be cleaned")
            return

        cleaned_calcs = []

        for called_descendant in self.node.called_descendants:
            if isinstance(called_descendant, orm.CalcJobNode):
                try:
                    called_descendant.outputs.remote_folder._clean()  # pylint: disable=protected-access
                    cleaned_calcs.append(called_descendant.pk)
                except (OSError, KeyError):
                    pass

        if cleaned_calcs:
            self.report(f"cleaned remote folders of calculations: {' '.join(map(str, cleaned_calcs))}")

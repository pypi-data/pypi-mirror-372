#!/usr/bin/env python3
"""
submit_qstate_parallel.py

1) Génère le slab W(110) via ASE (bcc110).
2) Soumet en parallèle un job Fireball pour chaque qstate.
3) Injecte un sed pour nettoyer les quotes sur qstate dans fireball.in.
4) Affiche les PKs et termine immédiatement.
"""

import aiida
aiida.load_profile()

from ase.build import bcc110
from aiida.orm import load_code, Dict, RemoteData, KpointsData, StructureData
from aiida.engine import submit
from aiida_fireball.calculations.fireball import FireballCalculation

# 1) Construction du slab W(110)
slab = bcc110('W', size=(1,1,15), a=3.1652, vacuum=20.0)
structure = StructureData(ase=slab)

# 2) Code MPI et dossier Fdata
code = load_code('fireball_mpi@ruche')
fdata_remote = RemoteData(
    computer=code.computer,
    remote_path='/gpfs/workdir/mamloukm/fdata-WSSe/Fdata'
)

# 3) K-points 15×15×1
kpoints = KpointsData()
kpoints.set_kpoints_mesh([15, 15, 1])

# 4) Valeurs de qstate (float)
qstates = [0, 0.0078, 0.0156, 0.0233, 0.0311, 0.0389, 0.0467, 0.0545]

# 5) Paramètres Fireball de base (numériques)
base_params = {
    "OPTION": {
        "nstepi":   1,
        "nstepf":   5000,
        "icluster": 0,
        "iquench":  -1,
        "iqout":    1,
        "dt":        0.25,
        "itrans":   0,
        # qstate ajouté ci-dessous
    },
    "OUTPUT": {
        "iwrtxyz":     0,
        "iwrtdos":     0,
        "iwrteigen":   0,
        "iwrtcdcoefs": 0,
    },
}

# 6) Soumission en parallèle
print("Soumission des jobs qstate en parallèle…", flush=True)
for q in qstates:
    params = {**base_params}
    params["OPTION"]["qstate"] = q
    parameters = Dict(dict=params)

    builder = FireballCalculation.get_builder()
    builder.code         = code
    builder.structure    = structure
    builder.kpoints      = kpoints
    builder.parameters   = parameters
    builder.fdata_remote = fdata_remote

    builder.metadata.label       = f"opt_W_110_q{q}"
    builder.metadata.options.queue_name            = "cpu_long"
    builder.metadata.options.max_wallclock_seconds = 168 * 3600
    builder.metadata.options.resources = {
        "num_machines":             1,
        "num_mpiprocs_per_machine": 1,
        "num_cores_per_machine":    1,
    }

    # Nettoyage des quotes autour de qstate dans fireball.in
    builder.metadata.options.prepend_text = """
# Remove quotes around qstate
sed -i "s/\\(qstate *= *\\)'\\([0-9.]*d0\\)'/\\1\\2/" fireball.in
"""

    calc = submit(builder)
    print(f"  • qstate={q} → PK={calc.pk}", flush=True)

print("Tous les jobs ont été soumis. Le script se termine ici.")

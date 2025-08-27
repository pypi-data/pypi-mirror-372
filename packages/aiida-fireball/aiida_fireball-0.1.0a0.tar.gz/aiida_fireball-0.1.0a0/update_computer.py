#!/usr/bin/env python
import aiida
aiida.load_profile()

from ase.build import bulk, surface
from aiida.plugins import DataFactory
from aiida_fireball.calculations.fireball import FireballCalculation

# 1) Construire le slab W(110) en BCC
a = 3.165  # maille en Å
bulk_w = bulk('W', 'bcc', a=a)
slab = surface(bulk_w, (1, 1, 0), layers=4, vacuum=10.0)

# 2) Envelopper dans un StructureData AiiDA
StructureData = DataFactory('core.structure')
structure = StructureData(ase=slab)

# 3) Créer un KpointsData (maillage 4×4×1)
KpointsData = DataFactory('core.array.kpoints')
kpoints = KpointsData()
kpoints.set_kpoints_mesh([8, 8, 1])

# 4) Appeler la méthode generate_kpts()
kpts_content = FireballCalculation.generate_kpts(kpoints, structure)

# 5) Afficher le résultat
print("Contenu généré pour aiida.kpts :\n")
print(kpts_content)

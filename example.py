"""Example of pyscf2vmd.
"""

import numpy as np
from pyscf import gto, scf, lo
from pyscf2vmd import set_paths, Plotter, CubeFile

# Set paths for VMD and tachyon
set_paths(
    tachyon="/usr/local/lib/vmd/tachyon_LINUXAMD64",
    vmd="/usr/local/bin/vmd",
)

# Get some system and an orbital
mol = gto.Mole(
    atom="C 0 0 0.667; C 0 0 -0.667; H 0 0.923 -1.232; H 0 -0.923 -1.232; H 0 0.923 1.232; H 0 -0.923 1.232",
    basis="cc-pvdz",
    verbose=0,
)
mol.build()
mf = scf.RHF(mol)
mf.kernel()
orbital = mf.mo_coeff[:, mol.nelectron//2-1]

# Set options
options = dict(
    render_res=(1920, 1080),
    convert_to_png=True,
    isovalue=0.1,
    rotate=[90.0, -10.0, 90.0],
)

# Plot the orbital
with CubeFile(mol, orbital=orbital):
    plotter = Plotter(**options)
    plotter.run()

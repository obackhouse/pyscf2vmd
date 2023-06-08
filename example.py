"""Example of pyscf2vmd.
"""

import numpy as np
from pyscf import gto, scf
from pyscf2vmd import set_paths, Plotter, CubeFile

# Set paths for VMD and tachyon
set_paths(
    tachyon="/usr/local/lib/vmd/tachyon_LINUXAMD64",
    vmd="/usr/local/bin/vmd",
)

# Get some system and an orbital
mol = gto.Mole(
    atom="H 0 0 0; Li 0 0 1.64",
    basis="cc-pvdz",
    verbose=0,
)
mol.build()
mf = scf.RHF(mol)
mf.kernel()
orbital = mf.mo_coeff[:, mol.nelectron//2-1]

# Orthogonalise the orbital
s = mol.intor("int1e_ovlp")
w, v = np.linalg.eigh(s)
orth = np.dot(v * w[None]**0.5, v.T.conj())
orbital = np.dot(orth, orbital)

# Set options
options = dict(
    render_res = (1920, 1080),
    convert_to_png = True,
)

# Plot the orbital
with CubeFile(mol, orbital=orbital):
    plotter = Plotter(**options)
    plotter.run()

"""Example of pyscf2vmd for periodic systems.
"""

import numpy as np
from pyscf import lo
from pyscf.pbc import gto, dft
from pyscf.pbc.tools.k2gamma import mo_k2gamma
from pyscf2vmd import set_paths, Plotter, CubeFile

# Set paths for VMD and tachyon
set_paths(
    tachyon="/usr/local/lib/vmd/tachyon_LINUXAMD64",
    vmd="/usr/local/bin/vmd",
)

# Get some system and an orbital
cell = gto.Cell(
    atom="C 1.23 0.71 10; C 2.46 1.42 10",
    basis="gth-szv",
    pseudo="gth-pade",
    a=[[2.46, 0, 0], [1.23, 2.13, 0], [0, 0, 20]],
    verbose=0,
)
cell.build()
kmesh = [5, 5, 1]
mf = dft.KRKS(cell, xc="pbe,pbe", kpts=cell.make_kpts(kmesh))
mf = mf.density_fit(auxbasis="weigend")
mf.kernel()
supcell, mo_energy_sc, mo_coeff_sc, _ = mo_k2gamma(cell, mf.mo_energy, mf.mo_coeff, mf.kpts, kmesh=kmesh)
orbital = mo_coeff_sc[:, (cell.nelectron*np.prod(kmesh))//2-1]

# Set options
options = dict(
    render_res=(1920, 1080),
    convert_to_png=True,
    isovalue=0.04,
    atom_radius=0.1,
    bond_radius=0.0,
    rotate=[-45.0, 0.0, 0.0],
)

# Plot the orbital
with CubeFile(supcell, orbital=orbital):
    plotter = Plotter(**options)
    plotter.run()

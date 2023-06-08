"""
Functions for building the cube file.
"""

import os
import numpy as np
from pyscf import gto
from pyscf.tools import cubegen


class CubeFile:
    """Context manager to instantiate the cube file.
    """

    def __init__(
        self,
        mol: gto.Mole,
        orbital: np.ndarray = None,
        file: str = "input.cube",
    ):
        self.mol = mol
        self.orbital = orbital
        self.file = file

    def __enter__(self):
        """Instantiate the cube file.
        """

        orbital = self.orbital if self.orbital is not None else np.zeros((self.mol.nao,))
        cubegen.orbital(self.mol, self.file, orbital)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Remove the cube file.
        """

        os.system("rm -f %s" % self.file)

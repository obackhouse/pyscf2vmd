"""pyscf2vmd
"""

TACHYON_PATH = "/usr/local/lib/vmd/tachyon_LINUXAMD64"
VMD_PATH = "/usr/local/bin/vmd"

def set_paths(tachyon=None, vmd=None):
    """Set the paths for tachyon and VMD.
    """

    global TACHYON_PATH
    global VMD_PATH

    if tachyon is not None:
        TACHYON_PATH = tachyon

    if vmd is not None:
        VMD_PATH = vmd

from pyscf2vmd.draw import Plotter
from pyscf2vmd.cube import CubeFile

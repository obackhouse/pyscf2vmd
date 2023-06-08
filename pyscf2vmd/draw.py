"""
Functions for drawing the orbital in VMD.
"""

from typing import Iterable, Union, Any
import dataclasses
import datetime
import sys
import os

from pyscf2vmd import TACHYON_PATH, VMD_PATH


@dataclasses.dataclass
class Options:
    """Options for the VMD orbital plot.
    """

    # Display settings
    projection: str = "Stereographic"
    depthcue: bool = False
    axes: bool = False
    carbon_color: Iterable[float] = (0.5, 0.5, 0.5)
    background_color: Iterable[float] = (1.0, 1.0, 1.0)
    rotate: Union[Iterable[float], str] = (0.0, 0.0, 0.0)  # If str, load from visualisation state
    lights: Iterable[bool] = (True, True, False, False)
    shadows: bool = True
    zoom: float = 1.0

    # Molecule settings
    bond_radius: float = 0.15
    atom_radius: float = None  # set to None for 'licorice' layout
    mol_res: int = 200
    mol_material: str = "AOChalky"

    # Orbital settings
    show_orbitals: bool = True
    isovalue: float = 0.05
    orb_material: str = "AOShiny"
    orb_color_pos: Iterable[float] = (0.122, 0.467, 0.706)  # Matplotlib blue
    orb_color_neg: Iterable[float] = (1.000, 0.498, 0.055)  # Matplotlib orange

    # Render settings
    render_res: Iterable[float] = (4000, 3000)
    ambient_occlusion: bool = True
    ao_ambient: float = 0.7
    ao_direct: float = 0.2

    # Material settings
    material_settings: dict = dataclasses.field(
        default_factory=lambda: {
            "AOShiny": {
                "specular": 1.0,
                "ambient": 0.5,
                "shininess": 0.7,
            }
        }
    )

    # File settings
    input_file: str = "input.cube"
    keep_vmd_input: bool = False
    quit_vmd: bool = True
    tachyon_path: str = TACHYON_PATH
    vmd_path: str = VMD_PATH
    convert_to_png: bool = True

    # Other settings
    other_commands: Iterable[Any] = tuple()


class Plotter:
    """Class to handle the VMD plotting.
    """

    def __init__(self, options=None, **kwargs):
        if options is None:
            options = Options()
        self.options = options
        for key, val in kwargs.items():
            setattr(self.options, key, val)

    def init_input(self):
        """Initialise the VMD input file.
        """

        with open("input.vmd", "w") as f:
            f.write("# VMD input file generated using pyscf2vmd\n")
            f.write("# Input file: %s\n" % self.options.input_file)
            f.write("# Generated at %s\n\n" % datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    def clean(self):
        """Clean up input file.
        """

        if not self.options.keep_vmd_input:
            os.system("rm -f input.vmd")

        os.system("rm -f vmdscene.dat")
        os.system("mv vmdscene.dat.tga %s.tga" % self.options.input_file.split(".")[0])

        if self.options.convert_to_png:
            os.system("convert %s.tga %s.png" % (self.options.input_file.split(".")[0], self.options.input_file.split(".")[0]))
            os.system("rm -f %s.tga" % self.options.input_file.split(".")[0])

    def add_command(self, cmd):
        """Add command to the input file.
        """

        with open("input.vmd", "a") as f:
            f.write(cmd + "\n")

    def launch_vmd(self):
        """Launch VMD with the input file.
        """

        os.system("%s -e input.vmd" % self.options.vmd_path)

    def write_input(self):
        """Write the input file.
        """

        assert os.path.isfile(self.options.input_file)

        self.add_command("# Display settings")
        self.add_command("display projection %s" % self.options.projection)
        self.add_command("display depthcue %s" % ["off", "on"][self.options.depthcue])
        if not self.options.axes:
            self.add_command("axes location off")
        if self.options.ambient_occlusion:
            self.add_command("display ambientocclusion on")
            self.add_command("display aoambient %f" % self.options.ao_ambient)
            self.add_command("display aodirect %f" % self.options.ao_direct)
        for i, light in enumerate(self.options.lights):
            self.add_command("light %d %s" % (i, ["off", "on"][light]))
        self.add_command("display shadows %s" % ["off", "on"][self.options.shadows])
        self.add_command("\n")

        self.add_command("# Load molecule")
        self.add_command("mol delete all")
        self.add_command("mol new %s type %s" % (self.options.input_file, self.options.input_file.split(".")[-1]))
        self.add_command("\n")

        self.add_command("# Material settings")
        for mat, val in self.options.material_settings.items():
            for prop, value in val.items():
                self.add_command("material change %s %s %f" % (prop, mat, value))
        self.add_command("\n")

        self.add_command("# Add the molecule representation")
        self.add_command("mol delrep 0 top")
        if self.options.atom_radius is None:
            self.add_command("mol representation licorice %f %d %d" % (self.options.bond_radius, self.options.mol_res, self.options.mol_res))
        else:
            self.add_command("mol representation CPK %f %f %d %d" % (self.options.atom_radius * 5, self.options.bond_radius * 5, self.options.mol_res, self.options.mol_res))
        self.add_command("mol color Name")
        self.add_command("mol material %s" % self.options.mol_material)
        self.add_command("mol addrep top")
        self.add_command("\n")

        if self.options.show_orbitals is not None:
            self.add_command("# Add the positive orbital representation")
            self.add_command("mol representation Isosurface %f 0 0 0 1 1" % self.options.isovalue)
            self.add_command("mol selection all")
            self.add_command("mol material %s" % self.options.orb_material)
            self.add_command("color change rgb 30 %f %f %f" % tuple(self.options.orb_color_pos))
            self.add_command("mol color ColorID 30")
            self.add_command("mol addrep 0")
            self.add_command("\n")

            self.add_command("# Add the negative orbital representation")
            self.add_command("mol representation Isosurface %f 0 0 0 1 1" % -self.options.isovalue)
            self.add_command("mol selection all")
            self.add_command("mol material %s" % self.options.orb_material)
            self.add_command("color change rgb 29 %f %f %f" % tuple(self.options.orb_color_neg))
            self.add_command("mol color ColorID 29")
            self.add_command("mol addrep 0")
            self.add_command("\n")

        if self.options.carbon_color:
            self.add_command("# Change colours")
            self.add_command("color change rgb 31 %f %f %f" % tuple(self.options.carbon_color))
            self.add_command("color Name C orange2")
            self.add_command("color Type C orange2")
        if self.options.background_color:
            self.add_command("color change rgb 32 %f %f %f" % tuple(self.options.background_color))
            self.add_command("color Display Background orange3")
        if self.options.carbon_color or self.options.background_color:
            self.add_command("\n")

        self.add_command("# Rotate the view")
        if isinstance(self.options.rotate, (list, tuple)):
            self.add_command("rotate x by %f" % self.options.rotate[0])
            self.add_command("rotate y by %f" % self.options.rotate[1])
            self.add_command("rotate z by %f" % self.options.rotate[2])
        elif self.options.rotate is not None:
            with open(self.options.rotate, "r") as f:
                lines = f.readlines()
                for i in range(len(lines)):
                    if lines[i].startswith("set viewpoints"):
                        start = i
                        break
                for i in range(start, len(lines)):
                    if lines[i].startswith("unset topmol"):
                        end = i+1
                        break
                self.add_command("set viewplist {}")
                self.add_command("set fixedlist {}")
                for line in lines[start:end]:
                    self.add_command(line.strip())
        self.add_command("scale by %f" % self.options.zoom)
        self.add_command("\n")

        if len(self.options.other_commands):
            self.add_command(self.options.other_commands)
            self.add_command("\n")

        self.add_command("# Render the image")
        self.add_command("render Tachyon vmdscene.dat "
            + "\"%s\" " % self.options.tachyon_path
            + "-aasamples 12 %s -format TARGA "
            + "-res %d %d " % self.options.render_res
            + "-o %s.tga"
        )
        self.add_command("\n")

        if self.options.quit_vmd:
            self.add_command("# cya")
            self.add_command("quit")

    def run(self):
        """Run the workflow.
        """

        self.init_input()
        self.write_input()
        self.launch_vmd()
        self.clean()

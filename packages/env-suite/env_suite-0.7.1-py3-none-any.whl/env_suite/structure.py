"""
A module for parsing and representing the structure of a molecule.
"""
# Imports
import numpy as np
import re


# TODO: replace by ase parser?
class Parser():
    """
    A class for representing the structure of a molecule

    Parameters
    ----------
    Filename : str
        The name of the file containing the structure.

    Returns
    -------
    structure_dict : dict
        A dictionary containing the structure of the molecule.
    """

    def __init__(self, filename: str):
        self.filename = filename

    def vasp(self) -> dict:
        """
        Parses a VASP PSCAR file and returns a dictionary
        """
        with open(self.filename, 'r') as f:
            data = f.readlines()
        data = [x.strip().split() for x in data]
        name: str = data[0][0]
        scale_factor: float = float(data[1][0])
        lattice_vectors: np.ndarray = np.array(data[2:5], dtype=float)
        atoms: list = data[5]
        natoms: list = [int(x) for x in data[6]]
        _n: int = sum(natoms)
        coord_type: str = data[7][0].lower()
        if coord_type == 'direct':
            coord_type = 'fractional'
        else:
            coord_type = 'cartesian'
        coords: np.ndarray = np.array(data[8:8+_n], dtype=float)
        atom_list: list = [f'{symbol} ' * num
                           for symbol, num in zip(atoms, natoms)]
        atom_list = ' '.join(atom_list).split()

        a1, a2, a3 = lattice_vectors
        volume = np.dot(a1, np.cross(a2, a3))

        # 2 PI is included in the summation
        recip_lattice_vectors = np.array([
            np.cross(a2, a3),
            np.cross(a3, a1),
            np.cross(a1, a2)
        ]) / volume

        structure_dict = {'name': name,
                          'scale_factor': scale_factor,
                          'lattice_vectors': lattice_vectors,
                          'recip_lattice_vectors': recip_lattice_vectors,
                          'atoms': atoms,
                          'natoms': natoms,
                          'coord_type': coord_type,
                          'coords': coords,
                          'atom_list': atom_list,
                          'volume': volume,
                          'N': _n}

        return structure_dict

    def xyz(self) -> dict:
        """
        Parses an XYZ file and returns a dictionary
        """

        with open(self.filename, 'r') as f:
            data = f.readlines()
        data = [x.split() for x in data]
        name: str = self.filename.split('.')[0]
        natoms: int = int(data[0][0])
        atom_list: np.ndarray = np.array(
                [x[0] for x in data[2:2+natoms]]
                )
        coords: np.ndarray = np.array(
                [x[1:] for x in data[2:2+natoms]],
                dtype=float)

        structure_dict = {'name': name,
                          'N': natoms,
                          'atom_list': atom_list,
                          'coord_type': 'cartesian',
                          'coords': coords}

        return structure_dict


def get_index(atoms: list,
              atom: str,
              natoms: list,
              ) -> np.ndarray:
    """
    Returns the index of a given atom

    Parameters
    ----------
    atoms : list
        A list of the atoms in the structure.
    atom : str
        The atom to find the index of.
    natoms : list
        A list of the number of each atom in the structure.

    Returns
    -------
    index : np.ndarray
        The index of the atom in the structure.
    """

    atom = re.split(r'(\d+)', atom)
    for ind, sym in enumerate(atoms):
        if sym == atom[0]:
            index = ind

    prev = np.sum(natoms[:index])
    return int(prev) + int(atom[1]) - 1


def generate_qm_idc(qm, ref):

    for site in qm:
        idc = np.flatnonzero(np.isclose(ref, site).all(axis=1))

        if len(idc) == 0:
            raise ValueError('No matching sites found')
        elif len(idc) == 1:
            yield idc[0]
        else:
            raise ValueError('Multiple matching sites found')

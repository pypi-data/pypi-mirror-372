from itertools import product
from functools import reduce
from math import ceil
from collections import Counter

# from pymatgen.core.structure import Molecule
# from pymatgen.analysis.graphs import StructureGraph
# from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
# from pymatgen.analysis.local_env import IsayevNN
import networkx as nx
import networkx.algorithms.isomorphism as iso

from phonopy.interface.vasp import read_vasp  # TODO: replace by alternative POSCAR parser
import numpy as np
import numpy.linalg as la

from .utils import ModuleImporter


def generate_molecular_graph(structure, bonding_cutoff=3.0):

    # Imports pymatgen modules
    p_graphs = ModuleImporter('pymatgen.analysis.graphs')
    p_local_env = ModuleImporter('pymatgen.analysis.local_env')
    p_analyzer = ModuleImporter('pymatgen.symmetry.analyzer')

    # Import classes
    StructureGraph = p_graphs.StructureGraph
    IsayevNN = p_local_env.IsayevNN
    SpacegroupAnalyzer = p_analyzer.SpacegroupAnalyzer

    strategy = IsayevNN(cutoff=bonding_cutoff, allow_pathological=True)
    # Updated to use the recommended from_local_env_strategy to fix deprecation warning
    graph = StructureGraph.from_local_env_strategy(structure, strategy, weights=True)

    sym_structure = SpacegroupAnalyzer(structure).get_symmetrized_structure()
    equivalent_positions = sym_structure.as_dict()['equivalent_positions']

    # build directed multi-graph
    twoway = nx.MultiDiGraph(graph.graph)
    # nodes are labelled by species
    nx.set_node_attributes(twoway,
        {node: {'symm_equiv': (structure[node].specie, equivalent_positions[node])} for node in twoway})

    def flip_edge(u, v, data):
        return v, u, {key: tuple(-i for i in val) if key == 'to_jimage'
                      else val for key, val in data.items()}

    # edges are labelled by periodic image crossing
    twoway.add_edges_from([flip_edge(*edge) for edge in twoway.edges(data=True)])

    return twoway


def split_molecular_graph(graph, filter_unique=False):

    connected = nx.connected_components(nx.Graph(graph))

    subgraphs = map(graph.subgraph, connected)

    def filter_unique_graphs(graphs):

        edge_match = iso.numerical_edge_match("weight", 1.0)
        node_match = iso.categorical_node_match("symm_equiv", None)

        unique_graphs = set()

        for graph in graphs:

            def graph_match(g):
                return nx.is_isomorphic(
                    graph, g, node_match=node_match, edge_match=edge_match)

            already_present = map(graph_match, unique_graphs)

            if not any(already_present):
                unique_graphs.add(graph)
                yield graph

    if filter_unique:
        return list(filter_unique_graphs(subgraphs))
    else:
        return list(subgraphs)


def extract_molecule(structure, graph, central_index=None):

    # Imports pymatgen modules
    p_structure = ModuleImporter('pymatgen.core.structure')
    Molecule = p_structure.Molecule

    # walk graph and consider to_jimage
    def generate_shifts():

        start = next(iter(graph.nodes())) if central_index is None else central_index

        def walk(shifts, edge):
            a, b = edge
            return shifts | {b: shifts[a] + graph[a][b][0]['to_jimage']}

        edges = nx.bfs_edges(graph, source=start)
        shifts = reduce(walk, edges, {start: np.zeros(3)})
        return dict(sorted(shifts.items()))

    shifts = generate_shifts()

    species = [structure.species[idx] for idx in shifts]
    coords = [structure.lattice.get_cartesian_coords(
        structure.frac_coords[idx] + shift) for idx, shift in shifts.items()]
    molecule = Molecule(species, coords)

    return list(shifts.keys()), molecule


def get_unique_entities(structure):

    # Imports pymatgen modules
    p_analyzer = ModuleImporter('pymatgen.symmetry.analyzer')
    SpacegroupAnalyzer = p_analyzer.SpacegroupAnalyzer

    sym_structure = SpacegroupAnalyzer(structure).get_symmetrized_structure()
    structure_dict = sym_structure.as_dict()
    equivalent_positions = structure_dict['equivalent_positions']

    molecular_graph = generate_molecular_graph(structure)
    connected_graphs = split_molecular_graph(molecular_graph, filter_unique=True)
    indices, molecules = zip(*map(lambda x: extract_molecule(structure, x), connected_graphs))

    elements = [site.specie.symbol for site in structure]

    mappings = [[equivalent_positions[idx] for idx in shift_dict]
                for shift_dict in indices]

    return equivalent_positions, elements, mappings, molecules


def generate_qm_region(idx, graph, structure):
    connected_graphs = split_molecular_graph(graph, filter_unique=False)
    central_graph = next(filter(lambda nodes: idx in nodes, connected_graphs))
    _, mol = extract_molecule(structure, central_graph, central_index=idx)
    central_site = structure.sites[idx]
    shift = np.array([central_site.x, central_site.y, central_site.z])
    return mol, shift


def build_cluster(poscar, central_idc=None, cluster_expansion=None,
                  cluster_cutoff=None):

    if cluster_expansion is not None:
        cluster = UnitSupercell.from_poscar(
            poscar, cluster_expansion, central_idc=central_idc)
    elif cluster_cutoff is not None:
        cluster = UnitSphere.from_poscar(
            poscar, cluster_cutoff, central_idc=central_idc)
    else:
        ValueError("Invalid cluster specification!")

    return cluster


class UnitCluster:
    """Base class for cluster of specific morphology made from unit cells.

    Parameters
    ----------
    lat_vecs : list
        Lattice vectors of unit cell as rows
    coords : list
        Coordinates of each atom in cell as fraction of cell parameters
    atom_data : list
        List of tuples containing atomic numbers, symbols, and original indices
    centre : list
        Coordinates of the centre of interest

    Attributes
    ----------
    cart_coords : list
        Cartesian coordinates of the expanded and shifted structure
    labels : list
        Labels for each atom in the final cluster, including boundary info.
    """
    def __init__(self, lat_vecs, coords, atom_data, centre, *args, **kwargs):

        self.lat_vecs = lat_vecs
        self.unit_coords = coords
        self.atom_data = atom_data
        # keep atom_numbers for compatibility with spin_phonon_suite
        self.atom_numbers = [ad[0] for ad in self.atom_data]

        # Periodically pre-shift unit cell to centre of interest, based on expansion parity
        translated_coords = self.recentre_unitcell(coords, centre, *args)
        
        # Symmetrise the translated cell by duplicating and pre-labeling all boundary atoms
        symm_points = self._symmetrise_cell(translated_coords)
        
        # Neatly print the padded cell, including boundary atoms
        self._print_padded_cell(symm_points)

        # Generate the full cluster, merging overlaps and creating final labels
        cart_coords, self.labels, atom_fractions = self.generate_cluster(symm_points, *args)

        # Apply final translation to move the geometric centre of the cluster to the origin
        final_shift_frac = self.get_final_shift_vector(*args)
        final_shift_cart = final_shift_frac @ self.lat_vecs
        self.cart_coords = cart_coords - final_shift_cart

        self.frac_coords = self.cart_coords @ la.inv(self.lat_vecs)
        self.n_atoms = len(self.cart_coords)
        self.n_cell = len(list(self.generate_cell_idc(*args)))
        
        a1, a2, a3 = self.lat_vecs
        self.unit_volume = np.dot(a1, np.cross(a2, a3))

        # The following is for Ewald summation, where 2pi is included in the summation
        self.recip_vecs = np.array([
            np.cross(a2, a3),
            np.cross(a3, a1),
            np.cross(a1, a2)
        ]) / self.unit_volume
        
        # Perform and print the atom fraction consistency check
        # This is that the number of atoms is equal to the N * Z, where N is
        # the number of unit cells, and Z is atoms per unit cell (taking into 
        # account atom fractions)
        self._check_and_print_consistency(self.labels, atom_fractions, *args)

    @classmethod
    def from_poscar(cls, poscar_name, *args, central_idc=None, centre=None):
        atoms = read_vasp(poscar_name)
        coords = atoms.scaled_positions
        
        atom_data = [(num, sym, i+1) for i, (num, sym) in enumerate(zip(atoms.numbers, atoms.get_chemical_symbols()))]

        if centre is not None:
            centre_frac = centre
        elif central_idc is not None:
            centre_frac = np.mean(coords[list(central_idc)], axis=0)
        else:
            centre_frac = np.zeros(3)

        return cls(atoms.cell, coords, atom_data, centre_frac, *args)
    
    def _symmetrise_cell(self, frac_coords):
        """
        Creates a 'padded' cell by duplicating all boundary atoms and pre-labeling them
        with a charge fraction.
        Returns a list of tuples: (coordinate, original_index, atom_fraction)
        """
        symm_points = []
        
        for i, coord in enumerate(frac_coords):
            # Pre-label the atom with its fraction.
            # After recentring, coords are in [0, 1), so only check for 0.0
            is_boundary = np.isclose(coord, 0.0)
            on_boundary_count = np.sum(is_boundary)
            atom_fraction = 1.0 / (2**on_boundary_count)
            
            symm_points.append((coord, i, atom_fraction))

            if on_boundary_count == 0:
                continue

            # Generate all 2^N-1 other permutations for N boundary dimensions
            for j in range(1, 1 << on_boundary_count):
                new_coord = np.copy(coord)
                offset_indices = np.where(is_boundary)[0]
                
                for k, offset_idx in enumerate(offset_indices):
                    if (j >> k) & 1:
                        # Create symmetric partner at 1.0 for each 0.0 boundary
                        new_coord[offset_idx] = 1.0
                
                symm_points.append((new_coord, i, atom_fraction))
                
        return symm_points

    def generate_cluster(self, symm_points, *args):
        """Builds cluster, merges overlaps, and assigns boundary-aware labels."""

        # 1. Tile the symmetrised/pre-labeled points to create the raw cluster
        all_points = []
        for cell_idc in self.generate_cell_idc(*args):
            for frac_coord, original_idx, atom_fraction in symm_points:
                cart_coord = (frac_coord + cell_idc) @ self.lat_vecs
                all_points.append((cart_coord, original_idx, atom_fraction))

        # 2. Group points by rounding coordinates to find overlaps
        unique_points = {}
        for cart_coord, original_idx, atom_fraction in all_points:
            key = tuple(np.round(cart_coord, 6))
            if key not in unique_points:
                # Store the original, higher-precision coordinate the first time a key is seen
                unique_points[key] = {'coord': cart_coord, 'merges': []}
            unique_points[key]['merges'].append((original_idx, atom_fraction))

        # 3. Create final list of atoms and labels by summing atom fractions
        final_cart_coords = []
        final_labels = []
        final_atom_fractions = []

        for key, data in unique_points.items():
            # Use the stored, higher-precision coordinate for the final output
            final_cart_coords.append(data['coord'])
            merged_points = data['merges']

            original_idx, base_fraction = merged_points[0]
            symbol = self.atom_data[original_idx][1]
            original_label_idx = self.atom_data[original_idx][2]

            # Sum the atom fractions of all merged points
            total_atom_fraction = sum(p[1] for p in merged_points)
            final_atom_fractions.append(total_atom_fraction)

            # Determine boundary suffix from the total atom fraction
            boundary_suffix = ""
            if np.isclose(total_atom_fraction, 1.0):
                boundary_suffix = ""  # Interior
            elif np.isclose(total_atom_fraction, 0.5):
                boundary_suffix = ".f"  # Face
            elif np.isclose(total_atom_fraction, 0.25):
                boundary_suffix = ".e"  # Edge
            elif np.isclose(total_atom_fraction, 0.125):
                boundary_suffix = ".c"  # Corner
            # Handle other boundary cases
            else:
                base_fraction_is_edge = any(np.isclose(p[1], 0.25) for p in merged_points)
                if np.isclose(total_atom_fraction, 0.75):
                    boundary_suffix = ".e34" if base_fraction_is_edge else ".c68"
                elif np.isclose(total_atom_fraction, 0.375):
                    boundary_suffix = ".c38"
                elif np.isclose(total_atom_fraction, 0.625):
                    boundary_suffix = ".c58"
                elif np.isclose(total_atom_fraction, 0.875):
                    boundary_suffix = ".c78"

            label = f"{symbol}.ENV{boundary_suffix}.{original_label_idx}"
            final_labels.append(label)

        return np.array(final_cart_coords), final_labels, final_atom_fractions

    def _print_padded_cell(self, symm_points):
        """Neatly prints the boundary atoms in the padded, pre-labeled unit cell."""
        print("\nBoundary atoms in translated unit cell:")
        print(f"{'Atom':<6} {'Orig Idx':<9} {'x':>8} {'y':>8} {'z':>8}   {'Atom Fraction':<15}")
        print("-" * 65)
        
        found_boundary_atom = False
        for coord, original_idx, atom_fraction in symm_points:
            if atom_fraction < 1.0:
                found_boundary_atom = True
                symbol = self.atom_data[original_idx][1]
                print(f"{symbol:<6} {original_idx:<9} {coord[0]:8.4f} {coord[1]:8.4f} {coord[2]:8.4f}   {atom_fraction:<15.4f}")
        
        if not found_boundary_atom:
            print("No boundary atoms found in this unit cell.")

        print("-" * 65 + "\n")

    def _check_and_print_consistency(self, final_labels, final_atom_fractions, *args):
        """Performs a final check and prints a summary of the generated cluster."""

        n_atoms_poscar = len(self.atom_data)
        n_tiled_cells = len(list(self.generate_cell_idc(*args)))
        total_atom_sum = sum(final_atom_fractions)
        
        # Map suffixes to descriptive names
        suffix_map = {
            "f": "Face", "e": "Edge", "c": "Corner",
            "e34": "Edge (3/4)", "c38": "Corner (3/8)", "c58": "Corner (5/8)",
            "c68": "Corner (6/8)", "c78": "Corner (7/8)"
        }

        # Count boundary types from the generated labels
        counts = Counter()
        for label in final_labels:
            if 'ENV' not in label:
                counts['QM'] += 1
                continue
            
            parts = label.split('.')
            if len(parts) >= 3 and parts[1] == 'ENV':
                if len(parts) == 3:
                    counts['Interior'] += 1
                else:
                    suffix = parts[2]
                    descriptive_name = suffix_map.get(suffix, f"Unknown ({suffix})")
                    counts[descriptive_name] += 1
            else:
                counts['Unknown'] += 1
        
        print("\nCluster consistency check:")
        print(f"{'Atoms in POSCAR:':<25} {n_atoms_poscar}")
        print(f"{'Tiled Unit Cells:':<25} {n_tiled_cells}")
        print("-" * 40)
        print(f"{'Total Atoms in Cluster:':<25} {self.n_atoms}")
        print("\nBoundary atom summary:")
        for b_type, count in sorted(counts.items()):
            print(f"  - {b_type+':':<22} {count}")
        print("-" * 40)
        print(f"{'Sum of atom fractions:':<25} {total_atom_sum:.4f}")
        
        # Corrected atom conservation check
        if np.isclose(total_atom_sum, n_tiled_cells * n_atoms_poscar):
            print("Atom conservation check:       PASS")
        else:
            print("Atom conservation check:       FAIL")
        print("-" * 40 + "\n")

    def recentre_unitcell(self, frac, centre, *args):
        """This method is dynamically handled in subclasses."""
        raise NotImplementedError("recentre_unitcell must be implemented in a subclass")

    def get_final_shift_vector(self, *args):
        """This method is dynamically handled in subclasses."""
        raise NotImplementedError("get_final_shift_vector must be implemented in a subclass")


class UnitSupercell(UnitCluster):

    def generate_cell_idc(self, expansion):
        """Generates symmetric cell indices for tiling."""
        def expansion_range(num):
            if num % 2 == 0:  # even, e.g., 2 -> [-1, 0]
                return range(-(num // 2), num // 2)
            else:  # odd, e.g., 3 -> [-1, 0, 1]
                return range(-(num // 2), num // 2 + 1)

        for nvec in product(*map(expansion_range, expansion)):
            yield nvec
            
    def recentre_unitcell(self, frac, centre, expansion):
        """
        Translates unit cell so the central atom is at the correct position
        (0.0 or 0.5) based on the parity of the supercell expansion.
        """
        # For even expansion, centre is 0.0. For odd, centre is 0.5.
        target_centre = np.array([0.0 if n % 2 == 0 else 0.5 for n in expansion])
        return (frac - centre + target_centre) % 1.0

    def get_final_shift_vector(self, expansion):
        """
        Calculates the vector needed to shift the geometric centre of the
        supercell to the origin.
        """
        return np.array([0.0 if n % 2 == 0 else 0.5 for n in expansion])


class UnitSphere(UnitCluster):

    def generate_cell_idc(self, cutoff):

        def expansion_range(vec1, vec2, vec3):
            norm_vec = np.cross(vec2, vec3)
            num = ceil(abs(cutoff / np.dot(norm_vec / la.norm(norm_vec), vec1)))
            return range(-num, num + 1)

        cyc_perm = [[self.lat_vecs[i - j] for i in range(3)] for j in range(3)]

        for nvec in product(*map(expansion_range, *cyc_perm)):

            r = np.sum([ni * ci for ni, ci in zip(nvec, self.lat_vecs)], axis=0)

            if la.norm(r) <= cutoff:
                yield nvec
    
    def recentre_unitcell(self, frac, centre, cutoff):
        """Translates unit cell so the central atom is at (0.5, 0.5, 0.5)."""
        return (frac - centre + 0.5) % 1.0

    def get_final_shift_vector(self, cutoff):
        """
        Calculates the vector needed to shift the geometric centre of the
        spherical cluster to the origin.
        """
        return np.array([0.5, 0.5, 0.5])


def write_molcas_basis_interior_only(labels, charge_dict, name):
    """
    Writes a Molcas basis file for environment charges,
    containing only interior (unscaled) charges.
    """
    with open(name, 'w') as f:
        f.write("* This file was generated by env_suite (interior charges only)\n")
        for elem, (lab, chrg) in zip(labels, charge_dict.items()):
            f.write(f"/{elem}.{name}.{lab}.0s.0s.\n")
            f.write("Dummy basis set for atomic charges of environment\n")
            f.write("no ref\n")
            f.write(f"{chrg:.9f} 0\n")
            f.write("0 0\n")
    return

def write_molcas_basis_specific(elements, charge_dict, name, required_types):
    """
    Writes a molcas basis file, containing only
    the necessary boundary types for each element.
    """
    
    # Map suffix to charge scaling factor
    scaling_factors = {
        "interior": 1.0, "f": 0.5, "e": 0.25, "c": 0.125,
        "c38": 0.375, "c58": 0.625, "e34": 0.75, "c68": 0.75, "c78": 0.875
    }
    
    with open(name, 'w') as f:
        f.write("* This file was generated by env_suite (including boundary charges)\n")
        
        # Iterate through all atoms in the POSCAR to handle non-equivalent sites
        for original_index, elem in enumerate(elements, start=1):
            if elem in required_types:
                charge = charge_dict[original_index]
                
                # Check which boundary types are actually present for this element
                # and write only those to the ENV file.
                for boundary_type in sorted(list(required_types[elem])):
                    suffix = "" if boundary_type == "interior" else f".{boundary_type}"
                    scaled_charge = charge * scaling_factors.get(boundary_type, 1.0)
                    
                    f.write(f"/{elem}.{name}{suffix}.{original_index}.0s.0s.\n")
                    f.write("Dummy basis set for atomic charges of environment\n")
                    f.write("no ref\n")
                    f.write(f"{scaled_charge:.9f} 0\n")
                    f.write("0 0\n")
    return


def write_basistype_table():
    """Writes the basistype.tbl file required by Molcas for ENV basis sets."""
    content = "ENV ANO AE_ RH_ PN_"
    with open("basistype.tbl", "w") as f:
        f.write(content)

"""
Computed the infinite periodic electrostatic potential
using the Ewald method and fits a set of arbitrary point
charges to the potential.
"""

import numpy as np
from scipy import constants
from scipy.special import erfc
from scipy.spatial.distance import cdist, pdist, squareform
from scipy.optimize import lsq_linear
from time import perf_counter

from .structure import Parser, generate_qm_idc
from .output import OutputWriter
from .cells import UnitSupercell, UnitCluster


###################
# Miguel was here #
###################

ALPHA = 0.2
EVCONV = 1e10 * constants.e / (4 * np.pi * constants.epsilon_0)


def create_images(coords: np.ndarray,
                  n: np.ndarray,  # Summation limits
                  lattice_vectors: np.ndarray
                  ) -> np.ndarray:
    """
    Creates the periodic images of the unit cell of dimensions
    of the summation limits.

    Parameters
    ----------
    coords : np.ndarray
        The coordinates of the unit cell.
    n : np.ndarray
        The summation limits.
    lattice_vectors : np.ndarray
        The lattice vectors of the unit cell.

    Returns
    -------
    images : np.ndarray
        The periodic images of the unit cell.
    """

    n1 = list(range(-n[0], n[0]+1))
    n2 = list(range(-n[1], n[1]+1))
    n3 = list(range(-n[2], n[2]+1))
    _n = np.array([[n1[i], n2[j], n3[k]]
                   for i in range(len(n1))
                   for j in range(len(n2))
                   for k in range(len(n3))])

    images = np.array([coord + _n[i]
                       for i in range(len(_n))
                       for coord in coords])

    return images @ lattice_vectors, _n


def calculate_fm(n, bv):
    """
    Calculates the reciprocal lattice vector images

    Parameters
    ----------
    n : np.ndarray
        The summation image indecies.
    bv : np.ndarray
        The reciprocal lattice vectors of the unit cell.

    Returns
    -------
    fm : np.ndarray
        The reciproal lattice vector images.
    """
    m = [x for x in n if not (x == 0).any()]
    return np.array(list(map(lambda x: bv @ x, m)), dtype=float)


def reciprocal_exponential(fm):
    """
    Calculates the reciprocal exponential term of the Ewald sum.

    Parameters
    ----------
    fm : np.ndarray
        The reciprocal lattice vector image.

    Returns
    -------
    reciprocal_exponential : float
    """
    return np.exp(-(np.pi**2 * fm @ fm / ALPHA**2)) / (fm @ fm)


def reciprocal_cosine(fm, r1, r2):
    """
    Calculates the reciprocal cosine term of the Ewald sum.

    Parameters
    ----------
    fm : np.ndarray
        The reciprocal lattice vector image.
    r1 : np.ndarray
        The coordinate of atom i.
    r2 : np.ndarray
        The coordinate of atom j.

    Returns
    -------
    reciprocal_cosine : float
    """
    if (r1 == r2).all():
        return 0
    else:
        return np.cos(2 * np.pi * fm @ (r1 - r2))


def ewald_reciprocal(coords: np.ndarray,
                     lattice_vectors: np.ndarray,
                     reciprocal_vectors: np.ndarray,
                     q: np.ndarray,
                     n: np.ndarray,  # Summation image indecies
                     volume: float,
                     ) -> np.ndarray:
    """
    Calculates the reciprocal space contribution to the potential

    Parameters
    ----------
    coords : np.ndarray
        The coordinates of the unit cell.
    lattice_vectors : np.ndarray
        The lattice vectors of the unit cell.
    reciprocal_vectors : np.ndarray
        The reciprocal lattice vectors of the unit cell.
    q : np.ndarray
        The charges of the atoms in the unit cell.
    n : np.ndarray
        The summation image indecies.
    volume : float
        The volume of the unit cell.

    Returns
    -------
    V_recip : np.ndarray
    """
    coords = coords @ lattice_vectors
    prefactor = EVCONV / (np.pi * volume)
    fm = calculate_fm(n, reciprocal_vectors)
    expo = np.array(sum(list(map(reciprocal_exponential, fm))))
    cosine = np.array(list(map(lambda r: sum(list(map(lambda x, y: reciprocal_cosine(x, r, y), fm, coords))), coords)), dtype=float)
    return prefactor * q * expo * cosine


def error_function(q, r1, r2):
    """
    Calculates the complementary error function term of the Ewald sum.

    Parameters
    ----------
    q : float
        The charge of atom j.
    r1 : np.ndarray
        The coordinate of atom i.
    r2 : np.ndarray
        The coordinate of atom j.

    Returns
    -------
    error_function : float
    """
    if (r1 == r2).all():
        return 0
    else:
        return q * erfc(ALPHA * np.linalg.norm(r1 - r2))/np.linalg.norm(r1 - r2)


def ewald_real_space(coords: np.ndarray,
                     q: np.ndarray,
                     lattice_vectors: np.ndarray,
                     images: np.ndarray,
                     n: np.ndarray,
                     ):
    """
    Calculates the real space contribution to the potential

    Parameters
    ----------
    coords : np.ndarray
        The coordinates of the unit cell.
    q : np.ndarray
        The charges of the atoms in the unit cell.
    lattice_vectors : np.ndarray
        The lattice vectors of the unit cell.
    images : np.ndarray
        The periodic images of the unit cell.
    n : np.ndarray
        The summation image indecies.
    """
    coords = coords @ lattice_vectors
    q = np.tile(q, len(n))
    error_component = np.array(list(map(lambda r: sum(list(map(lambda x: error_function(q[x], r, images[x]), range(len(q))))), coords)), dtype=float)
    return EVCONV * error_component


def ewald_self(q: np.ndarray,
               ) -> np.ndarray:
    """
    Computes the self interaction contribution to the Ewald sum.

    Parameters
    ----------
    q : np.ndarray

    Returns
    -------
    self : np.ndarray
    """

    prefactor = -2 * ALPHA / np.sqrt(np.pi)
    e_self = np.array(
            list(map(lambda x: prefactor * x, q))
            ).flatten()
    return e_self * EVCONV


def build_zones(cluster: UnitSupercell,
                ewald_potential: np.ndarray,
                r_cut: float,
                q: np.ndarray,
                ):
    """
    Builds the exact point charge region and the parameter
    region.

    Parameters
    ----------
    cluster : UnitSupercell
        The unit supercell.
    ewald_potential : np.ndarray
        The Ewald potential.
    r_cut : float
        The cutoff radius.
    q : np.ndarray
        The charges of the unit cell.

    Returns
    -------
    exact : np.ndarray
        The exact point charge region.
    param : np.ndarray
        The parameter region.
    """

    ewald_potential = np.tile(ewald_potential, cluster.n_cell)
    q = np.tile(q, cluster.n_cell)

    supercell = np.concatenate((cluster.cart_coords,
                                ewald_potential[:, None],
                                q[:, None]),
                               axis=1)

    sphere = np.array([coord for coord in supercell
                       if np.linalg.norm(coord[:3]) < r_cut])

    param = np.array([coord for coord in supercell
                      if np.linalg.norm(coord[:3]) > r_cut])

    return sphere, param


def drive_dipole(sphere: np.ndarray,
                 param: np.ndarray,
                 ):
    """
    Drives the total dipole moment to zero.

    Parameters
    ----------
    sphere : np.ndarray
        The exact point charge region.
    param : np.ndarray
        The parameter region.

    Returns
    -------
    sphere : np.ndarray
        The exact point charge region.
    param : np.ndarray
        The parameter region.
    """

    target = np.zeros(3)

    def calc_dipole(sphere: np.ndarray,
                    param: np.ndarray,
                    ) -> np.ndarray:
        sphere = np.array(sphere[:, :5], dtype=float)
        param = np.array(param[:, :5], dtype=float)
        d_sphere = sphere[:, 4] @ sphere[:, :3]
        d_param = param[:, 4] @ param[:, :3]
        return d_sphere + d_param

    def calc_rmsd(dipole: np.ndarray,
                  target: np.ndarray,
                  ) -> float:
        return np.sqrt(np.sum((dipole - target)**2) / len(dipole))

    initial_dipole = calc_dipole(sphere, param)

    rmsd = calc_rmsd(initial_dipole, target)
    print("Initial dipole moment: {:.3f}  {:.3f}  {:.3f}".format(
        *initial_dipole))
    print(f'Initial RMSD: {rmsd:.3f}')

    r = param[:, :3]

    d = - np.array(initial_dipole, dtype=float)
    x = np.linalg.lstsq(r.T, d, rcond=None)[0]
    param[:, 4] += x

    final_dipole = calc_dipole(sphere, param)
    rmsd = calc_rmsd(final_dipole, target)
    print("Final dipole moment: {:.3f}  {:.3f}  {:.3f}".format(
        *final_dipole))
    print(f'Final RMSD: {rmsd:.3f}')

    return param


def fit_parameters(sphere: np.ndarray,
                   param: np.ndarray,
                   verbose: int,
                   ):
    """
    Fits the parameter region such that the potential in the
    exact point charge region and the quantum mechanical (QM)
    region is the calculated Ewald potential.

    Parameters
    ----------
    sphere : np.ndarray
        The exact point charge region.
    param : np.ndarray
        The parameter region.
    verbose : int
        The verbosity level.

    Returns
    -------
    param : np.ndarray
        The parameter region.
    """

    # sum_j (q + dq) / rij - V_ewald = 0
    # sum_j (dq) / rij = V_ewald - sum_j (q) / rij
    # cx = d, d = - sum_j (q) / rij
    # QR decomposition
    # AQ = [A1(N_c), A2(N - N_c)]
    # b2 = b1 - A1(R^{-T}d)
    # Q^T x = [x1, x2]
    # A2 x2 = b2
    # x = Q @ [x1, x2]

    sphere_coords = np.array(sphere[:, :3], dtype=float)
    param_coords = np.array(param[:, :3], dtype=float)
    sphere_q = np.array(sphere[:, 4], dtype=float)
    param_q = np.array(param[:, 4], dtype=float)

    bi = np.array(sphere[:, 3], dtype=float)

    A = 1 / cdist(sphere_coords, param_coords, metric='euclidean')
    rijs = squareform(1 / pdist(sphere_coords, metric='euclidean'))
    p_sphere = rijs @ (EVCONV * sphere_q)
    p_param = A @ (EVCONV * param_q)

    bi = bi - p_sphere - p_param

    c = np.ones((1, len(param_coords)))
    d = - np.sum(sphere_q) + np.sum(param_q)

    Q, R = np.linalg.qr(c.T, mode='complete')

    AQ = A @ Q

    b2 = bi - AQ[:, 0] * (1/R[0]).T * d

    x2 = lsq_linear(AQ[:, 1:],
                    b2,
                    bounds=(-15, 15),
                    method='bvls',
                    tol=1e-6,
                    max_iter=10000,
                    verbose=verbose).x

    x1 = (1/R[0]).T * d
    x = np.concatenate((x1, x2))
    x = Q @ x

    x = x / EVCONV

    x = param_q + x

    # rmsd
    q = np.concatenate((sphere_q, x))
    coords = np.concatenate((sphere_coords, param_coords))
    rij = squareform(1 / pdist(coords, metric='euclidean'))
    rij[np.where(rij == np.inf)] = 0

    potential = EVCONV * q @ rij
    ewald = np.array(sphere[:, 3], dtype=float)
    rmsd = np.sqrt(np.sum((potential[:len(sphere)] - ewald)**2) / len(ewald))
    print(f'RMSD: {rmsd}')

    param[:, 4] = x

    return param, rmsd


def write_output(sphere: np.ndarray,
                 param: np.ndarray,
                 ):
    """
    Writes the 'ewald.out' file containing the coordinates
    and charges for using in OpenMolcas as an xfield input.

    Parameters
    ----------
    sphere : np.ndarray
        The exact point charge region.
    param : np.ndarray
        The parameter region.
    """
    with open('ewald.out', 'w') as f:
        for i in range(len(sphere)):
            f.write('{:.8f}\t{:.8f}\t{:.8f}\t{:.10f}\n'.format(
                sphere[i, 0],
                sphere[i, 1],
                sphere[i, 2],
                sphere[i, 4],
            ))
        for i in range(len(param)):
            f.write('{:.8f}\t{:.8f}\t{:.8f}\t{:.10f}\n'.format(
                param[i][0],
                param[i][1],
                param[i][2],
                param[i][4],
            ))


def check_errors(cluster, q):
    """
    Puts a limit on the number of atoms in the supercell.
    """
    coords = cluster.cart_coords
    unit_coords = cluster.unit_coords

    if len(coords) > 10000:
        print('WARNING: The number of atoms in the Ewald sum is very large. ')
        print('         This may take a long time to run.')
    elif len(coords) > 15000:
        raise ValueError('The number of atoms in the Ewald sum is too large. ')

    if len(q) != len(unit_coords):
        raise ValueError('The number of charges does not match the number of atoms.')

    if not np.allclose(np.sum(q), 0):
        raise ValueError('The total charge of the system is not zero.')


def ewald_potential(cluster: UnitCluster,
                    qm_region: np.ndarray,
                    charges: np.ndarray,
                    r_cut: int,
                    verbose: int,
                    n: list):
    """
    Calculates and fits the ewald potential

    Parameters
    ----------
    cluster : UnitCluster
        The cluster object.
    qm_region : np.ndarray
        The quantum mechanical region.
    charges : np.ndarray
        The charges of the unit cell.
    r_cut : int
        The cutoff radius.
    verbose : int
        The verbosity level.
    n : list
        The summation limits.

    Returns
    -------
    calculation dictionary: dict
        The calculation dictionary.
    """

    # Create a full calculation dict
    calc_dict = {}

    # replace with cluster ?
    av = cluster.lat_vecs
    coords = cluster.unit_coords
    bv = cluster.recip_vecs
    v = cluster.unit_volume

    # Parse charges
    q = np.loadtxt(charges)

    calc_dict.update({'Unit cell coordinates': coords,
                      'Lattice vectors': av,
                      'Reciprocal lattice vectors': bv,
                      'Unit cell volume': v,
                      'Unit cell charges': q,
                      })

    # Error check
    check_errors(cluster, q)

    images, n = create_images(coords, n, av)

    # compute the ewald sums new method
    recip = ewald_reciprocal(coords, av, bv, q, n, v)
    real = ewald_real_space(coords, q, av, images, n)
    self_int = ewald_self(q)
    potential = recip + real + self_int

    calc_dict.update({"Ewald real": real,
                      "Ewald recip": recip,
                      "Ewald self": self_int,
                      "Ewald potential": potential})

    # generate the sphere and parameter zones
    sphere, param = build_zones(cluster, potential, r_cut, q)

    # Drive the total dipole moment to zero
    param = drive_dipole(sphere, param)

    # Perform the fitting procedure and write the outputs
    param, rmsd = fit_parameters(sphere, param, verbose)

    calc_dict.update({"Fitting RMSD": rmsd})

    print('len sphere {} len param {} len qm {}'.format(len(sphere), len(param), len(qm_region)))

    # Remove qm region from sphere
    qm_idc = list(generate_qm_idc(qm_region, sphere[:, :3]))

    sphere = np.delete(sphere, qm_idc, axis=0)

    print('len sphere {} len param {} len qm {}'.format(len(sphere), len(param), len(qm_region)))


    calc_dict.update({'qm region': qm_region,
                      'Sphere': sphere,
                      'Param': param,
                      })

    return calc_dict

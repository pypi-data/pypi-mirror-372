import os
import numpy as np
import pickle

from dynasor.qpoints import get_spherical_qpoints
from dynasor.correlation_functions import compute_dynamic_structure_factors
from dynasor.post_processing import get_spherically_averaged_sample_binned
from dynasor.trajectory import Trajectory


def test_regression_test_with_old_cmdline():
    # traj index files
    this_dir = os.path.dirname(__file__)
    traj_fname = os.path.join(
        this_dir, 'trajectory_reader/trajectory_files/dump_long_with_velocities.xyz')
    index_fname = os.path.join(this_dir, 'trajectory_reader/trajectory_files/index_file_dump_long')

    # number of atoms, needed for normalization since normalization is now different
    n_atoms = 320
    atoms_counts = dict(Cs=64, Pb=64, Br=192)

    # input parameters
    time_window = 6
    dt = 100
    q_max = 4  # Previously in 2*pi*nm^{-1}, now in 2*pi*Å^{-1}
    q_bins = 20

    # run dynasor
    traj = Trajectory(traj_fname, trajectory_format='extxyz', atomic_indices=index_fname)
    q_points = get_spherical_qpoints(traj.cell, q_max)
    mask = np.logical_and(q_points[:, 0] >= 0, q_points[:, 1] >= 0)  # keep only first octant
    mask = np.logical_and(mask, q_points[:, 2] >= 0)  # keep only first octant
    q_points = q_points[mask]
    sample = compute_dynamic_structure_factors(traj, q_points, dt=dt, window_size=time_window,
                                               calculate_currents=True, calculate_incoherent=True)
    sample2 = get_spherically_averaged_sample_binned(sample, num_q_bins=q_bins)

    # load old commandline results for the same traj
    fname = os.path.join(this_dir, 'dynasor_old_cmdline.pickle')
    old_cmdline_results = pickle.load(open(fname, 'rb'))

    data_dict_old = dict()
    types = 'Cs Pb Br'.split()
    for (v, k, info) in old_cmdline_results:
        for i, t in enumerate(types):
            k = k.replace(str(i), t)
        k = k.replace('_k_', '_q_')
        data_dict_old[k] = v

    # compare simple things, time, omega, q
    assert np.allclose(sample2.time, data_dict_old['t'])
    # assert np.allclose(sample2.omega, data_dict_old['w'])
    # qbins differ slightly since q_max is no longer exactly 40.0 but based on the actually q-points
    # assert np.allclose(sample2['q_norms'], data_dict_old['k'])

    # compare all incoherent
    for key in sample2.available_correlation_functions:
        if '_s_' not in key:
            continue
        if '_w_' in key:  # dont check frequency domain, new dynasor uses slightly different freqs
            continue
        atom_type = key.split('_')[-1]
        array_new = getattr(sample2, key) * n_atoms / atoms_counts[atom_type]
        array_old = data_dict_old[key]
        assert np.allclose(array_new.T, array_old)

    # For coherent parts we only compare for A-A pairs since AB calculations are slightly different
    corr_list_new = ['Fqt_coh', 'Clqt', 'Ctqt']
    corr_list_old = ['F_q_t', 'Cl_q_t', 'Ct_q_t']
    pairs = ['Cs_Cs', 'Pb_Pb', 'Br_Br']
    for corr_name_new, corr_name_old in zip(corr_list_new, corr_list_old):
        for pair in pairs:
            key_new = corr_name_new + '_' + pair
            key_old = corr_name_old + '_' + pair
            s1, s2 = pair.split('_')
            multiplicity = 1.0 if s1 == s2 else 2.0
            norm = n_atoms / (multiplicity * np.sqrt(atoms_counts[s1] * atoms_counts[s2]))

            array_new = getattr(sample2, key_new) * norm
            array_old = data_dict_old[key_old].T
            if corr_name_new[0] == 'C':
                # v (and thus j) previously had the unit nm/fs. This has been changed to Å/fs,
                # which means that the old current correlations must be multiplied by 100 to be
                # comparable to the new current correlations.
                array_old *= 100
                assert np.allclose(array_new, array_old)
            else:
                assert np.allclose(array_new, array_old)

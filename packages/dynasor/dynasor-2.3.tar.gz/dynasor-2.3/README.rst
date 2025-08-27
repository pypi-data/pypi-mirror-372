dynasor
=======

**dynasor** is a tool for calculating total and partial dynamic structure factors as well as related correlation functions from molecular dynamics (MD) simulations.
By analyzing these functions one can access the dynamics of a system without resorting to perturbative approaches.
Moreover by combining in particular the structure factor with the cross sections (or form factors) of, e.g., neutrons, X-rays or electrons, one can predict experimental spectra.
The main input consists of a trajectory from a MD simulation, i.e., a file containing snapshots of the particle coordinates and optionally velocities, that correspond to consecutively and equally spaced points in (simulation) time.

**dynasor** provides both python and a command line interface.
The following snippet illustrates how one can calculate dynamic structure factors using the former.

.. code-block:: python

   traj = Trajectory('dump.xyz', trajectory_format='extxyz')
   q_points = generate_spherical_qpoints(traj.cell, q_max=20)
   sample = compute_dynamic_structure_factors(traj, q_points=q_points, dt=5, window_size=100)
   sample.write_to_npy('test.npy')

**dynasor** can be installed via `pip <https://pypi.org/project/dynasor/>`_ or `conda <https://anaconda.org/conda-forge/dynasor>`_.
Please consult the `installation section of the user guide <https://dynasor.materialsmodeling.org/installation.html>`_ for details.

The full documentation can be found in the `user guide <http://dynasor.materialsmodeling.org/>`_.
For questions and help please use the `dynasor discussion forum on matsci.org <https://matsci.org/dynasor>`_.
**dynasor** and its development are hosted on `gitlab <https://gitlab.com/materials-modeling/dynasor>`_.

When using **dynasor**  in your research please cite the following papers:

| *Dynasor – A tool for extracting dynamical structure factors and current correlation functions from molecular dynamics simulations*
| Erik Fransson, Mattias Slabanja, Paul Erhart, and Göran Wahnström
| Advanced Theory and Simulations **4**, 2000240 (2021); DOI:`10.1002/adts.202000240 <https://doi.org/10.1002/adts.202000240>`_

| *Dynasor 2: From simulation to experiment through correlation functions*
| Esmée Berger, Erik Fransson, Fredrik Eriksson, Eric Lindgren, Göran Wahnström, Thomas Holm Rod, and Paul Erhart
| Computer Physics Communications **316**, 109759 (2025); DOI: `10.1016/j.cpc.2025.109759 <https://doi.org/10.1016/j.cpc.2025.109759>`_
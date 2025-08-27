from copy import deepcopy
from typing import Optional
from warnings import warn
import numpy as np
from dynasor.post_processing.weights import Weights
from dynasor.sample import Sample, StaticSample, DynamicSample
from numpy.typing import NDArray


def get_weighted_sample(sample: Sample,
                        weights: Weights,
                        atom_type_map: Optional[dict[str, str]] = None) -> Sample:
    r"""
    Weights correlation functions with atomic weighting factors

    The weighting of a partial dynamic structure factor
    :math:`S_\mathrm{AB}(\boldsymbol{q}, \omega)`
    for atom types :math:`A` and :math:`B` is carried out as

    .. math::

        S_\mathrm{AB}(\boldsymbol{q}, \omega)
        = f_\mathrm{A}(\boldsymbol{q}) f_\mathrm{B}(\boldsymbol{q})
        S_\mathrm{AB}(\boldsymbol{q}, \omega)

    :math:`f_\mathrm{A}(\boldsymbol{q})` and :math:`f_\mathrm{B}(\boldsymbol{q})`
    are atom-type and :math:`\boldsymbol{q}`-point dependent weights.

    If sample has incoherent correlation functions, but :attr:`weights` does not contain
    information on how to weight the incoherent part, then it will be dropped from the
    returned :attr:`Sample` object (and analogously for current correlation functions).

    Parameters
    ----------
    sample
        Input sample to be weighted.
    weights
        Object containing the weights :math:`f_\mathrm{X}(\boldsymbol{q})`.
    atom_type_map
        Map between the atom types in the :class:`Sample` and the ones used in
        the :class:`Weights` object, e.g., Ba &rarr; Ba(2+).

    Returns
    -------
        A :class:`Sample` instance with the weighted partial and total structure factors.
    """

    # check input arguments
    if sample.has_incoherent and not weights.supports_incoherent:
        warn('The Weights class does not support incoherent scattering, dropping the latter '
             'from the weighted sample.')

    if sample.has_currents and not weights.supports_currents:
        warn('The Weights class does not support current correlations, dropping the latter '
             'from the weighted sample.')

    # setup new input dicts for new Sample
    data_dict = dict()
    for key in sample.dimensions:
        data_dict[key] = sample[key]

    # Map the atom types in the sample to the types in the weights object.
    # Useful, for instance, when using weights for charged atomic species.
    atom_types = [(at, at) for at in sample.atom_types]
    if atom_type_map is not None:
        # Fallback to use the atom type from species (`at`) if it's not mapped.
        atom_types = [(at, atom_type_map.get(at, at)) for at in atom_type_map]

    # generate atomic weights for each q-point and compile to arrays
    if 'q_norms' in sample.dimensions:
        q_norms = sample.q_norms
    else:
        q_norms = np.linalg.norm(sample.q_points, axis=1)

    weights_coh = dict()
    for at, weight_at in atom_types:
        weight_array = np.reshape([weights.get_weight_coh(weight_at, q) for q in q_norms], (-1, 1))
        weights_coh[at] = weight_array
    if sample.has_incoherent and weights.supports_incoherent:
        weights_incoh = dict()
        for at, weight_at in atom_types:
            weight_array = np.reshape([
                weights.get_weight_incoh(weight_at, q) for q in q_norms
                ], (-1, 1))
            weights_incoh[at] = weight_array

    # weighting of correlation functions
    if isinstance(sample, StaticSample):
        data_dict_Sq = _compute_weighting_coherent(sample, 'Sq', weights_coh)
        data_dict.update(data_dict_Sq)
    elif isinstance(sample, DynamicSample):
        # coherent
        Fqt_coh_dict = _compute_weighting_coherent(sample, 'Fqt_coh', weights_coh)
        data_dict.update(Fqt_coh_dict)
        Sqw_coh_dict = _compute_weighting_coherent(sample, 'Sqw_coh', weights_coh)
        data_dict.update(Sqw_coh_dict)

        # incoherent
        if sample.has_incoherent and weights.supports_incoherent:
            Fqt_incoh_dict = _compute_weighting_incoherent(sample, 'Fqt_incoh', weights_incoh)
            data_dict.update(Fqt_incoh_dict)
            Sqw_incoh_dict = _compute_weighting_incoherent(sample, 'Sqw_incoh', weights_incoh)
            data_dict.update(Sqw_incoh_dict)

        # currents
        if sample.has_currents and weights.supports_currents:
            Clqt_dict = _compute_weighting_coherent(sample, 'Clqt', weights_coh)
            data_dict.update(Clqt_dict)
            Clqw_dict = _compute_weighting_coherent(sample, 'Clqw', weights_coh)
            data_dict.update(Clqw_dict)

            Ctqt_dict = _compute_weighting_coherent(sample, 'Ctqt', weights_coh)
            data_dict.update(Ctqt_dict)
            Ctqw_dict = _compute_weighting_coherent(sample, 'Ctqw', weights_coh)
            data_dict.update(Ctqw_dict)

    new_sample = sample.__class__(
        data_dict,
        simulation_data=deepcopy(sample.simulation_data),
        history=deepcopy(sample.history))
    new_sample._append_history(
        'get_weighted_sample',
        dict(
            atom_type_map=atom_type_map,
            weights_class=weights.__class__.__name__,
            weights_parameters=weights.parameters.to_dict(),
        ))

    return new_sample


def _compute_weighting_coherent(
    sample: Sample,
    name: str,
    weight_dict: dict,
) -> dict[str, NDArray[float]]:
    """
    Helper function for weighting and summing partial coherent correlation functions.
    """
    data_dict = dict()
    total = np.zeros(sample[name].shape)
    for s1, s2 in sample.pairs:
        key_pair = f'{name}_{s1}_{s2}'
        partial = np.real(np.conjugate(weight_dict[s1]) * weight_dict[s2]) * sample[key_pair]
        data_dict[key_pair] = partial
        total += partial
    data_dict[name] = total
    return data_dict


def _compute_weighting_incoherent(
    sample: Sample,
    name: str,
    weight_dict: dict,
) -> dict[str, NDArray[float]]:
    """
    Helper function for weighting and summing partial incoherent correlation functions.
    """
    data_dict = dict()
    total = np.zeros(sample[name].shape)
    for s1 in sample.atom_types:
        key = f'{name}_{s1}'
        partial = np.real(np.conjugate(weight_dict[s1]) * weight_dict[s1]) * sample[key]
        data_dict[key] = partial
        total += partial
    data_dict[name] = total
    return data_dict

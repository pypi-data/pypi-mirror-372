from copy import deepcopy
from typing import Optional
import numpy as np
from dynasor.sample import Sample


def get_sample_averaged_over_independent_runs(
        samples: list[Sample],
        live_dangerously: Optional[bool] = False,
) -> Sample:
    """
    Compute an averaged sample from multiple samples obtained from identical independent runs.

    Note all the metadata and dimensions in all samples must be the same.
    Otherwise a `ValueError` is raised (unless `live_dangerously` is set to `True`).

    Parameters
    ----------
    samples
        List of all sample objects to be averaged over.
    live_dangerously
        Setting to `True` allows for averaging over samples
        which metadata information is not identical.
    """

    # get metadata and dimensions from first sample
    sample_ref = samples[0]
    data_dict = dict()
    simulation_data = deepcopy(sample_ref.simulation_data)

    # test that all samples have identical dimensions
    for m, sample in enumerate(samples):
        if sorted(sample.dimensions) != sorted(sample_ref.dimensions):
            raise ValueError(f'Sample dimensions do not match for sample #{m}.')
        for dim in sample_ref.dimensions:
            if dim not in sample.dimensions:
                raise ValueError(f'Sample dimensions do not match for sample #{m}.')
            if not np.allclose(sample[dim], sample_ref[dim]):
                raise ValueError(f'Sample dimensions do not match for sample #{m}.')

    for dim in sample_ref.dimensions:
        data_dict[dim] = sample_ref[dim]

    # test that all samples have identical metadata
    if not live_dangerously:
        for m, sample in enumerate(samples):
            for key, val in simulation_data.items():
                if key not in sample.simulation_data:
                    raise ValueError(
                        f'Sample #{m} is missing "{key}" in the simulation_data field.')
                match = True
                if isinstance(val, dict):
                    for k, v in val.items():
                        match &= sample.simulation_data[key].get(k, None) == val[k]
                elif isinstance(val, np.ndarray):
                    match &= np.allclose(sample.simulation_data[key], val)
                elif isinstance(val, float):
                    match &= np.isclose(sample.simulation_data[key], val)
                else:
                    match &= sample.simulation_data[key] == val
                if not match:
                    raise ValueError(f'Field "{key}" of sample #{m} does not match.')

    # average all correlation functions
    for key in sample.available_correlation_functions:
        data = []
        for sample in samples:
            data.append(sample[key])
        data_average = np.nanmean(data, axis=0)
        data_dict[key] = data_average

    # keep history of original samples
    previous_history = []
    for m, s in enumerate(samples):
        for h in s.history:
            rec = h.copy()
            rec['func'] += f'_sample{m}'
            previous_history.append(rec)

    # compose new sample object
    new_sample = sample.__class__(
        data_dict,
        simulation_data=simulation_data,
        history=previous_history)
    new_sample._append_history(
        'get_sample_averaged_over_independent_runs',
        dict(
            live_dangerously=live_dangerously,
            n_samples=len(samples),
        ))

    return new_sample

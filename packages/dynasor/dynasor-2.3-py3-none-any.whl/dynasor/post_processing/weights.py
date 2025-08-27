from typing import Any, Optional
from pandas import DataFrame


class Weights:
    """
    Class holding weights and support functions for weighting of samples.

    Parameters
    ----------
    weights_coh
        A dict with keys and values representing the atom types and their corresponding
        coherent scattering length, ``{'A': b_A }``.
    weights_incoh
        A dict with keys and values representing the atom types and their corresponding
        incoherent scattering length, ``{'A': b_A }``.
    supports_currents
        Whether or not the coherent weights should be applied to current-correlation functions.
    """

    def __init__(
        self,
        weights_coh: dict[str, Any],
        weights_incoh: Optional[dict[str, Any]] = None,
        supports_currents: Optional[bool] = True,
    ):
        self._weights_coh = weights_coh
        self._weights_incoh = weights_incoh
        self._supports_currents = supports_currents

    def get_weight_coh(self, atom_type: str, q_norm: float = None) -> float:
        """Get the coherent weight for a given atom type and q-vector norm."""
        if atom_type not in self._weights_coh.keys():
            raise ValueError(f'Coherent weights for {atom_type} have not been specified')
        return self._weights_coh[atom_type]

    def get_weight_incoh(self, atom_type: str, q_norm: float = None) -> float:
        """Get the incoherent weight for a given atom type and q-vector norm."""
        if self._weights_incoh is None:
            return None
        if atom_type not in self._weights_incoh.keys():
            raise ValueError(f'Incoherent weights for {atom_type} have not been specified')
        return self._weights_incoh[atom_type]

    @property
    def parameters(self) -> DataFrame:
        """Parameters used for weighting.
        """
        atom_types = set(self._weights_coh.keys())
        if self._weights_incoh:
            atom_types |= set(self._weights_incoh.keys())
        data = []
        for s in atom_types:
            record = dict(
                atom_type=s,
                coherent=self._weights_coh.get(s, None),
            )
            data.append(record)
            if self._weights_incoh:
                record.update(dict(incoherent=self._weights_incoh.get(s, None)))
        return DataFrame(data).sort_values('atom_type', ignore_index=True)

    @property
    def supports_currents(self) -> bool:
        """
        Wether or not this :class:`Weights` object supports weighting of current correlations.
        """
        return self._supports_currents

    @property
    def supports_incoherent(self) -> bool:
        """
        Whether or not this :class:`Weights` object supports weighting of incoherent
        correlation functions.
        """
        return self._weights_incoh is not None

    def __str__(self):
        s = ['weights coherent:']
        for key, val in self._weights_coh.items():
            s.append(f'  {key}: {val}')

        # Return early if incoherent weights
        # are None
        if self._weights_incoh is None:
            return '\n'.join(s)

        s.append('weights incoherent:')
        for key, val in self._weights_incoh.items():
            s.append(f'  {key}: {val}')
        return '\n'.join(s)

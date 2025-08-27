import json
from re import search
from importlib.resources import files
from typing import Optional
from warnings import warn

from numpy import exp, abs, pi
from pandas import DataFrame, concat
from .weights import Weights


class ElectronScatteringFactors(Weights):
    r"""This class generates sample weights corresponding to electron scattering factors.
    The scattering factors are parametrized as sums of exponentials
    of the following form

    .. math::

        f(q) = \sum_{i=1}^k a_i \exp(-b_i s^2),

    with :math:`s=\sin(\theta)/\lambda`, where and :math:`a_i` and :math:`b_i`
    are fitting parameters. Note that there are two parametrizations for the elemental
    scattering factors; one valid up to :math:`s = 2.0\,\mathrm{Å}^{-1}`
    and the other valid up to :math:`s = 6.0\,\mathrm{Å}^{-1}`.
    By default, the parametrization valid up to :math:`s = 6.0\,\mathrm{Å}^{-1}`
    is used. Ionic scattering factors only have a single parametrization.

    The parametrizations are based on the following publications:

    * Elemental scattering factors are based on Table 1 and Table 3
      from L.-M. Peng, G. Ren, S. L. Dudarev and M. J. Whelan,
      Acta Crystallographica Section A **52**, 257-276 (1996);
      `doi: 10.1107/S0108767395014371 <https://doi.org/10.1107/S0108767395014371>`_.
    * Ionic scattering factors are based on Table 1 from
      Lian-Mao. Peng, Acta Crystallographica Section A **54**, 481-485 (1998);
      `doi: 10.1107/S0108767398001901 <https://doi.org/10.1107/S0108767398001901>`_.

    Parameters
    ----------
    atom_types
        List of atomic species for which to retrieve scattering lengths.
    parametrization
        Parametrization to use.
    """

    def __init__(
            self,
            atom_types: list[str],
            parametrization: Optional[str] = 'smax6',
    ):
        self._parametrization = parametrization
        scattering_factors = self._read_scattering_factors(self._parametrization)
        # Select the relevant species
        scattering_factors = scattering_factors[
                scattering_factors.index.isin(atom_types)]  # Atom species is index
        self._scattering_factors = scattering_factors

        # Check if any of the fetched form factors are missing,
        # indicating that it is missing in the experimental database.
        for s in atom_types:
            row = scattering_factors[scattering_factors.index == s]
            if row.empty:
                raise ValueError('Missing tabulated values '
                                 f'for requested species {s}.')

        weights_coh = scattering_factors.to_dict(orient='index')
        supports_currents = False
        super().__init__(weights_coh, None, supports_currents=supports_currents)

    def get_weight_coh(self, atom_type, q_norm):
        """Get the coherent weight for a given atom type and q-vector norm."""
        return self._compute_f(self._weights_coh[atom_type],
                               q_norm,
                               self._parametrization,
                               self._get_charge(atom_type))

    @property
    def parameters(self) -> DataFrame:
        """Parametrization used to compute the coherent scattering factors
        :math:`f(q)` for the selected species.
        """
        return self._scattering_factors

    def _get_charge(self, atom_type: str) -> float:
        """
        Extracts the ionic charge from the atom type.
        """
        match = search(r'(\d+)?([+-])', atom_type)
        if match:
            magnitude = int(match.group(1)) if match.group(1) else 1
            charge = magnitude * (1 if match.group(2) == '+' else -1)
            return charge
        return None  # If no charge is found

    def _compute_f(
            self,
            coefficients: dict,
            q_norm: float,
            parametrization: str,
            charge: Optional[int] = None):
        r"""Compute electronic scattering factors :math:`f(q)`.
        The scattering factors are parametrized as a sum
        of exponentials of the form

        .. math::

            f(q) = \sum_{i=1}^k a_i * exp(-b_i * s**2)

        Ions are also offset by

        .. math::

            (m_0 e^2) / (8 \pi^2 \hbar^2) C / s^2 \approx 0.023934 C / s^2

        where :math:`C` is the ionic charge.

        Parameters
        ----------
        coefficients
            Parametrization parameters; read from the corresponding source file.
        q_norm
            The :math:`|q|`-value at which to evaluate the form factor.
        parametrization
            If the Peng parametrization valid up to :math:`s = 6.0\,\mathrm{Å}^{-1}`
            or :math:`s = 2.0\,\mathrm{Å}^{-1}` should be used.
        charge
            Integer representing the ionic charge. `None` if no charge to avoid division by zero.
        """
        s_max = 6.0 if parametrization == 'smax6' else 2.0

        s = q_norm / (4 * pi)  # q in dynasor is q = 4 pi sin(theta) / lambda.
        s_squared = s*s        # s = sin(theta) / lambda in the Waasmaier paper.
        if abs(s) > s_max:
            warn(f'Peng parametrization is not reliable for q'
                 f' above {(s_max * 4 * pi):.2f} rad/Å'
                 f' (corresponding to s={s_max} 1/Å).'
                 ' Parametrisations for ions are accurate up to s=6.0 1/Å')
        nmax = 5

        if charge is not None:
            f = 0.023934 * charge / s_squared
        else:
            f = 0.0
        for i in range(1, nmax+1):
            f += coefficients[f'a{i}'] * exp(-coefficients[f'b{i}'] * s_squared)
        return f

    def _read_scattering_factors(self, parametrization: str) -> DataFrame:
        r"""
        Extracts the parametrization for the form factors :math:`f(q)`,
        for both elemental systems and ionic species.

        Parameters
        ----------
        parametrization
            If the Peng parametrization valid up to :math:`s = 6.0\,\mathrm{Å}^{-1}`
            or :math:`s = 2.0\,\mathrm{Å}^{-1}` should be used.
        """
        if parametrization == 'smax2':
            data_file = files(__package__) / \
                'form-factors/electron-parameters-kmax2-peng-1996.json'
        elif parametrization == 'smax6':
            data_file = files(__package__) / \
                'form-factors/electron-parameters-kmax6-peng-1996.json'
        else:
            raise ValueError(f'Unknown parametrization {parametrization}')

        data_file_ions = files(__package__) / \
            'form-factors/electron-parameters-ions-peng-1998.json'

        frames = []
        for df in [data_file, data_file_ions]:
            with open(df) as fp:
                coefficients = json.load(fp)
                frames.append(DataFrame.from_dict(coefficients))

        scattering_factors = concat(frames)
        scattering_factors.index.names = ['species']
        return scattering_factors

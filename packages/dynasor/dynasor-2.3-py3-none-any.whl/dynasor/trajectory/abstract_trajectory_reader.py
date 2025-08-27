from abc import ABC, abstractmethod
from dynasor.logging_tools import logger


class AbstractTrajectoryReader(ABC):
    """Provides a way to iterate through a molecular dynamics trajectory
    file.

    Each frame/time-step is returned as a trajectory_frame.
    """

    # unit conversion tables
    lengthunits_to_Angstrom_table = {
        'Angstrom': 1.0,
        'nm': 10.0,
        'pm': 1e3,
        'fm': 1e6,
    }

    timeunits_to_fs_table = {
        'fs': 1.0,
        'ps': 1000,
        'ns': 1000000,
    }

    @abstractmethod
    def __iter__(self):
        """ Iterates through the trajectory file, frame by frame. """
        pass

    @abstractmethod
    def __next__(self):
        """ Gets next trajectory frame. """
        pass

    @abstractmethod
    def close(self):
        """ Closes down, release resources etc. """
        pass

    def set_unit_scaling_factors(self, length_unit: str, time_unit: str):
        # setup units
        if length_unit is None:
            logger.info('Assuming the trajectory has the default length unit (Ångström), since no '
                        'unit was specified.')
            self.x_factor = self.lengthunits_to_Angstrom_table['Angstrom']
        elif length_unit not in self.lengthunits_to_Angstrom_table:
            raise ValueError(f'Specified length unit {length_unit} is not an available option.')
        else:
            self.x_factor = self.lengthunits_to_Angstrom_table[length_unit]
        if time_unit is None:
            logger.info('Assuming the trajectory has the default time unit (fs), since no '
                        'unit was specified.')
            self.t_factor = self.timeunits_to_fs_table['fs']
        elif time_unit not in self.timeunits_to_fs_table:
            raise ValueError(f'Specified time unit {time_unit} is not an available option.')
        else:
            self.t_factor = self.timeunits_to_fs_table[time_unit]
        self.v_factor = self.x_factor / self.t_factor

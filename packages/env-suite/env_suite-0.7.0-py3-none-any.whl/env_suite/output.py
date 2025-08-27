"""
A module for handeling output to the user.
"""

import h5py
import numpy as np


class OutputWriter():
    """
    A class for writing output files to the user.
    """

    def __init__(self, filename):
        """
        Initialize the output writer.

        Parameters
        ----------
        filename : str
            The name of the file to write to.
        """

        self.filename = filename

    def write_h5(self, dict):
        """
        takes a dictionary input and writes it to an hdf5 file
        """

        with h5py.File(self.filename, 'w') as f:
            for key, value in dict.items():
                f.create_dataset(key, data=value)
        coloured_output('green', f'Output written to {self.filename}')

    def write_txt(self, dict):
        """
        takes a dictionary input and writes it to a txt file
        """

        with open(self.filename, 'w') as f:
            for key, value in dict.items():
                f.write(f'{key}:\n')
                f.write('-' * len(key) + '\n')
                if isinstance(value, np.ndarray):
                    for row in value:
                        f.write(f'{"  ".join([str(x) for x in row]):.8f}\n')
                elif isinstance(value, list):
                    for row in value:
                        f.write(f'{row}  ')
                elif isinstance(value, dict):
                    for key, value in value.items():
                        f.write(f'{key}')
                        f.write('-' * len(key) + '\n')
                        if isinstance(value, np.ndarray):
                            for row in value:
                                f.write(f'{"  ".join([str(x) for x in row]):.8f}\n')
                        elif isinstance(value, list):
                            for row in value:
                                f.write(f'{row}  ')
                        else:
                            f.write(f'{value}\n')
                else:
                    f.write(f'{value}\n')
                f.write('\n')


def coloured_output(colour, string):
    colours = {'red': '\033[91m',
               'green': '\033[92m',
               'yellow': '\033[93m',
               'blue': '\033[94m',
               'magenta': '\033[95m',
               'cyan': '\033[96m',
               'white': '\033[97m',
               'black': '\033[98m',
               'end': '\033[0m'
    }
    if colour in colours:
        print(colours[colour] + string + colours['end'])
    else:
        raise ValueError(f'Colour {colour} not supported')

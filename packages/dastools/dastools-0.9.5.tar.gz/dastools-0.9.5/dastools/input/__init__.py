from pathlib import Path
from dastools.input.optodas import OptoDASDetector
from dastools.input.tdms import TDMSDetector
from dastools.input.optodas import OptoDASReader
from dastools.input.optodas import OptoDAS2D
from dastools.input.tdms import TDMSReader
from typing import Type
from typing import Union
from typing import Literal


def str2class(name: str) -> Type[Union[TDMSReader, OptoDASReader]]:
    if name.lower() == 'tdms':
        return TDMSReader
    if name.lower() == 'optodas':
        return OptoDASReader
    raise Exception('Unknown class %s!' % name)


def checkDASdata(experiment: str, directory: Path = '.',
                 mode: Literal['1D', '2D'] = '1D') -> Type[Union[TDMSReader, OptoDASReader]]:
    # Check data format from the dataset (if any)
    if TDMSDetector().checkDASdata(experiment, directory):
        return TDMSReader

    if OptoDASDetector().checkDASdata(experiment, directory):
        return OptoDASReader if mode == '1D' else OptoDAS2D

    raise Exception('Input format cannot be guessed from the files found in the directory')

import os

from importlib import resources
from shutil import copyfile

import pandas as pd


PACKAGE_NAME = "jrpyvis"


def load(file):
    """
    Import a dataset.

    The datasets that can be imported using this function are as follows:
    - diamonds
    - exercise
    - flights
    - healthexp
    - iris
    - penguins
    - planets

    Parameters
    ----------
    file: chr
        The name of the dataset (from the list above), or the corresonding
        filename within the jrpyvis package.

    Return
    ------
    pandas.DataFrame
        A pandas dataframe containing the corresponding dataset. See the seaborn
        documentation for details of the original datasets.

    Examples
    --------
    jrpyvis.data.load("diamonds") # Load the seaborn 'diamonds' dataset.
    """
    # Ensure file has .zip extension
    file += '.zip' * (not file.endswith('.zip'))

    # Absolute path to data
    abs_path = resources.files(PACKAGE_NAME) / "data" / file

    return pd.read_csv(abs_path)


def populate_examples():
    # Get absolute path to data folder
    data_path = resources.files(PACKAGE_NAME) / "data"

    # Get list of data files
    pkg_data = os.listdir(data_path)

    # Drop compressed files
    files = [file for file in pkg_data if not file.endswith('.zip')]

    # Copy files to current dir
    for file in files:
        abs_path = data_path / file
        copyfile(abs_path, file)
        print(f'\nCreated file {file} in current directory.\n')

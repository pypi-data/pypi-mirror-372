import os.path as path
from pkg_resources import resource_filename
from shutil import copyfile


def get_example_mplstyle(filename="example_solution.mplstyle"):
    """Copy example from package resources to current working directory."""
    file_path = resource_filename(__name__, path.join("solutions", filename))
    copyfile(file_path, filename)
    print(f"\nCreated file {filename} in current directory!\n")

import os
import ast
import sys
import shutil
import logging
import subprocess
import requirements
from pathlib import Path
from poly_hammer_utils.utilities import shell
from poly_hammer_utils.constants import RESOURCES_FOLDER


IGNORE_PATTERNS = [
    "__pycache__",
    "*.pyc"
]


def get_dict_from_python_file(python_file: Path, dict_name: str) -> dict:
    """
    Gets the first dictionary from the given file that matches the given variable name.

    Args:
        python_file (Path): A file object to read from.
        dict_name (str): The variable name of a dictionary.

    Returns:
        dict: The value of the dictionary.
    """
    dictionary = {}
    with open(python_file, 'r') as file:
        tree = ast.parse(file.read())

        for item in tree.body:
            if hasattr(item, 'targets'):
                for target in item.targets:
                    if getattr(target, 'id', None) == dict_name:
                        for index, key in enumerate(item.value.keys):
                            # add string as dictionary value
                            if hasattr(item.value.values[index], 's'):
                                dictionary[key.s] = item.value.values[index].s

                            # add number as dictionary value
                            elif hasattr(item.value.values[index], 'n'):
                                dictionary[key.s] = item.value.values[index].n

                            # add list as dictionary value
                            elif hasattr(item.value.values[index], 'elts'):
                                list_value = []
                                for element in item.value.values[index].elts:
                                    # add a number to the list
                                    if hasattr(element, 'n'):
                                        list_value.append(element.n)

                                    # add a string to the list
                                    elif hasattr(element, 's'):
                                        list_value.append(element.s)

                                dictionary[key.s] = list_value
                        break
    return dictionary


def get_addon_version_number(addon_folder_path: Path) -> str:
    """
    Gets the version number from the addons bl_info

    :param str addon_folder_path: The path to the addon folder.
    :return str: The version of the addon.

    Args:
        addon_folder_path (Path): The path to the addon folder.

    Returns:
        str: The version of the addon.
    """
    bl_info = get_dict_from_python_file(addon_folder_path / '__init__.py', 'bl_info')
    version_numbers = [str(number) for number in bl_info['version']]
    version_number = '.'.join(version_numbers)
    return version_number
    
def get_addon_zip_path(addon_folder_path: Path, output_folder: Path) -> Path:
    """
    Gets the path to the addons zip file.

    Args:
        addon_folder_path (Path): The path to the addon folder.
        output_folder (Path): The path to the output folder.

    Returns:
        Path: The full path to the released zip file.
    """
    version_number = get_addon_version_number(addon_folder_path)
    output_folder_path = output_folder / f'{addon_folder_path.name}_{version_number}.zip'
    os.makedirs(output_folder_path.parent, exist_ok=True)
    return output_folder_path

def set_folder_contents_permissions(folder_path: Path, permission_level: int):
    """
    Goes through all files and folders contained in the folder and modifies their permissions to
    the given permissions.

    Args:
        folder_path (Path): The full path to the folder you would like to modify permissions on.
        permission_level (int): The octal permissions value.
    """
    for root, directories, files in os.walk(folder_path):
        for directory in directories:
            os.chmod(os.path.join(root, directory), permission_level)
        for file in files:
            os.chmod(os.path.join(root, file), permission_level)


def install_requirements(
        addon_folder_path: Path, 
        requirements_file_path: Path
    ):
    """
    Installs the requirements into the addon's resources packages folder.

    Args:
        addon_folder_path (Path): The path to the addon folder.
        requirements_file_path (Path): The path to the requirements file.
    """
    with open(requirements_file_path, 'r') as requirements_file:
        for requirement in requirements.parse(requirements_file):
            versioned_package = f'{requirement.name}{"".join(requirement.specs[0])}'
            target = addon_folder_path / 'resources' / 'packages'

            shell(f'pip install --upgrade --target="{target}" {versioned_package}')

def zip_addon(
        addon_folder_path: Path, 
        output_folder: Path, 
        requirements: Path | None = None,
        ignore_patterns: tuple[str] = ()
    ) -> Path:
    """
    Zips up the addon.

    Args:
        addon_folder_path (Path): The path to the addon folder.
        
        output_folder (Path): The path to the output folder.

        requirements (Path): The path to the requirements file. If None, 
            no extra packages from the addon will be installed.
        
        ignore_patterns (tuple[str]): The patterns to ignore when zipping the addon.

    Returns:
        Path: The full path to the released zip file.
    """
    ignore_patterns = list(ignore_patterns)

    # installing addons requirements
    if requirements:
        install_requirements(addon_folder_path=addon_folder_path, requirements_file_path=requirements)

    logging.info(f'zipping addon "{addon_folder_path.name}" to "{output_folder}"')
    # get the folder paths
    versioned_zip_file_path = get_addon_zip_path(
        addon_folder_path=addon_folder_path, 
        output_folder=output_folder
    )
    versioned_folder_path = versioned_zip_file_path.parent / versioned_zip_file_path.name.replace('.zip', '')

    # change the permissions to allow the folders contents to be modified.
    if sys.platform == 'win32':
        set_folder_contents_permissions(addon_folder_path.parent, 0o777)

    # remove the existing zip archive
    if versioned_zip_file_path.exists():
        try:
            os.remove(versioned_zip_file_path)
        except PermissionError:
            logging.warning(f'Could not delete {versioned_folder_path}!')

    ignore_patterns.extend(IGNORE_PATTERNS)
    # copy the addon module in to the versioned directory with its addon module name as a sub directory
    shutil.copytree(
        addon_folder_path,
        versioned_folder_path / addon_folder_path.name,
        ignore=shutil.ignore_patterns(*ignore_patterns)
    )

    # make a zip archive of the copied folder
    shutil.make_archive(versioned_folder_path, 'zip', versioned_folder_path)

    # remove the copied directory
    shutil.rmtree(versioned_folder_path)

    # return the full path to the zip file
    return versioned_zip_file_path

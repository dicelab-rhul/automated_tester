__author__ = "cloudstrife9999"

import os

from os import walk, rename, listdir
from shutil import which
from json import load
from common import global_config
from strings import *
from typing import Iterable


def list_missing_software() -> list:
    missing: list = []

    for software in global_config[required_software_key]:
        if which(software) is None:
            missing.append(software)

    return missing


def validate_submission():
    code_directory = global_config[code_directory_key]
    tests_directory = global_config[tests_directory_key]

    if not os.path.isdir(code_directory):
        raise IOError("{} is not a valid directory. Aborting...".format(code_directory))

    if tests_directory is not None and not os.path.isdir(tests_directory):
        raise IOError("{} is not a valid directory. Aborting...".format(tests_directory))

    if not listdir(code_directory):
        raise IOError("Empty submission for {}. Aborting...".format(os.path.basename(code_directory)))


def list_empty_files(code_directory: str) -> list:
    empty: list = []

    for f in yield_all_useful_files_in_directory(directory=code_directory):
        if is_file_empty_for_all_intents_and_purposes(f=f):
            empty.append(os.path.basename(f))

    return empty


def is_file_empty_for_all_intents_and_purposes(f: str) -> bool:
    _check_file(file_path=f)

    lines = load_stripped_lines(file_path=f)

    for line in lines:
        if len(line) > 0:
            return False

    return True


def list_missing_files(cmd: list, test_files_excluded: bool=True) -> list:
    missing_files: list = []
    file_list: list = __get_relevant_file_names_from_cmd(cmd=cmd)

    for f in file_list:
        name: str = os.path.basename(f)
        if test_files_excluded and name.startswith(test_prefix):
            continue
        elif not os.path.isfile(f):
            missing_files.append(name)

    return missing_files


def __get_relevant_file_names_from_cmd(cmd: list) -> list:
    relevant_files: list = []

    for elm in cmd:
        if not "." in elm:
            continue
        
        tokens: list = elm.split(".")

        # This is safe, as we already checked for the presence of "." within elm.
        extension: str = "." + tokens[-1]

        if tokens[-2] != "" and extension in global_config[notable_extensions_key]:
            relevant_files.append(elm)

    return relevant_files


# Maybe in the future we'll be less lenient with this kind of "errors".
def rename_incorrectly_named_efficient_searches_files() -> None:
    for f in yield_all_useful_files_in_directory(global_config[code_directory_key]):
        possibly_incorrect_name: str = os.path.basename(f)

        if possibly_incorrect_name in global_config[common_misspellings_key].keys():
            correct_name: str = global_config[common_misspellings_key][possibly_incorrect_name]
            rename(f, os.path.join(os.path.dirname(f), correct_name))


def load_lines(file_path: str, min_len: int=1) -> list:
    _check_file(file_path=file_path)

    try:
        with open(file_path, "r") as f:
            return [line for line in f.readlines() if len(line) > min_len]
    except Exception as e:
        raise IOError("There was an error while accessing or reading {}".format(file_path)) from e


def load_stripped_lines(file_path: str, min_len: int=1) -> list:
    return [line.strip() for line in load_lines(file_path=file_path, min_len=min_len)]


def load_lines_without_trailing_newlines(file_path: str, min_len: int=1) -> list:
    to_return: list = []
    newlines: list = ["\n", "\r"]

    lines: list = load_lines(file_path=file_path, min_len=min_len)

    for line in lines:
        while len(line) > 0 and line[-1] in newlines:
            line = line[:-1]

        if len(line) > 0:
            to_return.append(line)

    return to_return


def load_json(file_path: str) -> dict:
    _check_file(file_path=file_path)

    try:
        with open(file_path, "r") as f:
            return load(fp=f)
    except Exception as e:
        raise IOError("There was an error while accessing/reading/parsing {}".format(file_path)) from e


def _check_file(file_path: str) -> None:
    if file_path is None:
        raise ValueError("A file path cannot be None.")
    elif os.path.isdir(file_path):
        raise ValueError("{} is an existing directory, not a regular file or symlink.".format(file_path))
    elif not os.path.isfile(file_path) and not os.path.islink(file_path):
        raise ValueError("{} is not a valid regular file or symlink.".format(file_path))


def yield_all_useful_files_in_directory(directory: str, extensions:list=None) -> Iterable:
    if extensions is None:
        extensions = global_config[notable_extensions_key]

    for d, _, files in walk(directory):
        for f in files:
            for extension in extensions:
                if f.endswith(extension):
                    yield os.path.join(d, f)
                    break

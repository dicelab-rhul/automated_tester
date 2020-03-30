__author__ = "cloudstrife9999"

import os

from os import walk, rename, listdir
from shutil import which
from json import load
from common import config


def list_missing_software() -> list:
    missing: list = []

    for software in config["required_software"]:
        if which(software) is None:
            missing.append(software)

    return missing


def validate_submission():
    code_directory = config["code_directory"]
    tests_directory = config["tests_directory"]

    if not os.path.isdir(code_directory):
        raise IOError("{} is not a valid directory. Aborting...".format(code_directory))

    if tests_directory is not None and not os.path.isdir(tests_directory):
        raise IOError("{} is not a valid directory. Aborting...".format(tests_directory))

    if not listdir(code_directory):
        raise IOError("Empty submission for {}. Aborting...".format(os.path.basename(code_directory)))


def list_empty_files(code_directory: str) -> list:
    empty: list = []

    for f in yield_all_useful_files_in_directory(directory=code_directory):
        if is_file_empty_for_all_intents_and_purposes(dir=dir, f=f):
            empty.append(os.path.basename(f))


def is_file_empty_for_all_intents_and_purposes(dir: str, f: str) -> bool:
    file_path: str = os.path.join(dir, f)

    _check_file(file_path=file_path)

    lines = load_stripped_lines(file_path=file_path)

    for line in lines:
        if len(line) > 0:
            return False

    return True


def list_missing_files(cmd: list, test_files_excluded: bool=True) -> list:
    missing_files: list = []
    file_list: list = [f for f in filter(lambda f: f.endswith(".pl"), cmd)]

    for f in file_list:
        name: str = os.path.basename(f)
        if test_files_excluded and name.startswith("test"):
            continue
        elif not os.path.isfile(f):
            missing_files.append(name)

    return missing_files


# Maybe in the future we'll be less lenient with this kind of "errors".
def rename_incorrectly_named_efficient_searches_files() -> None:
    for f in yield_all_useful_files_in_directory(config["code_directory"]):
        possibly_incorrect_name: str = os.path.basename(f)

        if possibly_incorrect_name in config["common_misspellings"].keys():
            correct_name: str = config["common_misspellings"][possibly_incorrect_name]
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
    elif not os.path.isfile(file_path): # Symlinks are not supported.
        raise ValueError("{} is not a valid file.".format(file_path))


def yield_all_useful_files_in_directory(directory: str, extensions:list=None) -> iter:
    if extensions is None:
        extensions = config["notable_extensions"]

    for dir, _, files in walk(directory):
        for f in files:
            for extension in extensions:
                if f.endswith(extension):
                    yield os.path.join(dir, f)
                    break

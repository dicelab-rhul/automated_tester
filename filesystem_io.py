import os

from os import walk, rename, listdir
from shutil import which
from json import load


def list_missing_software(software_list: list) -> list:
    missing: list = []

    for software in software_list:
        if which(software) is None:
            missing.append(software)

    return missing


def validate_submission(code_directory: str, tests_directory: str, skip_tests: bool):
    if not os.path.isdir(code_directory):
        raise IOError("{} is not a valid directory. Aborting...".format(code_directory))

    if not skip_tests and not os.path.isdir(tests_directory):
        raise IOError("{} is not a valid directory. Aborting...".format(tests_directory))

    if not listdir(code_directory):
        raise IOError("Empty submission for {}. Aborting...".format(os.path.basename(code_directory)))


def list_empty_files(code_directory: str) -> list:
    empty: list = []

    for f in yield_all_files_in_directory(directory=code_directory):
        if f.endswith(".pl") and is_file_empty_for_all_intents_and_purposes(dir=dir, f=f):
            empty.append(os.path.basename(f))


def is_file_empty_for_all_intents_and_purposes(dir: str, f: str) -> bool:
    file_path: str = os.path.join(dir, f)

    _check_file(file_path=file_path)

    lines = load_stripped_lines(file_path=file_path)

    for line in lines:
        if len(line) > 0:
            return False

    return True


def list_missing_files(cmd: list, directory: str, test_files_excluded: bool=True) -> list:
    missing_files: list = []
    file_list: list = [os.path.join(directory, f) for f in filter(lambda f: f.endswith(".pl"), cmd)]

    for f in file_list:
        name: str = os.path.basename(f)
        if test_files_excluded and name.startswith("test"):
            continue
        elif not os.path.isfile(f):
            return missing_files.append(name)

    return missing_files


def rename_incorrectly_named_efficient_searches_files(code_directory: str) -> None:
    for f in yield_all_files_in_directory(code_directory): # Maybe in the future we'll be less lenient with this kind of "errors".
        if os.path.basename(f) == "efficient_search.pl":
            new_name: str = "efficient_searches.pl"
            rename(f, os.path.join(os.path.dirname(f), new_name))
            break


def load_lines(file_path: str) -> list:
    _check_file(file_path=file_path)

    try:
        with open(file_path, "r") as f:
            return f.readlines()
    except Exception as e:
        raise IOError("There was an error while accessing or reading {}".format(file_path)) from e


def load_stripped_lines(file_path: str) -> list:
    return [line.strip() for line in load_lines(file_path=file_path)]


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


def yield_all_files_in_directory(directory: str) -> iter:
    for dir, _, files in walk(directory):
        for f in files:
            yield os.path.join(dir, f)

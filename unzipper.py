#!/usr/bin/env python3

__author__ = "cloudstrife9999"

from zipfile import ZipFile
from shutil import rmtree
from typing import Iterable
from argparse import ArgumentParser, Namespace

import os


def main() -> None:
    file_path: str = parse_arguments()
    dir_name: str = os.path.dirname(file_path)

    unzipped: str = unzip_file(file_path=file_path, destination_parent_directory=dir_name)
    submissions: Iterable = list_submission_dirs(parent_directory=unzipped)

    for submission in submissions:
        for elm in os.listdir(submission):
            if elm.endswith(".zip"):
                zipped: str = os.path.join(submission, elm)
                unzip_file(file_path=zipped, destination_parent_directory=submission, skip_check=True)

                break


def parse_arguments() -> str:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("-a", "--assignments-zip", required=True, type=str, metavar="assignments_zip", help="The path of the zip file containing all the submissions")

    args: Namespace = parser.parse_args()

    return args.assignments_zip


def list_submission_dirs(parent_directory: str) -> Iterable:
    for _, subdirs, _ in os.walk(parent_directory):
        for subdir in subdirs:
            yield os.path.join(parent_directory, subdir)
        
        break


def unzip_file(file_path, destination_parent_directory: str, skip_check=False) -> str:    
    with ZipFile(file_path, "r") as i_f:
        i_f.extractall(destination_parent_directory)

    unzipped: str = os.path.join(destination_parent_directory, os.path.basename(file_path)[:-4])

    if not skip_check and not os.path.exists(unzipped):
        raise IOError()
    
    os.remove(file_path)
    to_potentially_delete: str = os.path.join(destination_parent_directory, "__MACOSX")
    delete_directory(dir_path=to_potentially_delete)

    return unzipped


def delete_directory(dir_path: str) -> None:
    if os.path.isdir(dir_path):
        rmtree(dir_path)

        if os.path.exists(dir_path):
            raise IOError()


if __name__ == "__main__":
    main()

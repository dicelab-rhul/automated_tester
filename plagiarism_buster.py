#!/usr/bin/env python3

__author__ = "cloudstrife9999"

from argparse import ArgumentParser, Namespace
from filesystem_io import load_lines_without_trailing_newlines, yield_all_useful_files_in_directory
from printer import print_json
from builder import build_submission_id

import os


def look_for_plagiarism(code_directory: str, snippet: list) -> list:
    duplicates: list = []

    for f in yield_all_useful_files_in_directory(directory=code_directory):
        submission_id = build_submission_id(candidate=os.path.dirname(f))

        if check_for_pattern(path=f, snippet=snippet):
            case: dict = {
                submission_id: {
                    f: snippet
                } 
            }

            duplicates.append(case)

    return duplicates


def check_for_pattern(path: str, snippet: list) -> bool:
    lines: list = load_lines_without_trailing_newlines(file_path=path)

    if len(snippet) > len(lines):
        return False 

    index: int = -1

    for i in range(len(lines)):
        line: str = lines[i]

        if line == snippet[0]:
            index = i
            break
    
    if index == -1:
        return False

    lines = lines[index:]

    for i in range(len(snippet)):
        if snippet[i] != lines[i]:
            return False

    return True


def main() -> None:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("-d", "--code-directory", required=True, metavar="code_directory", type=str, help="The parent directory of all the submissions.")
    parser.add_argument("-s", "--snippet_path", type=str, required=True, metavar="snippet_path", help="The path of the snippet code to check.")

    args: Namespace = parser.parse_args()
    code_directory: str = args.code_directory
    snippet: list = load_lines_without_trailing_newlines(file_path=args.snippet_path)
    duplicates: dict = look_for_plagiarism(code_directory=code_directory, snippet=snippet)

    print_json(to_print=duplicates)


if __name__ == "__main__":
    main()

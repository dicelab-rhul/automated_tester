#!/usr/bin/env python3


from os import walk
from os.path import basename, join
from argparse import ArgumentParser, Namespace
from json import dumps


def load_code_snippet(path: str) -> list:
    with open(path, "r") as i_f:
        return [line.replace("\n", "") for line in i_f.readlines()]


def look_for_plagiarism(code_directory: str, snippet: list) -> list:
    duplicates: list = []

    for directory, _, files in walk(code_directory):
        submission_id = basename(directory)

        for f in files:
            if f.endswith(".pl"):
                path: str = join(directory, f)

                if check_for_pattern(path=path, submission_id=submission_id, snippet=snippet):
                    case: dict = {
                        submission_id: {
                            f: snippet
                        } 
                    }

                    duplicates.append(case)
                    break

    return duplicates


def check_for_pattern(path: str, submission_id: str, snippet: list) -> bool:
    with open(path, "r") as i_f:
        lines: list = [line.replace("\n", "") for line in i_f.readlines()]

    for l in snippet:
        if l not in lines:
            return False

    return True


def main() -> None:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("-d", "--code-directory", required=True, metavar="code_directory", type=str, help="The directory which contains the student code.")
    parser.add_argument("-s", "--snippet_path", type=str, required=True, metavar="snippet_path", help="The path of the snippet code to check.")

    args: Namespace = parser.parse_args()
    code_directory: str = args.code_directory
    snippet: list = load_code_snippet(path=args.snippet_path)

    duplicates: dict = look_for_plagiarism(code_directory=code_directory, snippet=snippet)

    print(dumps(duplicates, indent=4))


if __name__ == "__main__":
    main()

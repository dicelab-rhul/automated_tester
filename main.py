#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from sys import exit
from os import walk, listdir, rename
from os.path import exists, isdir, isfile, join, basename
from pwn import process
from json import load, dumps
from re import match
from sys import version_info
from shutil import which
from traceback import print_exc


test_cases_with_errors: list = []


def main() -> None:
    args: list = parse_arguments()
    
    if not check_for_valid_submission(args=args):
        return

    if not check_for_software_dependencies():
        return

    parts_weights: dict = load_parts_weights(args[3])
    submission_id: str = basename(args[0])
    test_cases: list = generate_test_cases(test_cases_file=args[2])

    preprocess_submission(code_directory=args[0])
    result: dict = check_submission(test_cases=test_cases, code_directory=args[0], tests_directory=args[1], parts_weights=parts_weights)

    process_result(result=result, submission_id=submission_id, parts_weights=parts_weights)


def parse_arguments() -> list:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("-d", "--code-directory", required=True, metavar="code_directory", type=str, help="The directory which contains the student code.")
    parser.add_argument("-t", "--tests-directory", required=False, metavar="tests_directory", type=str, help="The directory which contains the tests.")
    parser.add_argument("-c", "--test-cases-file", required=True, metavar="test_cases_file", type=str, help="The test cases file.")
    parser.add_argument("-w", "--weights-file", required=True, metavar="weights_file", type=str, help="The config file with the parts' weights.")

    args: Namespace = parser.parse_args()

    code_directory: str = args.code_directory
    tests_directory: str = args.tests_directory
    test_cases_file: str = args.test_cases_file
    weights_file: str = args.weights_file

    if tests_directory is None:
        tests_directory = code_directory

    return [code_directory, tests_directory, test_cases_file, weights_file]


def check_for_valid_submission(args: list) -> bool:
    if len(args) != 4:
        return False

    code_directory: str = args[0]
    tests_directory: str = args[1]

    for directory in [code_directory, tests_directory]:
        if not isdir(directory):
            print("{} is not a valid directory. Aborting...".format(directory))
            return False

    if not listdir(code_directory):
        print("Empty submission for {}. Not performing any test.".format(basename(code_directory)))
        return False

    return True


def check_for_software_dependencies() -> bool:
    if which("swipl") is None:
        print("swipl not found. Aborting...")
        return False

    return True


def load_parts_weights(weights_file: str) -> None:
    try:
        with open(weights_file, "r") as i_f:
            return load(i_f)
    except Exception as e:
        raise IOError("{} is malformed or not a valid file. Cannot load the parts' weights. Aborting...".format(weights_file)) from e


def generate_test_cases(test_cases_file: str) -> list:
    try:
        with open(test_cases_file, "r") as i_f:
            return load(i_f)
    except Exception as e:
        raise IOError("{} is malformed or not a valid file. Cannot load the test cases. Aborting...".format(test_cases_file)) from e


def preprocess_submission(code_directory: str) -> None:
    for directory, _, files in walk(code_directory):
        for f in files:
            # Maybe in the future we'll be less lenient with this kind of "errors".
            if f == "efficient_search.pl":
                new_name: str = "efficient_searches.pl"
                rename(join(directory, f), join(directory, new_name))


def check_submission(test_cases: list, code_directory: str, tests_directory: str, parts_weights: dict) -> dict:
    print("\n###################################################")
    print("Checking {}".format(code_directory))
    print("###################################################\n")

    test_result: dict = build_test_result_stub(parts_weights=parts_weights)

    for test_case in test_cases:
        test_result = check_test_case(test_case=test_case, test_result=test_result, code_directory=code_directory, tests_directory=tests_directory)

    return test_result


def build_test_result_stub(parts_weights: dict) -> dict:
    result: dict = {}

    for part in parts_weights.keys():
        result[part] = {
            "correct": 0,
            "to_manually_review": 0
        }

    return result


def check_test_case(test_case: dict, test_result: dict, code_directory: str, tests_directory: str) -> dict:
    correct: int = 0
    to_review: int = 0

    try:
        part: str = test_case["part"]
        cmd: list = build_swipl_command(test_case=test_case, code_directory=code_directory, tests_directory=tests_directory)
        queries: dict = test_case["queries"]

        if missing_files(code_directory=code_directory, cmd=cmd, queries=queries.keys()):
            test_cases_with_errors.append(test_case)
            test_result[part]["to_manually_review"] += len(queries)
            return test_result

        p = process(cmd)
        p.sendline("set_prolog_flag(answer_write_options,[quoted(true), portray(true), spacing(next_argument)]).")
        p.recv()

        for query, result in queries.items():
            p.sendline(query)
            output: str = str(p.recv(), "utf-8")

            while output.startswith("Welcome to") or output.startswith("Warning") or "true." in output:
                output = str(p.recv(), "utf-8")

            if "ERROR:" in output:
                if test_case not in test_cases_with_errors:
                    test_cases_with_errors.append(test_case)

                test_result[part]["to_manually_review"] += 1
                continue

            if check_output(cmd=cmd, query=query, expected_result=result, output=output):
                correct += 1
            else:
                to_review += 1
    except Exception as e:
        print("{}: got {}".format(cmd, repr(e)))
        print_exc()
        test_cases_with_errors.append(test_case)
        to_review = len(test_case["queries"]) - correct 
    
    test_result[part]["correct"] += correct
    test_result[part]["to_manually_review"] += to_review

    return test_result


def build_swipl_command(test_case: dict, code_directory: str, tests_directory: str) -> list:
    cmd = test_case["cmd"].split(" ")
    cmd[2] = join(code_directory, cmd[2])
    cmd[-1] = join(tests_directory, cmd[-1])

    if len(cmd) == 5:
       cmd[3] = join(code_directory, cmd[3])

    return cmd


def missing_files(code_directory: str, cmd: list, queries: list) -> bool:
    to_check: list = []

    to_check.append(join(code_directory, basename(cmd[2])))
    to_check.append(join(code_directory, basename(cmd[3])))

    if len(cmd) == 5:
        to_check.append(join(code_directory, basename(cmd[4])))

    for f in to_check:
        if basename(f).startswith("test"):
            continue
        if not exists(f) or not isfile(f):
            for query in queries:
                print("'{}', query: '{}' --> OK ? False".format(cmd, query))
                print("The submission is missing {}".format(basename(f)))
                print("---------------------------------------------------")
            return True

    return False
    

def check_output(cmd: list, query: str, expected_result: str, output) -> bool:
    m: match = match("Res = \[.*\]\.", output)
    result: bool = m is not None and (m[0] == expected_result or can_match(m[0], expected_result))

    print("'{}', query: '{}' --> OK ? {}".format(cmd, query, result))
    print("Expected: {}".format(expected_result))

    if m:
        print("Got:      {}".format(m[0]))
    else:
        print("Got:      {}".format(output.strip()))

    print("---------------------------------------------------")

    if result is None or type(result) != bool:
        return False
    else:
        return result

def can_match(unordered: str, ordered: str) -> bool:
    u: str = unordered[7:-1]
    o: str = ordered[7:-1]

    u_tokens = u.split(", ")
    o_tokens = o.split(", ")

    if len(u_tokens) != len(o_tokens):
        return False

    for token in o_tokens:
        if token not in u_tokens:
            return False
        else:
            u_tokens.remove(token)

    return True


def process_result(result: dict, submission_id: str, parts_weights: dict) -> None:
    if len(test_cases_with_errors) > 0:
        print("\n##### The following test cases for submission {} errored out. Some marks may be still awarded after a manual review. #####\n".format(submission_id))
        print(dumps(obj=test_cases_with_errors, indent=4))

    for part in result.keys():
        result[part]["partial_mark"] = parts_weights[part] * result[part]["correct"] / (result[part]["correct"] + result[part]["to_manually_review"])

    print("\nResult for {}:\n".format(submission_id))
    print(dumps(obj=result, indent=4))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from sys import exit
from os import walk, listdir
from os.path import exists, isdir, isfile, join, basename
from pwn import process
from json import load, dumps
from re import match
from sys import version_info
from shutil import which


test_cases_with_syntax_errors: list = []


def main() -> None:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("-d", "--code-directory", required=True, metavar="code_directory", type=str, help="The directory which contains the student code.")
    parser.add_argument("-t", "--tests-directory", required=False, metavar="tests_directory", type=str, help="The directory which contains the tests.")
    parser.add_argument("-c", "--test-cases-file", required=True, metavar="test_cases_file", type=str, help="The test cases file.")

    args: Namespace = parser.parse_args()
    code_directory: str = args.code_directory
    tests_directory: str = args.tests_directory
    test_cases_file: str = args.test_cases_file

    if tests_directory is None:
        tests_directory = code_directory

    for directory in [code_directory, tests_directory]:
        if not isdir(directory):
            print("{} is not a valid directory. Aborting...".format(directory))
            exit(-1)

    submission_id: str = basename(code_directory)

    if not listdir(code_directory):
        print("Empty submission for {}. Not performing any test.".format(submission_id))
        exit(-1)

    if which("swipl") is None:
        print("swipl not found. Aborting...")
        exit(-1)

    test_cases: list = generate_test_cases(test_cases_file=test_cases_file)

    if test_cases_file is None:
        print("{} is malformed or not a valid file. Cannot load the test cases. Aborting...".format(test_cases_file))
        exit(-1)

    check_for_syntax_errors(test_cases=test_cases, code_directory=code_directory, tests_directory=tests_directory)
    result: dict = check_submission(test_cases=test_cases, code_directory=code_directory, tests_directory=tests_directory)

    print("\nResult for {}: correct: {}, to manually review (incorrect or with syntax errors or crashed): {}\n".format(submission_id, result["correct"], result["to_manually_review"]))

    if len(test_cases_with_syntax_errors) > 0:
        print("\n##### The submission for {} has syntax errors in the following test cases! It must be manually reviewed. #####\n".format(submission_id))
        print(dumps(obj=test_cases_with_syntax_errors, indent=4))


def generate_test_cases(test_cases_file: str) -> list:
    try:
        with open(test_cases_file, "r") as i_f:
            return load(i_f)
    except:
        return None


def check_for_syntax_errors(test_cases: list, code_directory: str, tests_directory: str) -> None:
    for test_case in test_cases:
        cmd = test_case["cmd"].split(" ")
        cmd[2] = join(code_directory, cmd[2])
        cmd[-1] = join(tests_directory, cmd[-1])

        if len(cmd) == 5:
            cmd[3] = join(code_directory, cmd[3])

        p = process(cmd)
        output: str = str(p.recv(), "utf-8")

        if "ERROR:" in output:
            test_cases_with_syntax_errors.append(test_case)
            continue

        queries: dict = test_case["queries"]

        for query, result in queries.items():
            p.sendline(query)
            output = str(p.recv(), "utf-8")

            if "ERROR:" in output:
                test_cases_with_syntax_errors.append(test_case)
                break


def check_submission(test_cases: list, code_directory: str, tests_directory: str) -> dict:
    print("---------------------------------------------------")
    print("Checking {}".format(code_directory))
    print("---------------------------------------------------")

    test_result: dict = {
        "correct": 0,
        "to_manually_review": 0
    }

    for test_case in test_cases:
        if test_case in test_cases_with_syntax_errors:
            test_result["to_manually_review"] += len(test_case["queries"])
            continue

        correct: int = 0
        to_review: int = 0

        try:
            cmd = test_case["cmd"].split(" ")
            cmd[2] = join(code_directory, cmd[2])
            cmd[-1] = join(tests_directory, cmd[-1])

            if len(cmd) == 5:
                cmd[3] = join(code_directory, cmd[3])

            p = process(cmd)
            str(p.recv(), "utf-8")
            queries: dict = test_case["queries"]

            for query, result in queries.items():
                p.sendline(query)
                output = str(p.recv(), "utf-8")

                if check_output(cmd=cmd, query=query, expected_result=result, output=output):
                    correct += 1
                else:
                    to_review += 1
        except:
            test_cases_with_syntax_errors.append(test_case)
            to_review = len(test_case["queries"]) - correct 
        
        test_result["correct"] += correct
        test_result["to_manually_review"] += to_review

    return test_result
    

def check_output(cmd: list, query: str, expected_result: str, output) -> bool:
    m: match = match("Res = \[.*\]\.", output)
    result: bool = m and m[0] == expected_result

    print("'{}', query: '{}' --> OK ? {}".format(cmd, query, result))
    print("Expected: {}".format(expected_result))

    if m:
        print("Got:      {}".format(m[0]))
    else:
        print("Got:      {}".format(output.strip()))

    if result is None or type(result) != bool:
        return False
    else:
        return result


if __name__ == "__main__":
    main()

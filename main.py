#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from sys import exit
from os import walk, listdir
from os.path import exists, isdir, isfile, join
from pwn import process
from json import load
from re import match
from pprint import pp


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

    if not listdir(code_directory):
        print("Empty submission!")
        exit(-1)

    test_cases: list = generate_test_cases(test_cases_file=test_cases_file)

    if test_cases_file is None:
        print("{} is not a valid file. Aborting...".format(test_cases_file))
        exit(-1)

    check_for_syntax_errors(test_cases=test_cases, code_directory=code_directory, tests_directory=tests_directory)

    check_submission(test_cases=test_cases, code_directory=code_directory, tests_directory=tests_directory)

    if len(test_cases_with_syntax_errors) > 0:
        print("\n##### The submission has syntax errors in the following test cases! It must be manually reviewed. #####\n")
        pp(test_cases_with_syntax_errors)


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


def check_submission(test_cases: list, code_directory: str, tests_directory: str) -> None:
    print("---------------------------------------------------")
    print("Checking {}".format(code_directory))
    print("---------------------------------------------------")

    for test_case in test_cases:
        if test_case in test_cases_with_syntax_errors:
            continue

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

                check_output(cmd=cmd, query=query, expected_result=result, output=output)
        except:
            test_cases_with_syntax_errors.append(test_case)


def check_output(cmd: list, query: str, expected_result: str, output) -> None:
    m: match = match("Res = \[.*\]\.", output)
    result: bool = m and m[0] == expected_result

    print("'{}', query: '{}' --> OK ? {}".format(cmd, query, result))
    print("Expected: {}".format(expected_result))

    if m:
        print("Got:      {}".format(m[0]))
    else:
        print("Got:      {}".format(output.strip()))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from sys import exit
from colorama import init as colorama_init
from filesystem_io import *
from printer import *
from builder import *
from parser import PrologOutputParser
from prolog_io import PrologIO

import os


test_cases_with_errors: list = []
timeout: int = None


def main() -> None:
    colorama_init()
    args: list = parse_arguments()
    
    print_submission_header(code_directory=args[0])
    check_submission_validity(code_directory=args[0], tests_directory=args[1])
    check_required_software()

    config: dict = load_json(file_path=args[3])
    parts_weights: dict = config["parts"]
    global timeout

    if timeout is None:
        timeout = config["timeout"]

    print_timeout_info(timeout=timeout)

    submission_id: str = os.path.basename(args[0])
    test_cases: list = load_json(file_path=args[2])

    rename_incorrectly_named_efficient_searches_files(code_directory=args[0])
    result: dict = check_submission(test_cases=test_cases, code_directory=args[0], tests_directory=args[1], parts_weights=parts_weights)

    print_test_cases_with_errors(test_cases_with_errors=test_cases_with_errors, submission_id=submission_id)
    print_final_result(result=result, submission_id=submission_id, parts_weights=parts_weights)


def check_submission_validity(code_directory: str, tests_directory: str) -> None:
    try:
        validate_submission(code_directory=code_directory, tests_directory=tests_directory)
    except Exception as e:
        print_exception_message(e=e)
        exit(-1)


def check_required_software() -> None:
    missing: list = list_missing_software(software_list=["swipl"])

    if missing:
        print_missing_software_dependencies(missing=missing)
        exit(-1)


def parse_arguments() -> list:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("-d", "--code-directory", required=True, metavar="code_directory", type=str, help="The directory which contains the student code.")
    parser.add_argument("-t", "--tests-directory", required=False, metavar="tests_directory", type=str, help="The directory which contains the tests.")
    parser.add_argument("-c", "--test-cases-file", required=True, metavar="test_cases_file", type=str, help="The test cases file.")
    parser.add_argument("-C", "--config-file", required=True, metavar="config_file", type=str, help="The config file.")
    parser.add_argument("-T", "--test-timeout", required=False, metavar="test_timeout", type=int, help="The timeout for each test in seconds.")

    args: Namespace = parser.parse_args()

    code_directory: str = args.code_directory
    tests_directory: str = args.tests_directory
    test_cases_file: str = args.test_cases_file
    config_file: str = args.config_file
    test_timeout: int = args.test_timeout

    if tests_directory is None:
        tests_directory = code_directory

    if test_timeout is not None:
        global timeout
        timeout = test_timeout

    return [code_directory, tests_directory, test_cases_file, config_file]


def check_submission(test_cases: list, code_directory: str, tests_directory: str, parts_weights: dict) -> dict:
    test_result: dict = build_test_result_stub(parts_weights=parts_weights)

    for test_case in test_cases:
        test_result = check_test_case(test_case=test_case, test_result=test_result, code_directory=code_directory, tests_directory=tests_directory)

    return test_result


def check_test_case(test_case: dict, test_result: dict, code_directory: str, tests_directory: str) -> dict:
    try:
        part: str = test_case["part"]
        cmd: list = build_swipl_command(test_case=test_case, code_directory=code_directory, tests_directory=tests_directory)
        
        print_test_case_group(cmd=cmd)

        queries: dict = test_case["queries"]
        missing_files: list = list_missing_files(cmd=cmd, directory=code_directory, test_files_excluded=True)
        
        if missing_files:
            print_test_outcome_if_missing_files(cmd=cmd, missing_files=missing_files)
            test_cases_with_errors.append(test_case)
            test_result[part]["to_manually_review"] += len(queries)
            return test_result

        p = PrologIO(cmd=cmd, timeout=timeout)
        p.run()

        correct, to_review = run_queries(cmd=cmd, test_case=test_case, test_result=test_result, part=part, queries=queries, p=p)
        test_result[part]["correct"] += correct
        test_result[part]["to_manually_review"] += to_review
    except Exception:
        print_exception()
        test_cases_with_errors.append(test_case)
        test_result[part]["to_manually_review"] += len(test_case["queries"])

    return test_result


def run_queries(cmd: list, test_case: dict, test_result: dict, part: str, queries: list, p: PrologIO) -> tuple:
    parser: PrologOutputParser = PrologOutputParser()
    correct: int = 0
    to_review: int = 0

    for query, result in queries.items():
        output: str = p.send_and_receive(to_send=query, keep_receiving_if_received=["Welcome to", "Warning", "true."])

        if parser.has_error_message(output=output):
            errored_out_test_case: dict = build_errored_out_test_case(test_case=test_case, cmd=cmd, query=query)
            test_cases_with_errors.append(errored_out_test_case)                

            to_review += 1
            continue

        query_result: str = parser.parse_output(output=output)
        passed: bool = parser.check_output(result=query_result, expected_result=result, out_of_order_allowed=True) # TODO: check this.

        correct += passed
        to_review += (not passed)
        
        print_test_outcome(cmd=cmd, query=query, passed=passed, expected_output=result, actual_output=query_result)
    
    return correct, to_review


if __name__ == "__main__":
    main()

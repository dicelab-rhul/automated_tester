#!/usr/bin/env python3

__author__ = "cloudstrife9999"

from argparse import ArgumentParser, Namespace
from sys import exit
from colorama import init as colorama_init
from typing import Union

from filesystem_io import *
from printer import *
from builder import *
from prolog_parser import PrologOutputParser
from prolog_io import PrologIO
from common import global_config
from strings import *


def main() -> None:
    colorama_init()
    parse_cli_arguments()
    print_submission_header()
    check_submission_validity()
    check_required_software()
    load_general_config()
    print_info()

    submission_id: str = build_submission_id(candidate=global_config[code_directory_key])
    test_cases: Union[list, dict] = load_json(file_path=global_config[test_cases_file_key])
    result: dict = check_submission(test_cases=test_cases)

    print_test_cases_with_errors(submission_id=submission_id)
    print_final_result(result=result, submission_id=submission_id)
    print_footer()


def check_submission_validity() -> None:
    try:
        validate_submission()
    except Exception as e:
        print_exception_message(e=e)
        exit(-1)


def check_required_software() -> None:
    missing: list = list_missing_software()

    if missing:
        print_missing_software_dependencies(missing=missing)
        exit(-1)


def load_general_config() -> None:
    config: dict = load_json(file_path=global_config[config_file_key])

    global_config[parts_weights_key] = config[parts_key]
    global_config[exceptions_debug_key] = config[exceptions_debug_key]
    global_config[result_regex_key] = config[result_regex_key]

    if global_config[timeout_key] is None:
        global_config[timeout_key] = config[timeout_key]


def parse_cli_arguments() -> None:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("-d", "--code-directory", required=True, metavar=code_directory_key, type=str, help="The directory which contains the student code.")
    parser.add_argument("-t", "--tests-directory", required=False, metavar=tests_directory_key, type=str, help="The directory which contains the tests.")
    parser.add_argument("-c", "--test-cases-file", required=True, metavar=test_cases_file_key, type=str, help="The test cases file.")
    parser.add_argument("-C", "--config-file", required=True, metavar=config_file_key, type=str, help="The config file.")
    parser.add_argument("-T", "--test-timeout", required=False, metavar=test_timeout_key, type=Union[int, float], help="The timeout for each test in seconds.")

    args: Namespace = parser.parse_args()

    global_config[code_directory_key] = args.code_directory
    global_config[tests_directory_key] = args.tests_directory
    global_config[timeout_key] = args.test_timeout
    global_config[test_cases_file_key] = args.test_cases_file
    global_config[config_file_key] = args.config_file


def check_submission(test_cases: Union[list, dict]) -> dict:
    rename_incorrectly_named_efficient_searches_files()

    test_result: dict = build_test_result_stub()

    for test_case in test_cases:
        test_result = check_test_case(test_case=test_case, test_result=test_result)

    return test_result


def check_test_case(test_case: dict, test_result: dict) -> dict:
    part: str = test_case[part_key]
    has_tests: bool = test_case[has_tests_key]
    cmd: list = build_swipl_command(test_case=test_case, has_tests=has_tests)
    queries: dict = test_case[queries_key]

    print_test_case_group(cmd=cmd)
    
    return do_check_test_case(test_case=test_case, cmd=cmd, part=part, queries=queries, test_result=test_result)


def do_check_test_case(test_case: dict, cmd: list, part: str, queries: dict, test_result: dict) -> dict:
    try:
        missing_files: list = list_missing_files(cmd=cmd, test_files_excluded=True)

        if missing_files:
            print_test_outcome_if_missing_files(cmd=cmd, queries=queries, missing_files=missing_files)
            reason: str = "Missing or empty {}".format(missing_files)
            save_errored_out_test_cases(test_case=test_case, cmd=cmd, queries=queries, reason=reason)
            test_result[part][to_manually_review_key] += len(queries)
            
            return test_result

        p = PrologIO(cmd=cmd)
        p.start()

        correct, to_review = run_queries(cmd=cmd, test_case=test_case, test_result=test_result, part=part, queries=queries, p=p)
        test_result[part][correct_key] += correct
        test_result[part][to_manually_review_key] += to_review
    except Exception as e:
        print_exception_maybe()
        reason: str = "Got exception: {}".format(repr(e))
        save_errored_out_test_cases(test_case=test_case, cmd=cmd, queries=queries, reason=reason)
        test_result[part][to_manually_review_key] += len(test_case[queries_key])

    return test_result



def save_errored_out_test_cases(test_case: dict, cmd: list, queries: dict, reason: str) -> None:
    test_case_with_errors_group: list = build_errored_out_test_case_group(test_case=test_case, cmd=cmd, queries=queries, reason=reason)
        
    for test_case_with_errors in test_case_with_errors_group:
        storage[test_cases_with_errors_key].append(test_case_with_errors)


def run_queries(cmd: list, test_case: dict, test_result: dict, part: str, queries: dict, p: PrologIO) -> tuple:
    parser: PrologOutputParser = PrologOutputParser()
    correct: int = 0
    to_review: int = 0

    # TODO: maybe "order_matters" is a property of single queries, rather than query groups.
    order_matters: bool = test_case[order_matters_key]

    for query, result in queries.items():
        output: str = p.send_and_receive(to_send=query)

        if parser.has_error_message(output=output) or output == "":
            errored_out_test_case: dict = build_errored_out_test_case(test_case=test_case, cmd=cmd, query=query, output=output)
            storage[test_cases_with_errors_key].append(errored_out_test_case)
            fake_output = build_fake_output_after_error_or_timeout(real_output=output)
            print_test_outcome(cmd=cmd, query=query, passed=False, expected_output=result, actual_output=fake_output, order_matters=order_matters)

            to_review += 1
            continue

        query_result: str = parser.parse_output(output=output)
        passed: bool = parser.check_output(result=query_result, expected_result=result, out_of_order_allowed=not order_matters)
        correct += passed
        to_review += (not passed)
        
        print_test_outcome(cmd=cmd, query=query, passed=passed, expected_output=result, actual_output=query_result)
    
    p.stop()

    return correct, to_review


if __name__ == "__main__":
    main()

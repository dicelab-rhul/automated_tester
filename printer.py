__author__ = "cloudstrife9999"

from colorama import Fore, Style
from builder import build_final_result
from traceback import print_exc
from sys import stdout
from common import global_config, storage
from strings import *
from json import dumps


def print_missing_software_dependencies(missing: list) -> None:
    for elm in missing:
        print("{}{}{} not found.{}".format(Style.BRIGHT, Fore.RED, elm, Style.RESET_ALL))
        print("{}{}Aborting...{}".format(Style.BRIGHT, Fore.RED, Style.RESET_ALL))


def print_submission_header() -> None:
    print("\n{}###################################################".format(Style.BRIGHT))
    print("Checking {}".format(global_config["code_directory"]))
    print("###################################################{}".format(Style.RESET_ALL))


def print_timeout_info() -> None:
    print("\n{}{}INFO: the timeout for each query is {} seconds.{}".format(Style.BRIGHT, Fore.GREEN, global_config[timeout_key], Style.RESET_ALL))


def print_exception_maybe() -> None:
    if global_config[exceptions_debug_key]:
        print_exc(file=stdout)


def print_exception_message(e: Exception) -> None:
    print("{}{}{}{}".format(Style.BRIGHT, Fore.RED, str(e), Style.RESET_ALL))


def print_empty_files_warning(empty: list) -> None:
    for f in empty:
        print("{}{}Warning: file {} has no content.{}".format(Style.BRIGHT, Fore.RED, f, Style.RESET_ALL)) 


def print_test_case_group(cmd: list) -> None:
    print("\n---------------------------------------------------")
    print("{}Test group:    {}{}{}".format(Style.BRIGHT, Fore.MAGENTA, " ".join(cmd), Style.RESET_ALL))
    print("---------------------------------------------------\n")
    print("---------------------------------------------------")


def print_test_cases_with_errors(submission_id: str) -> None:
    test_cases_with_errors: list = storage[test_cases_with_errors_key]

    if len(test_cases_with_errors) > 0:
        print("\n{}{}##### The following test cases for submission {} errored out. Some marks may be still awarded after a manual review. #####{}\n".format(Style.BRIGHT, Fore.RED, submission_id, Style.RESET_ALL))

        for test_case in test_cases_with_errors:
            print("{}Part:     {}{}{}".format(Style.BRIGHT, Fore.MAGENTA, test_case[part_key], Style.RESET_ALL))
            print("{}Cmd:      {}{}{}".format(Style.BRIGHT, Fore.BLUE, test_case[cmd_key], Style.RESET_ALL))

            for query in test_case[queries_key].keys():
                print("{}Query:    {}{}{}".format(Style.BRIGHT, Fore.YELLOW, query, Style.RESET_ALL))
            print("{}Reason:   {}{}{}".format(Style.BRIGHT, Fore.RED, test_case[reason_key], Style.RESET_ALL))
            print()

        print()
    else:
        print("\n{}{}##### None of the test cases errored out. Good! #####{}\n".format(Style.BRIGHT, Fore.GREEN, Style.RESET_ALL))

    print("---------------------------------------------------\n")


def print_test_outcome(cmd: list, query: str, passed: bool, expected_output: str, actual_output: str, order_matters: bool=False) -> bool:
    if passed:
        passed_color = Fore.GREEN
    else:
        passed_color = Fore.RED
        actual_output = actual_output.strip()

    if order_matters:
        order = "YES"
    else:
        order = "NO"

    if actual_output.startswith("<") and actual_output.endswith(">"):
        output_color = Fore.RED
    else:
        output_color = Fore.YELLOW
        
    print("{}Test case:     {}{}{}".format(Style.BRIGHT, Fore.BLUE, " ".join(cmd), Style.RESET_ALL))
    print("{}Query:         {}{}{}".format(Style.BRIGHT, Fore.BLUE, query, Style.RESET_ALL))
    print("{}Expected:      {}{}{}".format(Style.BRIGHT, Fore.YELLOW, expected_output, Style.RESET_ALL))
    print("{}Got:           {}{}{}".format(Style.BRIGHT, output_color, actual_output, Style.RESET_ALL))
    print("{}Order matters? {}{}{}".format(Style.BRIGHT, Fore.YELLOW, order, Style.RESET_ALL))
    print("{}Passed?        {}{}{}".format(Style.BRIGHT, passed_color, passed, Style.RESET_ALL))

    print_coincidence_warning_if_necessary(passed=passed, expected_output=expected_output, actual_output=actual_output)

    print("---------------------------------------------------")


def print_coincidence_warning_if_necessary(passed: bool, expected_output: str, actual_output: str) -> None:
    if passed and expected_output == "Res = []." and actual_output == expected_output:
        print("{}INFO:          {}Check whether this result is correct by coincidence.{}".format(Style.BRIGHT, Fore.YELLOW, Style.RESET_ALL))


def print_test_outcome_if_missing_files(cmd: list, queries: list, missing_files: list) -> bool:
    for query in queries:
        print("{}Test case:   {}{}{}".format(Style.BRIGHT, Fore.BLUE, " ".join(cmd), Style.RESET_ALL))
        print("{}Query:       {}{}{}".format(Style.BRIGHT, Fore.BLUE, query, Style.RESET_ALL))
        print("{}Passed?      {}{}{}".format(Style.BRIGHT, Fore.RED, False, Style.RESET_ALL))
        print("{}Reason:      {}Missing {}{}".format(Style.BRIGHT, Fore.YELLOW, missing_files, Style.RESET_ALL))
        print("---------------------------------------------------")


def print_final_result(result: dict, submission_id: str) -> None:
    result = build_final_result(result=result)

    print("{}{}Results for {}:{}{}\n".format(Style.BRIGHT, Fore.GREEN, submission_id, Style.RESET_ALL, Style.BRIGHT))

    for part, res in result.items():
        print("{}{}{}:".format(Fore.YELLOW, part, Fore.WHITE))

        longest_key_length: int = max(map(len, res))

        for k, v in res.items():
            buffer: str = " " * (longest_key_length - len(k))

            if k == correct_key:
                v = "{}{}{}".format(Fore.GREEN, v, Fore.WHITE)
            elif k == to_manually_review_key:
                v = "{}{}{}".format(Fore.RED, v, Fore.WHITE)
            elif k == partial_mark_key:
                v = "{}{}{}".format(Fore.BLUE, v, Fore.WHITE)
                
            print("    {}:{} {}".format(k, buffer, v))
        
    print("\n---------------------------------------------------")


def print_json(to_print: dict, indend=4, sort_keys=False) -> None:
    print(dumps(obj=to_print, indent=indend, sort_keys=sort_keys))

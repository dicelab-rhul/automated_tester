from json import dumps
from colorama import Fore, Style
from builder import build_final_result
from traceback import print_exc
from sys import stdout


def print_missing_software_dependencies(missing: list) -> None:
    for elm in missing:
        print("{}{}{} not found.{}".format(Style.BRIGHT, Fore.RED, elm, Style.RESET_ALL))
        print("{}{}Aborting...{}".format(Style.BRIGHT, Fore.RED, Style.RESET_ALL))


def print_submission_header(code_directory: str) -> None:
    print("\n{}###################################################".format(Style.BRIGHT))
    print("Checking {}".format(code_directory))
    print("###################################################{}".format(Style.RESET_ALL))


def print_timeout_info(timeout: int) -> None:
    print("\n{}{}INFO: the timeout for each query is {} seconds.{}".format(Style.BRIGHT, Fore.GREEN, timeout, Style.RESET_ALL))

def print_exception() -> None:
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


def print_test_cases_with_errors(test_cases_with_errors: list, submission_id: str) -> None:
    if len(test_cases_with_errors) > 0:
        print("\n{}{}##### The following test cases for submission {} errored out. Some marks may be still awarded after a manual review. #####{}\n".format(Style.BRIGHT, Fore.RED, submission_id, Style.RESET_ALL))

        for test_case in test_cases_with_errors:
            print("{}Part:     {}{}{}".format(Style.BRIGHT, Fore.YELLOW, test_case["part"], Style.RESET_ALL))
            print("{}Cmd:      {}{}{}".format(Style.BRIGHT, Fore.YELLOW, test_case["cmd"], Style.RESET_ALL))

            for query in test_case["queries"].keys():
                print("{}Query:    {}{}{}".format(Style.BRIGHT, Fore.YELLOW, query, Style.RESET_ALL))
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

    if actual_output == "":
        actual_output = "<nothing was returned by the query>"
        output_color = Fore.RED
    elif actual_output == "<aborted due to a syntax error>":
        output_color = Fore.RED
    else:
        output_color = Fore.YELLOW
        
    print("{}Test case:     {}{}{}".format(Style.BRIGHT, Fore.BLUE, " ".join(cmd), Style.RESET_ALL))
    print("{}Query:         {}{}{}".format(Style.BRIGHT, Fore.BLUE, query, Style.RESET_ALL))
    print("{}Expected:      {}{}{}".format(Style.BRIGHT, Fore.YELLOW, expected_output, Style.RESET_ALL))
    print("{}Got:           {}{}{}".format(Style.BRIGHT, output_color, actual_output, Style.RESET_ALL))
    print("{}Order matters? {}{}{}".format(Style.BRIGHT, Fore.YELLOW, order, Style.RESET_ALL))
    print("{}Passed?        {}{}{}".format(Style.BRIGHT, passed_color, passed, Style.RESET_ALL))
    print("---------------------------------------------------")


def print_test_outcome_if_missing_files(cmd: list, queries: list, missing_files: list) -> bool:
    for query in queries:
        print("{}Test case:   {}{}{}".format(Style.BRIGHT, Fore.BLUE, " ".join(cmd), Style.RESET_ALL))
        print("{}Query:       {}{}{}".format(Style.BRIGHT, Fore.BLUE, query, Style.RESET_ALL))
        print("{}Passed?      {}{}{}".format(Style.BRIGHT, Fore.RED, False, Style.RESET_ALL))
        print("{}Reason:      {}Missing {}{}".format(Style.BRIGHT, Fore.YELLOW, missing_files, Style.RESET_ALL))
        print("---------------------------------------------------")


def print_json(src: dict, indent=4) -> None:
    print(dumps(obj=src, indent=indent))


def print_final_result(result: dict, submission_id: str, parts_weights: dict) -> None:
    result = build_final_result(result=result, parts_weights=parts_weights)

    print("{}{}Results for {}:{}{}\n".format(Style.BRIGHT, Fore.GREEN, submission_id, Style.RESET_ALL, Style.BRIGHT))

    for part, res in result.items():
        print("{}{}{}:".format(Fore.YELLOW, part, Fore.WHITE))

        for k, v in res.items():
            if k == "correct":
                k += " "*11 # TODO: remove this magic number.
                v = "{}{}{}".format(Fore.GREEN, v, Fore.WHITE)
            elif k == "to_manually_review":
                v = "{}{}{}".format(Fore.RED, v, Fore.WHITE)
            elif k == "partial_mark":
                k += " "*6 # TODO: remove this magic number.
                v = "{}{}{}".format(Fore.BLUE, v, Fore.WHITE)
                
            print("    {}: {}".format(k, v))
        
    print("\n---------------------------------------------------")

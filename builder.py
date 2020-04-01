__author__ = "cloudstrife9999"

from common import global_config
from strings import *

import os


def build_submission_id(candidate: str) -> str:
    if candidate.endswith(os.path.sep):
        candidate = candidate[:-1]

    return os.path.basename(candidate)


def build_test_result_stub() -> dict:
    result: dict = {}

    for part in global_config[parts_weights_key].keys():
        result[part] = {
            correct_key: 0,
            to_manually_review_key: 0
        }

    return result


def build_swipl_command(test_case: dict, has_tests: bool) -> list:
    code_directory: str = global_config[code_directory_key]
    tests_directory: str = global_config[tests_directory_key]
    cmd = test_case[cmd_key].split(" ")
    cmd[1] = os.path.join(code_directory, cmd[1])

    if tests_directory is not None and has_tests:
        cmd[-1] = os.path.join(tests_directory, cmd[-1])

    if len(cmd) == 4:
        cmd[2] = os.path.join(code_directory, cmd[2])

    return cmd


def build_errored_out_test_case_group(test_case: dict, cmd: list=[unknown_key], queries: list=[], reason: str=unknown_key) -> list:
    return [build_errored_out_test_case(test_case=test_case, cmd=cmd, query=query, output=reason) for query in queries]


def build_errored_out_test_case(test_case: dict, cmd: list, query: str, output: str) -> dict:
    if output == "":
        reason: str = "A timeout occurred, or nothing was returned in response to the query."
    elif "Missing" in output or "Got exception: " in output:
        reason: str = output
    else:
        reason: str = "There was an error with the Prolog program."

    return {
        cmd_key: " ".join(cmd),
        queries_key: {
            query: list(filter(lambda k: k == query, test_case[queries_key].keys()))[0]
        },
        part_key: test_case[part_key],
        reason_key: reason
    }


def build_fake_output_after_error_or_timeout(real_output: str) -> str:
    for elm in global_config[error_patterns_key]:
        if elm in real_output:
            return "<aborted due to a Prolog error>"

    return "<a timeout occurred, or nothing was returned in response to the query>"


def build_final_result(result: dict) -> dict:
    parts_weights: dict = global_config[parts_weights_key]

    for part in result.keys():
        partial_mark: float = parts_weights[part] * result[part][correct_key] / (result[part][correct_key] + result[part][to_manually_review_key])

        if partial_mark.is_integer():
            result[part][partial_mark_key] = int(partial_mark)
        else:
            result[part][partial_mark_key] = round(partial_mark, 2)

    return result
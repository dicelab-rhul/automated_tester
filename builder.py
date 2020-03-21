import os


def build_submission_id(candidate: str) -> str:
    if candidate.endswith("/"):
        candidate = candidate[:-1]

    return os.path.basename(candidate)


def build_test_result_stub(parts_weights: dict) -> dict:
    result: dict = {}

    for part in parts_weights.keys():
        result[part] = {
            "correct": 0,
            "to_manually_review": 0
        }

    return result


def build_swipl_command(test_case: dict, code_directory: str, tests_directory: str) -> list:
    cmd = test_case["cmd"].split(" ")
    cmd[1] = os.path.join(code_directory, cmd[1])
    cmd[-1] = os.path.join(tests_directory, cmd[-1])

    if len(cmd) == 4:
        cmd[2] = os.path.join(code_directory, cmd[2])

    return cmd


def build_errored_out_test_case(test_case: dict, cmd: list, query: str) -> dict:
    return {
        "cmd": " ".join(cmd),
        "queries": {
            query: list(filter(lambda k: k == query, test_case["queries"].keys()))[0]
        },
        "part": test_case["part"]
    }


def build_final_result(result: dict, parts_weights: dict) -> dict:
    for part in result.keys():
        partial_mark: float = parts_weights[part] * result[part]["correct"] / (result[part]["correct"] + result[part]["to_manually_review"])

        if partial_mark.is_integer():
            result[part]["partial_mark"] = int(partial_mark)
        else:
            result[part]["partial_mark"] = round(partial_mark, 2)

    return result
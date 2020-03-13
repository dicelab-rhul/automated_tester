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


test_cases_with_syntax_errors: list = []

# The remaining point adding up to 100 are assigned after the code inspection (i.e., style).
parts_weights: dict = {
    "T1(a)": 10,
    "T1(b)": 10,
    "T1(c)": 10,
    "T2(a)": 12,
    "T2(b)": 12,
    "T2(c)": 12,
    "T2(d)": 20,
}


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

    preprocess_submission(code_directory=code_directory)

    #check_for_syntax_errors(test_cases=test_cases, code_directory=code_directory, tests_directory=tests_directory)
    result: dict = check_submission(test_cases=test_cases, code_directory=code_directory, tests_directory=tests_directory)


    for part in result.keys():
        result[part]["partial_mark"] = parts_weights[part] * result[part]["correct"] / (result[part]["correct"] + result[part]["to_manually_review"])


    print("\nResult for {}:\n".format(submission_id))
    print(dumps(obj=result, indent=4))

    if len(test_cases_with_syntax_errors) > 0:
        print("\n##### The submission for {} has syntax errors in the following test cases! It must be manually reviewed. #####\n".format(submission_id))
        print(dumps(obj=test_cases_with_syntax_errors, indent=4))


def preprocess_submission(code_directory: str) -> None:
    for directory, _, files in walk(code_directory):
        for f in files:
            if f == "efficient_search.pl":
                new_name: str = "efficient_searches.pl"
                rename(join(directory, f), join(directory, new_name))


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
        "T1(a)": {
            "correct": 0,
            "to_manually_review": 0
        },
        "T1(b)": {
            "correct": 0,
            "to_manually_review": 0
        },
        "T1(c)": {
            "correct": 0,
            "to_manually_review": 0
        },
        "T2(a)": {
            "correct": 0,
            "to_manually_review": 0
        },
        "T2(b)": {
            "correct": 0,
            "to_manually_review": 0
        },
        "T2(c)": {
            "correct": 0,
            "to_manually_review": 0
        },
        "T2(d)": {
            "correct": 0,
            "to_manually_review": 0
        },
    }

    for test_case in test_cases:
        #if test_case in test_cases_with_syntax_errors:
            #test_result["to_manually_review"] += len(test_case["queries"])
            #continue

        correct: int = 0
        to_review: int = 0

        try:
            part: str = test_case["part"]
            cmd = test_case["cmd"].split(" ")
            cmd[2] = join(code_directory, cmd[2])
            cmd[-1] = join(tests_directory, cmd[-1])

            if len(cmd) == 5:
                cmd[3] = join(code_directory, cmd[3])

            queries: dict = test_case["queries"]

            if missing_files(code_directory=code_directory, cmd=cmd):
                test_cases_with_syntax_errors.append(test_case)
                test_result[part]["to_manually_review"] += len(queries)
                continue

            p = process(cmd)
            p.sendline("set_prolog_flag(answer_write_options,[quoted(true), portray(true), spacing(next_argument)]).")
            p.recv()

            for query, result in queries.items():
                p.sendline(query)
                output: str = str(p.recv(), "utf-8")

                if output.startswith("ERROR"):
                    if test_case not in test_cases_with_syntax_errors:
                        test_cases_with_syntax_errors.append(test_case)

                    test_result[part]["to_manually_review"] += 1
                    continue

                while output.startswith("Welcome to") or output.startswith("Warning") or "true." in output:
                    output = str(p.recv(), "utf-8")

                if check_output(cmd=cmd, query=query, expected_result=result, output=output):
                    correct += 1
                else:
                    to_review += 1
        except Exception as e:
            print("{}: got {}".format(cmd, repr(e)))
            print_exc()
            test_cases_with_syntax_errors.append(test_case)
            to_review = len(test_case["queries"]) - correct 
        
        test_result[part]["correct"] += correct
        test_result[part]["to_manually_review"] += to_review

    return test_result


def missing_files(code_directory: str, cmd: list) -> bool:
    to_check: list = []

    to_check.append(join(code_directory, basename(cmd[2])))
    to_check.append(join(code_directory, basename(cmd[3])))

    if len(cmd) == 5:
        to_check.append(join(code_directory, basename(cmd[4])))

    for f in to_check:
        if basename(f).startswith("test"):
            continue
        if not exists(f) or not isfile(f):
            print("The submission is missing {}".format(f))
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


if __name__ == "__main__":
    main()

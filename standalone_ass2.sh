#!/bin/bash

# This is to test a single submission.

SWIPL="swipl"

if ! which ${SWIPL} 1>/dev/null; then
    echo "${SWIPL} not found. Aborting..."
    exit -1
fi

if [ -z "${1}" ]; then
    echo "Usage: ${0} <assignment_code_directory_path>"
    exit -1
fi

./main.py -d ${1} -t tests2 -c test_cases_ass2.json -C marking_config_ass2.json SILENT=1 2>/dev/null

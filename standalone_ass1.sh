#!/bin/bash

# This is to test a single submission.

PIP3="python3-pip"
SWIPL="swipl"
PWNTOOLS="pwntools"

for PACKAGE in ${PIP} ${SWIPL}; do
    if ! which ${PACKAGE} 1>/dev/null; then
        echo "${PACKAGE} not found. Aborting..."
        exit -1
    fi
done

if ! pip3 list | grep -F ${PWNTOOLS} 1>/dev/null; then
    echo "${PWNTOOLS} not found. Aborting..."
    exit -1
fi

if [ -z "${1}" ]; then
    echo "Usage: ${0} <assignment_code_directory_path>"
    exit -1
fi

./main.py -d ${1} -t tests -c test_cases_ass1.json -C marking_config_ass1.json SILENT=1 2>/dev/null

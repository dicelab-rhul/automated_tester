#!/bin/bash

# This is to test a single submission.

: '
PIP3="pip3"
SWIPL="swipl"
PWNTOOLS="pwntools"
COLORAMA="colorama"

for PACKAGE in ${PIP} ${SWIPL}; do
    if ! which ${PACKAGE} 1>/dev/null; then
        echo "${PACKAGE} not found. Aborting..."
        exit -1
    fi
done

for PACKAGE in ${PWNTOOLS} ${COLORAMA}; do
    if ! ${PIP3} list 2>/dev/null | grep -F ${PACKAGE} 1>/dev/null; then
        echo "${PACKAGE} not installed (${PIP3} install ${PACKAGE}). Aborting..."
        exit -1
    fi
done
'

if [ -z "${1}" ]; then
    echo "Usage: ${0} <assignment_code_directory_path>"
    exit -1
fi

./main.py -d ${1} -t tests2 -c test_cases_ass2.json -C marking_config_ass2.json SILENT=1 2>/dev/null

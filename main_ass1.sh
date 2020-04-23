#!/bin/bash

# This is to test all the submissions in one go.

PIP3="pip3"
SWIPL="swipl"
PWNTOOLS="pwntools"
COLORAMA="colorama"

# Change this to your needs.
SUBMISSIONS_PARENT_DIRECTORY="assignment1"

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

chmod 700 main.py

for dir in $(ls ${SUBMISSIONS_PARENT_DIRECTORY}); do ./main.py -d ${SUBMISSIONS_PARENT_DIRECTORY}/${dir} -t tests -c test_cases_ass1.json -C marking_config_ass1.json SILENT=1 2>/dev/null; done

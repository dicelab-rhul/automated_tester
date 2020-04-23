#!/bin/bash

# This is to test all the submissions in one go.

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

chmod 700 main.py

for dir in $(ls assignment2); do ./main.py -d assignment2/${dir} -t tests2 -c test_cases_ass2.json -C marking_config_ass2.json SILENT=1 2>/dev/null; done

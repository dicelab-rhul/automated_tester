#!/bin/bash

# This is to test all the submissions in one go.

PIP3="python3-pip"
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
    if ! pip3 list 2>/dev/null | grep -F ${PACKAGE} 1>/dev/null; then
        echo "${PACKAGE} not installed (pip3 install ${PACKAGE}). Aborting..."
        exit -1
    fi
done

chmod 700 main.py

for dir in $(ls assignment2); do ./main.py -d assignment2/${dir} -t tests2 -c test_cases_ass2.json -C marking_config_ass2.json SILENT=1 2>/dev/null; done

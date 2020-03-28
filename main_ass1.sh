#!/bin/bash

# This is to test all the submissions in one go.

SWIPL="swipl"

if ! which ${SWIPL} 1>/dev/null; then
    echo "${SWIPL} not found. Aborting..."
    exit -1
fi

chmod 700 main.py

for dir in $(ls assignment1); do ./main.py -d assignment1/${dir} -t tests -c test_cases_ass1.json -C marking_config_ass1.json SILENT=1 2>/dev/null; done

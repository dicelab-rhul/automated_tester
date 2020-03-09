#!/bin/bash

for dir in $(ls assignment1); do ./main.py -d assignment1/${dir} -t tests -c test_cases.json SILENT=1 2>/dev/null; done
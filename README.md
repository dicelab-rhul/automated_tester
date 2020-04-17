# Prolog Coursework evaluator

## DISCLAIMER

- To any student stumbling upon this repo (good job BTW, it means you are just curious enough): nothing in here will replace the effort you need to put into the coursework. Not even the unpublished query results (which are not revealing BTW).

- The authors are not liable, if you copy-paste something from this repo into your code, and then fail the coursework.

- Certain relevant files are not shared on this repo.

## Support INFO

Supported: GNU/Linux and other unix Operating Systems.
MS Windows is currently not supported, because of the `pwntools` dependency.

## Dependencies

You may need to install the following (you may have to replace `apt`, depending on your OS):

```console
$ sudo apt install python3
$ sudo apt install swipl
$ pip3 install pwntools
...
```

## Run the script an all the submissions

For `assigment 1`: ensure the `assignment1` folder is in the same directory as `main_ass1.sh`.

```console
$ chmod 700 main_ass1.sh
$ ./main_ass1.sh
...
```

For better results, pipe the output into a file.

For `assigment 2`: follow the procedure for `assignment 1`, changing `main_ass1.sh` to `main_ass2.sh`, and `assignment1` to `assignment2`.

## Standalone run

For `assigment 1`: to run the tester on a single submission:

```console
$ chmod 700 standalone_ass1.sh
$ ./standalone_ass1.sh <path_to_the_submission_code_folder>
...
```

For better results, pipe the output into a file.

For `assigment 2`: follow the procedure for `assignment 1`, changing `standalone_ass1.sh` to `standalone_ass2.sh`.

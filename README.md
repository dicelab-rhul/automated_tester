# Support INFO

Supported: GNU/Linux and other unix Operating Systems.
MS Windows is currently not supported, because of the `pwntools` dependency.

# Dependencies

You may need to install the following (you may have to replace `apt`, depending on your OS):

```console
$ sudo apt install python3
$ sudo apt install swipl
$ pip3 install pwntools
```

# Run the script an all the submissions

For `assigment 1`: ensure the `assignment1` folder is in the same directory as `main_ass1.sh`.

```console
$ chmod 700 main_ass1.sh
$ ./main_ass1.sh
```

For better results, pipe the output into a file.

# Standalone run

For `assigment 1`: to run the tester on a single submission:

```console
$ chmod 700 standalone_ass1.sh
$ ./standalone_ass1.sh <path_to_the_submission_code_folder>
```

For better results, pipe the output into a file.

For `assigment 2`: follow the procedure for `assignment 1`, changing `standalone_ass1.sh` to `standalone_ass2.sh`.
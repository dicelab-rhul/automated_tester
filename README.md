# Support INFO

The system is meant for GNU/Linux and other unix operating systems.
MS Windows is currently not supported because of the `pwntools` dependency.

# Dependencies

You may need to install the following (you may have to replace `apt`, depending on your OS):

```console
$ sudo apt install python3
$ sudo apt install swipl
$ pip3 install pwntools
```

# Run the script an all the submissions

Be sure to put the extracted `assignment1` folder (download it from Slack) in the same directory as `main.sh`

```console
$ chmod 700 main.sh
$ ./main.sh
```

For better results, pipe the output into a file.

# Standalone run

To run the tester on a single submission:

```console
$ chmod 700 standalone.sh
$ ./standalone.sh <path_to_the_submission_code_folder>
```

For better results, pipe the output into a file.
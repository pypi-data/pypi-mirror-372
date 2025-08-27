# TuxParse
TuxParse, by [Linaro](https://www.linaro.org/), is a command line tool to parse build and boot log files.

# Installing TuxParse

To install tuxlava to your home directory at ~/.local/bin:

```shell
pip3 install -U --user -e .
```

# Options
```shell
usage: tuxparse [-h] [--log-file LOG_FILE] [--result-file RESULT_FILE] [--log-parser {boot_test,build,test}] [--unique] [--debug]

TuxParse, parse build, boot/test log files and print the output to the stdout.

options:
  -h, --help            show this help message and exit
  --log-file LOG_FILE   Log file to parser
  --result-file RESULT_FILE
                        Result JSON file to read and write too
  --log-parser {boot_test,build,test}
                        Which log parser to run, when boot_test or build log-file should be logs.txt or build.log, and for test it should be lava-logs.yaml
  --unique              make unique
  --debug               Display debug messages
```

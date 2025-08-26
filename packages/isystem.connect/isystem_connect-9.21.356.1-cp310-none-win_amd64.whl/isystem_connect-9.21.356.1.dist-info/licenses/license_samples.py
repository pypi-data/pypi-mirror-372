import os
import argparse


license_buffer: list


def argument_parser():
    usage = "Add/replace license in samples, with specified in license."
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('-d', '--path', dest='samples_path', action='store', required=True,
                        help='Path to python samples directory.')

    parser.add_argument('-l', '--license', dest='license_path', action='store', required=True,
                        help='Path to python sample license.')
    options = parser.parse_args()
    return options


def fix_sample(file_name: str):
    lines: list
    with open(file_name, 'r') as file:
        lines = file.readlines()
        index = 0

        # skip empty files such as __init__.py
        if not len(lines):
            return
        for line in lines:
            if not line.strip().startswith('#'):
                break
            index += 1

        # if license file does not end with empty line, add one
        if not license_buffer[-1].endswith('\n'):
            license_buffer.append('\n')

        # strip all empty newlines before start of text,
        # to keep the same format of license header across all samples.
        #
        # - start of file
        # - # Copyright text.
        # - empty line
        # - # script description.
        # Example:
        # ^ start of file
        # # This script is licensed under BSD License, see file LICENSE.txt.
        # #
        # # (c) TASKING Germany GmbH, 2022
        # <first empty line>
        # # This script demonstrates, ...

        while lines[index].strip() == '':
            index += 1
        lines = lines[index:]
        lines = license_buffer + ['\n'] + lines
    with open(file_name, 'w') as file:
        file.writelines(lines)


def walk_dir(path: str):
    count = 0
    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith('.py'):
                fix_sample(os.path.join(root, name))
                count += 1
    return count


if __name__ == '__main__':
    opts = argument_parser()
    with open(opts.license_path) as lcs:
        license_buffer = lcs.readlines()

    number_of_files = walk_dir(opts.samples_path)
    print(f'fixed {number_of_files}')

# Notes:
# Is file LICENSE.txt visible on the docs page?

import argparse
import json
import os
import shutil
import subprocess


def create_compile_commands_json(cmd_args, append):
    json_file = 'compile_commands.json'
    current_dir = os.getcwd()
    compiler_cmd = cmd_args[0]
    compiler_path = shutil.which(compiler_cmd)
    full_compiler_cmd = compiler_path
    filename = cmd_args[-1]

    out = dict()
    out['file'] = os.path.join(current_dir, filename)
    out['command'] = os.path.join(full_compiler_cmd, " ".join(cmd_args))
    out['directory'] = current_dir
    # Check if output binary file has been defined
    o = '-o'
    if o in cmd_args:
        idx = cmd_args.index(o)
        obj_file = cmd_args[idx+1]
        out['output'] = os.path.join(current_dir, obj_file)
    else:
        out['output'] = os.path.join(current_dir, 'a.out')

    dump = []
    if append:
        try:
            with open(json_file, 'r') as file:
                dump.append(json.load(file)[0])
        except FileNotFoundError:
            # File doesn't exist, so we'll just pass silently
            pass
        except json.JSONDecodeError:
            # In case the file exists but isn't valid JSON
            print(f"Error: {json_file} is not a valid JSON file.")
            exit(1)

    with open(json_file, 'w') as file:
        json.dump(dump, file, indent=2)
        file.write('\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Simple build utility for C/C++',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("cmd", type=str, help="Compiler command. Example: \"g++ main.cpp\"")
    parser.add_argument(
            "-c",
            dest="compile_commands",
            action="store_true",
            default=True,
            help="Create compile_commands.json file for build",
        )
    parser.add_argument(
            "-ca",
            dest="append",
            action="store_true",
            default=False,
            help="Append output to existing compile_commands.json",
        )
    parser.add_argument(
            "-v",
            dest="verbose",
            action="store_true",
            default=False,
            help="Verbose mode. Outputs the stdout result of the build command",
        )
    args = parser.parse_args()

    cmd_args = args.cmd.split()
    result = subprocess.run(cmd_args, capture_output=True, text=True)

    if not result.returncode == 0:
        if args.verbose:
            print(result.stderr)
        exit(result.returncode)
    if args.verbose:
        if result.stdout:  # Don't print empty string (contains extra line feed)
            print(result.stdout)

    if args.compile_commands:
        create_compile_commands_json(cmd_args, args.append)

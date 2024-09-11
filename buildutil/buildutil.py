import argparse
import json
import os
import shutil
import subprocess


def create_compile_commands_json(cmd_args):
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
    dump.insert(0, out)
    with open(json_file, 'w') as file:
        json.dump(dump, file, indent=2)
        file.write('\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Simple build utility for C/C++',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("cmd", type=str, help="Compiler command")
    parser.add_argument(
            "-c",
            dest="compile_commands",
            action="store_true",
            default=True,
            help="Create compile_commands.json file for build",
        )
    args = parser.parse_args()

    cmd_args = args.cmd.split()
    result = subprocess.run(cmd_args, capture_output=True, text=True)

    if not result.returncode == 0:
        print(result.stderr)
        exit(result.returncode)
    print(result.stdout)

    if args.compile_commands:
        create_compile_commands_json(cmd_args)

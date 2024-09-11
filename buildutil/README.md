# Buildtool

A simple build helper tool for C/C++. Currently, it only generates a <i>compile_commands.json</i> file, which is used by various editors that support clangd LSP. This tool is useful when you need to generate a <i>compile_commands.json</i> file for building a single C/C++ file, without the need to set up a complex project, such as one using CMake.

### Usage example
Run
```
python3 buildutil.py -v "g++ -o test -std=c++20 main.cpp"
```
Result
```
[
  {
    "file": "/Users/mattilaa/main.cpp",
    "command": "/usr/bin/g++/g++ -o test -std=c++20 main.cpp",
    "directory": "/Users/mattilaa",
    "output": "/Users/mattilaa/test"
  }
]

```

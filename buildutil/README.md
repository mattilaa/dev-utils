# Buildtool

A simple build helper tool for C/C++. Currently, it only generates a compile_commands.json file, which is used by various editors that support clangd LSP. This tool is useful when you need to generate a compile_commands.json file for building a single C/C++ file, without the need to set up a complex project, such as one using CMake.

### Usage example
```
python3 buildutil.py -v "g++ -o ma -std=c++20 main.cpp"
```

# Cmake Project Creator

Simple helper script for creating Cmake projects easily. It creates a file structure to the desired location. It also fetches GoogleTest framework for unit testing.
```
.
├── CMakeLists.txt
├── README.rd
├── include
│   └── hello.h
├── src
│   └── main.cpp
└── tests
    └── test.cpp
```
### Usage example
```
python3 cmake_project_creator.py testproject --path=~/projects/testproject --std=c++17
```
Creates a Cmake project using C++17. Root path for the project is ~/projects/testproject
```
python3 cmake_project_creator.py testproject --path=~/projects/testproject --std=c++17 --enable-asan --add-benchmark
```
Creates a Cmake project with Google Benchmark and enabling address sanitizer. Benchmark example snippet is located in ./benchmarks

### Dependencies
```
cmake
python3.7 (at least)
```

### Building
```
mkdir build
cd build
cmake ..
make
```

## Have fun!

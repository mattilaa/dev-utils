#!/usr/bin/env python3

import argparse
import os


class CmakeProjectCreator:
    def __init__(self, args):
        self.params = args

        # Strip c++ prefix from standard
        self.params.std = args.std.split('++')[-1]

        # Directory structure
        self.dirs = dict()
        self.dirs['project_path'] = os.path.expanduser(args.path)
        self.dirs['include_dir'] = os.path.join(args.path, "include")
        self.dirs['src_dir'] = os.path.join(args.path, "src")
        self.dirs['tests_dir'] = os.path.join(args.path, "tests")
        self.dirs['benchmarks_dir'] = os.path.join(args.path, "benchmarks")

    def create_project(self):
        """ Create project directories and file contents """

        self.__create_project_dirs()
        self.__create_contents()
        print(self.params)

    def __create_project_dirs(self):
        os.makedirs(self.dirs['include_dir'], exist_ok=True)
        os.makedirs(self.dirs['src_dir'], exist_ok=True)
        os.makedirs(self.dirs['tests_dir'], exist_ok=True)
        if self.params.benchmark is True:
            os.makedirs(self.dirs['benchmarks_dir'], exist_ok=True)

    def __create_contents(self):
        # Create full file paths
        example_h = (
            os.path.join(self.dirs['include_dir'], self.params.project_name +
                         ".h")
        )
        example_cpp = (
            os.path.join(self.dirs['src_dir'], self.params.project_name +
                         ".cpp")
        )
        main_cpp = (
            os.path.join(self.dirs['src_dir'], "main.cpp")
        )
        test_cpp = (
            os.path.join(self.dirs['tests_dir'], "test_" +
                         self.params.project_name + ".cpp")
        )
        benchmark_cpp = (
            os.path.join(self.dirs['benchmarks_dir'], "benchmark_" +
                         self.params.project_name + ".cpp")
        )
        cmakelists = (
            os.path.join(self.dirs['project_path'], "CMakeLists.txt")
        )
        clang_format = (
            os.path.join(self.dirs['project_path'], ".clang_format")
        )
        readme = (
            os.path.join(self.dirs['project_path'], "README.md")
        )

        contents = dict()

        # Create example.h
        contents[example_h] = self.__create_exmaple_h()

        # Create main if project is not library
        if not self.params.lib:
            contents[main_cpp] = self.__create_main_cpp()

        # Create example.cpp
        contents[example_cpp] = self.__create_example_cpp()

        # Create test.cpp
        contents[test_cpp] = self.__create_test_cpp()

        # Create benchmark.cpp
        if self.params.benchmark is True:
            contents[benchmark_cpp] = self.__create_benchmark_cpp()

        # Create CMakeLists.txt
        contents[cmakelists] = self.__create_cmakelists()

        # Create .clang_format
        if self.params.create_format is True:
            contents[clang_format] = self.__create_format()

        # Create README.rd
        contents[readme] = self.__create_readme()

        # Write files
        for path, content in contents.items():
            with open(path, "w") as file:
                file.write(content)
        print(f"""CMake project '{self.params.project_name}' \
 created successfully in '{self.params.path}'!""")

    # Private methods
    def __create_exmaple_h(self):
        upper_project_name = self.params.project_name.upper()
        content = f"""#ifndef {upper_project_name}_H
#define {upper_project_name}_H

#include <iostream>

namespace example
{{
    int add(int a, int b);
}}

#endif
"""
        return content

    def __create_example_cpp(self):
        content = f"""#include "{self.params.project_name}.h"
namespace example
{{
    int add(int a, int b)
    {{
        return a + b;
    }}
}}
"""
        return content

    def __create_main_cpp(self):
        content = f"""#include "{self.params.project_name}.h"

int main(int argc, char* argv [])
{{
    std::cout << "Hello result: " << example::add(2, 4) << "\\n";
}}
"""
        return content

    def __create_test_cpp(self):
        content = f"""#include <gtest/gtest.h>
#include "{self.params.project_name}.h"

TEST(HelloTest, BasicAssertions)
{{
    // Expect two strings not to be equal.
    EXPECT_STRNE("hello", "world");
    // Expect equality.
    EXPECT_EQ(7 * 6, 42);
}}

int main(int argc, char **argv)
{{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}}
"""
        return content

    def __create_benchmark_cpp(self):
        content = """#include <benchmark/benchmark.h>
#include <vector>
#include <algorithm>

// Example function to benchmark
void ExampleFunction(std::vector<int>& data)
{{
    std::sort(data.begin(), data.end());
}}

// Benchmark for the example function
static void BM_ExampleFunction(benchmark::State& state)
{{
    // Setup code
    std::vector<int> data(state.range(0));
    std::generate(data.begin(), data.end(), std::rand);

    // Run the benchmark
    for(auto _ : state)
    {{
        // We need to make a copy of the data for each iteration
        std::vector<int> data_copy = data;
        ExampleFunction(data_copy);
    }}

    // Set the items processed per iteration
    state.SetItemsProcessed(state.iterations() * state.range(0));
}}

// Register the function as a benchmark
BENCHMARK(BM_ExampleFunction)->Range(8, 8<<10);

BENCHMARK_MAIN();
"""
        return content

    def __create_cmakelists(self):
        content = f"""cmake_minimum_required(VERSION 3.12)
project({self.params.project_name})

# Create compile_commands.json in build directory
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Set C++ standard
set(CMAKE_CXX_STANDARD {self.params.std})
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Add include directory
include_directories(include)
"""

        if self.params.lib:
            content = content + f"""
# Library target
add_library({self.params.project_name}
    src/{self.params.project_name}.cpp
)
"""
        else:
            content = content + f"""
# Executable target
add_executable({self.params.project_name}
    src/main.cpp
    include/{self.params.project_name}.h
    src/{self.params.project_name}.cpp
)
"""

        content = content + f"""
# Fetch GoogleTest
include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/tags/release-1.12.1.zip
)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

# Enable testing
enable_testing()

# Add test executable
add_executable(test_{self.params.project_name}
    tests/test_{self.params.project_name}.cpp
)

# Link test executable against gtest & gtest_main
target_link_libraries(test_{self.params.project_name}
    gtest_main
)

include(GoogleTest)
gtest_discover_tests(test_{self.params.project_name})
"""

        if self.params.asan is True:
            content = content + """
# Enable AddressSanitizer
if (CMAKE_CXX_COMPILER_ID MATCHES "Clang" OR CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    set(ASAN_FLAGS "-fsanitize=address -fno-omit-frame-pointer")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${ASAN_FLAGS}")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${ASAN_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${ASAN_FLAGS}")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} ${ASAN_FLAGS}")
endif()
"""

        if self.params.benchmark is True:
            content = content + f"""
# Fetch Google Benchmark
FetchContent_Declare(
    googlebenchmark
    URL https://github.com/google/benchmark/archive/refs/tags/v1.6.1.zip
)
FetchContent_MakeAvailable(googlebenchmark)

# Add benchmark executable
add_executable(
    benchmark_{self.params.project_name}
    {self.dirs['benchmarks_dir']}/benchmark_{self.params.project_name}.cpp
)

# Link benchmark executable against benchmark library
target_link_libraries(
    benchmark_{self.params.project_name} benchmark::benchmark
)
"""
        return content

    def __create_format(self):
        content = """Language:        Cpp
BasedOnStyle:    Google
IndentWidth:     4
TabWidth:        4
UseTab:          Never
BreakBeforeBraces: Allman
AllowShortIfStatementsOnASingleLine: false
ColumnLimit:     80
PointerAlignment: Left
SpaceAfterControlStatementKeyword: true
IndentPPDirectives: AfterHash
ConstructorInitializerIndentWidth: 2
ContinuationIndentWidth: 2
SpaceBeforeParens: Custom
SpaceBeforeParensOptions:
  AfterControlStatements: false
"""
        return content

    def __create_readme(self):
        content = f"""{self.params.project_name}

## About
Add description here
"""
        return content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Create a simple CMake project with GoogleTest setup.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("project_name", type=str, help="The name of the project")
    parser.add_argument(
        "--std",
        type=str,
        choices=["c++11", "c++14", "c++17", "c++20"],
        help="The C++ standard version (c++11, c++14, c++17, c++20)",
    )
    parser.add_argument(
        "--lib",
        dest="lib",
        action="store_true",
        help="Create library project instead of program project",
    )
    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help="The root path where the project will be created",
    )
    parser.add_argument(
        "--add-benchmark",
        dest="benchmark",
        action="store_true",
        help="Add Google Benchmark into the project",
    )
    parser.add_argument(
        "--enable-asan",
        dest="asan",
        action="store_true",
        help="Enable address sanitizer",
    )
    parser.add_argument(
        "--create-formatfile",
        dest="create_format",
        action="store_true",
        help="Create .clang-format file",
    )

    args = parser.parse_args()

    cr = CmakeProjectCreator(args)
    cr.create_project()

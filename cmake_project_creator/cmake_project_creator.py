#!/usr/bin/env python3

import argparse
import os


def create_cmake_project(
        project_path,
        project_name,
        cpp_standard,
        is_lib,
        add_benchmark,
        enable_asan,
        create_format):
    # Expand the user home directory symbol (~) to the full path
    project_path = os.path.expanduser(project_path)
    project_dir = os.path.join(project_path)
    upper_project_name = project_name.upper()

    # Directory structure
    include_dir = os.path.join(project_dir, "include")
    src_dir = os.path.join(project_dir, "src")
    tests_dir = os.path.join(project_dir, "tests")
    benchmarks_dir = os.path.join(project_dir, "benchmarks")

    # Create directories
    os.makedirs(include_dir, exist_ok=True)
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)
    if add_benchmark:
        os.makedirs(benchmarks_dir, exist_ok=True)

    # Create example header in include directory
    hello_h_content = f"""#ifndef {upper_project_name}_H
#define {upper_project_name}_H

#include <iostream>

namespace example
{{
    int add(int a, int b);
}}

#endif
"""

    with open(os.path.join(include_dir, project_name + ".h"), "w") as file:
        file.write(hello_h_content)

    if is_lib:
        # Create library cpp in src directory
        mylib_cpp_content = """
namespace example
{{
    int add(int a, int b)
    {{
        return a + b;
    }}
}}
"""

        with open(os.path.join(src_dir, project_name + ".cpp"), "w") as file:
            file.write(mylib_cpp_content)

    else:
        # Create main.cpp in src directory
        main_cpp_content = f"""#include "{project_name}.h"

int main(int argc, char* argv [])
{{
    std::cout << "Hello result: " << example::add(2, 4) << "\\n";
}}
"""
        with open(os.path.join(src_dir, "main.cpp"), "w") as file:
            file.write(main_cpp_content)
        example_cpp_content = f"""#include "{project_name}.h"

namespace example
{{
    int add(int a, int b)
    {{
        return a * b;
    }}
}}
"""

        with open(os.path.join(src_dir, project_name + ".cpp"), "w") as file:
            file.write(example_cpp_content)

    # Create test.cpp in tests directory
    test_cpp_content = f"""#include <gtest/gtest.h>
#include "{project_name}.h"

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

    with open(os.path.join(tests_dir, "test.cpp"), "w") as file:
        file.write(test_cpp_content)

    if add_benchmark:
        benchmark_cpp_content = """#include <benchmark/benchmark.h>
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

        with open(os.path.join(benchmarks_dir, "benchmark.cpp"), "w") as file:
            file.write(benchmark_cpp_content)

    # Create CMakeLists.txt in the root directory
    cmake_lists_content = f"""cmake_minimum_required(VERSION 3.12)
project({project_name})

# Create compile_commands.json in build directory
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Set C++ standard
set(CMAKE_CXX_STANDARD {cpp_standard})
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Add include directory
include_directories(include)
"""

    if is_lib:
        cmake_lists_content = cmake_lists_content + f"""
# Library target
add_library({project_name} src/{project_name}.cpp)
"""
    else:
        cmake_lists_content = cmake_lists_content + f"""
# Executable target
add_executable({project_name} src/main.cpp include/{project_name}.h src/{project_name}.cpp)
"""

    cmake_lists_content = cmake_lists_content + f"""
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
add_executable(
  test_{project_name}
  tests/test.cpp
)

# Link test executable against gtest & gtest_main
target_link_libraries(
  test_{project_name} gtest_main)

include(GoogleTest)
gtest_discover_tests(test_{project_name})
"""

    if enable_asan:
        cmake_lists_content = cmake_lists_content + """
# Enable AddressSanitizer
if (CMAKE_CXX_COMPILER_ID MATCHES "Clang" OR CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    set(ASAN_FLAGS "-fsanitize=address -fno-omit-frame-pointer")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${ASAN_FLAGS}")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${ASAN_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${ASAN_FLAGS}")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} ${ASAN_FLAGS}")
endif()
"""

    if add_benchmark:
        cmake_lists_content = cmake_lists_content + f"""
# Fetch Google Benchmark
FetchContent_Declare(
  googlebenchmark
  URL https://github.com/google/benchmark/archive/refs/tags/v1.6.1.zip
)
FetchContent_MakeAvailable(googlebenchmark)

# Add benchmark executable
add_executable(
  benchmark_{project_name}
  benchmarks/benchmark.cpp
)

# Link benchmark executable against benchmark library
target_link_libraries(
  benchmark_{project_name} benchmark::benchmark
)
"""

    with open(os.path.join(project_dir, "CMakeLists.txt"), "w") as file:
        file.write(cmake_lists_content)

    if create_format:
        clang_format_contents = """Language:        Cpp
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

        with open(os.path.join(project_dir, ".clang-format"), "w") as file:
            file.write(clang_format_contents)

    # Create README.md in the root directory
    readme_content = """Empty project"""
    with open(os.path.join(project_dir, "README.rd"), "w") as file:
        file.write(readme_content)

    print(f"CMake project '{project_name}' created successfully in '{project_path}'!")


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

    # Extract the C++ standard version number from the input string
    # (e.g., "c++17" -> "17")
    cpp_standard = args.std.split('++')[-1]

    create_cmake_project(
        args.path,
        args.project_name,
        cpp_standard,
        args.lib,
        args.benchmark,
        args.asan,
        args.create_format,
    )

import os
import argparse
import subprocess

def create_cmake_project(project_path, project_name, cpp_standard, enable_asan):
    # Expand the user home directory symbol (~) to the full path
    project_path = os.path.expanduser(project_path)
    project_dir = os.path.join(project_path)

    # Directory structure
    include_dir = os.path.join(project_dir, "include")
    src_dir = os.path.join(project_dir, "src")
    tests_dir = os.path.join(project_dir, "tests")

    # Create directories
    os.makedirs(include_dir, exist_ok=True)
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)

    # Create hello.h in include directory
    hello_h_content = """
#ifndef HELLO_H
#define HELLO_H

#include <iostream>

static void hello()
{
    std::cout << "Hello, World!\\n";
}

#endif // HELLO_H
    """
    with open(os.path.join(include_dir, "hello.h"), "w") as file:
        file.write(hello_h_content)

    # Create main.cpp in src directory
    main_cpp_content = """
#include "hello.h"

int main(int argc, char* argv [])
{
    hello();
}
    """
    with open(os.path.join(src_dir, "main.cpp"), "w") as file:
        file.write(main_cpp_content)

    # Create test.cpp in tests directory
    test_cpp_content = """
#include <gtest/gtest.h>
#include "hello.h"

TEST(HelloTest, BasicAssertions) {
    // Expect two strings not to be equal.
    EXPECT_STRNE("hello", "world");
    // Expect equality.
    EXPECT_EQ(7 * 6, 42);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
    """
    with open(os.path.join(tests_dir, "test.cpp"), "w") as file:
        file.write(test_cpp_content)

    # Create CMakeLists.txt in the root directory
    cmake_lists_content = f"""
cmake_minimum_required(VERSION 3.10)
project({project_name})

# Create compile_commands.json in build directory
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Set C++ standard
set(CMAKE_CXX_STANDARD {cpp_standard})
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Add include directory
include_directories(include)

# Add the executable
add_executable({project_name} src/main.cpp)

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
    with open(os.path.join(project_dir, "CMakeLists.txt"), "w") as file:
        file.write(cmake_lists_content)

    # Create README.md in the root directory
    readme_content = """
Empty project
    """
    with open(os.path.join(project_dir, "README.rd"), "w") as file:
        file.write(readme_content)

    print(f"CMake project '{project_name}' created successfully in '{project_path}'!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Create a simple CMake project with GoogleTest setup.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('project_name', type=str, help='The name of the project')
    parser.add_argument('--std', type=str, choices=['c++11', 'c++14', 'c++17', 'c++20'], default='c++11', help='The C++ standard version (c++11, c++14, c++17, c++20)')
    parser.add_argument('--path', type=str, default='.', help='The root path where the project will be created')
    parser.add_argument('--enable-asan', dest='asan', action='store_true', help="Enable address sanitizer.")

    args = parser.parse_args()

    # Extract the C++ standard version number from the input string (e.g., "c++17" -> "17")
    cpp_standard = args.std.split('++')[-1]

    create_cmake_project(args.path, args.project_name, cpp_standard, args.asan)


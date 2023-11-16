cmake_minimum_required(VERSION 3.10)
project("JennyStatsGen" VERSION 1.0 LANGUAGES CXX)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

###
# Qt 
###
# Ensure the QT5 package is installed
find_package(Qt5 COMPONENTS Widgets REQUIRED)

# For charts and basic plots
find_package(Qt5 COMPONENTS Charts REQUIRED)

# Tell CMake to run uic when necessary
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOUIC_SEARCH_PATHS src/gui/qt-ui-components)

# Include the directory where the generated UI header files are located
include_directories(${CMAKE_CURRENT_BINARY_DIR}/JennyStatsGen_autogen/include)

# If you have .cpp and .h files under src/gui/qt-ui-components
file(GLOB GUI_SOURCES "src/gui/qt-ui-components/*.cpp" "src/gui/qt-ui-components/*.h")

# If you're using .ui files
file(GLOB UI_FILES "src/gui/qt-ui-components/*.ui")

# Include directories for header files
include_directories(${PROJECT_SOURCE_DIR}/include)

# Source files
set(SOURCES
    src/main.cpp
    # TODO other .cpp files
)
###
# Security improvements:
###
# -Wall -Wextra -Werror: Turns on most compiler warnings and treats them as errors.
# -Wformat -Wformat-security: Warns about format string vulnerabilities.
# -fstack-protector-strong: Adds stack protection to prevent stack overflows.
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    add_compile_options(-Wall -Wextra -Werror -Wformat -Wformat-security -fstack-protector-strong)
elseif(MSVC)
    add_compile_options(/W4 /WX /GS)
endif()
# Automated code security analysis 
# Static code analysis courtesy of cppcheck
find_program(CPPCHECK cppcheck)
if(CPPCHECK)
    add_custom_target(
        cppcheck
        COMMAND ${CPPCHECK}
        --enable=warning,performance,portability
        --std=c++17
        --verbose
        --error-exitcode=1
        --language=c++
        ${PROJECT_SOURCE_DIR}/src
        ${PROJECT_SOURCE_DIR}/include
    )
endif()
# Supplementary code analysis to cppcheck using clang-tidy
# set(CMAKE_CXX_CLANG_TIDY clang-tidy;--checks=*;--warnings-as-errors=*;)
# set(CMAKE_CXX_CLANG_TIDY clang-tidy;--checks=*;)
set(CMAKE_CXX_CLANG_TIDY clang-tidy;--checks=cppcoreguidelines-*,bugprone-*,performance-*;)

# ASan: AddressSanitizer. Enabled by default. To override run cmake with `cmake -DENABLE_ASAN=OFF ..`
option(ENABLE_ASAN "Enable Address Sanitizer" ON)
if(ENABLE_ASAN)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address")
    set(CMAKE_LINKER_FLAGS "${CMAKE_LINKER_FLAGS} -fsanitize=address")
endif()

# UBSan: UndefinedBehaviorSanitizer. Enabled by default. To override run cmake with `cmake -DENABLE_UBSAN=OFF ..`
option(ENABLE_UBSAN "Enable Undefined Behavior Sanitizer" ON)
if(ENABLE_UBSAN)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=undefined")
    set(CMAKE_LINKER_FLAGS "${CMAKE_LINKER_FLAGS} -fsanitize=undefined")
endif()

# TSan: ThreadSanitizer. Enabled by default. To override run cmake with `cmake -DENABLE_TSAN=OFF ..`
option(ENABLE_TSAN "Enable Thread Sanitizer" ON)
if(ENABLE_TSAN)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=thread")
    set(CMAKE_LINKER_FLAGS "${CMAKE_LINKER_FLAGS} -fsanitize=thread")
endif()

###
# Executable
###
add_executable(${PROJECT_NAME} ${SOURCES} ${GUI_SOURCES} ${UI_FILES})

target_link_libraries(${PROJECT_NAME} Qt5::Widgets)
target_link_libraries(${PROJECT_NAME} Qt5::Charts)

#!/bin/bash
# Run cppcheck
cppcheck --enable=warning,performance,portability --error-exitcode=1 --language=c++ --std=c++17 /app/src /app/include && \
# Disable AdressSanitizer and ThreadSanitizer
cmake -S . -B build -DENABLE_ASAN=OFF -DENABLE_TSAN=OFF && \
make -C build

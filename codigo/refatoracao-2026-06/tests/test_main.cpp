#include "test_framework.h"

std::vector<TestCase> g_tests;

int main() {
    int passed = 0;
    int failed = 0;
    
    std::cout << "Running " << g_tests.size() << " tests..." << std::endl;
    
    for (const auto& test : g_tests) {
        std::cout << "Running test: " << test.name << "..." << std::endl;
        try {
            test.func();
            passed++;
            std::cout << "  [OK]" << std::endl;
        } catch (const std::exception& e) {
            failed++;
        }
    }
    
    std::cout << "\nTest Results: " << passed << " passed, " << failed << " failed." << std::endl;
    
    return failed == 0 ? 0 : 1;
}

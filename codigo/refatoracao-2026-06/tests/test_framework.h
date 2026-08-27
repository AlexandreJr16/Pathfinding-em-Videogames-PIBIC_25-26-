#pragma once
#include <iostream>
#include <vector>
#include <string>
#include <functional>
#include <stdexcept>

struct TestCase {
    std::string name;
    std::function<void()> func;
};

extern std::vector<TestCase> g_tests;

#define TEST_CASE(name) \
    void test_##name(); \
    struct Register_##name { \
        Register_##name() { \
            g_tests.push_back({#name, test_##name}); \
        } \
    } register_##name; \
    void test_##name()

#define EXPECT_EQ(val1, val2) \
    if ((val1) != (val2)) { \
        std::cerr << "  [FAIL] " << __FILE__ << ":" << __LINE__ \
                  << ": Expected " << (val1) << " to equal " << (val2) << std::endl; \
        throw std::runtime_error("Test failed"); \
    }

#define EXPECT_TRUE(cond) \
    if (!(cond)) { \
        std::cerr << "  [FAIL] " << __FILE__ << ":" << __LINE__ \
                  << ": Expected true, got false" << std::endl; \
        throw std::runtime_error("Test failed"); \
    }

#include "test_framework.h"
#include "../src/heuristics.h"

TEST_CASE(heuristicaManhattan_basic) {
    std::pair<int, int> start = {0, 0};
    std::pair<int, int> goal = {3, 4};
    int dist = heuristicaManhattan(start, goal);
    EXPECT_EQ(dist, 7);
}

TEST_CASE(heuristicaZero_returns_zero) {
    std::pair<int, int> start = {10, 5};
    std::pair<int, int> goal = {3, 4};
    int dist = heuristicaZero(start, goal);
    EXPECT_EQ(dist, 0);
}

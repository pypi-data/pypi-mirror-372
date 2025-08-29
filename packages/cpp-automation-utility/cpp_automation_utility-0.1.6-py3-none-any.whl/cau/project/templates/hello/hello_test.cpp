#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <hello.hpp>

using ::testing::StrEq;

TEST(HelloWorld, IsCorrect)
{
    auto expected = std::string{"Hello, World!"};
    auto result = HelloWorld();

    ASSERT_THAT(result, StrEq(expected));
}

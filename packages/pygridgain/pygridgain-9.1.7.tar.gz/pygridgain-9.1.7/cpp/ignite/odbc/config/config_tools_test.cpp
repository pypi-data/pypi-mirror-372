/*
 *  Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */

#include "config_tools.h"
#include "ignite/odbc/common_types.h"

#include <gtest/gtest.h>

using namespace ignite;

/**
 * Test suite.
 */
class config_tools_test : public ::testing::Test {};

TEST_F(config_tools_test, parse_address_basic) {
    auto test_parse_address = [](const std::vector<end_point> &exp, std::string_view in) {
        auto res = parse_address(in);
        ASSERT_EQ(exp.size(), res.size());

        for (size_t i = 0; i < exp.size(); ++i) {
            EXPECT_EQ(exp[i], res[i]) << "Vectors differ at index " << i;
        }
    };

    test_parse_address({{"127.0.0.1", 10800}}, "127.0.0.1");
    test_parse_address({{"127.0.0.1", 10800}, {"127.0.0.1", 10800}}, "127.0.0.1,127.0.0.1");
    test_parse_address({{"127.0.0.1", 42}}, "127.0.0.1:42");

    test_parse_address(
        {{"127.0.0.1", 42}, {"localhost", 1550}, {"0.0.0.0", 10800}}, "127.0.0.1:42, localhost:1550,0.0.0.0    ");

    test_parse_address({}, "");
    test_parse_address({}, ",,,");
    test_parse_address({}, ",,,");
    test_parse_address({{"127.0.0.1", 10800}}, ",,,,127.0.0.1,,,,");
}

TEST_F(config_tools_test, normalize_argument_string_basic) {
    auto test_normalize_argument_string = [](std::string_view exp, std::string_view in) {
        EXPECT_EQ(normalize_argument_string(in), exp);
    };

    test_normalize_argument_string("", "");
    test_normalize_argument_string("abc", "abc");
    test_normalize_argument_string("abc", "Abc");
    test_normalize_argument_string("abc", "ABC");
    test_normalize_argument_string("a b c", " A B C ");
}

TEST_F(config_tools_test, parse_connection_string_basic) {
    auto test_parse_connection_string = [](const config_map &exp, std::string_view in) {
        EXPECT_EQ(parse_connection_string(in), exp);
    };

    test_parse_connection_string({{"key1", "value1"}, {"key2", "value2"}}, "key1=value1;key2 = value2;");

    test_parse_connection_string({}, "");
    test_parse_connection_string({}, ";;");

    test_parse_connection_string({{"k1", "v1"}}, "k1=v1;k1=v2;k1=v3");
}

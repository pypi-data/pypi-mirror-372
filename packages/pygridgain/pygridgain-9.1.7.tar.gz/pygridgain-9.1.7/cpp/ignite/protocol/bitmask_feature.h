/*
 *  Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */

#pragma once

#include "ignite/protocol/bitset_span.h"

#include <vector>
#include <cstddef>

namespace ignite::protocol {

/**
 * Protocol bitmask features.
 */
enum class bitmask_feature {
    /** Qualified name table requests. */
    TABLE_REQS_USE_QUALIFIED_NAME = 2,
};

/**
 * Get all supported bitmask features in binary form.
 *
 * @return Return all supported bitmask features in binary form.
 */
inline std::vector<std::byte> all_supported_bitmask_features() {
    std::vector<std::byte> res(1, std::byte{0});

    bitset_span span(res.data(), res.size());
    span.set(static_cast<std::size_t>(bitmask_feature::TABLE_REQS_USE_QUALIFIED_NAME));

    return res;
}

} // namespace ignite::protocol

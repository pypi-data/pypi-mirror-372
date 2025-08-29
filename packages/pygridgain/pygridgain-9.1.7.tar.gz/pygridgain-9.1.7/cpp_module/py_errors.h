/*
 *  Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */

#pragma once

#include "py_object.h"

#include "ignite/common/ignite_error.h"

/**
 * Convert C++ error to a Python IgniteError.
 *
 * @param err C++ error.
 * @return Python object for the error.
 */
py_object py_get_ignite_error(const ignite::ignite_error &err);

/**
 * Convert C++ error to a Python IgniteError and set it as a current error.
 *
 * @param err C++ error to set.
 */
void py_set_ignite_error(const ignite::ignite_error &err);

/**
 * Create a Python IgniteError and set it as a current error.
 *
 * @param err Error message.
 */
inline void py_set_ignite_error(const std::string &err) {
    py_set_ignite_error(ignite::ignite_error(err));
}
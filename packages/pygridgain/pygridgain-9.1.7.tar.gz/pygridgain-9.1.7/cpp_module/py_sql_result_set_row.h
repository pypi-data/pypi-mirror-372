/*
 * Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */


#pragma once

#include "ignite/protocol/reader.h"

#include <Python.h>


/**
 * Create a new instance of _PySqlResultSetRow python class.
 *
 * @param row_data Row data.
 * @param meta Row meta.
 * @return A new result set row class instance.
 */
PyObject* make_py_sql_result_set_row(ignite::bytes_view row_data, const std::vector<ignite::ignite_type> &meta);

/**
 * Prepare _PySqlResultSetRow type for registration.
 */
int prepare_py_sql_result_set_row_type();

/**
 * Register _PySqlResultSetRow type within module.
 */
int register_py_sql_result_set_row_type(PyObject* mod);
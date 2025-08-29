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
 * Create a new instance of _PySqlResultSet python class.
 *
 * @param reader A reader to read the result set data.
 * @return A new result set class instance.
 */
PyObject* make_py_sql_result_set(ignite::protocol::reader &reader);

/**
 * Prepare _PySqlResultSet type for registration.
 */
int prepare_py_sql_result_set_type();

/**
 * Register _PySqlResultSet type within module.
 */
int register_py_sql_result_set_type(PyObject* mod);
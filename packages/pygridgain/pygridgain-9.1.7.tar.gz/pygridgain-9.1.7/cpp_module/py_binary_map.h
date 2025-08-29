/*
 * Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */


#pragma once

#include <string>

#include <Python.h>


/**
 * Create a new instance of PyBinaryMap python class.
 *
 * @param full_table_name Table name.
 * @param table_id Table ID.
 * @return A new connection class instance.
 */
PyObject* make_py_binary_map(std::string full_table_name, std::int64_t table_id);

/**
 * Prepare PyBinaryMap type for registration.
 */
int prepare_py_binary_map_type();

/**
 * Register PyBinaryMap type within module.
 */
int register_py_binary_map_type(PyObject* mod);
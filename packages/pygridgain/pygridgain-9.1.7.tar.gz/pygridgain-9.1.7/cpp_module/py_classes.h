/*
 *  Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */

#pragma once

#include <Python.h>

/**
 * Get pygridgain.aio_connection.HandshakeResponse class.
 *
 * @return Python class instance. The object reference counter should not be changed.
 */
PyObject* py_get_handshake_response_class();

/**
 * Get pygridgain.aio_connection.ResponseHeader class.
 *
 * @return Python class instance. The object reference counter should not be changed.
 */
PyObject* py_get_response_header_class();

/**
 * Get pygridgain.ignite_error.IgniteError class.
 *
 * @return Python class instance. The object reference counter should not be changed.
 */
PyObject* py_get_ignite_error_class();

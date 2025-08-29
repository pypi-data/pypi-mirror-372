/*
 * Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */

#include "py_classes.h"
#include "py_errors.h"
#include "py_object.h"

py_object py_get_ignite_error(const ignite::ignite_error &err) {
    auto error_class = py_get_ignite_error_class();
    if (!error_class)
        return nullptr;

    py_object args{PyTuple_New(2)};
    if (!args)
        return nullptr;

    PyTuple_SET_ITEM(args.get(), 0, PyLong_FromLongLong(std::int64_t(err.get_status_code())));
    PyTuple_SET_ITEM(args.get(), 1, PyUnicode_FromString(err.what()));

    py_object py_err{PyObject_Call(error_class, args.get(), nullptr)};
    return py_err;
}

void py_set_ignite_error(const ignite::ignite_error &err) {
    auto error_class = py_get_ignite_error_class();
    if (!error_class)
        return;

    py_object py_err = py_get_ignite_error(err);
    if (!py_err)
      return;

    PyErr_SetObject(error_class, py_err.get());
}

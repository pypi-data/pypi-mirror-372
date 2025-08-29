/*
 * Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */

#include "py_classes.h"
#include "py_object.h"

namespace {

/**
 * Get the class from the python module.
 *
 * @param mod_name Module name.
 * @param class_name Class name.
 * @return Python class instance.
 */
PyObject* py_get_module_class(const char* mod_name, const char* class_name) {
    py_object module{PyImport_ImportModule(mod_name)};
    if (!module)
        return nullptr;

    return PyObject_GetAttrString(module.get(), class_name);
}

} // anonymous namespace;


#define LAZY_INIT_MODULE_CLASS(mod_name, class_name)            \
    static PyObject* instance{nullptr};                         \
    if (!instance)                                              \
        instance = py_get_module_class(mod_name, class_name);   \
    return instance

PyObject* py_get_handshake_response_class() {
    LAZY_INIT_MODULE_CLASS("pygridgain.async_node_connection", "HandshakeResponse");
}

PyObject* py_get_response_header_class() {
    LAZY_INIT_MODULE_CLASS("pygridgain.async_node_connection", "ResponseHeader");
}

PyObject* py_get_ignite_error_class() {
    LAZY_INIT_MODULE_CLASS("pygridgain.ignite_error", "IgniteError");
}
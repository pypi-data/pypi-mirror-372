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

#include "ignite/protocol/client_operation.h"
#include "ignite/protocol/writer.h"
#include "ignite/protocol/buffer_adapter.h"
#include "ignite/common/bytes_view.h"
#include "ignite/protocol/reader.h"

/**
 * Get binary data from the python object.
 *
 * @param py_data Python object (bytes | bytearray)
 * @return Bytes view.
 */
[[nodiscard]] ignite::bytes_view get_py_binary_data(PyObject* py_data);

/**
 * Pack request.
 *
 * @param op Operation code.
 * @param req_id Request ID.
 * @param wr Writer callback.
 * @return Data buffer.
 */
template<typename WriteCallback>
[[nodiscard]] std::vector<std::byte> pack_request(
    ignite::protocol::client_operation op, std::int64_t req_id, WriteCallback &wr)
{
    std::vector<std::byte> message;
    ignite::protocol::buffer_adapter buffer(message);
    buffer.reserve_length_header();

    ignite::protocol::writer writer(buffer);
    writer.write(std::int32_t(op));
    writer.write(req_id);
    if (!wr(writer))
        return {};

    buffer.write_length_header();
    return message;
}

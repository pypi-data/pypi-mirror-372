# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
from pygridgain.error_code import ErrorCode, ErrorGroup


class IgniteError(Exception):
    """
    Ignite error.
    """

    def __init__(self, code: ErrorCode | int, message: str):
        super().__init__(message)
        self._code = int(code)

    @property
    def code(self) -> int:
        """
        Gets the raw error code.
        """
        return self._code

    @property
    def error_code(self) -> ErrorCode:
        """
        Gets the error code.
        """
        return ErrorCode.from_error_code(self._code)

    @property
    def error_group(self) -> ErrorGroup:
        """
        Gets the error group.
        """
        return ErrorGroup.from_error_code(self._code)


connection_errors = (IOError, OSError, EOFError)

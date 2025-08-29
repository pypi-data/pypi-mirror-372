# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/

from enum import IntFlag
from typing import Optional

from pygridgain.constants import PROTOCOL_BYTE_ORDER


class BitmaskFeature(IntFlag):
    UNKNOWN = 0

    def __bytes__(self) -> bytes:
        """
        Convert feature flags array to bytearray bitmask.

        :return: Bitmask as bytearray.
        """
        full_bytes = self.bit_length() // 8 + 1
        return self.to_bytes(full_bytes, byteorder=PROTOCOL_BYTE_ORDER)

    @staticmethod
    def all_supported() -> "BitmaskFeature":
        """
        Get all supported features.

        :return: All supported features.
        """
        supported = BitmaskFeature(0)
        for feature in BitmaskFeature:
            supported |= feature
        return supported

    @staticmethod
    def no_supported() -> "BitmaskFeature":
        """
        Get zero supported features.

        :return: No supported features.
        """
        return BitmaskFeature(0)

    @staticmethod
    def from_array(features_array: bytes) -> Optional["BitmaskFeature"]:
        """
        Get features from bytearray.

        :param features_array: Feature bitmask as an array,
        :return: Return features.
        """
        if features_array is None:
            return None
        return BitmaskFeature.from_bytes(features_array, byteorder=PROTOCOL_BYTE_ORDER)

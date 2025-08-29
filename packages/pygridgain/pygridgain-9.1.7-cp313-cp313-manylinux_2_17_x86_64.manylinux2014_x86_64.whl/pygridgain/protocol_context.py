# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/

from typing import Tuple

from pygridgain.bitmask_feature import BitmaskFeature


class ProtocolContext:
    """
    Protocol context. Provides ability to easily check supported protocol features.
    """

    def __init__(self, version: Tuple[int, int, int], features: BitmaskFeature = None):
        self._version = version
        self._features = features

    def __str__(self):
        return f"ProtocolContext(version={self._version}, features={self._features})"

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return ProtocolContext(self.version, self.features)

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version: Tuple[int, int, int]):
        """
        Set version.

        :param version: Version to set.
        """
        self._version = version

    @property
    def features(self):
        return self._features

    @features.setter
    def features(self, features: BitmaskFeature):
        """
        Try and set new feature set.

        :param features: Features to set.
        """
        self._features = features

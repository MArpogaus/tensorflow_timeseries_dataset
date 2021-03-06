# -*- time-stamp-pattern: "changed[\s]+:[\s]+%%$"; -*-
# AUTHOR INFORMATION ##########################################################
# file    : cyclical_feature_encoder.py
# author  : Marcel Arpogaus <marcel dot arpogaus at gmail dot com>
#
# created : 2022-01-07 09:02:38 (Marcel Arpogaus)
# changed : 2022-03-17 17:23:19 (Marcel Arpogaus)
# DESCRIPTION #################################################################
# ...
# LICENSE #####################################################################
# Copyright 2022 Marcel Arpogaus
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################
import numpy as np
import tensorflow as tf


def default_cycl_getter(df, k):
    try:
        cycl = getattr(df, k)
    except AttributeError:
        cycl = getattr(df.index, k)
    return cycl


class CyclicalFeatureEncoder:
    def __init__(
        self, cycl_name, cycl_max, cycl_min=0, cycl_getter=default_cycl_getter
    ):
        self.cycl_max = cycl_max
        self.cycl_min = cycl_min
        self.cycl_getter = cycl_getter
        self.cycl_name = cycl_name

    def encode(self, data):
        cycl = self.cycl_getter(data, self.cycl_name)
        sin = np.sin(
            2 * np.pi * (cycl - self.cycl_min) / (self.cycl_max - self.cycl_min + 1)
        )
        cos = np.cos(
            2 * np.pi * (cycl - self.cycl_min) / (self.cycl_max - self.cycl_min + 1)
        )
        assert np.allclose(
            cycl, self.decode(sin, cos)
        ), f'Decoding failed. Is "cycl_min/max" ({self.cycl_min}/{self.cycl_max}) correct?'
        return sin, cos

    def __call__(self, data):
        data = data.copy()
        sin, cos = self.encode(data)
        data[self.cycl_name + "_sin"] = sin
        data[self.cycl_name + "_cos"] = cos
        return data

    def decode(self, sin, cos):
        angle = (tf.math.atan2(sin, cos) + 2 * np.pi) % (2 * np.pi)
        return (angle * (self.cycl_max - self.cycl_min + 1)) / (
            2 * np.pi
        ) + self.cycl_min

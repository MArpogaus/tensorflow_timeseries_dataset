# -*- time-stamp-pattern: "changed[\s]+:[\s]+%%$"; -*-
# AUTHOR INFORMATION ##########################################################
# file    : windowed_time_series_pipeline.py
# author  : Marcel Arpogaus <marcel dot arpogaus at gmail dot com>
#
# created : 2022-01-07 09:02:38 (Marcel Arpogaus)
# changed : 2022-01-07 09:02:38 (Marcel Arpogaus)
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
# REQUIRED PYTHON MODULES #####################################################
import tensorflow as tf

from tensorflow_time_series_dataset.pipeline.batch_processor import BatchPreprocessor
from tensorflow_time_series_dataset.pipeline.patch_generator import PatchGenerator


class WindowedTimeSeriesPipeline:
    def __init__(
        self,
        history_size,
        prediction_size,
        history_columns,
        meta_columns,
        prediction_columns,
        shift,
        batch_size,
        cycle_length,
        shuffle_buffer_size,
        seed,
    ):
        assert (
            prediction_size > 0
        ), "prediction_size must be a positive integer greater than zero"
        self.history_size = history_size
        self.prediction_size = prediction_size
        self.window_size = history_size + prediction_size
        self.history_columns = history_columns
        self.meta_columns = meta_columns
        self.prediction_columns = prediction_columns
        self.shift = shift
        self.batch_size = batch_size
        self.cycle_length = cycle_length
        self.shuffle_buffer_size = shuffle_buffer_size
        self.seed = seed

    def __call__(self, ds):

        if self.shuffle_buffer_size > 0:
            ds = ds.shuffle(
                self.cycle_length * self.shuffle_buffer_size, seed=self.seed
            )

        ds = ds.interleave(
            PatchGenerator(self.window_size, self.shift),
            cycle_length=self.cycle_length,
            num_parallel_calls=tf.data.experimental.AUTOTUNE,
        )

        if self.shuffle_buffer_size > 0:
            ds = ds.shuffle(self.batch_size * self.shuffle_buffer_size, seed=self.seed)

        ds = ds.batch(self.batch_size, drop_remainder=True)

        ds = ds.map(
            BatchPreprocessor(
                self.history_size,
                self.history_columns,
                self.meta_columns,
                self.prediction_columns,
            ),
            num_parallel_calls=tf.data.experimental.AUTOTUNE,
        )

        ds = ds.prefetch(tf.data.experimental.AUTOTUNE)

        return ds

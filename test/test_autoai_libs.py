# Copyright 2019 IBM Corporation
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

from lale.lib.autoai_libs import float32_transform
from lale.lib.lale import Hyperopt
from lale.lib.sklearn import LogisticRegression as LR
import autoai_libs.utils.fc_methods
import lale.lib.autoai_libs
import numpy as np
import sklearn.datasets
import sklearn.model_selection
import unittest

class TestAutoaiLibs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        iris = sklearn.datasets.load_iris()
        iris_X, iris_y = iris.data, iris.target
        iris_train_X, iris_test_X, iris_train_y, iris_test_y = \
            sklearn.model_selection.train_test_split(iris_X, iris_y)
        cls._iris = {'train_X': iris_train_X, 'train_y': iris_train_y,
                     'test_X': iris_test_X, 'test_y': iris_test_y}

    def doTest(self, trainable, train_X, train_y, test_X, test_y):
        trained = trainable.fit(train_X, train_y)
        transformed = trained.transform(test_X)
        with self.assertWarns(DeprecationWarning):
            trainable.transform(train_X)
        trainable.to_json()
        trainable_pipeline = trainable >> float32_transform() >> LR()
        trained_pipeline = trainable_pipeline.fit(train_X, train_y)
        trained_pipeline.predict(test_X)
        hyperopt = Hyperopt(estimator=trainable_pipeline, max_evals=1)
        trained_hyperopt = hyperopt.fit(train_X, train_y)
        trained_hyperopt.predict(test_X)

    def test_NumpyColumnSelector(self):
        trainable = lale.lib.autoai_libs.NumpyColumnSelector()
        self.doTest(trainable, **self._iris)

    def test_CompressStrings(self):
        n_columns = self._iris['train_X'].shape[1]
        trainable = lale.lib.autoai_libs.CompressStrings(
            dtypes_list=['int_num' for i in range(n_columns)],
            misslist_list=[[] for i in range(n_columns)])
        self.doTest(trainable, **self._iris)

    def test_NumpyReplaceMissingValues(self):
        trainable = lale.lib.autoai_libs.NumpyReplaceMissingValues()
        self.doTest(trainable, **self._iris)

    def test_NumpyReplaceUnknownValues(self):
        trainable = lale.lib.autoai_libs.NumpyReplaceUnknownValues(
            filling_values=42.0)
        self.doTest(trainable, **self._iris)

    def test_boolean2float(self):
        trainable = lale.lib.autoai_libs.boolean2float()
        self.doTest(trainable, **self._iris)

    def test_CatImputer(self):
        trainable = lale.lib.autoai_libs.CatImputer()
        self.doTest(trainable, **self._iris)

    def test_float32_transform(self):
        trainable = lale.lib.autoai_libs.float32_transform()
        self.doTest(trainable, **self._iris)

    def test_FloatStr2Float(self):
        n_columns = self._iris['train_X'].shape[1]
        trainable = lale.lib.autoai_libs.FloatStr2Float(
            dtypes_list=['int_num' for i in range(n_columns)])
        self.doTest(trainable, **self._iris)

    def test_OptStandardScaler(self):
        trainable = lale.lib.autoai_libs.OptStandardScaler()
        self.doTest(trainable, **self._iris)

    def test_NumImputer(self):
        trainable = lale.lib.autoai_libs.NumImputer()
        self.doTest(trainable, **self._iris)

    def test_NumpyPermuteArray(self):
        trainable = lale.lib.autoai_libs.NumpyPermuteArray(
            axis=0, permutation_indices=[2,0,1,3])
        self.doTest(trainable, **self._iris)

    def test_TA1(self):
        trainable = lale.lib.autoai_libs.TA1(
            fun=np.rint, name='round', datatypes=['numeric'], feat_constraints=[autoai_libs.utils.fc_methods.is_not_categorical], col_names=['a', 'b', 'c', 'd'], col_dtypes=[np.dtype('float32'), np.dtype('float32'), np.dtype('float32'), np.dtype('float32')])
        self.doTest(trainable, **self._iris)

################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2022-2025. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################

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

"""
Schema-enhanced versions of the operators from `autoai-ts-libs`_ to enable hyperparameter tuning.

.. _`autoai-ts-libs`: https://pypi.org/project/autoai-ts-libs/

Operators
=========

* autoai_ts_libs.lale. `AutoaiTSPipeline`_
* autoai_ts_libs.lale. `AutoaiWindowTransformedTargetRegressor`_
* autoai_ts_libs.lale. `AutoaiWindowedWrappedRegressor`_
* autoai_ts_libs.lale. `AutoRegression`_
* autoai_ts_libs.lale. `cubic`_
* autoai_ts_libs.lale. `DifferenceFlattenAutoEnsembler`_
* autoai_ts_libs.lale. `EnsembleRegressor`_
* autoai_ts_libs.lale. `fill`_
* autoai_ts_libs.lale. `flatten_iterative`_
* autoai_ts_libs.lale. `FlattenAutoEnsembler`_
* autoai_ts_libs.lale. `LocalizedFlattenAutoEnsembler`_
* autoai_ts_libs.lale. `linear`_
* autoai_ts_libs.lale. `MT2RForecaster`_
* autoai_ts_libs.lale. `next`_
* autoai_ts_libs.lale. `previous`_
* autoai_ts_libs.lale. `SmallDataWindowTargetTransformer`_
* autoai_ts_libs.lale. `StandardRowMeanCenter`_
* autoai_ts_libs.lale. `StandardRowMeanCenterMTS`_
* autoai_ts_libs.lale. `T2RForecaster`_
* autoai_ts_libs.lale. `TSPipeline`_
* autoai_ts_libs.lale. `WatForeForecaster`_
* autoai_ts_libs.lale. `WindowStandardRowMeanCenterMTS`_
* autoai_ts_libs.lale. `WindowStandardRowMeanCenterUTS`_
* autoai_ts_libs.lale. `WindowTransformerMTS`_
* autoai_ts_libs.lale. `TSADPipeline`_
* autoai_ts_libs.lale. `UnivariateGraphLassoAD`_
* autoai_ts_libs.lale. `PointwiseBoundedAnomalyDetector`_
* autoai_ts_libs.lale. `WindowedIsolationForest`_
* autoai_ts_libs.lale. `Flatten`_
* autoai_ts_libs.lale. `GeneralizedAnomalyModel`_
* autoai_ts_libs.lale. `GaussianGraphicalModel`_
* autoai_ts_libs.lale. `WindowedNN`_
* autoai_ts_libs.lale. `WindowedPCA`_
* autoai_ts_libs.lale. `WindowedLOF`_


.. _`AutoaiTSPipeline`: autoai_ts_libs.lale.autoai_ts_pipeline.html
.. _`AutoaiWindowTransformedTargetRegressor`: autoai_ts_libs.lale.autoai_window_transformed_target_regressor.html
.. _`AutoaiWindowedWrappedRegressor`: autoai_ts_libs.lale.autoai_windowed_wrapped_regressor.html
.. _`AutoRegression`: autoai_ts_libs.lale.auto_regression.html
.. _`cubic`: autoai_ts_libs.lale.cubic.html
.. _`DifferenceFlattenAutoEnsembler`: autoai_ts_libs.lale.difference_flatten_auto_ensembler.html
.. _`EnsembleRegressor`: autoai_ts_libs.lale.ensemble_regressor.html
.. _`fill`: autoai_ts_libs.lale.fill.html
.. _`flatten_iterative`: autoai_ts_libs.lale.flatten_iterative.html
.. _`FlattenAutoEnsembler`: autoai_ts_libs.lale.flatten_auto_ensembler.html
.. _`LocalizedFlattenAutoEnsembler`: autoai_ts_libs.lale.localized_flatten_auto_ensembler.html
.. _`linear`: autoai_ts_libs.lale.linear.html
.. _`MT2RForecaster`: autoai_ts_libs.lale.mt2r_forecaster.html
.. _`next`: autoai_ts_libs.lale.next.html
.. _`previous`: autoai_ts_libs.lale.previous.html
.. _`SmallDataWindowTargetTransformer`: autoai_ts_libs.lale.small_data_window_target_transformer.html
.. _`StandardRowMeanCenter`: autoai_ts_libs.lale.standard_row_mean_center.html
.. _`StandardRowMeanCenterMTS`: autoai_ts_libs.lale.standard_row_mean_center_mts.html
.. _`T2RForecaster`: autoai_ts_libs.lale.t2r_forecaster.html
.. _`TSPipeline`: autoai_ts_libs.lale.ts_pipeline.html
.. _`WatForeForecaster`: autoai_ts_libs.lale.watfore_forecaster.html
.. _`WindowStandardRowMeanCenterMTS`: autoai_ts_libs.lale.window_standard_row_mean_center_mts.html
.. _`WindowStandardRowMeanCenterUTS`: autoai_ts_libs.lale.window_standard_row_mean_center_uts.html
.. _`WindowTransformerMTS`: autoai_ts_libs.lale.window_transformer_mts.html
.. _`TSADPipeline`: autoai_ts_libs.lale.ts_ad_pipeline.html
.. _`UnivariateGraphLassoAD`: autoai_ts_libs.lale.graph_lasso_ad.html
.. _`PointwiseBoundedAnomalyDetector`: autoai_ts_libs.lale.pointwise_bounded_ad.html
.. _`WindowedIsolationForest`: autoai_ts_libs.lale.windowed_isolation_forest.html
.. _`Flatten`: autoai_ts_libs.lale.flatten.html
.. _`GeneralizedAnomalyModel`: autoai_ts_libs.lale.generalized_anomaly_model.html
.. _`GaussianGraphicalModel`: autoai_ts_libs.lale.gaussian_graphical_anomaly_model.html
.. _`WindowedNN`: autoai_ts_libs.lale.windowed_nn.html
.. _`WindowedPCA`: autoai_ts_libs.lale.windowed_pca.html
.. _`WindowedLOF`: autoai_ts_libs.lale.windowed_lof.html
"""
from sklearn.experimental import enable_iterative_imputer  # noqa

from .auto_regression import AutoRegression
from .autoai_ts_pipeline import AutoaiTSPipeline
from .autoai_window_transformed_target_regressor import (
    AutoaiWindowTransformedTargetRegressor,
)
from .autoai_windowed_wrapped_regressor import AutoaiWindowedWrappedRegressor
from .cubic import cubic
from .difference_flatten_auto_ensembler import DifferenceFlattenAutoEnsembler
from .ensemble_regressor import EnsembleRegressor
from .fill import fill
from .flatten_auto_ensembler import FlattenAutoEnsembler
from .flatten_iterative import flatten_iterative
from .linear import linear
from .localized_flatten_auto_ensembler import LocalizedFlattenAutoEnsembler
from .mt2r_forecaster import MT2RForecaster
from .next import next
from .previous import previous
from .small_data_window_target_transformer import SmallDataWindowTargetTransformer
from .small_data_window_transformer import SmallDataWindowTransformer
from .standard_row_mean_center import StandardRowMeanCenter
from .standard_row_mean_center_mts import StandardRowMeanCenterMTS
from .t2r_forecaster import T2RForecaster
from .ts_pipeline import TSPipeline
from .watfore_forecaster import WatForeForecaster
from .window_standard_row_mean_center_mts import WindowStandardRowMeanCenterMTS
from .window_standard_row_mean_center_uts import WindowStandardRowMeanCenterUTS
from .window_transformer_mts import WindowTransformerMTS
from .ts_ad_pipeline import TSADPipeline
from .graph_lasso_ad import UnivariateGraphLassoAD
from .pointwise_bounded_ad import PointwiseBoundedAnomalyDetector
from .windowed_isolation_forest import WindowedIsolationForest

# from .flatten import Flatten
# from .generalized_anomaly_model import GeneralizedAnomalyModel
from .gaussian_graphical_anomaly_model import GaussianGraphicalModel
from .windowed_nn import WindowedNN
from .windowed_pca import WindowedPCA
from .windowed_lof import WindowedLOF

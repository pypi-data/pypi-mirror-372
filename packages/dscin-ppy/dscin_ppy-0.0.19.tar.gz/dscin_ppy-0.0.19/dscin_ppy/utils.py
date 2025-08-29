
# Silence future warnings
import warnings
warnings.simplefilter(action='ignore')

from sklearn.ensemble import RandomForestRegressor

from .functions import timing

import logging
# Configure logging
log = logging.getLogger(__name__)

# timed random forest regressor
class TimedRandomForestRegressor(RandomForestRegressor):
    @timing
    def fit(self, X, y, sample_weight=None):
        return super().fit(X, y, sample_weight)

from darts.models import Prophet
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler

from .utils import extend_future_covariates


def train_and_forecast(train_val_dict: dict[str, TimeSeries | Scaler]) -> TimeSeries:
    target_train = train_val_dict.get('target_train')
    volume_train = train_val_dict.get('volume_train')

    # Prophet 학습
    model = Prophet()
    model.fit(target_train, future_covariates=volume_train)

    future_covariates = extend_future_covariates(180, volume_train)

    forecast_series = model.predict(180, future_covariates=future_covariates)

    return forecast_series
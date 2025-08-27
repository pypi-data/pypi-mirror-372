import pandas as pd
import numpy as np
from darts import TimeSeries


def extend_future_covariates(need_steps: int, volume_series: TimeSeries) -> TimeSeries:
    """
    주어진 시계열(volume_series)의 마지막 값을 기준으로 미래 구간을 일정 길이(need_steps)만큼 확장합니다.

    이 함수는 Darts 모델에서 future covariates가 예측 구간만큼 충분히 존재해야 할 때 사용됩니다.
    마지막 값을 복제하여 미래 값을 생성하므로, future covariates가 일정하고 단순할 경우 유용합니다.

    Parameters:
        need_steps (int): 확장할 미래 구간의 스텝 수 (예: 180 - output_chunk_length)
        volume_series (TimeSeries): 기준이 되는 시계열 (예: 거래량)

    Returns:
        TimeSeries: 기존 시계열에 미래 구간이 덧붙여진 확장된 TimeSeries 객체

    Example:
        >>> extended = extend_future_covariates(45, volume_series)
        >>> print(extended.end_time())  # 기존보다 45 스텝 뒤 시간 출력
    """
    last_val = volume_series.last_value()
    future_dates = pd.date_range(
        start=volume_series.end_time() + volume_series.freq,
        periods=need_steps, freq=volume_series.freq
    )
    future_vals = np.full((need_steps, 1), last_val)

    extra_ts = TimeSeries.from_times_and_values(
        future_dates, future_vals, columns=volume_series.components
    )
    extended_volume_scaled = volume_series.append(extra_ts)
    return extended_volume_scaled




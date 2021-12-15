from datetime import datetime

import numpy as np
from requests import get

from constants import EXCLUDED, UNITS, API_KEY


def get_params_from_data(data):
    date = datetime.utcfromtimestamp(data.get("dt"))
    temp = data.get("temp").get("day")
    pcp = data.get("rain")
    clouds = data.get("clouds")
    pressure = data.get("pressure")
    humidity = data.get("humidity")
    wind_speed = data.get("wind_speed")
    return {
        'date': date,
        'temp': temp,
        'pcp': pcp,
        'clouds': clouds,
        'pressure': pressure,
        'humidity': humidity,
        'wind_speed': wind_speed
    }


def get_forecast_by_cords_in_json_format(cords):
    lat, lon = cords
    link = f"https://api.openweathermap.org/data/2.5/onecall" \
           f"?lat={lat}" \
           f"&lon={lon}" \
           f"&exclude={EXCLUDED}" \
           f"&units={UNITS}" \
           f"&appid={API_KEY}"
    try:
        result = get(link).json()
    except Exception as e:
        print(f'[ERROR] : {e}')
        return
    return result


def sum_values_in_array_by_value_name(array_of_forecasts, value_type):
    array_of_values = []
    for forecast in array_of_forecasts:
        value = getattr(forecast, value_type)
        if value:
            array_of_values.append(value)
    return sum(array_of_values) / len(array_of_forecasts)


def moving_average(x, w):
    list_of_averages = list(np.convolve(x, np.ones(w), 'valid') / w)
    result = list(map(float, list_of_averages))
    return result


def get_dict_of_lists_of_moving_means(array_of_forecasts, value_type):
    array = np.array([getattr(forecast, value_type) for forecast in array_of_forecasts])
    moving_average_array = [float(array[0])]  # Here we want to save first value, that can't be average
    moving_average_array.extend(moving_average(array, 2))
    list_of_forecast_dates = [str(forecast.date) for forecast in array_of_forecasts]
    return dict(zip(list_of_forecast_dates, moving_average_array))

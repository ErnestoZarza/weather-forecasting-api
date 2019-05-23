import json
import requests
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from .utils import UNITS, is_valid_date


# PATH = '/Users/vero/PycharmProjects/weather_forecast_api/data/openweathermap_forecast_berlin.json'

def check_date(date, time):
    try:
        # date variables
        year = int(date[0:4])
        month = int(date[4:6])
        day = int(date[6:])

        # time variable
        hour = int(time[0:2])
        minutes = int(time[2:])

    except ValueError:
        return Response(
            data={
                "message": "The given date is not in the valid format YYYYMMDD/HHMM",
                "status": "error"
            },
            status="error"
        )
    try:
        date_display = datetime(year, month, day, hour, minutes)
    except ValueError:
        return Response(
            data={
                "message": "The given date is not a valid date",
                "status": "error"
            },
            status="error"
        )

    if not is_valid_date(date_display):
        return Response(
            data={
                "message": "Can not get a forecasts further out than 5 days",
                "status": "error"
            },
            status="error"
        )
    return date_display


class WeatherSummaryView(generics.RetrieveAPIView):
    """
        GET http://<domain-name>/weather/summary/berlin/<date>/<hour minute>/

    """

    def get(self, request, *args, **kwargs):
        date = kwargs['date']
        time = kwargs['hour_minute']

        date_display = check_date(date, time)

        city = kwargs['city']
        api_key = settings.WEATHER_API_KEY

        endpoint = 'http://api.openweathermap.org/data/2.5/weather?q=%s,DE&units=metric&appid=%s' % (city, api_key)

        data_response = requests.get(endpoint)

        response_data = {}

        if data_response.status_code == 200:  # SUCCESS

            data = data_response.json()
            temp = round(data['main']['temp'])
            print("ok")

            response_data = {"description": data["weather"][0]["description"],
                             "humidity": {"unit": "%", "value": data["main"]["humidity"]},
                             "pressure": {"unit": "hPa", "value": data["main"]["pressure"]},
                             "temperature": {"unit": "°C", "value": temp},
                             "timestamp": date_display.strftime('%Y-%m-%d %H:%M:%S'),
                             "status": "success"
                             }

            return Response(response_data)

        else:
            response_data['status'] = 'error'
            if data_response.status_code == 404:  # NOT FOUND
                response_data['message'] = 'No forecasts available for this city: %s' % city
            else:
                response_data['message'] = 'The Weather API is not available at the moment. Please try again later.'


class WeatherDetailView(generics.RetrieveAPIView):
    """
        http://<domain-name>/weather/temperature/berlin/<date>/<hour minute>/

    """

    def get(self, request, *args, **kwargs):

        date = kwargs['date']
        time = kwargs['hour_minute']

        date_display = check_date(date, time)

        city = kwargs['city']
        api_key = settings.WEATHER_API_KEY

        endpoint = 'http://api.openweathermap.org/data/2.5/weather?q=%s,DE&units=metric&appid=%s' % (city, api_key)

        data_response = requests.get(endpoint)

        # response result
        response_data = {}

        if data_response.status_code == 200:  # SUCCESS

            detail = kwargs["detail"]
            data = data_response.json()

            if detail == "temperature":
                value = round(data['main']['temp'])
            else:
                try:
                    value = data_response["main"][detail]

                except ValueError:
                    return Response(
                        data={
                            "message": "The given detail is invalid, the details available"
                                       "are temperature, pressure and humidity",
                            "status": "error"
                        },
                        status="error"
                    )

            response_data = {"unit": UNITS[detail],
                             "value": value,
                             "timestamp": date_display.strftime('%Y-%m-%d %H:%M:%S'),
                             "status": "success"
                             }

            return Response(response_data)

        else:
            response_data['status'] = 'error'
            if data_response.status_code == 404:  # NOT FOUND
                response_data['message'] = 'No forecasts available for this city: %s' % city
            else:
                response_data['message'] = 'The Wheater API is not available at the moment. Please try again later.'

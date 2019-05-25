import requests
from datetime import datetime

from django.conf import settings
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .utils import UNITS, is_valid_date


def check_parameters(date, time):
    """Method that check if it is a invalid datetime for the forecast service"""
    try:
        # date variables
        year = int(date[0:4])
        month = int(date[4:6])
        day = int(date[6:])

        # time variable
        hour = int(time[0:2])
        minutes = int(time[2:])

    except ValueError:
        return False, Response(
            data={
                "message": "The given date is not in the valid format YYYYMMDD/HHMM",
                "status": "error"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        date_display = datetime(year, month, day, hour, minutes)
    except ValueError:
        return False, Response(
            data={
                "message": "The given date is not a valid date",
                "status": "error"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not is_valid_date(date_display):
        return False, Response(
            data={
                "message": "Can not get a forecasts further out than 5 days",
                "status": "error"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    return True, date_display


def retrieve_data_from_api(city):
    """Method to retrieve the data from the weather api (openweathermap.org)"""
    api_key = settings.WEATHER_API_KEY
    # with 'units = metrics' the temperature in the response is in °C
    endpoint = 'http://api.openweathermap.org/data/2.5/weather?q=%s,DE&units=metric&appid=%s' % (city, api_key)

    data_response = requests.get(endpoint)

    if data_response.status_code == 200:  # SUCCESS

        return True, data_response.json()
    else:
        response_data = {}
        if data_response.status_code == 404:  # NOT FOUND
            response_data['message'] = 'No forecasts available for this city: %s' % city
        else:
            response_data['message'] = 'The Weather API is not available at the moment. Please try again later.'

        response_data['status'] = 'error'
        return False, Response(response_data,
                               status=status.HTTP_400_BAD_REQUEST
                               )


class WeatherSummaryView(generics.RetrieveAPIView):
    """
        GET http://weather-information-api.herokuapp.com/weather/summary/<city>/<date>/<hour minute>/

    """

    # Cache page for the requested url
    @method_decorator(cache_page(60 * 60 * 2))
    def get(self, request, *args, **kwargs):
        # date variables
        date = kwargs['date']
        time = kwargs['hour_minute']

        valid_parameters, response = check_parameters(date, time)

        if valid_parameters:
            date_display = response
        else:  # Error with the datetime parameters
            return response

        city = kwargs['city']

        success, api_response = retrieve_data_from_api(city)

        if success:

            temp = round(api_response['main']['temp'])

            response_data = {"description": api_response["weather"][0]["description"],
                             "humidity": {"unit": "%", "value": api_response["main"]["humidity"]},
                             "pressure": {"unit": "hPa", "value": api_response["main"]["pressure"]},
                             "temperature": {"unit": "°C", "value": temp},
                             "timestamp": date_display.strftime('%Y-%m-%d %H:%M:%S'),
                             "status": "success"
                             }

            return Response(response_data)
        else:
            return api_response


class WeatherDetailView(generics.RetrieveAPIView):
    """
       GET http://weather-information-api.herokuapp.com/weather/temperature/<city>/<date>/<hour minute>/

    """

    # Cache page for the requested url
    @method_decorator(cache_page(60 * 60 * 2))
    def get(self, request, *args, **kwargs):
        # datetime variables
        date = kwargs['date']
        time = kwargs['hour_minute']

        valid_date, response = check_parameters(date, time)

        if valid_date:
            date_display = response
        else:  # Error with the date parameters
            return response

        detail = kwargs["detail"]

        # checking valid details
        invalid_detail = detail != "temperature" and detail != "pressure" and detail != "humidity"

        if not detail or invalid_detail:
            return Response(
                data={
                    "message": "The given detail is invalid, the details available "
                               " are: temperature, pressure and humidity",
                    "status": "error"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        city = kwargs['city']

        success, api_response = retrieve_data_from_api(city)

        if success:

            if detail == "temperature":
                value = round(api_response['main']['temp'])

            else:
                value = api_response["main"][detail]

            result_data = {"unit": UNITS[detail],
                           "value": value,
                           "timestamp": date_display.strftime('%Y-%m-%d %H:%M:%S'),
                           "status": "success"
                           }

            return Response(result_data)

        else:
            return api_response


def home_view(request):
    template = 'home.html'
    context = {}
    return render(request, template, context)

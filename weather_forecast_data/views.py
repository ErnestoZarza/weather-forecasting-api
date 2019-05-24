import requests
from datetime import datetime

from django.conf import settings
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status
from django.shortcuts import render

from .utils import UNITS, is_valid_date


def check_parameters(date, time, city):
    """Method that check if it is a invalid datetime and a valid city for the forecast service"""

    if not city:
        return False, Response(
            data={
                "message": "The city parameter can not be empty",
                "status": "error"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

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
    # TODO check empty entries
    """
        GET http://weather-information-api.herokuapp.com/weather/summary/berlin/<date>/<hour minute>/

    """

    def get(self, request, *args, **kwargs):
        # date variables
        date = kwargs['date']
        time = kwargs['hour_minute']
        city = kwargs['city']

        valid_parameters, response = check_parameters(date, time, city)

        if valid_parameters:
            date_display = response
        else:  # Error with the parameters
            return response

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
       GET http://weather-information-api.herokuapp.com/weather/temperature/berlin/<date>/<hour minute>/

    """

    def get(self, request, *args, **kwargs):
        # datetime variables
        date = kwargs['date']
        time = kwargs['hour_minute']
        city = kwargs['city']

        valid_date, response = check_parameters(date, time, city)

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

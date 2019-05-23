import requests
from datetime import datetime

from django.conf import settings
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from .utils import UNITS, is_valid_date


def check_date(date, time):
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


class WeatherSummaryView(generics.RetrieveAPIView):
    """
        GET http://<domain-name>/weather/summary/berlin/<date>/<hour minute>/

    """

    def get(self, request, *args, **kwargs):
        # date variables
        date = kwargs['date']
        time = kwargs['hour_minute']

        valid_date, response = check_date(date, time)

        if valid_date:
            date_display = response
        else:  # Error with the date parameters
            return response

        city = kwargs['city']
        api_key = settings.WEATHER_API_KEY

        endpoint = 'http://api.openweathermap.org/data/2.5/weather?q=%s,DE&units=metric&appid=%s' % (city, api_key)

        data_response = requests.get(endpoint)

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
            response_data = {}
            if data_response.status_code == 404:  # NOT FOUND
                response_data['message'] = 'No forecasts available for this city: %s' % city
            else:
                response_data['message'] = 'The Weather API is not available at the moment. Please try again later.'

            response_data['status'] = 'error'
            return Response(response_data,
                            status=status.HTTP_400_BAD_REQUEST
                            )


class WeatherDetailView(generics.RetrieveAPIView):
    """
       GET http://<domain-name>/weather/temperature/berlin/<date>/<hour minute>/

    """

    def get(self, request, *args, **kwargs):
        # datetime variables
        date = kwargs['date']
        time = kwargs['hour_minute']

        valid_date, response = check_date(date, time)

        if valid_date:
            date_display = response
        else:  # Error with the date parameters
            return response

        city = kwargs['city']
        api_key = settings.WEATHER_API_KEY

        endpoint = 'http://api.openweathermap.org/data/2.5/weather?q=%s,DE&units=metric&appid=%s' % (city, api_key)

        data_response = requests.get(endpoint)

        if data_response.status_code == 200:  # SUCCESS

            detail = kwargs["detail"]
            data = data_response.json()

            if detail == "temperature":
                value = round(data['main']['temp'])

            else:
                try:
                    value = data["main"][detail]

                except KeyError:
                    return Response(
                        data={
                            "message": "The given detail is invalid, the details available "
                                       " are: temperature, pressure and humidity",
                            "status": "error"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            result_data = {"unit": UNITS[detail],
                           "value": value,
                           "timestamp": date_display.strftime('%Y-%m-%d %H:%M:%S'),
                           "status": "success"
                           }

            return Response(result_data)

        else:
            result_data = {}
            if data_response.status_code == 404:  # NOT FOUND
                result_data['message'] = 'No forecasts available for this city: %s' % city
            else:
                result_data['message'] = 'The Weather API is not available at the moment. Please try again later.'
                result_data['status'] = 'error'
            return Response(result_data,
                            status=status.HTTP_400_BAD_REQUEST
                            )

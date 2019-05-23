import json
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from .utils import units

PATH = '/Users/vero/PycharmProjects/weather_forecast_api/data/openweathermap_forecast_berlin.json'


# Create your views here.


class WeatherSummaryView(generics.RetrieveAPIView):
    """
        GET http://<domain-name>/weather/summary/berlin/<date>/<hour minute>/

    """

    def get(self, request, *args, **kwargs):
        try:
            date = kwargs["date"]
            time = kwargs["hour_minute"]

            # date variables
            year = int(date[0:4])
            month = int(date[4:6])
            day = int(date[6:])

            # time variable
            hour = int(time[0:2])
            minutes = int(time[2:])

            date_display = datetime(year, month, day, hour, minutes)

            with open(PATH, 'r') as data:
                data_response = json.load(data)
                temp_k = float(data_response["main"]["temp"])
                temp_c = int(temp_k - 273.15)
                print("ok")

                response_data = {"description": data_response["weather"][0]["description"],
                                 "humidity": {"unit": "%", "value": data_response["main"]["humidity"]},
                                 "pressure": {"unit": "hPa", "value": data_response["main"]["pressure"]},
                                 "temperature": {"unit": "°C", "value": temp_c},
                                 "timestamp": date_display.strftime('%Y-%m-%d %H:%M:%S'),
                                 "status": "success"
                                 }

                return Response(response_data)

        except ValueError:
            return Response(
                data={
                    "message": "Something went wrong",
                    "status": "error"
                },
                status=status.HTTP_404_NOT_FOUND
            )


class WeatherDetailView(generics.RetrieveAPIView):
    """
        http://<domain-name>/weather/temperature/berlin/<date>/<hour minute>/

    """

    def get(self, request, *args, **kwargs):
        try:
            date = kwargs["date"]
            time = kwargs["hour_minute"]

            # date variables
            year = int(date[0:4])
            month = int(date[4:6])
            day = int(date[6:])

            # time variable
            hour = int(time[0:2])
            minutes = int(time[2:])

            date_display = datetime(year, month, day, hour, minutes)

            detail = kwargs["detail"]
            if detail == "temperature":
                detail = "temp"

            with open(PATH, 'r') as data:
                data_response = json.load(data)
                temp_k = float(data_response["main"]["temp"])
                temp_c = int(temp_k - 273.15)
                print("ok")

                response_data = {"description": data_response["weather"][0]["description"],
                                 detail: {"unit": units[detail], "value": data_response["main"][detail]},
                                 "timestamp": date_display.strftime('%Y-%m-%d %H:%M:%S'),
                                 "status": "success"
                                 }

                return Response(response_data)

        except ValueError:
            return Response(
                data={
                    "message": "Something went wrong with... ",
                    "status": "error"
                },
                status=status.HTTP_404_NOT_FOUND
            )

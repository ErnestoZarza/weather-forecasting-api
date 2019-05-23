"""weather_forecast_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from weather_forecast_data.views import weather_summary_view, weather_detail_view

# summary
# http://<domain-name>/weather/summary/berlin/<date>/<hour minute>/

# detail
# http://<domain-name>/weather/temperature/berlin/<date>/<hour minute>/
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('r^weather/summary/<city>/<date>/<hour_minute>/', weather_summary_view, name='weather-summary'),
    url('r^weather/<detail>/<city>/<date>/<hour_minute>/', weather_detail_view, name='weather-detail')

]

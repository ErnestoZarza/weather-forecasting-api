# Weather Forecast Information Service

This project is an REST Service based web application that allows to retrieve information of the weather forecast for an
specific city.

## Getting Started

For the information we are going to use the openweathermap.org web site. The data used is 
collected by calling http://api.openweathermap.org/data/2.5/weather?q=city,DE&appid=<APP_ID> 


## Deployment

This application was implemented using the following technologies:


* [Python](https://www.python.org/) - Programming Language
* [Django](https://www.djangoproject.com/) - Web Framework
* [Django Rest](https://www.django-rest-framework.org/) - Web API

## Requirements

* Python 3.x.x
* Django 2.x.x

## Runing the application

To run this application, clone the repository on your local machine and execute the following commands.

```
$ cd weather_forecast_api
$ virtualenv virtenv
$ source virtenv/bin/activate
$ pip install -r requirements.txt
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver
 ```

## Application

Running the application.  

```
https://weather-information-api.herokuapp.com

```


### API

You can use the API in this way in order to retrieve the information:

#### Weather summary

Endpoint to query the general weather summary for a specific location and date/time
combination.


```
curl https://weather-information-api.herokuapp.com/weather/summary/<city>/<date>/<hour minute>/

example:
https://weather-information-api.herokuapp.com/weather/summary/berlin/20190526/1800/
``` 


#### Specific details

Endpoint to also retrieve specific details for each of [temperature, pressure, humidity]
for the specific location and date/time combination.

```
curl https://weather-information-api.herokuapp.com/weather/temperature/<city>/<date>/<hour minute>/

example:
https://weather-information-api.herokuapp.com/weather/temperature/berlin/20190526/1800/  
```

#### Error cases

The application controls if there are any errors.

Example 1: This error is because the date in the call correspond date in the past / future (more than 5 days).

```
curl https://weather-information-api.herokuapp.com/weather/summary/berlin/20190506/1800/

The result will be:

"message": "Can not get a forecasts further out than 5 days",
"status": "error"

```



Example 2: If the date's format in the call is not valid.

```
curl https://weather-information-api.herokuapp.com/weather/summary/berlin/2019/1800/

The result will be:

"message": "The given date is not in the valid format YYYYMMDD/HHMM",
"status": "error"

```

Example 3: If the detailed information in the call has an invalid name or is empty.

```
curl https://weather-information-api.herokuapp.com/weather/z/berlin/20190526/1800/

The result will be:

"message": "The given detail is invalid, the details available  are: temperature, pressure and humidity",
"status": "error"

```

Example 4: If the city in the call has an invalid name or is empty.

```
curl http://127.0.0.1:8000/weather/temperature/be/20190526/1800/

The result will be:

"message": "No forecasts available for this city: bn",
"status": "error"

```


## Running the tests

To run the test cases of the application, enter the following command

```
$ python manage.py test
```

Additional questions

Q- If we wanted the temperature in the response in Kelvin rather than in Celsius, how
could we specify this in the API calls?

A- We can modify or add a new url pattern for the call and define a variable (on the url), in order to specify if we want the temperature data in degrees Celsius or in Kelvin. Also, the Weather API provide 3 different temperature units, Fahrenheit, Celsius and Kelvin units. For temperature in Fahrenheit we need to use „units=imperial“ and  for temperature in Celsius, units=metric.

Q- How would you test your REST service?

A- Although, Django Rest Framework offers an interface in order to test and retrieve the information of our API. We can use alternative ways. One is implement a test code using the libraries provided by Django REST Framework (APITestCase, APIClient) in order to verify the correctness output of the service. 

Another way is to use an API Testing Software, wich is a software testing type which focuses on the determination if the developed APIs meet expectations regarding the functionality, reliability, performance, and security of the application. There are many softwares in order to test our REST service, one recommendation is to use Postman (https://www.getpostman.com/). 

I think that testing our service strongly depends in our requirements and of course in the nature of our application/service, this allows us to analyze the pros and cons of each testing solution. This approach gives you a good chance to identify the suitable tool for your project.

Q- How would you check the code coverage of your tests?

A- Using the django-nose package.

Q- How could the API be documented for third-parties to use?

A- We have different ways to do this. The first one is to use the built-in API documentation (rest_framework.documentation), that include a documentation of endpoints, a support for API interaction and code samples for the available API client libraries. A good practice is to document your views and your methods. 

Another way is to use third party packages for the API documentation. Django Rest Swagger is one popular API documentation tool. The package produces well presented API documentation, and includes interactive tools for testing API endpoints. 

A different approach could be the self describing implementation of our API. The API in the browser representation that REST framework provides makes it possible for your API to be entirely self describing. The documentation for each API endpoint can be provided simply by visiting the URL in your browser.

Q- How would you restrict access to this API?

A- Using the Django REST framework’s Permissions. In REST framework are always defined as a list of permission classes that we can use depending on our requirements. Moreover, you can set a  permission policy. This can be configured globally or defining a different policy per view. Also, you can create your own implementation of permissions class inheriting from Rest Framework - permissions. 

In addition, the models in Django provides a “Django Model Permissions“ that can be used to restrict the access of our API data. An alternative way is using third party package/libraries in order to add permissions, Rest Condition, Django Rest Framework API Key, Django Rest Framework Roles are examples of this packages.	

Q- How would you try to accomplish daily forecast recoveries from openweather.org,
keeping the web service up to date?

A- I would try to take an advantage from the Django’s Cache and create a policy to fetch in a daily basis the most important or populars (with more calls) requests in cache. The Django calls to an API are expensive, so we have to take that into consideration in our process.


### Author:

* **Ernesto Zarza**


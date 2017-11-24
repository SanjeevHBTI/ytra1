# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

# import requests
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "yatraFlightBooking":
        return {}
    
    '''
    baseurl = "https://maps.googleapis.com/maps/api/geocode/json?latlng=28.7041,77.1025"
    yql_url = baseurl + "&format=json"
    result = urlopen(yql_url).read()
    data1 = json.loads(result)
    data = "https://flight.yatra.com/air-search-ui/dom2/trigger?ADT=1&CHD=0&INF=0&arrivalDate=23/11/2017&class=Economy&destination=BOM&destinationCountry=IN&flexi=0&flight_depart_date=22/11/2017&noOfSegments=2&origin=DEL&originCountry=IN&source=fresco-home&type=R&version=1.1&viewName=normal"
    res = makeWebhookResult_1(data)
    '''
    
    baseurl = "https://flight.yatra.com/air-service/dom2/search?type=O&viewName=normal&flexi=0&noOfSegments=1&origin=DEL&originCountry=IN&destination=BLR&destinationCountry=IN&flight_depart_date=25/11/2017&ADT=1&CHD=0&INF=0&class=Economy&source=fresco-homeUrl"
    yql_url = baseurl + "&format=json"
    result = urlopen(yql_url).read()
    data = json.loads(result)
    
    res = makeWebhookResult_1(data['airportName']['DEL'])
#     res = makeWebhookResult_1(data['data']['content']['address'])
    return res

def makeWebhookResult_1(data):
    speech = data
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"

def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today the weather in " + location.get('city') + ": " + condition.get('text') + \
             ", And the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')

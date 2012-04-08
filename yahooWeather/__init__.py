#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# This is a weather plugin for SiriServerCore  
# created by Eichhoernchen
#
# It uses various the services from yahoo
#
#
# This file is free for private use, you need a commercial license for paid servers
#
# It's distributed under the same license as SiriServerCore
#
# You can view the license here:
# https://github.com/Eichhoernchen/SiriServerCore/blob/master/LICENSE
#
# So if you have a SiriServerCore commercial license 
# you are allowed to use this plugin commercially otherwise you are breaking the law
#
# You must make sure to get propper allowens from yahoo to use their API commercially
#
# This file can be freely modified, but this header must retain untouched
#  
# 

from datetime import date
from plugin import *
from siriObjects.weatherObjects import WeatherHourlyForecast, \
    WeatherCurrentConditions, WeatherCondition, WeatherUnits, \
    WeatherBarometricPressure, WeatherWindSpeed, WeatherDailyForecast, \
    WeatherForecast, WeatherObject, WeatherLocation, WeatherForecastSnippet
from xml.etree import ElementTree
import random
import urllib
import urllib2


appleWeek = {
'Sun': 1,
'Mon': 2,
'Tue': 3,
'Wed': 4,
'Thu': 5,
'Fri': 6,
'Sat': 7
}

countries = {
    "af": "Afghanistan",
    "al": "Albania",
    "dz": "Algeria",
    "as": "American Samoa",
    "ad": "Andorra",
    "ao": "Angola",
    "ai": "Anguilla",
    "aq": "Antarctica",
    "ag": "Antigua and Barbuda",
    "ar": "Argentina",
    "am": "Armenia",
    "aw": "Aruba",
    "au": "Australia",
    "at": "Austria",
    "az": "Azerbaijan",
    "bs": "Bahamas",
    "bh": "Bahrain",
    "bd": "Bangladesh",
    "bb": "Barbados",
    "by": "Belarus",
    "be": "Belgium",
    "bz": "Belize",
    "bj": "Benin",
    "bm": "Bermuda",
    "bt": "Bhutan",
    "bo": "Bolivia",
    "ba": "Bosnia and Herzegowina",
    "bw": "Botswana",
    "bv": "Bouvet Island",
    "br": "Brazil",
    "io": "British Indian Ocean Territory",
    "bn": "Brunei Darussalam",
    "bg": "Bulgaria",
    "bf": "Burkina Faso",
    "bi": "Burundi",
    "kh": "Cambodia",
    "cm": "Cameroon",
    "ca": "Canada",
    "cv": "Cape Verde",
    "ky": "Cayman Islands",
    "cf": "Central African Republic",
    "td": "Chad",
    "cl": "Chile",
    "cn": "China",
    "cx": "Christmas Island",
    "cc": "Cocos (Keeling) Islands",
    "co": "Colombia",
    "km": "Comoros",
    "cg": "Congo",
    "cd": "Congo, The Democratic Republic of the",
    "ck": "Cook Islands",
    "cr": "Costa Rica",
    "ci": "Cote D'Ivoire",
    "hr": "Croatia (local name: Hrvatska)",
    "cu": "Cuba",
    "cy": "Cyprus",
    "cz": "Czech Republic",
    "dk": "Denmark",
    "dj": "Djibouti",
    "dm": "Dominica",
    "do": "Dominican Republic",
    "tp": "East Timor",
    "ec": "Ecuador",
    "eg": "Egypt",
    "sv": "El Salvador",
    "gq": "Equatorial Guinea",
    "er": "Eritrea",
    "ee": "Estonia",
    "et": "Ethiopia",
    "fk": "Falkland Islands (Malvinas)",
    "fo": "Faroe Islands",
    "fj": "Fiji",
    "fi": "Finland",
    "fr": "France",
    "fx": "France, metropolitan",
    "gf": "French Guiana",
    "pf": "French Polynesia",
    "tf": "French Southern Territories",
    "ga": "Gabon",
    "gm": "Gambia",
    "ge": "Georgia",
    "de": "Germany",
    "gh": "Ghana",
    "gi": "Gibraltar",
    "gr": "Greece",
    "gl": "Greenland",
    "gd": "Grenada",
    "gp": "Guadeloupe",
    "gu": "Guam",
    "gt": "Guatemala",
    "gn": "Guinea",
    "gw": "Guinea-Bissau",
    "gy": "Guyana",
    "ht": "Haiti",
    "hm": "Heard and Mc Donald Islands",
    "va": "Holy See (Vatican City State)",
    "hn": "Honduras",
    "hk": "Hong Kong",
    "hu": "Hungary",
    "is": "Iceland",
    "in": "India",
    "id": "Indonesia",
    "ir": "Iran (Islamic Republic of)",
    "iq": "Iraq",
    "ie": "Ireland",
    "il": "Israel",
    "it": "Italy",
    "jm": "Jamaica",
    "jp": "Japan",
    "jo": "Jordan",
    "kz": "Kazakhstan",
    "ke": "Kenya",
    "ki": "Kiribati",
    "kp": "Korea, Democratic People's Republic of",
    "kr": "Korea, Republic of",
    "kw": "Kuwait",
    "kg": "Kyrgyzstan",
    "la": "Lao People's Democratic Republic",
    "lv": "Latvia",
    "lb": "Lebanon",
    "ls": "Lesotho",
    "lr": "Liberia",
    "ly": "Libyan Arab Jamahiriya",
    "li": "Liechtenstein",
    "lt": "Lithuania",
    "lu": "Luxembourg",
    "mo": "Macau",
    "mk": "Macedonia, The Former Yugoslav Republic of",
    "mg": "Madagascar",
    "mw": "Malawi",
    "my": "Malaysia",
    "mv": "Maldives",
    "ml": "Mali",
    "mt": "Malta",
    "mh": "Marshall Islands",
    "mq": "Martinique",
    "mr": "Mauritania",
    "mu": "Mauritius",
    "yt": "Mayotte",
    "mx": "Mexico",
    "fm": "Micronesia, Federated States of",
    "md": "Moldova, Republic of",
    "mc": "Monaco",
    "mn": "Mongolia",
    "ms": "Montserrat",
    "ma": "Morocco",
    "mz": "Mozambique",
    "mm": "Myanmar",
    "na": "Namibia",
    "nr": "Nauru",
    "np": "Nepal",
    "nl": "Netherlands",
    "an": "Netherlands Antilles",
    "nc": "New Caledonia",
    "nz": "New Zealand",
    "ni": "Nicaragua",
    "ne": "Niger",
    "ng": "Nigeria",
    "nu": "Niue",
    "nf": "Norfolk Island",
    "mp": "Northern Mariana Islands",
    "no": "Norway",
    "om": "Oman",
    "pk": "Pakistan",
    "pw": "Palau",
    "pa": "Panama",
    "pg": "Papua New Guinea",
    "py": "Paraguay",
    "pe": "Peru",
    "ph": "Philippines",
    "pn": "Pitcairn",
    "pl": "Poland",
    "pt": "Portugal",
    "pr": "Puerto Rico",
    "qa": "Qatar",
    "re": "Reunion",
    "ro": "Romania",
    "ru": "Russian Federation",
    "rw": "Rwanda",
    "kn": "Saint Kitts and Nevis",
    "lc": "Saint Lucia",
    "vc": "Saint Vincent and the Grenadines",
    "ws": "Samoa",
    "sm": "San Marino",
    "st": "Sao Tome and Principe",
    "sa": "Saudi Arabia",
    "sn": "Senegal",
    "sc": "Seychelles",
    "sl": "Sierra Leone",
    "sg": "Singapore",
    "sk": "Slovakia (Slovak Republic)",
    "si": "Slovenia",
    "sb": "Solomon Islands",
    "so": "Somalia",
    "za": "South Africa",
    "gs": "South Georgia and the South Sandwich Islands",
    "es": "Spain",
    "lk": "Sri Lanka",
    "sh": "St. Helena",
    "pm": "St. Pierre and Miquelon",
    "sd": "Sudan",
    "sr": "Suriname",
    "sj": "Svalbard and Jan Mayen Islands",
    "sz": "Swaziland",
    "se": "Sweden",
    "ch": "Switzerland",
    "sy": "Syrian Arab Republic",
    "tw": "Taiwan, Province of China",
    "tj": "Tajikistan",
    "tz": "Tanzania, United Republic of",
    "th": "Thailand",
    "tg": "Togo",
    "tk": "Tokelau",
    "to": "Tonga",
    "tt": "Trinidad and Tobago",
    "tn": "Tunisia",
    "tr": "Turkey",
    "tm": "Turkmenistan",
    "tc": "Turks and Caicos Islands",
    "tv": "Tuvalu",
    "ug": "Uganda",
    "ua": "Ukraine",
    "ae": "United Arab Emirates",
    "gb": "United Kingdom",
    "us": "United States",
    "um": "United States Minor Outlying Islands",
    "uy": "Uruguay",
    "uz": "Uzbekistan",
    "vu": "Vanuatu",
    "ve": "Venezuela",
    "vn": "Viet Nam",
    "vg": "Virgin Islands (British)",
    "vi": "Virgin Islands (U.S.)",
    "wf": "Wallis and Futuna Islands",
    "eh": "Western Sahara",
    "ye": "Yemen",
    "yu": "Yugoslavia",
    "zm": "Zambia",
    "zw": "Zimbabwe",
    }

waitText = {
    'de-DE': [u"Einen Moment bitte", u"OK"],
    'en-US': [u"One moment please", u"OK"]
}

errorText = {
    'de-DE': [u"Entschuldigung aber zur Zeit ist die Funktion nicht verfügbar."],
    'en-US': [u"Sorry this is not available right now."]
}

noDataForLocationText = {
    'de-DE': [u"Entschuldigung aber für ihren Standort finde ich keine Daten."],
    'en-US': [u"Sorry, I cannot find any data for your location."]
}

dailyForcast = {
    'de-DE': [u"Hier ist die Vorhersage für {0}, {1}"],
    'en-US': [u"This is the forecast for {0}, {1}"]
}

yweather = "{http://xml.weather.yahoo.com/ns/rss/1.0}"
geo = "{http://www.w3.org/2003/01/geo/wgs84_pos#}"
place = "{http://where.yahooapis.com/v1/schema.rng}"

idFinder = re.compile("/(?P<locationID>[A-z0-9_]+).html")

class yahooWeather(Plugin):
    
    def __init__(self):
        super(yahooWeather, self).__init__()
        self.loopcounter = 0
    
    
    def showWaitPlease(self, language):
        rootAnchor = UIAddViews(self.refId)
        rootAnchor.dialogPhase = rootAnchor.DialogPhaseReflectionValue
        
        waitView = UIAssistantUtteranceView()
        waitView.text = waitView.speakableText = random.choice(waitText[language])
        waitView.listenAfterSpeaking = False
        waitView.dialogIdentifier = "Misc#ident" # <- what is the correct one for this?
        
        rootAnchor.views = [waitView]
        
        self.sendRequestWithoutAnswer(rootAnchor)
    
    
    def getWeatherLocation(self, locationId, xml):
        item = xml.find("channel/item")
        location = xml.find("channel/{0}location".format(yweather))
        
        weatherLocation = WeatherLocation()
        if location is None:
            return weatherLocation
        
        weatherLocation.city = location.get("city")
        weatherLocation.countryCode = location.get("country")
        weatherLocation.latitude = item.find("{0}lat".format(geo)).text
        weatherLocation.longitude = item.find("{0}long".format(geo)).text
        weatherLocation.locationId = locationId
        weatherLocation.stateCode = location.get("region")
        weatherLocation.accuracy = weatherLocation.AccuracyBestValue
        return weatherLocation
    
    def getWeatherUnits(self, xml):
        units = xml.find("channel/{0}units".format(yweather))
        
        weatherUnits = WeatherUnits()
        if units is None:
            return weatherUnits
        
        ydistance = units.get("distance")
        if ydistance == "mi":
            weatherUnits.distanceUnits = weatherUnits.DistanceUnitsMilesValue
        elif ydistance == "km":
            weatherUnits.distanceUnits = weatherUnits.DistanceUnitsKilometersValue
        elif ydistance == "m":
            weatherUnits.distanceUnits = weatherUnits.DistanceUnitsMetersValue
        elif ydistance == "ft":
            weatherUnits.distanceUnits = weatherUnits.DistanceUnitsFeetValue
            
        ypressure = units.get("pressure")
        if ypressure == "mb":
            weatherUnits.pressureUnits = weatherUnits.PressureUnitsMBValue
        elif ypressure == "in":
            weatherUnits.pressureUnits = weatherUnits.PressureUnitsINValue
            
        yspeed = units.get("speed")
        if yspeed == "km/h":
            weatherUnits.speedUnits = weatherUnits.SpeedUnitsKPHValue
        elif yspeed == "mph":
            weatherUnits.speedUnits = weatherUnits.SpeedUnitsMPHValue
            
        ytemp = units.get("temperature")
        if ytemp == "F":
            weatherUnits.temperatureUnits = weatherUnits.TemperatureUnitsFahrenheitValue
        elif ytemp == "C":
            weatherUnits.temperatureUnits = weatherUnits.TemperatureUnitsCelsiusValue
        
        return weatherUnits
    
    def getWeatherBarometrics(self, xml):
        barometric = xml.find("channel/{0}atmosphere".format(yweather))
        
        weatherBaro = WeatherBarometricPressure()
        if barometric is None:
            return weatherBaro
        
        yrising = barometric.get("rising")
        if yrising == "0":
            weatherBaro.trend = weatherBaro.TrendSteadyValue
        elif yrising == "1":
            weatherBaro.trend = weatherBaro.TrendRisingValue
        elif yrising == "2":
            weatherBaro.trend = weatherBaro.TrendFallingValue
        weatherBaro.value = barometric.get("pressure")
        
        return weatherBaro
    
    
    def getWeatherWind(self, xml):
        wind = xml.find("channel/{0}wind".format(yweather))
        weatherWind = WeatherWindSpeed()
        if wind is None:
            return weatherWind
        
        weatherWind.value = wind.get("speed")
        weatherWind.windDirectionDegree = int(wind.get("direction"))
        
        # north is 0 make intervals from -22.5,+22.5 results in 45 interval for each direction
        if weatherWind.windDirectionDegree >= 337.5 and weatherWind.windDirectionDegree <= 22.5:
            weatherWind.windDirection = weatherWind.DirectionNorthValue
        elif weatherWind.windDirectionDegree >= 22.5 and weatherWind.windDirectionDegree <= 67.5:
            weatherWind.windDirection = weatherWind.DirectionNorthEastValue
        elif weatherWind.windDirectionDegree >= 67.5 and weatherWind.windDirectionDegree <= 112.5:
            weatherWind.windDirection = weatherWind.DirectionEastValue
        elif weatherWind.windDirectionDegree >= 112.5 and weatherWind.windDirectionDegree <= 157.5:
            weatherWind.windDirection = weatherWind.DirectionSouthEastValue
        elif weatherWind.windDirectionDegree >= 157.5 and weatherWind.windDirectionDegree <= 202.5:
            weatherWind.windDirection = weatherWind.DirectionSouthValue
        elif weatherWind.windDirectionDegree >= 202.5 and weatherWind.windDirectionDegree <= 247.5:
            weatherWind.windDirection = weatherWind.DirectionSouthWestValue
        elif weatherWind.windDirectionDegree >= 247.5 and weatherWind.windDirectionDegree <= 292.5:
            weatherWind.windDirection = weatherWind.DirectionWestValue
        elif weatherWind.windDirectionDegree >= 292.5 and weatherWind.windDirectionDegree <= 337.5:
            weatherWind.windDirection = weatherWind.DirectionNorthWestValue
        return weatherWind
    
    def getWeatherCurrentConditions(self, xml):
        item = xml.find("channel/item")
        wind = xml.find("channel/{0}wind".format(yweather))
        barometric = xml.find("channel/{0}atmosphere".format(yweather))
        astronomy = xml.find("channel/{0}astronomy".format(yweather))
        currentCondition = item.find("{0}condition".format(yweather))
        
        if currentCondition is None:
            return None
        weatherCondition = WeatherCondition()
        weatherCondition.conditionCodeIndex = int(currentCondition.get("code"))
        weatherCondition.conditionCode = weatherCondition.ConditionCodeIndexTable[weatherCondition.conditionCodeIndex]
        
        current = WeatherCurrentConditions()
        current.dayOfWeek = currentCondition.get("date").split(",")[0]
        current.temperature = currentCondition.get("temp")
        current.barometricPressure = self.getWeatherBarometrics(xml)
        current.condition = weatherCondition
        current.percentHumidity = barometric.get("humidity")
        current.sunrise = astronomy.get("sunrise")
        current.sunset = astronomy.get("sunset")
        current.temperature = currentCondition.get("temp")
        current.timeOfObservation = xml.find("channel/lastBuildDate").text
        current.visibility = barometric.get("visibility")
        current.windChill = wind.get("chill")
        current.windSpeed = self.getWeatherWind(xml)
        return current
        

    def showCurrentWeatherWithWOEID(self, language, woeid, metric = True):
        # we can only get 2 day weather with woeid that suxx
        weatherLookup = "http://weather.yahooapis.com/forecastrss?w={0}&u={1}".format(woeid, "c" if metric else "f")
        result = getWebsite(weatherLookup, timeout=5)
        if result == None:
            self.say(random.choice(errorText[language]))
            self.complete_request()
            return
        
        result = ElementTree.XML(result)
        
        #get the item
        item = result.find("channel/item")
        if item is None:
            self.say(random.choice(noDataForLocationText[language]))
            self.complete_request()
            return
        
        # they change the language code using the other forecast link..
        weatherLocation = None
        
        match = idFinder.search(item.find("link").text)
        if match != None:
            loc = match.group('locationID')
            weatherLocation = self.getWeatherLocation(loc[:-2], result)
            fiveDayForecast = "http://xml.weather.yahoo.com/forecastrss/{0}.xml".format(loc)
            
            
            try:
                result = self.getWebsite(fiveDayForecast, timeout=5)
                result = ElementTree.XML(result)
                item = result.find("channel/item")
            except:
                pass
        
        if weatherLocation == None:
            weatherLocation = self.getWeatherLocation(woeid, result)
        
        if item is None:
            self.say(random.choice(noDataForLocationText[language]))
            self.complete_request()
            return
        
        forecast = WeatherObject()
        forecast.currentConditions = self.getWeatherCurrentConditions(result)
        if forecast.currentConditions == None:
            self.say(random.choice(noDataForLocationText[language]))
            self.complete_request()
            return
        
        forecast.extendedForecastUrl = item.find("link").text
        forecast.units = self.getWeatherUnits(result)
        forecast.view = forecast.ViewDAILYValue
        forecast.weatherLocation = weatherLocation
        forecast.hourlyForecasts = []
        
        dailyForecasts = []
        for dailyForecast in result.findall("channel/item/{0}forecast".format(yweather)):
            weatherDaily = WeatherDailyForecast()
            weatherDaily.timeIndex = appleWeek[dailyForecast.get("day")]
            weatherDaily.lowTemperature = int(dailyForecast.get("low"))
            weatherDaily.highTemperature = int(dailyForecast.get("high"))
            weatherDaily.isUserRequested = True
            dailyCondition = WeatherCondition()
            dailyCondition.conditionCodeIndex = int(dailyForecast.get("code"))
            dailyCondition.conditionCode = dailyCondition.ConditionCodeIndexTable[dailyCondition.conditionCodeIndex]
            weatherDaily.condition = dailyCondition
            dailyForecasts.append(weatherDaily)
    
        forecast.dailyForecasts = dailyForecasts
        snippet = WeatherForecastSnippet()
        snippet.aceWeathers = [forecast]
        
        showViewsCMD = UIAddViews(self.refId)
        showViewsCMD.dialogPhase = showViewsCMD.DialogPhaseSummaryValue
        displaySnippetTalk = UIAssistantUtteranceView()
        displaySnippetTalk.dialogIdentifier = "Weather#forecastCommentary"
        countryName = countries[forecast.weatherLocation.countryCode.lower()] if forecast.weatherLocation.countryCode.lower() in countries else forecast.weatherLocation.countryCode
        displaySnippetTalk.text = displaySnippetTalk.speakableText = random.choice(dailyForcast[language]).format(forecast.weatherLocation.city, countryName)
        
        showViewsCMD.views = [displaySnippetTalk, snippet]
        
        self.sendRequestWithoutAnswer(showViewsCMD)
        self.complete_request()
        
    def getNameFromGoogle(self, request):
        try:
            result = getWebsite(request, timeout=5)
            root = ElementTree.XML(result)
            location = root.find("result/formatted_address")
            location = location.text
            return location
        except:
            return None
    
    @register("en-US", "(what( is|'s) the )?weather( like)? in (?P<location>[\w ]+?)$")
    @register('de-DE', "(wie ist das )?wetter in (?P<location>[\w ]+?)$")
    def forcastWeatherAtLocation(self, speech, language, regex):
        self.showWaitPlease(language)
        location = regex.group("location")
        # lets refine the location using google
        googleGuesser = "http://maps.googleapis.com/maps/api/geocode/xml?address={0}&sensor=false&language={1}".format(urllib.quote(location.encode("utf-8")), language)
        googleLocation = self.getNameFromGoogle(googleGuesser)
        if googleLocation != None:
            location = googleLocation
            
        query = u"select woeid, placeTypeName from geo.places where text=\"{0}\" limit 1".format(location)
        lookup = u"http://query.yahooapis.com/v1/public/yql?q={0}&format=xml".format(urllib.quote(query.encode("utf-8")))
        #lookup = "http://where.yahooapis.com/geocode?location={0}&appid={1}".format(urllib.quote(location.encode("utf-8")), yahooAPIkey)
        
        result = getWebsite(lookup, timeout=5)
        if result == None:
            self.say(random.choice(errorText[language]))
            self.complete_request()
            return
        
        root = ElementTree.XML(result)
        placeTypeCode = root.find("results/{0}place/{0}placeTypeName".format(place))
        woeidElem = root.find("results/{0}place/{0}woeid".format(place))
        
        if woeidElem is None or placeTypeCode is None:
            self.say(random.choice(noDataForLocationText[language]))
            self.complete_request()
            return
        
        if placeTypeCode.get("code") != "7": #damn is this not a city
            # lets ask google what it think
            googleCapitalResolver = "http://maps.googleapis.com/maps/api/geocode/xml?address=capital%20of%20{0}&sensor=false&language={1}".format(urllib.quote(location.encode("utf-8")), language)
            location = self.getNameFromGoogle(googleCapitalResolver)
            if location != None and self.loopcounter < 2:
                x = re.match("(?P<location>.*)", location)
                # ok we should now have more details, lets call our self
                self.loopcounter += 1
                self.forcastWeatherAtLocation(speech, language, x)
                return
            else:
                self.say(random.choice(errorText[language]))
                self.complete_request()
                return
        
        self.showCurrentWeatherWithWOEID(language, woeidElem.text)
        
    @register("en-US", "weather|forecast")
    @register("de-DE", "wetter(vorhersage)?")
    def forcastWeatherAtCurrentLocation(self, speech, language):
        location = self.getCurrentLocation()
        self.showWaitPlease(language)
        
        lng = location.longitude
        lat = location.latitude
        
        # we need the corresponding WOEID to the location
        query = "select woeid from geo.places where text=\"{0},{1}\"".format(lat,lng)
        reverseLookup = "http://query.yahooapis.com/v1/public/yql?q={0}&format=xml".format(urllib.quote(query.encode("utf-8")))
        #reverseLookup = "http://where.yahooapis.com/geocode?location={0},{1}&gflags=R&appid={2}".format(lat, lng, yahooAPIkey)
        result = getWebsite(reverseLookup, timeout=5)
        if result == None:
            self.say(random.choice(errorText[language]))
            self.complete_request()
            return
        
        root = ElementTree.XML(result)
        woeidElem = root.find("results/{0}place/{0}woeid".format(place))
        
        
        
        if woeidElem is None:
            self.say(random.choice(noDataForLocationText[language]))
            self.complete_request()
            return
        
        
        self.showCurrentWeatherWithWOEID(language, woeidElem.text)
        
        
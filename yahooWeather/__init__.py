#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# This is a weather plugin for SiriServerCore  
# created by Eichhoernchen
#
# It uses various the services from yahoo
#
# You must obtain an API-key to use it
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

from plugin import *
from siriObjects.weatherObjects import WeatherHourlyForecast,\
    WeatherCurrentConditions, WeatherCondition
import random
import urllib2
from xml.etree import ElementTree

# obtain the api key for worldweatheronline
# if no key is there this will kill the plugin loading process and inform user
yahooAPIkey = APIKeyForAPI("yahoo")


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

class yahooWeather(Plugin):
    
    
    def showWaitPlease(self, language):
        rootAnchor = UIAddViews(self.refId)
        rootAnchor.dialogPhase = rootAnchor.DialogPhaseReflectionValue
        
        waitView = UIAssistantUtteranceView()
        waitView.text = waitView.speakableText = random.choice(waitText[language])
        waitView.listenAfterSpeaking = False
        waitView.dialogIdentifier = "Misc#ident" # <- what is the correct one for this?
        
        rootAnchor.views = [waitView]
        
        self.sendRequestWithoutAnswer(rootAnchor)
    
    def showCurrentWeatherWithWOEID(self, language, woeid, metric = True):
        weatherLookup = "http://weather.yahooapis.com/forecastrss?w={0}&u={1}".format(woeid, "c" if metric else "f")
        result = None
        try:
            result = urllib2.urlopen(weatherLookup, timeout=5).read()
        except:
            self.say(random.choice(errorText[language]))
            self.complete_request()
            return
        
        #get the item
        item = result.find("rss/channel/item")
        if item is None:
            self.say(noDataForLocationText[language])
            self.complete_request()
            return
        
        currentCondition = item.find("yweather:condition")
        if currentCondition is None:
            self.say(noDataForLocationText[language])
            self.complete_request()
            return
        
        
        condition = WeatherCondition()
        condition.conditionCodeIndex = currentCondition.get("code")
        condition.conditionCode = condition.ConditionCodeIndexTable[condition.conditionCodeIndex]
        
        today = currentCondition.get("date").split(",")[0]
        
        current = WeatherCurrentConditions()
        current.dayOfWeek = today
        current.barometricPressure
        
        current.condition = condition
        for foreCast in item.finall("yweather:forecast"):
            foreCast
    
    @register("en-US", "weather|forecast")
    def currentWeatherAtCurrentLocation(self, speech, language):
        location = self.getCurrentLocation()
        self.showWaitPlease(language)
        
        lng = location.longitude
        lat = location.latitude
        
        # we need the corresponding WOEID to the location
        reverseLookup = "http://where.yahooapis.com/geocode?location={0},{1}&gflags=R&appid={2}".format(lat, lng, yahooAPIkey)
        result = None
        try:
            result = urllib2.urlopen(reverseLookup, timeout=5).read()
        except:
            self.say(random.choice(errorText[language]))
            self.complete_request()
            return
        
        root = ElementTree.XML(result)
        woeidElem = root.find("Result/woeid")
        
        if woeidElem is None:
            self.say(noDataForLocationText[language])
            self.complete_request()
            return
        
        self.showCurrentWeatherWithWOEID(language, woeidElem.text)
        
        
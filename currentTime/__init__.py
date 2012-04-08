#!/usr/bin/python
# -*- coding: utf-8 -*-

from plugin import *
from siriObjects.clockObjects import ClockSnippet, ClockObject
import json
import random
import types
import urllib
import urllib2




localizations = {
    "search":
    {
      "de-DE": [u"Es wird gesucht ..."], 
      "en-US": [u"Looking up ..."]
    },                  
    "currentTime": 
    {
     "de-DE": [u"Es ist @{fn#currentTime}"], 
     "en-US": [u"It is @{fn#currentTime}"]
    }, 
    "currentTimeIn": 
    {
      "de-DE": [u"Die Uhrzeit in {0} ist @{{fn#currentTimeIn#{1}}}:"], 
      "en-US": [u"The time in {0} is @{{fn#currentTimeIn#{1}}}:"]
    },
    "failure":
    {
      "de-DE": [u"Es tut mir leid aber für eine Anfrage habe ich keine Uhrzeit."],
      "en-US": [u"I'm sorry but I don't have a time for this request"]
    }
}
def getNameFromGoogle(request):
    try:
        result = getWebsite(request, timeout=5)
        root = json.loads(result)
        location = root["results"][0]["formatted_address"]
        return location
    except:
        return None



class currentTime(Plugin):
    
    def showWait(self, language):
        textView = UIAssistantUtteranceView()
        textView.speakableText = textView.text = random.choice(localizations['search'][language])
        textView.dialogIdentifier = "Clock#getTime"

        rootAnchor = UIAddViews(self.refId)
        rootAnchor.dialogPhase = rootAnchor.DialogPhaseReflectionValue
        rootAnchor.scrollToTop = False
        rootAnchor.temporary = False
        rootAnchor.views = [textView]  
        
        self.sendRequestWithoutAnswer(rootAnchor)

    @register("de-DE", "(Wie ?viel Uhr.*)|(.*Uhrzeit.*)")     
    @register("en-US", "(What.*time.*)|(.*current time.*)")
    def currentTime(self, speech, language):
        #first tell that we look it up
        self.showWait(language)
        
        
        textView = UIAssistantUtteranceView()
        textView.text = textView.speakableText = random.choice(localizations["currentTime"][language])
        textView.dialogIdentifier = "Clock#showTimeInCurrentLocation"
        textView.listenAfterSpeaking = False
        
        clock = ClockObject()
        clock.timezoneId = self.connection.assistant.timeZoneId
        
        clockView = ClockSnippet()
        clockView.clocks = [clock]
        
        rootAnchor = UIAddViews(self.refId)
        rootAnchor.dialogPhase = rootAnchor.DialogPhaseSummaryValue
        rootAnchor.views = [textView, clockView]
        
        
        self.sendRequestWithoutAnswer(rootAnchor)
        self.complete_request()
    
    @register("de-DE", "(Wieviel Uhr.*in|Uhrzeit.*in) (?P<loc>[\w ]+)")
    @register("en-US", "(What.*time.*in|.*current time.*in) (?P<loc>[\w ]+)")
    def currentTimeIn(self, speech, language, matchedRegex):
        
        self.showWait(language)
        
        location = matchedRegex.group("loc")
        # ask google to enhance the request
        googleGuesser = "http://maps.googleapis.com/maps/api/geocode/json?address={0}&sensor=false&language={1}".format(urllib.quote(location.encode("utf-8")), language)
        googleLocation = getNameFromGoogle(googleGuesser)
        if googleLocation != None:
            location = googleLocation
        
        self.logger.debug(u"User requested time in: {0}".format(location))
        # ask yahoo for a timezoneID
        query = u"select name from geo.places.belongtos where member_woeid in (select woeid from geo.places where text=\"{0}\") and placetype=31".format(location.encode("utf-8"))
        request = u"http://query.yahooapis.com/v1/public/yql?q={0}&format=json&callback=".format(urllib.quote(query.encode("utf-8")))
        timeZoneId = None
        try:
            result = getWebsite(request, timeout=5)
            root = json.loads(result)
            place = root["query"]["results"]["place"]
            if type(place) == types.ListType:
                place = place[0]
            
            timeZoneId = place["name"]
        except:
            self.logger.exception("Error getting timezone")
        
        if timeZoneId == None:
            self.say(random.choice(localizations['failure'][language]))
            self.complete_request()
            return
        
        clock = ClockObject()
        clock.timezoneId = timeZoneId
        
        clockView = ClockSnippet()
        clockView.clocks = [clock]
        
        textView = UIAssistantUtteranceView()
        textView.listenAfterSpeaking = False
        textView.dialogIdentifier = "Clock#showTimeInOtherLocation"
        textView.text = textView.speakableText = random.choice(localizations["currentTimeIn"][language]).format(location, timeZoneId)
        
        rootAnchor = UIAddViews(self.refId)
        rootAnchor.dialogPhase = rootAnchor.DialogPhaseSummaryValue
        rootAnchor.scrollToTop = False
        rootAnchor.temporary = False
        rootAnchor.views = [textView, clockView]
        
        self.sendRequestWithoutAnswer(rootAnchor)
        self.complete_request()

## we should implement such a command if we cannot get the location however some structures are not implemented yet
#{"class"=>"AddViews",
#    "properties"=>
#        {"temporary"=>false,
#            "dialogPhase"=>"Summary",
#            "scrollToTop"=>false,
#            "views"=>
#                [{"class"=>"AssistantUtteranceView",
#                 "properties"=>
#                 {"dialogIdentifier"=>"Common#unresolvedExplicitLocation",
#                 "speakableText"=>
#                 "Ich weiß leider nicht, wo das ist. Wenn du möchtest, kann ich im Internet danach suchen.",
#                 "text"=>
#                 "Ich weiß leider nicht, wo das ist. Wenn du möchtest, kann ich im Internet danach suchen."},
#                 "group"=>"com.apple.ace.assistant"},
#                 {"class"=>"Button",
#                 "properties"=>
#                 {"commands"=>
#                 [{"class"=>"SendCommands",
#                  "properties"=>
#                  {"commands"=>
#                  [{"class"=>"StartRequest",
#                   "properties"=>
#                   {"handsFree"=>false,
#                   "utterance"=>
#                   "^webSearchQuery^=^Amerika^^webSearchConfirmation^=^Ja^"},
#                   "group"=>"com.apple.ace.system"}]},
#                  "group"=>"com.apple.ace.system"}],
#                 "text"=>"Websuche"},
#                 "group"=>"com.apple.ace.assistant"}]},
#    "aceId"=>"fbec8e13-5781-4b27-8c36-e43ec922dda3",
#    "refId"=>"702C0671-DB6F-4914-AACD-30E84F7F7DF3",
#    "group"=>"com.apple.ace.assistant"}
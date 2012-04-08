#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# This is a epg plugin for SiriServerCore  
# created by Eichhoernchen
#
# This file is free for private use, you need a commercial license for paid servers
#
# Also you must comply with http://tvprofil.net/ usage license for commercial use
# private use is for free
#
# It's distributed under the same license as SiriServerCore
#
# You can view the license here:
# https://github.com/Eichhoernchen/SiriServerCore/blob/master/LICENSE
#
# So if you have a SiriServerCore commercial license 
# you are allowed to use this plugin commercially otherwise you are breaking the law
#
# This file can be freely modified, but this header must retain untouched
#
#
# This plugin uses data from http://tvprofil.net/xmltv/ 
#  
# 

from Queue import Queue, Empty
from plugin import *
from xml.etree import ElementTree
import datetime
import time
import urllib2
from operator import itemgetter

# mapping forged from http://tvprofil.net/xmltv/
channels = [
    (["pro7", "pro 7", "pro sieben"], 'pro-7.de'),
    (["sat1", "sat 1", "sat eins"], 'sat-1.de'),
    (['rtl'], 'rtl.de.de'),
    (["rtl 2", "rtl2", "rtl zwei"], 'rtl-2.de'),
    (["3sat", "drei sat", "3 sat"], '3sat.de'),
    (['ard', 'das erste', 'dem ersten'], 'ard.de'),
    (['bayrisches fernsehen', 'bayern', 'bayern 3', 'bayern3', 'bayern drei'], 'bayern3.de'),
    (['hessischer rundfunk', 'hessen', 'hessen drei', 'hessen3', 'hessen 3'],'hr3.de'), 
    (['kabel1', 'kabel 1', 'kabel eins'], 'kabel-1.de'),
    (['zdf', 'das zweite', 'dem zweiten'], 'zdf.de'),
    (['vox'], 'vox.de'),
    (['comedy central'], 'comedy-central.de'),
    (['arte'], 'arte.de')
]

def program_from_xml(xml, lookupTime, inBetween=False):
    channel_name = xml.find("channel/display-name").text
    
    program = []
    for node in xml.findall('programme'):
        prog_date_start = datetime.datetime.strptime(node.get('start'), "%Y%m%d%H%M%S")
        prog_date_end = datetime.datetime.strptime(node.get('stop'), "%Y%m%d%H%M%S")
        include = False
        if inBetween:
            include = (lookupTime >= prog_date_start) and (lookupTime <= prog_date_end)
        else:
            include = prog_date_start >= lookupTime 
        if include:
            TitleData = node.find("title").text.split(',')
            title = TitleData[0]
            if len(TitleData) > 1:
                subTitle = u",".join(TitleData[1:]).strip()
            else:
                subTitle = u""
            program.append((channel_name, title, subTitle, prog_date_start, prog_date_end))
    return program

class ThreadProcessor(threading.Thread):
    def __init__(self, inQueue, outQueue, lookupTime, inBetween):
        self.queue = inQueue
        self.inBetween = inBetween
        self.lookupTime = lookupTime
        self.resultQueue = outQueue
        threading.Thread.__init__(self)
 
    
 
    def run(self):
        while True:
            #grabs host from queue
            try:
                host = self.queue.get()
            except Empty:
                break
            
            try:
                xml = getWebsite(host, timeout=5)
                xml = ElementTree.XML(xml)
                self.resultQueue.add_item(program_from_xml(xml, self.lookupTime, self.inBetween))
                
            except:
                pass
            #signals to queue job is done
            self.queue.task_done()

def getDailyProgramWithConstrains(lookupTime, inBetween=False):
    # we should get and process all that this in threads for speedup
    # spawn a pool of threads, and pass them queue instance
    inQueue = Queue()
    
    #populate queue with data   
    for _, channel_id in channels:
        daily = "http://tvprofil.net/xmltv/data/{0}/{1:%Y-%m-%d}_{0}_tvprofil.net.xml".format(channel_id, lookupTime)
        inQueue.put(daily)
    
    class ResultList():
        def __init__(self):
            self.lock = threading.Lock()
            self.items = []
            
        def add_item(self, x):
            with self.lock:
                self.items += x
         
    outQueue = ResultList()
    for i in range(5):
        t = ThreadProcessor(inQueue, outQueue, lookupTime, inBetween)
        t.setDaemon(True)
        t.start()
        
    inQueue.join()
    # now lets get a list of all programs which we can sort by start time
    dailyProgram = outQueue.items
    
    program = sorted(dailyProgram, key=itemgetter(3, 0))
    return program
    
class ElectronicProgramGuide(Plugin):
    
    
    def printProgram(self, program):
        if len(program) > 0:
            for entry in program:
                channel_name, title, subTitle, prog_date_start, prog_date_end = entry
                text = u"Um {0:%H:%M} Uhr auf {1}: {2}, {3}".format(prog_date_start, channel_name, title, subTitle)
                if prog_date_start.minute != 0:
                    sayText = u"Um {0:%H} Uhr {0:%M} auf {1}: {2}, {3}".format(prog_date_start, channel_name, title, subTitle)
                else:
                    sayText = u"Um {0:%H} Uhr auf {1}: {2}, {3}".format(prog_date_start, channel_name, title, subTitle)
                self.say(text, sayText)
        else:
            self.say(u"Entschuldigung aber ich habe keine Einträge gefunden.")
    
    
    @register("de-DE", u"Was (kommt|läuft) (?P<when>heute|morgen) (?P<late>spät )?(abend|abends) im Fernsehen")
    def eveningLate(self, speech, language, regex):
        late = 'late' in regex.groupdict()
        today = regex.group('when') == "heute"
        if today:
            lookupTime = datetime.datetime.today() 
        else:
            lookupTime = datetime.datetime.today() + datetime.timedelta(days=1)
        if not late:
            lookupTime = datetime.datetime(lookupTime.year, lookupTime.month, lookupTime.day, 20, 0, 0)
        else:
            lookupTime = datetime.datetime(lookupTime.year, lookupTime.month, lookupTime.day, 22, 0, 0)
            
            
        self.say(u"Einen Moment geduld bitte")
        
        program = getDailyProgramWithConstrains(lookupTime)
        self.printProgram(program)
        self.complete_request()
        
        
    
    @register("de-DE", u"Was (kommt|läuft) (jetzt|(gerade|grade|grad)|jetzt (gerade|grade|grad)|im moment) im Fernsehen")
    def now(self, speech, language):
        
        lookupTime = datetime.datetime.now() 
    
        self.say(u"Einen Moment geduld bitte")
        
        program = getDailyProgramWithConstrains(lookupTime, True)
        self.printProgram(program)
        self.complete_request()
    
    @register("de-DE", u"Was (kommt|läuft) (jetzt|(gerade|grade|grad)|jetzt (gerade|grade|grad)|im moment) auf (?P<channel>[\w ]+)")
    def nowOnChannel(self, speech, language, regex):
        channel = regex.group('channel').strip().lower()
        
        lookupTime = datetime.datetime.now()
        
        channel_id = None
        for channelNames, channelId in channels:
            if channel in channelNames:
                channel_id = channelId
                break
        
        if (channel_id == None):
            self.say("Entschuldigung den Sender kenne ich nicht!")
            self.complete_request()
            return
    
        daily = "http://tvprofil.net/xmltv/data/{0}/{1:%Y-%m-%d}_{0}_tvprofil.net.xml".format(channel_id, lookupTime)
             
        
        xml = getWebsite(daily, timeout=5)
        if xml == None:
            self.say("Ups, ich konnte keine Daten empfangen, versuch es später nocheinmal")
            self.complete_request()
            return
        
        # format for date is %Y%m%d%H%M%S
        
        xml = ElementTree.XML(xml)
        
        program = program_from_xml(xml, lookupTime, True)
        self.printProgram(program)
        self.complete_request() 
    
    @register("de-DE", u"Was (läuft|kommt) (?P<when>heute|morgen) abend auf (?P<channel>[\w ]+)")
    def evening(self, speech, language, regex):
        
        channel = regex.group('channel').strip().lower()
        today = regex.group('when') == "heute"
        if today:
            lookupTime = datetime.datetime.today() 
        else:
            lookupTime = datetime.datetime.today() + datetime.timedelta(days=1)
            
        lookupTime = datetime.datetime(lookupTime.year, lookupTime.month, lookupTime.day, 20, 0, 0)
        
        channel_id = None
        for channelNames, channelId in channels:
            if channel in channelNames:
                channel_id = channelId
                break
        
        if (channel_id == None):
            self.say("Entschuldigung den Sender kenne ich nicht!")
            self.complete_request()
            return
        
        daily = "http://tvprofil.net/xmltv/data/{0}/{1:%Y-%m-%d}_{0}_tvprofil.net.xml".format(channel_id, lookupTime)
             
        xml = getWebsite(daily, timeout=5)
        if xml == None:
            self.say("Ups, ich konnte keine Daten empfangen, versuch es später nocheinmal")
            self.complete_request()
            return
        
        xml = ElementTree.XML(xml)
        
        program = program_from_xml(xml, lookupTime)
        self.printProgram(program)
        self.complete_request() 

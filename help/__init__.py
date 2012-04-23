#!/usr/bin/python
# -*- coding: utf-8 -*-
#by Joh Gerna thanks for help to john-dev
#updated by Mike Pissanos (gaVRoS) for SiriServerCore
#altered by Devon Stewart (blast_hardcheese) to improve reliability

import re,os

from plugin import *

from PluginManager import plugins

class help(Plugin):
    __examples__= {
        'en-US': (
            'Help:\n'
            '  Help\n'
            '  Commands\n'
        ),
    }

    @register("de-DE", "(Hilfe)|(Befehle)")
    @register("en-US", "(Help)|(Commands)")
    def st_hello(self, speech, language):
        resp = {}
        for lang in plugins: # This dict may change, no way to cache reliably
            langresp = resp.setdefault(lang, [])
            if not lang == language: continue
            
            classes = []
            for rexp, Class, func in plugins.get(lang, []):
                if not Class in classes:
                    classes.append(Class)

            for Class in classes:
                if hasattr(Class, "__examples__"):
                    langresp.append(Class.__examples__.get(lang, "N/A"))

        r = '\n'.join(resp[language]).strip()
        if language == 'de-DE':
            self.say("Das sind die Befehle die in Deiner Sprache verfügbar sind:")
            self.say(r, " ")
        else:
            self.say("Here are the commands which are possible in your language:")
            self.say(r, " ")
        self.complete_request()

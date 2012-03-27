#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# This is a sms plugin for SiriServerCore  
# created by Eichhoernchen
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
# This file can be freely modified, but this header must retain untouched
#  
# 

from plugin import *
from siriObjects.baseObjects import ObjectIsCommand
from siriObjects.contactObjects import PersonSearch, PersonSearchCompleted
from siriObjects.smsObjects import SmsSms, SmsSnippet
from siriObjects.systemObjects import SendCommands, StartRequest, \
    PersonAttribute, Person, DomainObjectCreate, DomainObjectCreateCompleted, \
    DomainObjectUpdate, DomainObjectUpdateCompleted, DomainObjectRetrieve, \
    DomainObjectRetrieveCompleted, DomainObjectCommit, DomainObjectCommitCompleted, \
    DomainObjectCancel, DomainObjectCancelCompleted
from siriObjects.uiObjects import UIDisambiguationList, UIListItem, \
    UIConfirmationOptions, ConfirmSnippet, UIConfirmSnippet, UICancelSnippet
import datetime
import random
#import pytz

responses = {
'notFound': 
    {'de-DE': u"Entschuldigung, ich konnte niemanden in deinem Telefonbuch finden der so heißt",
     'en-US': u"Sorry, I did not find a match in your phone book"
    },
'devel':
    {'de-DE': u"Entschuldigung, aber diese Funktion befindet sich noch in der Entwicklungsphase",
     'en-US': u"Sorry this feature is still under development"
    },
 'select':
    {'de-DE': u"Wen genau?", 
     'en-US': u"Which one?"
    },
'selectNumber':
    {'de-DE': u"Welche Telefonnummer für {0}",
     'en-US': u"Which phone one for {0}"
    },
'mustRepeat': 
    {'de-DE': [u"Entschuldigung ich hab dich leider nicht verstanden."],
     'en-US': [u"Sorry, I did not understand, please try again", u"Sorry, I don't know what you want"]
     },
'askForMessage':
    {'de-DE': [u"Was willst du schreiben?", u"Was soll drin stehen?", u"Du kannst mir jetzt diktieren!"],
     'en-US': [u"What do you want to say?", u"What do you want to include in the message?", u"Please dictate me the contents!"]
     },
'showUpdate': 
    {'de-DE': [u"Ich hab deine Nachricht geschrieben. Willst du sie jetzt senden?", u"OK. Willst du die Nachricht jetzt senden?"],
     'en-US': [u"I updated your message. Ready to send it?", u"Ok, I got that, do you want to send it?", u"Thanks, do you want to send it now?"]
     },
'cancelSms': 
    {'de-DE': [u"OK, I schick sie nicht.", u"OK, ich hab sie verworfen"],
     'en-US': [u"OK, I won't send it.", u"OK, I deleted it."]
     },
'cancelFail':
    {'de-DE': [u"Sorry, aber mir ist ein Fehler beim Abbrechen passiert"],
     'en-US': [u"Sorry I could not properly cancel your message"]
     },
'createSmsFail':
    {'de-DE': [u"Ich konnte keine neue Nachricht anlegen, sorry"],
     'en-US': [u"I could not create a new message, sorry!"]
     },
'updateSmsFail':
    {'de-DE': [u"Entschuldigung ich konnte die Nachricht nicht schreiben"],
     'en-US': [u"Sorry, I could not update your message!"]
     },
'sendSms':
    {'de-DE': [u"OK, ich verschicke die Nachricht"],
     'en-US': [u"OK, I'll send your message."]
     },
'sendSmsFail':
    {'de-DE': [u"Umpf da ist was schief gelaufen, sorry"],
     'en-US': [u"Hm something gone wrong, I could not send the message, I'm very sorry"]
     },
'clarification':
    {'de-DE': [u"Fortfahren mit senden, abbrechen, anschauen oder ändern."],
     'en-US': [u"To continue, you can Send, Cancel, Review, or Change it."]
     }
}

questions = {
'answerSEND': 
    {'de-DE': ['yes', 'senden'], # you must include yes
     'en-US': ['yes', 'send']
     },
'answerCANCEL':
    {'de-DE': ['cancel', 'abbrechen', 'stop', 'nein'],  # you must include cancel
     'en-US': ['cancel', 'no', 'abort']
     },
'answerUPDATE':
    {'de-DE': ['ändern', 'verändern'],
     'en-US': ['change', 'update']
     },
'answerREVIEW':
    {'de-DE': ['anschauen', 'zeigen', 'zeig'],
     'en-US': ['review', 'view']
     }
}

snippetButtons = {
'denyText':
    {'de-DE': "Cancel",
     'en-US': "Cancel"
     },
'cancelLabel':
    {'de-DE': "Cancel",
     'en-US': "Cancel"
     },
'submitLabel':
    {'de-DE': "Send",
     'en-US': "Send"
     },
'confirmText':
    {'de-DE': "Send",
     'en-US': "Send"
     },
'cancelTrigger':
    {'de-DE': "Deny",
     'en-US': "Deny"
     }
}

speakableDemitter={
'en-US': u", or ",
'de-DE': u', oder '}


errorNumberTypes= {
'de-DE': u"Ich habe dich nicht verstanden, versuch es bitte noch einmal.",
'en-US': u"Sorry, I did not understand, please try again."
}

errorNumberNotPresent= {
'de-DE': u"Ich habe diese {0} von {1} nicht, aber eine andere.",
'en-US': u"Sorry, I don't have a {0} number from {1}, but another."
}


numberTypesLocalized= {
'_$!<Mobile>!$_': {'en-US': u"mobile", 'de-DE': u"Handynummer"},
'iPhone': {'en-US': u"iPhone", 'de-DE': u"iPhone-Nummer"},
'_$!<Home>!$_': {'en-US': u"home", 'de-DE': u"Privatnummer"},
'_$!<Work>!$_': {'en-US': u"work", 'de-DE': u"Geschäftsnummer"},
'_$!<Main>!$_': {'en-US': u"main", 'de-DE': u"Hauptnummer"},
'_$!<HomeFAX>!$_': {'en-US': u"home fax", 'de-DE': u'private Faxnummer'},
'_$!<WorkFAX>!$_': {'en-US': u"work fax", 'de-DE': u"geschäftliche Faxnummer"},
'_$!<OtherFAX>!$_': {'en-US': u"_$!<OtherFAX>!$_", 'de-DE': u"_$!<OtherFAX>!$_"},
'_$!<Pager>!$_': {'en-US': u"pager", 'de-DE': u"Pagernummer"},
'_$!<Other>!$_':{'en-US': u"other phone", 'de-DE': u"anderes Telefon"}
}

namesToNumberTypes = {
'de-DE': {'mobile': "_$!<Mobile>!$_", 'handy': "_$!<Mobile>!$_", 'zuhause': "_$!<Home>!$_", 'privat': "_$!<Home>!$_", 'arbeit': "_$!<Work>!$_"},
'en-US': {'work': "_$!<Work>!$_",'home': "_$!<Home>!$_", 'mobile': "_$!<Mobile>!$_"}
}

class shortMessaging(Plugin):
    
    def finalSend(self, sms, language):
        
        commitCMD = DomainObjectCommit(self.refId)
        commitCMD.identifier = SmsSms()
        commitCMD.identifier.identifier = sms.identifier
        
        answer = self.getResponseForRequest(commitCMD)
        if ObjectIsCommand(answer, DomainObjectCommitCompleted):
            answer = DomainObjectCommitCompleted(answer)
            # update the sms object with current identifier and time stamp
            sms.identifier = answer.identifier
            # the timestamp should be timezone aware
            # we could use the pytz lib for that
            # get the timezone from the assistant
            # and supply it to pytz which we can
            # supply to now()
            sms.dateSent = datetime.datetime.now() 
            # tell the user we sent the sms
            createAnchor = UIAddViews(self.refId)
            createAnchor.dialogPhase = createAnchor.DialogPhaseConfirmedValue
            
            # create a view to ask for the message
            askCreateView = UIAssistantUtteranceView()
            askCreateView.dialogIdentifier = "CreateSms#sentSMS"
            askCreateView.text = askCreateView.speakableText = random.choice(responses['sendSms'][language])
            askCreateView.listenAfterSpeaking = False
            
           
            snippet = SmsSnippet()
            snippet.smss = [sms]
            
            createAnchor.views = [askCreateView, snippet]
            
            self.sendRequestWithoutAnswer(createAnchor)
            self.complete_request()
        else:
            self.say(random.choice(responses['sendSmsFail'][language]))
            self.complete_request()
            
            
    def createSmsSnippet(self, sms, addConfirmationOptions, dialogIdentifier, text, language):
        createAnchor = UIAddViews(self.refId)
        createAnchor.dialogPhase = createAnchor.DialogPhaseConfirmationValue
        
        # create a view to ask for the message
        askCreateView = UIAssistantUtteranceView()
        askCreateView.dialogIdentifier = dialogIdentifier
        askCreateView.text = askCreateView.speakableText = text
        askCreateView.listenAfterSpeaking = True
        
        # create a snippet for the sms
        snippet = SmsSnippet()
        if addConfirmationOptions:
            # create some confirmation options
            conf = UIConfirmSnippet({})
            conf.requestId = self.refId
            
            confOpts = UIConfirmationOptions()
            confOpts.submitCommands = [SendCommands([conf, StartRequest(False, "^smsConfirmation^=^yes^")])]
            confOpts.confirmCommands = confOpts.submitCommands
            
            cancel = UICancelSnippet({})
            cancel.requestId = self.refId
            
            confOpts.cancelCommands = [SendCommands([cancel, StartRequest(False, "^smsConfirmation^=^cancel^")])]
            confOpts.denyCommands = confOpts.cancelCommands
            
            confOpts.denyText = snippetButtons['denyText'][language]
            confOpts.cancelLabel = snippetButtons['cancelLabel'][language]
            confOpts.submitLabel = snippetButtons['submitLabel'][language]
            confOpts.confirmText = snippetButtons['confirmText'][language]
            confOpts.cancelTrigger = snippetButtons['cancelTrigger'][language]
            
            snippet.confirmationOptions = confOpts
            
        snippet.smss = [sms]
        
        createAnchor.views = [askCreateView, snippet]
        
        return createAnchor
            
    def createNewMessage(self, phone, person):
        # create a new domain object the sms...
        x = SmsSms()
        x.recipients = [phone.number]
        msgRecipient = PersonAttribute()
        msgRecipient.object = Person()
        msgRecipient.object.identifier = person.identifier
        msgRecipient.data = phone.number
        msgRecipient.displayText = person.fullName
        x.msgRecipients = [msgRecipient]
        x.outgoing = True
        answer = self.getResponseForRequest(DomainObjectCreate(self.refId, x))
        if ObjectIsCommand(answer, DomainObjectCreateCompleted):
            answer = DomainObjectCreateCompleted(answer)
            x = SmsSms()
            x.outgoing = True
            x.identifier = answer.identifier
            return x
        else:
            return None
        
    def getSmssForIdentifier(self, identifier):
        # fetch the current version
        retrieveCMD = DomainObjectRetrieve(self.refId)
        x = SmsSms()
        x.identifier = identifier
        retrieveCMD.identifiers = [x]
        answer = self.getResponseForRequest(retrieveCMD)
        if ObjectIsCommand(answer, DomainObjectRetrieveCompleted):
            answer = DomainObjectRetrieveCompleted(answer)
            if len(answer.objects) > 1:
                self.logger.warning("I do not support multiple messages!")
            result = SmsSms()
            result.initializeFromPlist(answer.objects[0].to_plist())
            return result
        else:
            return None
        
    def askAndSetMessage(self, sms, language):
        createAnchor = self.createSmsSnippet(sms, False, "CreateSms#smsMissingMessage", random.choice(responses['askForMessage'][language]), language)

        smsText = self.getResponseForRequest(createAnchor)
        # update the domain object
        
        updateCMD = DomainObjectUpdate(self.refId)
        updateCMD.identifier = sms
        updateCMD.addFields = SmsSms()
        updateCMD.setFields = SmsSms()
        updateCMD.setFields.message = smsText
        updateCMD.removeFields = SmsSms()
        
        answer = self.getResponseForRequest(updateCMD)
        if ObjectIsCommand(answer, DomainObjectUpdateCompleted):
            return sms
        else:
            return None
            
    def showUpdateAndAskToSend(self, sms, language):
        createAnchor = self.createSmsSnippet(sms, True, "CreateSms#updatedMessageBody", random.choice(responses['showUpdate'][language]), language)
        
        response = self.getResponseForRequest(createAnchor)
        match = re.match("\^smsConfirmation\^=\^(?P<answer>.*)\^", response)
        if match:
            response = match.group('answer')
        
        return response
    
    def cancelSms(self, sms, language):
        # cancel the sms
        cancelCMD = DomainObjectCancel(self.refId)
        cancelCMD.identifier = SmsSms()
        cancelCMD.identifier.identifier = sms.identifier
        
        answer = self.getResponseForRequest(cancelCMD)
        if ObjectIsCommand(answer, DomainObjectCancelCompleted):
            createAnchor = UIAddViews(self.refId)
            createAnchor.dialogPhase = createAnchor.DialogPhaseCanceledValue
            cancelView = UIAssistantUtteranceView()
            cancelView.dialogIdentifier = "CreateSms#wontSendSms"
            cancelView.text = cancelView.speakableText = random.choice(responses['cancelSms'][language])
            createAnchor.views = [cancelView]
            
            self.sendRequestWithoutAnswer(createAnchor)
            self.complete_request()
        else:
            self.say(random.choice(responses['cancelFail'][language]))
            self.complete_request()
    
    def askForClarification(self, sms, language):
        createAnchor = self.createSmsSnippet(sms, True, "CreateSms#notReadyToSendSms", random.choice(responses['clarification'][language]), language)
        
        response = self.getResponseForRequest(createAnchor)
        match = re.match("\^smsConfirmation\^=\^(?P<answer>.*)\^", response)
        if match:
            response = match.group('answer')
            
        return response
        
    def message(self, phone, person, language):
        smsObj = self.createNewMessage(phone, person)
        if smsObj == None:
            self.say(random.choice(responses['createSmsFail'][language]))
            self.complete_request()
            return
        smsObj = self.askAndSetMessage(smsObj, language)
        if smsObj == None:
            self.say(random.choice(responses['updateSmsFail'][language]))
            self.complete_request()
            return
        satisfied = False
        state = "SHOW"
        
        # lets define a small state machine 
        while not satisfied:
            smsObj = self.getSmssForIdentifier(smsObj.identifier)
            if smsObj == None:
                self.say(u"Sorry I lost your sms.")
                self.complete_request()
                return
            
            if state == "SHOW":
                instruction = self.showUpdateAndAskToSend(smsObj, language).strip().lower()
                if any(k in instruction for k in (questions['answerSEND'][language])):
                    state = "SEND"
                    continue
                if any(k in instruction for k in (questions['answerCANCEL'][language])):
                    state = "CLARIFY"
                    continue
                self.say(random.choice(responses['mustRepeat'][language]))
                continue
            
            elif state == "WRITE":
                smsObj = self.askAndSetMessage(smsObj, language)
                if smsObj == None:
                    self.say(random.choice(responses['updateSmsFail'][language]))
                    self.complete_request()
                    return
                state = "SHOW"
                continue
            
            elif state == "CLARIFY":
                instruction = self.askForClarification(smsObj, language).strip().lower()
                if any(k in instruction for k in (questions['answerSEND'][language])):
                    state = "SEND"
                    continue
                if any(k in instruction for k in (questions['answerCANCEL'][language])):
                    state = "CANCEL"
                    continue
                if any(k in instruction for k in (questions['answerUPDATE'][language])):
                    state = "WRITE"
                    continue
                if any(k in instruction for k in (questions['answerREVIEW'][language])):
                    state = "SHOW"
                    continue
                self.say(random.choice(responses['mustRepeat'][language]))
                continue
            
            elif state == "CANCEL":
                self.cancelSms(smsObj, language)
                satisfied = True
                continue
            
            elif state == "SEND":
                self.finalSend(smsObj, language)
                satisfied = True
                continue
        
    def searchUserByName(self, personToLookup):
        search = PersonSearch(self.refId)
        search.scope = PersonSearch.ScopeLocalValue
        search.name = personToLookup
        answerObj = self.getResponseForRequest(search)
        if ObjectIsCommand(answerObj, PersonSearchCompleted):
            answer = PersonSearchCompleted(answerObj)
            return answer.results if answer.results != None else []
        else:
            raise StopPluginExecution("Unknown response: {0}".format(answerObj))
        return []
        
    def findPhoneForNumberType(self, person, numberType, language):         
        # first check if a specific number was already requested
        phoneToMessage = None
        if numberType != None:
            # try to find the phone that fits the numberType
            phoneToMessage = filter(lambda x: x.label == numberType, person.phones)
        else:
            favPhones = filter(lambda y: y.favoriteVoice if hasattr(y, "favoriteVoice") else False, person.phones)
            if len(favPhones) == 1:
                phoneToMessage = favPhones[0]
        if phoneToMessage == None:
            # lets check if there is more than one number
            if len(person.phones) == 1:
                if numberType != None:
                    self.say(errorNumberNotPresent.format(numberTypesLocalized[numberType][language], person.fullName))
                phoneToMessage = person.phones[0]
            else:
                # damn we need to ask the user which one he wants...
                while(phoneToMessage == None):
                    root = UIAddViews(self.refId)
                    root.dialogPhase = root.DialogPhaseClarificationValue
                    
                    utterance = UIAssistantUtteranceView()
                    utterance.dialogIdentifier = "ContactDataResolutionDucs#foundAmbiguousPhoneNumberForContact"
                    utterance.speakableText = utterance.text = responses['selectNumber'][language].format(person.fullName)
                    utterance.listenAfterSpeaking = True
                    
                    root.views = [utterance]
                    
                    lst = UIDisambiguationList()
                    lst.items = []
                    lst.speakableSelectionResponse = "OK!"
                    lst.listenAfterSpeaking = True
                    lst.selectionResponse = "OK"
                    root.views.append(lst)
                    for phone in person.phones:
                        numberType = numberTypesLocalized[phone.label][language] if phone.label in numberTypesLocalized else phone.label
                        item = UIListItem()
                        item.title = ""
                        item.text = u"{0}: {1}".format(numberType, phone.number)
                        item.selectionText = item.text
                        item.speakableText = u"{0}  ".format(numberType)
                        item.object = phone
                        item.commands = [SendCommands(commands=[StartRequest(handsFree=False, utterance=numberType)])]
                        lst.items.append(item)
                        
                    answer = self.getResponseForRequest(root)
                    numberType = self.getNumberTypeForName(answer, language)
                    if numberType != None:
                        matches = filter(lambda x: x.label == numberType, person.phones)
                        if len(matches) == 1:
                            phoneToMessage = matches[0]
                        else:
                            self.say(errorNumberTypes[language])
                    else:
                        self.say(errorNumberTypes[language])
        return phoneToMessage
    
    def getNumberTypeForName(self, name, language):
        # q&d
        if name != None:
            if name.lower() in namesToNumberTypes[language]:
                return namesToNumberTypes[language][name.lower()]
            else:
                for key in numberTypesLocalized.keys():
                    if numberTypesLocalized[key][language].lower() == name.lower():
                        return numberTypesLocalized[key][language]
        return name
        
    def presentPossibleUsers(self, persons, language):
        root = UIAddViews(self.refId)
        root.dialogPhase = root.DialogPhaseClarificationValue
        utterance = UIAssistantUtteranceView()
        utterance.dialogIdentifier = "ContactDataResolutionDucs#disambiguateContact"
        utterance.text = responses['select'][language]
        utterance.speakableText = responses['select'][language] 
        utterance.listenAfterSpeaking = True
        root.views = [utterance]
        # create a list with all the possibilities 
        lst = UIDisambiguationList()
        lst.items = []
        lst.speakableSelectionResponse = "OK!"
        lst.listenAfterSpeaking = True
        lst.selectionResponse = "OK"
        root.views.append(lst)
        for person in persons:
            item = UIListItem()
            item.object = person 
            item.selectionResponse = person.fullName
            item.selectionText = person.fullName
            item.title = person.fullName
            item.commands = [SendCommands([StartRequest(False, "^phoneCallContactId^=^urn:ace:{0}".format(person.identifier))])]
            lst.items.append(item)
        return root
    
    @register("en-US", "(Write|Send)( a)?( new)? (message|sms) to (?P<recipient>[\w ]+?)$")
    @register("de-DE", "(Sende|Schreib.)( eine)?( neue)? (Nachricht|sms) an (?P<recipient>[\w ]+?)$")
    def sendSMS(self, speech, lang, regex):
        recipient = regex.group('recipient')
        possibleRecipients = self.searchUserByName(recipient)
        personToMessage = None
        if len(possibleRecipients) > 0:
            if len(possibleRecipients) == 1:
                personToMessage = possibleRecipients[0]
            else:
                identifierRegex = re.compile("\^phoneCallContactId\^=\^urn:ace:(?P<identifier>.*)")
                #  multiple users, ask user to select
                while(personToMessage == None):
                    strUserToMessage = self.getResponseForRequest(self.presentPossibleUsers(possibleRecipients, lang))
                    self.logger.debug(strUserToMessage)
                    # maybe the user clicked...
                    identifier = identifierRegex.match(strUserToMessage)
                    if identifier:
                        strUserToMessage = identifier.group('identifier')
                        self.logger.debug(strUserToMessage)
                    for person in possibleRecipients:
                        if person.fullName == strUserToMessage or person.identifier == strUserToMessage:
                            personToMessage = person
                    if personToMessage == None:
                        # we obviously did not understand him.. but probably he refined his request... call again...
                        self.say(errorNumberTypes[lang])
                    
            if personToMessage != None:
                self.message(self.findPhoneForNumberType(personToMessage, None, lang), personToMessage, lang)
                return # complete_request is done there
        self.say(responses['notFound'][lang])                         
        self.complete_request()
        
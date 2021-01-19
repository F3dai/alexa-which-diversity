# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler
)

import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

import requests
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

apiUrl = 'https://api.diversitydata.io/?fullname='

skillName = 'Which Diversity'

# Wordlists to jazz it up a bit
names = ["Juan Cortez", "Donald Trump", "Kanye West", "Barack Obama", "Keith Large"]
greetings = ["Hi","Hey","Hey there", "Howdy","Hello", "Burev", "Hola"]

def getDiversity(url):
    try:
        resonse = requests.get(url).json()
    except Exception as e:
        resonse = False
    return resonse

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        greeting = random.choice(greetings)

        speak_output = "{}! Welcome to '{}'. Tell me a name, such as 'who is {}'".format(greeting,skillName, random.choice(names))
        
        reprompt_text = "Ask me a full name. For example, 'who is {}'.".format(random.choice(names))

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )

class queryNameIntentHandler(AbstractRequestHandler):
    
    """Handler for Name Query."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("queryNameIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # get slots
        slots = handler_input.request_envelope.request.intent.slots
        
        name = slots["name"].value
        
        # url encode name
        name = name.replace(' ', '%20')
        
        apiResponse = getDiversity(apiUrl + name) # Send API request, return dict (json)
        
        # No errors
        if apiResponse != False:
            apiFullName = apiResponse["fullname"]
            apiGender = apiResponse["gender"]
            apiEthnicity = apiResponse["ethnicity"]
            
            speak_output = "{} is a {} {}. Ask me another name or say 'bye' to exit.".format(apiFullName, apiEthnicity, apiGender)
        
        else: # If error poo
            speak_output = "Hmm, looks like that didn't work. Please try again."
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Tell me a name, such as 'who is {}'")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "This is {}. Provide me a name. For example, 'who is {}'. I will respond with a predicted gender and ethnicity.".format(skillName, random.choice(names))

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye! Thanks for using {}".format(skillName)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(queryNameIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()

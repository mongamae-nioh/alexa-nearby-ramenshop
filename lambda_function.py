# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

from shopinfo import reputationApi,geoLocation,mergeApiParameter,reputationInfo

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
#        speak_output = "Welcome, you can say Hello or Help. Which would you like to try?"
        speak_output = "近くのラーメン屋さんをお知らせします。"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        context = handler_input.request_envelope.context
#        print(context.geolocation.coordinate)
#        hundlerinput = handler_input.request_envelope.context
#        print(hundlerinput)

#        isgeosupported = handler_input.request_envelope.context.system.device.supported_interfaces.geolocation
#        if isgeosupported:
#            print('geolocation is supported.')

#        latitude = context.geolocation.coordinate.latitude_in_degrees
#        print(latitude1)
#        longitude = context.geolocation.coordinate.longitude_in_degrees
#        print(longitude1)
        
        param1 = reputationApi('ラーメン')
        apibase = param1.baseinfo()
        param2 = geoLocation("43.0555316", "141.3526345")
#        param2 = geoLocation('43.058377961865624', '141.25509169734372')
#        param2 = geoLocation(latitude, longitude)
        geolocation = param2.geolocation()
        merge = mergeApiParameter()
        param = merge.api_parameter(apibase, geolocation)
        url = param1.url

        #shop = restrantInfo(url, param)
        shop = reputationInfo(url, param)

        hitcount = shop.hit_count2()
        shop2 = shop.reputation_search()
        
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr['shopinfo'] = shop2
        
        if shop2:
            speak_output = f"{hitcount}件の口コミが見つかりました。"
        else:
            speak_output = '近くには見つかりませんでした。範囲を広げて探しましょうか？'
            ask_output = "範囲を広げて探しますか？"
            session_attr['shop'] = 'no'

            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .set_should_end_session(False)
                .response
                )

        session_attr['start'] = 0

        if len(shop2) < 3:
            session_attr['next'] = 'no'
            session_attr['q'] = 'no'

            for i in range(len(shop2)):
                speak_output += shop2[i]['name'] + '。'
                speak_output += shop2[i]['comment'] + 'お店までの距離はここから約' + str(shop2[i]['distance']) + 'メートルです。'
                
            return (
                handler_input.response_builder
                .speak(speak_output)
                .response
                )
        else:
            speak_output += 'いくつかをご紹介します。'
            for i in range(2):
                speak_output += shop2[i]['name'] + '。'
                speak_output += shop2[i]['comment'] + 'お店まではここから約' + str(shop2[i]['distance']) + 'メートルです。'
                
                session_attr['next'] = 'yes'
                session_attr['start'] += 1

            session_attr['end'] = session_attr['start'] + 2
            speak_output += "次の口コミを聞きますか？"
            session_attr['q'] = 'yes'

            ask_output = "そのほかの口コミを聞きますか？"

            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .set_should_end_session(False)
                .response
                )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class YesIntentHandler(AbstractRequestHandler):
    """Yes Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr['shopinfo']

        start = session_attr['start']
        end = session_attr['end']
        speak_output = ''
        if session_attr['q'] == 'yes' or session_attr['next'] == 'yes':
            for i in range(start, end):
                speak_output += session_attr['shopinfo'][i]['name'] + '。'
                speak_output += session_attr['shopinfo'][i]['comment'] + 'お店まではここから約' + str(session_attr['shopinfo'][i]['distance']) + 'メートルです。'
                session_attr['start'] += 1
                session_attr['end'] += 1

        return (
            handler_input.response_builder
                .speak(speak_output)
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
        speak_output = "Goodbye!"

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
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()

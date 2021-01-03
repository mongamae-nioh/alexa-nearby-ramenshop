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
from ask_sdk_model import ui

from ask_sdk_model import Response

#import shopinfo
from shopinfo import reputationSearchApi,geoLocation,searchRange,apiRequestParameter,reputationInfo

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 一度の発話で紹介する口コミの数（あまり長いとUXを損ねるため）
referrals_at_once = 2

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        context = handler_input.request_envelope.context
        speak_output = "近くのラーメン屋さんをお知らせします。"

        menu = reputationSearchApi().search_by_menu('ラーメン')
#        apibase = param1.baseinfo()

#        isgeosupported = handler_input.request_envelope.context.system.device.supported_interfaces.geolocation
#        if isgeosupported:
#            print('geolocation is supported.')

#        latitude = context.geolocation.coordinate.latitude_in_degrees
#        longitude = context.geolocation.coordinate.longitude_in_degrees

#        geolocation = geoLocation().set(latitude, longitude)

        ## 平和
        #geolocation = geoLocation().set('43.058377961865624', '141.25509169734372')

        ## すすきの
        #geolocation = geoLocation().set("43.0555316", "141.3526345")

        ## JR琴似駅
        #geolocation = geoLocation().set("43.081898", "141.306774")

        ## 宮の沢
        geolocation = geoLocation().set("43.08970911807292", "141.27771842709322")
        
        radius = searchRange().set(5) # 3000m

        parameter = apiRequestParameter().merge(menu, geolocation, radius)
        url = reputationSearchApi().url
        api_response = reputationInfo(url, parameter)

        hitcount = api_response.total_hits()
        shop_reputation = api_response.reputation_search()
        
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr['shopinfo'] = shop_reputation
        session_attr['remaining_reputations'] = len(shop_reputation)
        
        if shop_reputation:
            speak_output = f"{hitcount}件の口コミが見つかりました。"
        else:
            speak_output = 'すみません。お店は見つかりませんでした。'
            return (handler_input.response_builder.speak(speak_output).response)

        session_attr['shop_index_begin'] = 0
        
        shop_name = ''

        if session_attr['remaining_reputations'] <= referrals_at_once:
            session_attr['next_pages'] = 'no'
            
            for i in range(session_attr['remaining_reputations']):
                shop_name    += '・' + shop_reputation[i]['name'] + '(' \
                                + str(shop_reputation[i]['distance']) + 'm)' + '\n'
                speak_output += shop_reputation[i]['kana'] + '。' \
                                + shop_reputation[i]['comment'] \
                                + 'お店までの距離はここから約' + str(shop_reputation[i]['distance']) + 'メートルです。' \
                                + '口コミは以上です。' 

            return (handler_input.response_builder
            .speak(speak_output)
            .set_card(ui.StandardCard(title="検索結果",text=shop_name))
            .response)

        else:
            speak_output += 'いくつかをご紹介します。'
            for i in range(referrals_at_once):
                shop_name    += '・' + shop_reputation[i]['name'] + '(' \
                                + str(shop_reputation[i]['distance']) + 'm)' + '\n'
                speak_output += shop_reputation[i]['kana'] + '。' \
                                + shop_reputation[i]['comment'] \
                                + 'お店までの距離はここから約' + str(shop_reputation[i]['distance']) + 'メートルです。' \
                
                session_attr['next_pages'] = 'yes'
                session_attr['shop_index_begin'] += 1

            session_attr['shop_index_end'] = session_attr['shop_index_begin'] + referrals_at_once
            session_attr['remaining_reputations'] -= referrals_at_once
            speak_output += "次の口コミを聞きますか？"

            ask_output = "そのほかの口コミを聞きますか？"

            return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(ui.StandardCard(title="検索結果",text=shop_name))
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
        speak_output = "現在地の近くにあるラーメン屋さんの口コミを紹介します。"
        return (handler_input.response_builder.speak(speak_output).response)
        
class GoNextIntentHandler(AbstractRequestHandler):
    """Go Next shoplist Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GoNextIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        shopinfo = session_attr['shopinfo']

        start = session_attr['shop_index_begin']
        end = session_attr['shop_index_end']
        speak_output = ''
        shop_name = ''

        if session_attr['next_pages'] == 'yes' and session_attr['remaining_reputations'] > 0:
            if 0 < session_attr['remaining_reputations'] <= referrals_at_once:
                speak_output += "これが最後の口コミです。"
                
            if session_attr['remaining_reputations'] == 1:
                shop_name    += '・' + shopinfo[str(start)]['name'] + '(' \
                                + str(shopinfo[str(start)]['distance']) + 'm)' + '\n'
                speak_output += shopinfo[str(start)]['kana'] + '。' \
                                + shopinfo[str(start)]['comment'] \
                                + 'お店まではここから約' + str(shopinfo[str(start)]['distance']) + 'メートルです。' \
                                + '口コミは以上です。'
                                                
                return (handler_input.response_builder
                .speak(speak_output)
                .set_card(ui.StandardCard(title="検索結果",text=shop_name))
                .response)

            for i in range(start, end):
                shop_name    += '・' + shopinfo[str(i)]['name'] + '(' \
                                + str(shopinfo[str(i)]['distance']) + 'm)' + '\n'
                speak_output += shopinfo[str(i)]['kana'] + '。' \
                                + shopinfo[str(i)]['comment'] \
                                + 'お店まではここから約' + str(shopinfo[str(i)]['distance']) + 'メートルです。' \
                                
                session_attr['shop_index_begin'] += 1
                session_attr['next_pages'] = 'yes'

            session_attr['shop_index_end'] = session_attr['shop_index_begin'] + referrals_at_once
            session_attr['remaining_reputations'] -= referrals_at_once

            if session_attr['remaining_reputations'] <= 0:
                speak_output += "口コミは以上です。"
                return (handler_input.response_builder
                .speak(speak_output)
                .set_card(ui.StandardCard(title="検索結果",text=shop_name))
                .response)
                        
            speak_output += "次の口コミを聞きますか？"
            ask_output = "そのほかの口コミを聞きますか？"

            return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(ui.StandardCard(title="検索結果",text=shop_name))
                .ask(ask_output)
                .set_should_end_session(False)
                .response
                )

class NoIntentHandler(AbstractRequestHandler):
    """No Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "わかりました。"

        return (handler_input.response_builder.speak(speak_output).response)

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "わかりました。"

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

        speak_output = "すみません。よくわかりませんでした。"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .set_should_end_session(False)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GoNextIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())
lambda_handler = sb.lambda_handler()

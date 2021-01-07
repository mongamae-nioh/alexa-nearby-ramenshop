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
#from ask_sdk_model.ui import AskForPermissionsConsentCard

from ask_sdk_model import Response

#import shopinfo
from shopinfo import ReputationSearchApiParameter,GeoLocation,SearchRange,ApiRequestParameter,ReputationInfo

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 位置情報の共有を許可するように促すカードをAlexaアプリへ表示する関数の引数
permissions = ["alexa::devices:all:geolocation:read"]

# 探したいメニュー名
search_menu = 'ラーメン'

# 一度の発話で紹介する口コミの数（あまり長いとUXを損ねるため）
referrals_at_once = 2

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response     
        # デバイスが位置情報取得に対応しているか、Alexaアプリが位置情報の共有を許可しているかチェック
        context = handler_input.request_envelope.context
        isgeosupported = context.system.device.supported_interfaces.geolocation
        geo_object = context.geolocation
        if isgeosupported is None or geo_object is None:
            speak_output = "このスキルは、位置情報を使用します。\
                位置情報の共有を有効にするには、Alexaアプリに移動し、権限を有効にしてください。\
                なお、固定デバイスの場合は位置情報を取得するようには設定されていないため、このスキルはお使いになれません。"
            
            return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(ui.AskForPermissionsConsentCard(permissions=permissions))
                .response
            )

        # APIのリクエストパラメータ作成
        api = ReputationSearchApiParameter()

        menu = api.search_by_menu(search_menu)

        latitude = context.geolocation.coordinate.latitude_in_degrees
        longitude = context.geolocation.coordinate.longitude_in_degrees
        geolocation = GeoLocation.set(latitude, longitude)

        radius = SearchRange.set(5) # 3000m

        parameter = ApiRequestParameter.merge(menu, geolocation, radius)

        # APIレスポンス
        url = api.url
        api_response = ReputationInfo(url, parameter)

        hitcount = api_response.total_hits
        shop_reputation = api_response.reputation_search()
                
        if shop_reputation:
            speak_output = f"{hitcount}件の口コミが見つかりました。"
        else:
            speak_output = 'すみません。お店の口コミは見つかりませんでした。'
            return (handler_input.response_builder.speak(speak_output).response)

        session_attr = handler_input.attributes_manager.session_attributes
        session_attr['shopinfo'] = shop_reputation
        session_attr['remaining_reputations'] = len(shop_reputation)
        session_attr['shop_index_begin'] = 0

        shop_name = ''
        if session_attr['remaining_reputations'] <= referrals_at_once:
            session_attr['next_pages'] = 'no'
            
            for i in range(session_attr['remaining_reputations']):
                shop_name    += '・' + shop_reputation[i]['name'] \
                                + '(' + str(shop_reputation[i]['distance']) + 'm)' + '\n'
                speak_output += shop_reputation[i]['kana'] + '。' \
                                + shop_reputation[i]['comment'] \
                                + 'お店までの距離はここから約' + str(shop_reputation[i]['distance']) + 'メートルです。' \
                                + '口コミは以上です。' 

            return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(ui.StandardCard(title="検索結果",text=shop_name))
                .response
                )

        else:
            speak_output += 'いくつかをご紹介します。'
            for i in range(referrals_at_once):
                shop_name    += '・' + shop_reputation[i]['name'] \
                                + '(' + str(shop_reputation[i]['distance']) + 'm)' + '\n'
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
        speak_output = "現在地の近くにあるラーメン屋さんの口コミをご紹介します。"
        return (handler_input.response_builder.speak(speak_output).response)

class GoNextIntentHandler(AbstractRequestHandler):
    """店の情報を読み上げている途中で「次」、あるいは次の店の情報を聞くかという質問に「はい」と答えたときに呼び出されるインテント"""
    """次のお店情報を読み上げる。店舗情報があるうちは繰り返し呼び出しが可能"""
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
                                                
                return (
                    handler_input.response_builder
                    .speak(speak_output)
                    .set_card(ui.StandardCard(title="検索結果",text=shop_name))
                    .response
                    )

            for i in range(start, end):
                shop_name    += '・' + shop_reputation[i]['name'] \
                                + '(' + str(shop_reputation[i]['distance']) + 'm)' + '\n'
                speak_output += shopinfo[str(i)]['kana'] + '。' \
                                + shopinfo[str(i)]['comment'] \
                                + 'お店まではここから約' + str(shopinfo[str(i)]['distance']) + 'メートルです。' \
                                
                session_attr['shop_index_begin'] += 1
                session_attr['next_pages'] = 'yes'

            session_attr['shop_index_end'] = session_attr['shop_index_begin'] + referrals_at_once
            session_attr['remaining_reputations'] -= referrals_at_once

            if session_attr['remaining_reputations'] <= 0:
                speak_output += "口コミは以上です。"
                return (
                    handler_input.response_builder
                    .speak(speak_output)
                    .set_card(ui.StandardCard(title="検索結果",text=shop_name))
                    .response
                    )
                        
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
        else:
            speak_output = 'すみません。よくわかりませんでした。'
            return (handler_input.response_builder.speak(speak_output).response)

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

        return (handler_input.response_builder.speak(speak_output).response)

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

        return (handler_input.response_builder.speak(speak_output).response)

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

        return (handler_input.response_builder.speak(speak_output).response)

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

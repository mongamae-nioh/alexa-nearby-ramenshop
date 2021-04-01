import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import ui
from ask_sdk_model import Response
from shopinfo import ReputationSearchApiParameter,GeoLocation,SearchRange,ApiRequestParameter,ReputationInfo

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = f"現在地から近い{search_menu}屋さんの口コミをご紹介します。"
        return (handler_input.response_builder.speak(speak_output).response)

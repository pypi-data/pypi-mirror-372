from cs.translator.elhuyar import _
from plone import api
from plone.memoize.ram import cache
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zope.i18n import translate

import re
import requests


HEADERS = {"Accept": "application/json"}
TIMEOUT = 7


def cache_key(fun, self, language_pair, text):
    """Remove _authenticator and data-token to cache logged in"""
    text = re.sub(r"_authenticator=[a-zA-Z0-9]{40}", "", text)
    text = re.sub(r'data-token="[a-zA-Z0-9]{40}"', "", text)

    return (language_pair, text)


class Translator(Service):
    @cache(cache_key)
    def post_request(self, language_pair, text):
        """Post request to the API"""
        print("Someone or something called me")
        api_base_url = api.portal.get_registry_record(
            "cs.translator.elhuyar.elhuyar_a_p_i_config.api_base_url"
        )
        api_id = api.portal.get_registry_record(
            "cs.translator.elhuyar.elhuyar_a_p_i_config.api_id"
        )
        api_key = api.portal.get_registry_record(
            "cs.translator.elhuyar.elhuyar_a_p_i_config.api_key"
        )
        translation_engine = api.portal.get_registry_record(
            "cs.translator.elhuyar.elhuyar_a_p_i_config.translation_engine"
        )
        response = requests.post(
            f"{api_base_url}/translate_string",
            json={
                "api_id": api_id,
                "api_key": api_key,
                "translation_engine": translation_engine,
                # Language of the original text and target language
                # for the translation: es-eu | eu-es | etc
                "language_pair": language_pair,
                # hardcoded: Content type of the text: txt | html | xml
                "content_type": "html",
                "text": text,
            },
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        return response

    def reply(self):
        body = json_body(self.request)
        language_pair = body.get("language_pair", None)
        text = body.get("text", None)
        if not language_pair or not text:
            self.request.response.setStatus(400)
            return {
                "message": translate(
                    _("Incorrect params, language_pair and text are required"),
                    context=self.request,
                ),
            }
        try:
            result = self.post_request(language_pair, text)
            if result.ok:
                # Ignoring keys:
                # - "execution_time"
                # - "glossary_active_words"
                # - "interactive"
                # - "original_text"
                # - "source_sentences"
                # - "translated_sentences"
                # - "words"
                translated_text = result.json().get("translated_text", "")
                return {"translated_text": translated_text}
            else:
                try:
                    self.request.response.setStatus(result.status_code)
                    return result.json()
                except Exception:
                    return {
                        "message": translate(
                            _("Unexpected Error"), context=self.request
                        )
                    }

        except requests.exceptions.Timeout:
            self.request.response.setStatus(500)
            return {"message": translate(_("Timeout"), context=self.request)}

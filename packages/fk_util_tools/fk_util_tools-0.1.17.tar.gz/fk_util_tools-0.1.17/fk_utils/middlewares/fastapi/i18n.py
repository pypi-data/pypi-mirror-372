import os
import gettext
from pathlib import Path
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import Request
from mypy_boto3_translate.client import TranslateClient
from fk_utils.cache.redis import CacheService

AWS_REGION_NAME = os.environ.get("AWS_REGION_NAME", "us-east-2")


class TranslationWrapper:
    def __init__(self, lang: str, translation_dir: Path, redis_url: str):
        """Initializes the translation object for a specific language."""
        self.lang = lang
        self.translation_dir = translation_dir
        self.cache_service = CacheService(redis_url)

        self.translations = gettext.translation(
            "messages",
            localedir=self.translation_dir,
            languages=[self.lang],
            fallback=True,
        )
        self.translations.install()

        self.translate_client: TranslateClient = boto3.client(
            "translate", region_name=AWS_REGION_NAME
        )

    def gettext(self, message: str) -> str:
        """Returns the translation from the file or AWS Translate."""
        cache_key = f"translation:{self.lang}:{message}"
        cached_translation = self.cache_service.get(cache_key)
        if isinstance(cached_translation, dict) and self.lang in cached_translation:
            return cached_translation[self.lang]

        translated_message = self.translations.gettext(message)
        if translated_message == message:
            try:
                response = self.translate_client.translate_text(
                    Text=message,
                    SourceLanguageCode="en",
                    TargetLanguageCode=self.lang,
                )
                translated_message = response["TranslatedText"]
                self.cache_service.add(
                    cache_key, {self.lang: translated_message}, expiration_time=86400
                )
            except (BotoCoreError, ClientError) as e:
                print(f"Error en AWS Translate: {e}")
                translated_message = message

        return translated_message


async def set_locale(request: Request, translation_dir: Path, redis_url: str):
    """Sets the language according to the 'Accept-Language' header."""
    lang = request.headers.get("Accept-Language", "en")
    request.state.translation = TranslationWrapper(lang, translation_dir, redis_url)


def _(message: str, request: Request) -> str:
    """Gets the translation of the message using the language configured in the request."""
    return request.state.translation.gettext(message)

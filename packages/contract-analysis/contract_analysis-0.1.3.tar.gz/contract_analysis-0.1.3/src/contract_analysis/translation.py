
import requests
from datetime import datetime
from enum import Enum
from azure.core.credentials import TokenCredential
from .document import Document

class TranslationAction(Enum):
    TRANSLATE = "translate"
    DETECT = "detect"

class Translation:
    def __init__(self, credential: TokenCredential, translator_endpoint: str,
                 translator_region: str, target_language: str, document: Document):
        """
        Initializes the Translation service with Azure credentials and configuration.

        Args:
            credential (TokenCredential): Azure credential for authentication.
            translator_endpoint (str): Endpoint for Azure Translator.
            translator_region (str): Azure region for Translator.
            target_language (str): Target language for translation.
            document (Document): Document object to be translated.
        """
        self.credential = credential
        self.translator_endpoint = translator_endpoint.rstrip("/")
        self.translator_region = translator_region
        self.target_language = target_language
        self.document = document
        self.access_token = None
        self.token_expiry = None

    def _get_access_token(self):
        """
        Retrieves a new access token using the provided Azure credential.
        """
        token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
        self.access_token = token.token
        self.token_expiry = datetime.utcfromtimestamp(token.expires_on)

    def _ensure_token_valid(self):
        """
        Ensures the access token is valid and refreshes it if expired.
        """
        if not self.access_token or not self.token_expiry or datetime.utcnow() >= self.token_expiry:
            self._get_access_token()

    def translate_text(self, text: str = None, action: TranslationAction = TranslationAction.TRANSLATE) -> str:
        """
        Translates or detects the language of the given text using Azure Translator.

        Args:
            text (str): Text to be translated or detected.
            action (TranslationAction): Action to perform (TRANSLATE or DETECT).

        Returns:
            str: Translated text or detected language.

        Raises:
            RuntimeError: If the API request fails or response format is unexpected.
        """
        if action == TranslationAction.DETECT:
            full_text = self.document.extract_text()
            text = full_text[:1000].strip()

            if not text or all(ord(c) in list(range(0x00, 0x20)) + [0x7F] for c in text):
                return text

        self._ensure_token_valid()

        url = f"{self.translator_endpoint}/translator/text/v3.0/translate"
        params = {"api-version": "3.0", "to": [self.target_language]}
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Region": self.translator_region,
        }
        body = [{"text": text}]

        try:
            response = requests.post(url, headers=headers, params=params, json=body)
            response.raise_for_status()
            data = response.json()

            if action == TranslationAction.TRANSLATE:
                return data[0]["translations"][0]["text"]
            elif action == TranslationAction.DETECT:
                return data[0]["detectedLanguage"]["language"]

        except requests.RequestException as e:
            raise RuntimeError(f"API request failed: {e}") from e
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected response format: {response.text}") from e

    def translate_document(self):
        """
        Translates the document paragraph by paragraph and saves the translated version.
        """
        paragraphs = self.document.get_paragraphs()
        translated_texts = []

        for p in paragraphs:
            text = p.Range.Text.strip()
            if text and text != "\r":
                translated = self.translate_text(text, action=TranslationAction.TRANSLATE)
                translated_texts.append(translated)
            else:
                translated_texts.append("")

        self.document.save_translated(translated_texts)
        self.document.set_paths_to_use(translated=True)

    def check_document_language(self) -> str:
        """
        Detects the language of the document.

        Returns:
            str: Detected language code.
        """
        return self.translate_text(action=TranslationAction.DETECT)

    def translate_if_needed(self):
        """
        Translates the document if its language differs from the target language.
        """
        detected_language = self.check_document_language()
        if detected_language != self.target_language:
            self.translate_document()
        else:
            self.document.set_paths_to_use(translated=False)

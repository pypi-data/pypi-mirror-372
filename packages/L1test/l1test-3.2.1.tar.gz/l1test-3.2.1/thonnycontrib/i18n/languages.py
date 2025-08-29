import gettext, os

BASE_LANGUAGE_CODE = "en_US"
BASE_LANGUAGE_NAME = "English"

# https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes

LANGUAGES_DICT = {
    BASE_LANGUAGE_CODE: BASE_LANGUAGE_NAME,
    "fr_FR": "Français",
}


_translation = gettext.NullTranslations()


def tr(message: str) -> str:
    """ Translates the message to the current language."""
    return _translation.gettext(message)


def set_language(language_code: str) -> None:
    global _translation
    try:
        path = os.path.join(os.path.dirname(__file__), "locale")
        _translation = gettext.translation("l1test", path, [language_code])
    except Exception as e:
        _translation = gettext.NullTranslations()
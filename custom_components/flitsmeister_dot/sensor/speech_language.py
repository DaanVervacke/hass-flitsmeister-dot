"""Speech language sensor for the Flitsmeister DOT integration."""

from flitsmeister_dot_ble import SpeechLanguage

from custom_components.flitsmeister_dot.sensor.entity import FlitsmeisterDotSensorEntityDescription
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import EntityCategory

SPEECH_LANGUAGE_OPTIONS = [language.name.lower() for language in SpeechLanguage]

ENTITY_DESCRIPTIONS = (
    FlitsmeisterDotSensorEntityDescription(
        key="speech_language",
        translation_key="speech_language",
        device_class=SensorDeviceClass.ENUM,
        options=SPEECH_LANGUAGE_OPTIONS,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.speech_language.name.lower() if state.speech_language is not None else None,
    ),
)

# -*- coding: utf-8 -*-
import importlib
from typing import Callable

_root_lib_path = "sinapsis_elevenlabs.templates"

_template_lookup = {
    "ElevenLabsTTS": f"{_root_lib_path}.elevenlabs_tts",
    "ElevenLabsVoiceGeneration": f"{_root_lib_path}.elevenlabs_voice_generation",
    "ElevenLabsVoiceClone": f"{_root_lib_path}.elevenlabs_voice_clone",
    "ElevenLabsSTS": f"{_root_lib_path}.elevenlabs_sts",
}


def __getattr__(name: str) -> Callable:
    if name in _template_lookup:
        module = importlib.import_module(_template_lookup[name])
        return getattr(module, name)

    raise AttributeError(f"template `{name}` not found in {_root_lib_path}")


__all__ = list(_template_lookup.keys())

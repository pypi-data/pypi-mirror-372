
from difflib import SequenceMatcher
import tempfile
import logging
import re
import os
import sys
import audioop
from faster_whisper import WhisperModel
from requests.exceptions import ConnectionError, Timeout
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

# --- lazy, failure-triggered patch for SpeechRecognition FLAC encoding ---

import subprocess
from subprocess import PIPE, DEVNULL
import platform
import shutil
import threading
import speech_recognition as sr
import logging

logger = logging.getLogger(__name__)

# capture original
_origGetFlac = sr.AudioData.get_flac_data

# state
_encoderMode = None         # None | "native" | "ffmpeg" | "flac" | "sox"
_modeLock = threading.Lock()

CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

_BUILDERS = {
    "ffmpeg": lambda: ["ffmpeg", "-loglevel", "quiet", "-i", "pipe:0", "-f", "flac", "pipe:1"],
    "flac":   lambda: ["flac", "-s", "-f", "-", "-o", "-"],
    "sox":    lambda: ["sox", "-t", "wav", "-", "-t", "flac", "-"],
}


# def _selectEncoder():
#     for name in _BUILDERS:
#         if shutil.which(name):
#             return name, _BUILDERS[name]
#     raise RuntimeError("No encoder found in PATH. Please install ffmpeg, flac, or sox and ensure it is on your system PATH.")
def _selectEncoder():
    for name in _BUILDERS:
        if shutil.which(name):
            return name, _BUILDERS[name]
    # no external encoder found
    logger.warning(
        "No external encoder (ffmpeg, flac, sox) found in PATH. "
        "Falling back to native encoder or Whisper. "
        "If you encounter errors, install ffmpeg, flac, or sox and ensure it is on PATH."
    )
    return None, None



def _runExternal(self, name, buildCmd, convert_rate, convert_width):
    cmd = buildCmd()
    kwargs = {"stdin": PIPE, "stdout": PIPE, "stderr": DEVNULL, "close_fds": True}
    if platform.system() == "Windows":
        kwargs["creationflags"] = CREATE_NO_WINDOW

    p = subprocess.Popen(cmd, **kwargs)
    wav = self.get_wav_data(convert_rate, convert_width)
    try:
        p.stdin.write(wav)
    finally:
        p.stdin.close()

    out = p.stdout.read()
    rc = p.wait()
    if rc != 0 or not out:
        raise RuntimeError(f"{name} failed (exit {rc}) or produced no output.")
    return out


def _lazyGetFlac(self, convert_rate=None, convert_width=None):
    global _encoderMode

    # fast path if we've already decided
    mode = _encoderMode
    if mode == "native":
        # if __debug__:
        #     print("[FLAC] Using native SpeechRecognition encoder")
        return _origGetFlac(self, convert_rate, convert_width)
    if mode in _BUILDERS:
        # if __debug__:
        #     print(f"[FLAC] Using external encoder: {mode}")
        return _runExternal(self, mode, _BUILDERS[mode], convert_rate, convert_width)

    # first decision: try native; on failure, switch to external encoder
    with _modeLock:
        if _encoderMode is not None:
            return _lazyGetFlac(self, convert_rate, convert_width)  # someone else decided

        try:
            out = _origGetFlac(self, convert_rate, convert_width)
            _encoderMode = "native"
            return out
        except Exception:
            name, build = _selectEncoder()
            if name and build:
                _encoderMode = name
                return _runExternal(self, name, build, convert_rate, convert_width)
            else:
                # No external encoder → gracefully fallback
                logger.warning("Falling back to Whisper since no external encoders are available.")
                raise  # let higher-level catch handle Whisper


# apply wrapper
sr.AudioData.get_flac_data = _lazyGetFlac


def _selfCheck():
    """Run a quick silent test to confirm encoder works."""
    import array
    import math

    # 100ms silent audio (16kHz mono, 16-bit signed)
    sr_data = sr.AudioData(b"\x00\x00" * 1600, 16000, 2)
    try:
        _ = sr_data.get_flac_data()  # triggers lazy decision
        #print(f"[FLAC] Self-check passed: mode = {_encoderMode}")
    except Exception as e:
        print(f"[FLAC] Self-check failed: {e}")


# do an early probe at import
_selfCheck()



logger = logging.getLogger(__name__)


DEFAULT_WORD_REPL: dict[str, str] = {
    "dass": "dasi", "gass": "dasi",
    "deact": "deactivate", "de": "deactivate",
    "a i": "ai",
    "fuc": "fuck", "fuckkk": "fuck", "fuckk": "fuck", "fuckkker": "fucker",
    "fuckker": "fucker", "fuckkking": "fucking", "fuckking": "fucking", "motherfuker": "motherfucker",
    "bich": "bitch"
}

WHISPER_SIZES: dict[str, str] = {
    "tiny": "tiny",
    "base": "base",
    "small": "small",
    "medium": "medium",
    "largeV2": "large-v2",
    "largeV3": "large-v3"
}


class HoloSTT:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        super().__init__()
        if hasattr(self, "initialized"):
            return

        self._initComponents(parent)

        self.initialized = True

    def _initComponents(self, parent):
        self.parent = parent
        self._setDefaults()
        self._setWhisper()

    def _setDefaults(self):
        self.soundChannel   = getattr(self.parent, "soundChannel", 2) if self.parent else 2
        self.soundChoice    = getattr(self.parent, "soundChoice", 0) if self.parent else 0
        self.timeOut        = getattr(self.parent, "timeOut", 10) if self.parent else 10
        self.useFallback    = getattr(self.parent, "useFallback", False) if self.parent else False
        self.printing       = getattr(self.parent, "printing", False) if self.parent else False
        self.synthesizing   = getattr(self.parent, "synthesizing", False) if self.parent else False
        self.processing     = getattr(self.parent, "processing", False) if self.parent else False
        self.commands       = getattr(self.parent, "commands", {}) if self.parent else {}
        #self.wordRepl       = getattr(self.parent, "wordRepl", {}) if self.parent else {}
        self.wordRepl       = {**DEFAULT_WORD_REPL, **(getattr(self.parent, "wordRepl", {}) if self.parent else {})}
        self.recognizer     = getattr(self.parent, "recognizer", sr.Recognizer()) if self.parent else sr.Recognizer()
        self.storedOutput   = getattr(self.parent, "storedOutput", []) if self.parent else []
        self.isActivated    = getattr(self.parent, "isActivated", False) if self.parent else False
        self.whisperSize    = getattr(self.parent, "whisperSize", "small") if self.parent else WHISPER_SIZES["small"]

    def _setWhisper(self):
        self.whisper    = WhisperModel(
            self.whisperSize,
            device        = "cpu",
            compute_type  = "int8",
            cpu_threads=max(1, os.cpu_count() // 2),
            num_workers=max(1, os.cpu_count() // 2)
        )

    def getProperty(self, propName):
        propMap = {
            # whisper
            "whisperSize": lambda v: setattr(self, "whisperSize", str(v)),

            # pygame mixer properties
            "soundChannel": lambda v: setattr(self, "soundChannel", int(v)),
            "soundChoice":  lambda v: setattr(self, "soundChoice", int(v)),

            "timeOut":       lambda v: setattr(self, "timeOut", int(v)),
            #"useFallback":   lambda v: setattr(self, "useFallback", bool(v)),
            "printing":      lambda v: setattr(self, "printing", bool(v)),
            "synthesizing":  lambda v: setattr(self, "synthesizing", bool(v)),
            "commands":      lambda v: setattr(self, "commands", v),
            "wordRepl":      lambda v: setattr(self, "wordRepl", v),
        }
        getter = propMap.get(propName)
        if getter:
            return getter()
        else:
            raise AttributeError(f"Unknown property: '{propName}'. Allowed: {list(propMap)}")

    def setProperty(self, propName, value):
        propMap = {
            # whisper
            "whisperSize": lambda v: setattr(self, "whisperSize", str(v)),

            # pygame mixer properties
            "soundChannel": lambda v: setattr(self, "soundChannel", int(v)),
            "soundChoice":  lambda v: setattr(self, "soundChoice", int(v)),

            "timeOut":         lambda v: setattr(self, "timeOut", int(v)),
            #"useFallback":     lambda v: setattr(self, "useFallback", bool(v)),
            "printing":        lambda v: setattr(self, "printing", bool(v)),
            "synthesizing":    lambda v: setattr(self, "synthesizing", bool(v)),
            "commands":        lambda v: setattr(self, "commands", v),
            #"wordRepl":        lambda v: setattr(self, "wordRepl", v),
            "wordRepl":        self._setWordRepl
        }
        setter = propMap.get(propName)
        if setter:
            setter(value)
        else:
            raise AttributeError(f"Unknown property: '{propName}'. Allowed: {list(propMap)}")

    def _setWordRepl(self, userRepl):
        norm = lambda s: re.sub(r"\s+", " ", s.strip().lower())

        merged: dict[str, str] = {norm(k): v for k, v in DEFAULT_WORD_REPL.items()}

        if userRepl:
            for k, v in userRepl.items():
                merged[norm(k)] = v  # add/override only, never remove

        self.wordRepl = merged

        # Build one compiled regex for efficient replacement
        tokens = sorted(merged.keys(), key=len, reverse=True)
        escaped = [re.escape(t).replace(r"\ ", r"\s+") for t in tokens]
        pattern = r"(?<!\w)(" + "|".join(escaped) + r")(?!\w)"
        self._wordReplRx = re.compile(pattern, flags=re.IGNORECASE)
        self._wordReplMap = {t.lower(): merged[t] for t in merged}

    def voiceInput(self) -> str:
        printing = self.parent.printing if self.parent else self.printing
        if not printing:
            audio = self.captureAudio(selfSpeech=False)
            if not audio:
                return None
            try:
                text = self.processAudio(audio)
                if not text or self.ignoreInput(text):
                    return None
                return text.lower().strip()
            except Exception as e:
                logger.error(f"Audio Processing error:", exc_info=True)
                return None

    def ambientInput(self) -> str:
        audio = self.captureAudio(selfSpeech=True)
        if not audio:
            return None
        try:
            text = self.processAudio(audio)
            if not text or self.ignoreInput(text):
                return None
            return text
        except Exception as e:
            logger.error(f"Audio Processing error:", exc_info=True)
            return None

    def captureAudio(self, selfSpeech=False):
        parentSynth = self.parent.synthesizing if self.parent else self.synthesizing
        cond = parentSynth if selfSpeech else not parentSynth
        if cond:
            try:
                with sr.Microphone() as source:
                    recognizer = self.parent.recognizer if self.parent else self.recognizer
                    if not selfSpeech:
                        recognizer.adjust_for_ambient_noise(source, duration=2)
                    if selfSpeech:
                        systemVolume = self._getSystemVolume()
                        recognizer.energy_threshold = (
                            1.5 * (1000 + (systemVolume / 100) * (5000 - 1000))
                        )
                    try:
                        audio = recognizer.listen(
                            source,
                            timeout=5,
                            phrase_time_limit=10 if selfSpeech else None
                        )
                    except sr.WaitTimeoutError:
                        logger.warning("No speech detected: timed out while waiting for phrase.")
                        return None
                    if selfSpeech:
                        audioEnergy = audioop.rms(audio.get_raw_data(), audio.sample_width)
                        if audioEnergy < recognizer.energy_threshold + 500:
                            return None
                    if not selfSpeech:
                        if self.parent:
                            self.parent.processing = True
                        else:
                            self.processing = True
                    return audio
            except Exception as e:
                logger.error(f"Microphone error:", exc_info=True)
        return None
    
    def processAudio(self, audio):
        def process():
            if not audio or not isinstance(audio, sr.AudioData):
                return None
            try:
                result = self.recognizeWithGoogle(audio)
                return result
            except (sr.RequestError, ConnectionError, Timeout, sr.WaitTimeoutError, Exception):
                logger.error("Recognition Error:", exc_info=True)
                # useFallback = self.parent.useFallback if self.parent else self.useFallback
                # if useFallback:
                #     logger.info("Switching to Whisper for recognition.")
                #     # result = self.recognizeWithWhisper(audio)
                #     # return result
                #     result = self.recognizeWithGoogle(audio)
                #     return result
                try:
                    result = self.recognizeWithWhisper(audio)
                    return result
                except Exception as e:
                    logger.error("Recognition Error:", exc_info=True)
            return None

        timeOut = self.parent.timeOut if self.parent else self.timeOut
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(process)
            try:
                return future.result(timeout=timeOut)
            except FuturesTimeoutError:
                logger.warning("Audio processing timed out.")
                return None

    def recognizeWithGoogle(self, audio):
        recognizer = self.parent.recognizer if self.parent else self.recognizer
        try:
            text = recognizer.recognize_google(audio).lower()
            return self._cleanContent(text) if text else None
        except sr.UnknownValueError:
            logger.debug("Speech was unintelligible.")
            return None

    def recognizeWithWhisper(self, audio) -> str:
        tmpPath = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio.get_wav_data())
                tmpPath = tmp.name
            segments, _ = self.whisper.transcribe(tmpPath)
            text = " ".join(segment.text for segment in segments).strip().lower()
            return self._cleanContent(text) if text else None
        except sr.UnknownValueError:
            logger.debug("Speech was unintelligible.")
            return None
        except Exception:
            logger.error("Whisper Error:", exc_info=True)
            return None
        finally:
            if tmpPath and os.path.exists(tmpPath):
                os.remove(tmpPath)

    def keyboardInput(self, keyboardMsg="Enter your input:\n"):
        if self.parent:
            self.parent.isActivated = False
        else:
            self.isActivated = False
        msg = input(f"{keyboardMsg} ").lower()
        return msg.strip()

    def _getSystemVolume(self):
        if sys.platform == 'win32':
            import ctypes
            winmm = ctypes.WinDLL("winmm.dll")
            GetVolume = winmm.waveOutGetVolume
            volume = ctypes.c_uint()
            GetVolume(0, ctypes.byref(volume))
            left = volume.value & 0xFFFF
            right = (volume.value >> 16) & 0xFFFF
            return (left + right) / 2 / 65535 * 100
        elif sys.platform == 'darwin':
            import subprocess
            output = subprocess.run(
                ["osascript", "-e", "output volume of (get volume settings)"],
                capture_output=True, text=True)
            try:
                return float(output.stdout.strip())
            except Exception:
                return 50
        else:
            try:
                import subprocess
                proc = subprocess.run(['amixer', 'get', 'Master'], capture_output=True, text=True)
                for line in proc.stdout.split('\n'):
                    if 'Mono:' in line or 'Front Left:' in line:
                        percent = line.split('[')[1].split('%')[0]
                        return float(percent)
            except Exception:
                return 50

    def _cleanContent(self, text, applyReplacements=True, removeNums=False):
        if not text or not isinstance(text, str):
            return ""
        text = text.replace("\n", " ").replace("\n\n", " ")
        text = re.sub(r"[^\w\s]", "", text).lower().strip()
        wordRepl = self.parent.wordRepl if self.parent else self.wordRepl
        if applyReplacements and wordRepl:
            for word, rep in wordRepl.items():
                text = re.sub(rf"\b{re.escape(word)}\b", rep, text, flags=re.IGNORECASE)
        if removeNums:
            text = re.sub(r"\d+", "", text)
        return text

    def _compareTexts(self, recognized, stored):
        if not recognized or not isinstance(recognized, str):
            return "", 0, 0
        if not stored or not isinstance(stored, str):
            return "", 0, 0

        normRec = set(self._cleanContent(recognized, removeNums=True).split())
        normStored = set(self._cleanContent(stored, removeNums=True).split())
        filteredWords = normRec - normStored
        filteredText = " ".join(filteredWords)
        similarityRatio = self._checkSimilarity(filteredText, " ".join(normStored)) if filteredText else 0
        overlapRatio = len(filteredWords.intersection(normStored)) / len(filteredWords) if filteredWords else 0
        return filteredText, similarityRatio, overlapRatio

    def _checkSimilarity(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def ignoreInput(self, recognized, similarityThreshold=0.5, overlapThreshold=0.5):
        if not recognized or not isinstance(recognized, str):
            return False
        storedOutput = self.parent.storedOutput if self.parent else self.storedOutput
        stored = storedOutput[0] if storedOutput else ""
        _, similarityRatio, overlapRatio = self._compareTexts(recognized, stored)
        return similarityRatio > similarityThreshold or overlapRatio > overlapThreshold

    def allowInterruption(self, recognized, similarityThreshold=0.5, overlapThreshold=0.5):
        if not recognized or not isinstance(recognized, str):
            return False
        storedOutput = self.parent.storedOutput if self.parent else self.storedOutput
        stored = storedOutput[0] if storedOutput else ""
        _, similarityRatio, overlapRatio = self._compareTexts(recognized, stored)
        return similarityRatio <= similarityThreshold and overlapRatio <= overlapThreshold





















# from difflib import SequenceMatcher
# import tempfile
# import threading
# import logging
# import re
# import sys
# import speech_recognition as sr
# import audioop
# from requests.exceptions import ConnectionError, Timeout
# from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

# logger = logging.getLogger(__name__)


# DEFAULT_WORD_REPL: dict[str, str] = {
#     "dass": "dasi", "gass": "dasi",
#     "deact": "deactivate", "de": "deactivate",
#     "a i": "ai",
#     "fuc": "fuck", "fuckkk": "fuck", "fuckk": "fuck", "fuckkker": "fucker",
#     "fuckker": "fucker", "fuckkking": "fucking", "fuckking": "fucking", "motherfuker": "motherfucker",
#     "bich": "bitch"
# }


# class HoloSTT:
#     _instance = None
#     _lock = threading.Lock()

#     def __new__(cls, *args, **kwargs):
#         if cls._instance is None:
#             with cls._lock:
#                 if cls._instance is None:
#                     cls._instance = super().__new__(cls)
#         return cls._instance

#     def __init__(self, parent=None):
#         super().__init__()
#         if hasattr(self, "initialized"):
#             return

#         self._initComponents(parent)

#         self.initialized = True

#     def _initComponents(self, parent):
#         self.parent = parent
#         self._setDefaults()

#     def _setDefaults(self):
#         self.soundChannel   = getattr(self.parent, "soundChannel", 2) if self.parent else 2
#         self.soundChoice    = getattr(self.parent, "soundChoice", 0) if self.parent else 0
#         self.timeOut        = getattr(self.parent, "timeOut", 10) if self.parent else 10
#         self.useFallback    = getattr(self.parent, "useFallback", False) if self.parent else False
#         self.printing       = getattr(self.parent, "printing", False) if self.parent else False
#         self.synthesizing   = getattr(self.parent, "synthesizing", False) if self.parent else False
#         self.processing     = getattr(self.parent, "processing", False) if self.parent else False
#         self.commands       = getattr(self.parent, "commands", {}) if self.parent else {}
#         #self.wordRepl       = getattr(self.parent, "wordRepl", {}) if self.parent else {}
#         self.wordRepl       = {**DEFAULT_WORD_REPL, **(getattr(self.parent, "wordRepl", {}) if self.parent else {})}
#         self.recognizer     = getattr(self.parent, "recognizer", sr.Recognizer()) if self.parent else sr.Recognizer()
#         self.storedOutput   = getattr(self.parent, "storedOutput", []) if self.parent else []
#         self.isActivated    = getattr(self.parent, "isActivated", False) if self.parent else False

#     def getProperty(self, propName):
#         propMap = {
#             # pygame mixer properties
#             "soundChannel": lambda v: setattr(self, "soundChannel", int(v)),
#             "soundChoice":  lambda v: setattr(self, "soundChoice", int(v)),

#             "timeOut":       lambda v: setattr(self, "timeOut", int(v)),
#             "useFallback":   lambda v: setattr(self, "useFallback", bool(v)),
#             "printing":      lambda v: setattr(self, "printing", bool(v)),
#             "synthesizing":  lambda v: setattr(self, "synthesizing", bool(v)),
#             "commands":      lambda v: setattr(self, "commands", v),
#             "wordRepl":      lambda v: setattr(self, "wordRepl", v),
#         }
#         getter = propMap.get(propName)
#         if getter:
#             return getter()
#         else:
#             raise AttributeError(f"Unknown property: '{propName}'. Allowed: {list(propMap)}")

#     def setProperty(self, propName, value):
#         propMap = {
#             # pygame mixer properties
#             "soundChannel": lambda v: setattr(self, "soundChannel", int(v)),
#             "soundChoice":  lambda v: setattr(self, "soundChoice", int(v)),

#             "timeOut":         lambda v: setattr(self, "timeOut", int(v)),
#             "useFallback":     lambda v: setattr(self, "useFallback", bool(v)),
#             "printing":        lambda v: setattr(self, "printing", bool(v)),
#             "synthesizing":    lambda v: setattr(self, "synthesizing", bool(v)),
#             "commands":        lambda v: setattr(self, "commands", v),
#             #"wordRepl":        lambda v: setattr(self, "wordRepl", v),
#             "wordRepl":        self._setWordRepl
#         }
#         setter = propMap.get(propName)
#         if setter:
#             setter(value)
#         else:
#             raise AttributeError(f"Unknown property: '{propName}'. Allowed: {list(propMap)}")

#     def _setWordRepl(self, userRepl):
#         norm = lambda s: re.sub(r"\s+", " ", s.strip().lower())

#         merged: dict[str, str] = {norm(k): v for k, v in DEFAULT_WORD_REPL.items()}

#         if userRepl:
#             for k, v in userRepl.items():
#                 merged[norm(k)] = v  # add/override only, never remove

#         self.wordRepl = merged

#         # Build one compiled regex for efficient replacement
#         tokens = sorted(merged.keys(), key=len, reverse=True)
#         escaped = [re.escape(t).replace(r"\ ", r"\s+") for t in tokens]
#         pattern = r"(?<!\w)(" + "|".join(escaped) + r")(?!\w)"
#         self._wordReplRx = re.compile(pattern, flags=re.IGNORECASE)
#         self._wordReplMap = {t.lower(): merged[t] for t in merged}

#     def voiceInput(self) -> str:
#         printing = self.parent.printing if self.parent else self.printing
#         if not printing:
#             audio = self.captureAudio(selfSpeech=False)
#             if not audio:
#                 return None
#             try:
#                 text = self.processAudio(audio)
#                 if not text or self.ignoreInput(text):
#                     return None
#                 return text.lower().strip()
#             except Exception as e:
#                 logger.error(f"Audio Processing error:", exc_info=True)
#                 return None

#     def ambientInput(self) -> str:
#         audio = self.captureAudio(selfSpeech=True)
#         if not audio:
#             return None
#         try:
#             text = self.processAudio(audio)
#             if not text or self.ignoreInput(text):
#                 return None
#             return text
#         except Exception as e:
#             logger.error(f"Audio Processing error:", exc_info=True)
#             return None

#     def captureAudio(self, selfSpeech=False):
#         parentSynth = self.parent.synthesizing if self.parent else self.synthesizing
#         cond = parentSynth if selfSpeech else not parentSynth
#         if cond:
#             try:
#                 with sr.Microphone() as source:
#                     recognizer = self.parent.recognizer if self.parent else self.recognizer
#                     if not selfSpeech:
#                         recognizer.adjust_for_ambient_noise(source, duration=2)
#                     if selfSpeech:
#                         systemVolume = self._getSystemVolume()
#                         recognizer.energy_threshold = (
#                             1.5 * (1000 + (systemVolume / 100) * (5000 - 1000))
#                         )
#                     try:
#                         audio = recognizer.listen(
#                             source,
#                             timeout=5,
#                             phrase_time_limit=10 if selfSpeech else None
#                         )
#                     except sr.WaitTimeoutError:
#                         logger.warning("No speech detected: timed out while waiting for phrase.")
#                         return None
#                     if selfSpeech:
#                         audioEnergy = audioop.rms(audio.get_raw_data(), audio.sample_width)
#                         if audioEnergy < recognizer.energy_threshold + 500:
#                             return None
#                     if not selfSpeech:
#                         if self.parent:
#                             self.parent.processing = True
#                         else:
#                             self.processing = True
#                     return audio
#             except Exception as e:
#                 logger.error(f"Microphone error:", exc_info=True)
#         return None
    
#     def processAudio(self, audio):
#         def process():
#             if not audio or not isinstance(audio, sr.AudioData):
#                 return None
#             try:
#                 result = self.recognizeWithGoogle(audio)
#                 return result
#             except (sr.RequestError, ConnectionError, Timeout, sr.WaitTimeoutError, Exception):
#                 logger.error("Recognition Error:", exc_info=True)
#                 useFallback = self.parent.useFallback if self.parent else self.useFallback
#                 if useFallback:
#                     logger.info("Switching to Whisper for recognition.")
#                     # return self.recognizeWithWhisper(audio)
#                     result = self.recognizeWithGoogle(audio)
#                     return result
#             return None

#         timeOut = self.parent.timeOut if self.parent else self.timeOut
#         with ThreadPoolExecutor(max_workers=1) as executor:
#             future = executor.submit(process)
#             try:
#                 return future.result(timeout=timeOut)
#             except FuturesTimeoutError:
#                 logger.warning("Audio processing timed out.")
#                 return None

#     def recognizeWithGoogle(self, audio):
#         recognizer = self.parent.recognizer if self.parent else self.recognizer
#         try:
#             text = recognizer.recognize_google(audio).lower()
#             return self._cleanContent(text) if text else None
#         except sr.UnknownValueError:
#             logger.debug("Speech was unintelligible.")
#             return None

#     def keyboardInput(self, keyboardMsg="Enter your input:\n"):
#         if self.parent:
#             self.parent.isActivated = False
#         else:
#             self.isActivated = False
#         msg = input(f"{keyboardMsg} ").lower()
#         return msg.strip()

#     def _getSystemVolume(self):
#         if sys.platform == 'win32':
#             import ctypes
#             winmm = ctypes.WinDLL("winmm.dll")
#             GetVolume = winmm.waveOutGetVolume
#             volume = ctypes.c_uint()
#             GetVolume(0, ctypes.byref(volume))
#             left = volume.value & 0xFFFF
#             right = (volume.value >> 16) & 0xFFFF
#             return (left + right) / 2 / 65535 * 100
#         elif sys.platform == 'darwin':
#             import subprocess
#             output = subprocess.run(
#                 ["osascript", "-e", "output volume of (get volume settings)"],
#                 capture_output=True, text=True)
#             try:
#                 return float(output.stdout.strip())
#             except Exception:
#                 return 50
#         else:
#             try:
#                 import subprocess
#                 proc = subprocess.run(['amixer', 'get', 'Master'], capture_output=True, text=True)
#                 for line in proc.stdout.split('\n'):
#                     if 'Mono:' in line or 'Front Left:' in line:
#                         percent = line.split('[')[1].split('%')[0]
#                         return float(percent)
#             except Exception:
#                 return 50

#     def _cleanContent(self, text, applyReplacements=True, removeNums=False):
#         if not text or not isinstance(text, str):
#             return ""
#         text = text.replace("\n", " ").replace("\n\n", " ")
#         text = re.sub(r"[^\w\s]", "", text).lower().strip()
#         wordRepl = self.parent.wordRepl if self.parent else self.wordRepl
#         if applyReplacements and wordRepl:
#             for word, rep in wordRepl.items():
#                 text = re.sub(rf"\b{re.escape(word)}\b", rep, text, flags=re.IGNORECASE)
#         if removeNums:
#             text = re.sub(r"\d+", "", text)
#         return text

#     def _compareTexts(self, recognized, stored):
#         if not recognized or not isinstance(recognized, str):
#             return "", 0, 0
#         if not stored or not isinstance(stored, str):
#             return "", 0, 0

#         normRec = set(self._cleanContent(recognized, removeNums=True).split())
#         normStored = set(self._cleanContent(stored, removeNums=True).split())
#         filteredWords = normRec - normStored
#         filteredText = " ".join(filteredWords)
#         similarityRatio = self._checkSimilarity(filteredText, " ".join(normStored)) if filteredText else 0
#         overlapRatio = len(filteredWords.intersection(normStored)) / len(filteredWords) if filteredWords else 0
#         return filteredText, similarityRatio, overlapRatio

#     def _checkSimilarity(self, a, b):
#         return SequenceMatcher(None, a, b).ratio()

#     def ignoreInput(self, recognized, similarityThreshold=0.5, overlapThreshold=0.5):
#         if not recognized or not isinstance(recognized, str):
#             return False
#         storedOutput = self.parent.storedOutput if self.parent else self.storedOutput
#         stored = storedOutput[0] if storedOutput else ""
#         _, similarityRatio, overlapRatio = self._compareTexts(recognized, stored)
#         return similarityRatio > similarityThreshold or overlapRatio > overlapThreshold

#     def allowInterruption(self, recognized, similarityThreshold=0.5, overlapThreshold=0.5):
#         if not recognized or not isinstance(recognized, str):
#             return False
#         storedOutput = self.parent.storedOutput if self.parent else self.storedOutput
#         stored = storedOutput[0] if storedOutput else ""
#         _, similarityRatio, overlapRatio = self._compareTexts(recognized, stored)
#         return similarityRatio <= similarityThreshold and overlapRatio <= overlapThreshold



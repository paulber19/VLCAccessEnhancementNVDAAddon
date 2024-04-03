# appModules\vlc\vlc_utils.py
# A part of vlcAccessEnhancement add-on
# Copyright (C) 2024, paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import ui
import speech.speech
try:
	# NVDA >= 2024.1
	speakOnDemand = speech.speech.SpeechMode.onDemand
except AttributeError:
	# NVDA <= 2023.3
	speakOnDemand = None


def executeWithSpeakOnDemand(func, *args, **kwargs):
	from speech.speech import _speechState, SpeechMode
	if not speakOnDemand or _speechState.speechMode != SpeechMode.onDemand:
		return func(*args, **kwargs)
	_speechState.speechMode = SpeechMode.talk
	ret = func(*args, **kwargs)
	_speechState.speechMode = SpeechMode.onDemand
	return ret


def messageWithSpeakOnDemand(msg):
	executeWithSpeakOnDemand(ui.message, msg)

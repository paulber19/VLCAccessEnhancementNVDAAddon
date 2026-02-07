# shared\vlc_settingsHandler.py.
# a part of vlcAccessEnhancement add-on
# Copyright 2019-2025 paulber19
# This file is covered by the GNU General Public License.


import addonHandler
import os
import sys
from logHandler import log
import codecs
import shutil
import shlobj
import speech
import wx
from keyboardHandler import KeyboardInputGesture
from configobj import ConfigObj
from vlc_localeSettingsHandler import LocaleSettings
from vlc_special import makeAddonWindowTitle
from messages import alert, inform, confirm_YesNo, ReturnCode

addonHandler.initTranslation()
_curAddon = addonHandler.getCodeAddon()
debugToolsPath = os.path.join(_curAddon.path, "debugTools")
sys.path.append(debugToolsPath)
try:
	from debug import printDebug
except ImportError:

	def printDebug(msg):
		return
del sys.path[-1]


_defaultVlcKeysAssignment = {
	"key-toggle-fullscreen": "f",
	"key-leave-fullscreen": "escape",
	"key-loop": "l",
	"key-random": "r",
	"global-key-next": "",
	"key-next": "n",
	"global-key-prev": "",
	"key-prev": "p",
	"global-key-pause": "",
	"key-play-pause": "Space",
	"global-key-play": "",
	"global-key-faster": "",
	"key-faster": "numlock+numpadplus",
	"global-key-slower": "",
	"key-slower": "numlock+numpadminus",
	"global-key-rate-normal": "",
	"key-rate-normal": "=",
	"global-key-rate-faster-fine": "",
	"key-rate-faster-fine": "]",
	"global-key-rate-slower-fine": "",
	"key-rate-slower-fine": "[",
	"global-key-next": "",
	"key-next": "n",
	"global-key-prev": "",
	"key-prev": "p",
	"global-key-stop": "",
	"key-stop": "s",
	"global-key-position": "",
	"key-position": "t",
	"key-jump-extrashort": "shift+leftArrow",
	"global-key-jump+extrashort": "",
	"key-jump+extrashort": "shift+rightArrow",
	"global-key-jump-short": "",
	"key-jump-short": "alt+leftArrow",
	"global-key-jump+short": "",
	"key-jump+short": "alt+rightArrow",
	"global-key-jump-extrashort": "",
	"global-key-jump-medium": "",
	"key-jump-medium": "control+leftArrow",
	"global-key-jump+medium": "",
	"key-jump+medium": "control+rightArrow",
	"global-key-jump-long": "",
	"key-jump-long": "control+alt+leftArrow",
	"global-key-jump+long": "",
	"key-jump+long": "control+alt+rightArrow",
	"global-key-vol-up": "",
	"key-vol-up": "control+upArrow",
	"global-key-vol-down": "",
	"key-vol-down": "control+downArrow",
	"global-key-vol-mute": "",
	"key-vol-mute": "m",
	"key-intf-show": "i",
	# added because not documented in vlcrc
	"extra-key-vol-up": "upArrow",
	"extra-key-vol-down": "downArrow",
	"extra-key-jump+short": "rightArrow",
	"extra-key-jump-short": "leftArrow",
}
_vlcHotKeyHelp = (
	("", _("Jump commands:")),
	("key-jump+long", _("Jump 5 minutes after")),
	("key-jump-long", _("Jump 5 minutes before")),
	("key-jump+medium", _("Jump 1 minute after")),
	("key-jump-medium", _("Jump 1 minute before")),
	("key-jump+short", _("Jump 10 secondes after")),
	("extra-key-jump-short", _("Jump 10 secondes before")),
	("extra-key-jump+short", _("Jump 10 secondes after")),
	("key-jump-short", _("Jump 10 secondes before")),
	("key-jump+extrashort", _("Jump 3 secondes after")),
	("key-jump-extrashort", _("Jump 3 secondes before")),
	("", _("Speed commands")),
	("key-faster", _("Increase the playback speed")),
	("key-slower", _("Decrease the playback speed")),
	("key-rate-faster-fine", _("Slightly increase the playback speed")),
	("key-rate-slower-fine", _("Slightly decrease the playback speed")),
	("key-rate-normal", _("Normal rate")),
	("", _("Volume commands:")),
	("key-vol-up", _("Increase volume")),
	("key-vol-down", _("Decrease volume")),
	("extra-key-vol-up", _("Increase volume")),
	("extra-key-vol-down", _("Decrease volume")),
	("", _("Playing commands:")),
	("key-play-pause", _("Play / pause")),
	("key-stop", _("Stop the media")),
	("key-loop", _("Loop playback")),
	("key-random", _("Random playback")),
	("", _("Others commands:")),
	("key-toggle-fullscreen", _("Full screen")),
	("key-leave-fullscreen", _("Leave full screen")),
)

normalSpeedKeys = (
	"global-key-rate-normal",
	"key-rate-normal",
)

# others speed keys
speedKeys = (
	"global-key-faster",
	"key-faster",
	"global-key-slower",
	"key-slower",
	"global-key-rate-faster-fine",
	"key-rate-faster-fine",
	"global-key-rate-slower-fine",
	"key-rate-slower-fine"
)

# jump
jumpKeys = (
	"global-key-jump-extrashort",
	"key-jump-extrashort",
	"global-key-jump+extrashort",
	"key-jump+extrashort",
	"global-key-jump-short",
	"key-jump-short",
	"extra-key-jump-short",
	"global-key-jump+short",
	"key-jump+short",
	"extra-key-jump+short",
	"global-key-jump-medium",
	"key-jump-medium",
	"global-key-jump+medium",
	"key-jump+medium",
	"global-key-jump-long",
	"key-jump-long",
	"global-key-jump+long",
	"key-jump+long"
)

# volume
volumeKeys = (
	"global-key-vol-up",
	"key-vol-up",
	"global-key-vol-down",
	"key-vol-down",
	"extra-key-vol-up",
	"extra-key-vol-down",
)

muteKeys = (
	"global-key-vol-mute",
	"key-vol-mute"
)

playKeys = (
	"global-key-play",
	"key-play-pause",
	"key-stop",
)

movementKeys = (
	"global-key-next",
	"key-next",
	"global-key-prev",
	"key-prev",
)
jumpDelays = {
	"global-key-jump-extrashort": -3,
	"key-jump-extrashort": -3,
	"global-key-jump+extrashort": 3,
	"key-jump+extrashort": 3,
	"global-key-jump-short": -10,
	"key-jump-short": -10,
	"extra-key-jump-short": -10,
	"global-key-jump+short": 10,
	"key-jump+short": 10,
	"extra-key-jump+short": 10,
	"global-key-jump-medium": -60,
	"key-jump-medium": -60,
	"global-key-jump+medium": 60,
	"key-jump+medium": 60,
	"global-key-jump-long": -300,
	"key-jump-long": -300,
	"global-key-jump+long": 300,
	"key-jump+long": 300
}


class VLCSettings(object):
	def __init__(self, addon=None):
		printDebug("VLCSettings __init__")
		self.addon = addon if addon else addonHandler.getCodeAddon()
		self.addonDir = self.addon.path
		self.vlcSettingsDir = self.getVlcSettingsFolderPath()
		if self.vlcInitialized:
			printDebug("VLCSettings: VLC initialized")
		else:
			printDebug("VLCSettings: VLC not initialized")

	@property
	def vlcInitialized(self):
		return self.vlcSettingsDir is not None

	def getVlcSettingsFolderPath(self):
		try:
			if hasattr(shlobj, "SHGetKnownFolderPath"):
				configParent = shlobj.SHGetKnownFolderPath(
					shlobj.FolderId.ROAMING_APP_DATA
				)
			else:
				configParent = shlobj.SHGetFolderPath(0, shlobj.CSIDL_APPDATA)
		except WindowsError:
			log.warning("VLC settings directory not found")
			return None
		dir = os.path.join(configParent, "vlc")
		if os.path.exists(dir):
			return dir
		return None

	def isVLCRunning(self):
		name = "vlc.exe"
		from subprocess import check_output
		c = ["tasklist", "/v"]
		p = check_output(c).strip()
		tempList = str(p).split(r"\r\n")
		for process in tempList:
			if name == process[: len(name)]:
				return True
		return False

	def canDeleteConfigurationFolder(self):
		if self.isVLCRunning():
			# Translators: message to inform the user than VLC is running.
			msg = _("You must stop VLC application before delete configuration folder")
			# Translators: title of message box.
			dialogTitle = _("Warning")
			alert(msg, makeAddonWindowTitle(dialogTitle))
			return False
		if not self.vlcInitialized:
			# Translators: message to inform the user than VLC is not initialized.
			msg = _("Impossible, VLC application is not installed or initialized")
			# Translators: title of message box.
			dialogTitle = _("Warning")
			alert(msg, makeAddonWindowTitle(dialogTitle))
			return False
		return True

	def deleteConfigurationFolder(self):
		printDebug("deleteConfigurationFolder")
		if not self.canDeleteConfigurationFolder():
			return
		try:
			shutil.rmtree(self.vlcSettingsDir)
			# Translators: message to user: VLC configuration folder has been deleted"),
			msg = _(
				"VLC configuration folder (%s) has been deleted. "
				"Before modify VLC shortcuts, you must start VLC once.") % self.vlcSettingsDir
			# Translators: title of message box.
			dialogTitle = _("Information")
			inform(msg, makeAddonWindowTitle(dialogTitle) )
		except OSError:
			# Translators: message to user: VLC configuration folder cannot be deleted.
			msg = _("VLC configuration folder \"%s\" cannot be deleted") % self.vlcSettingsDir
			# Translators: title of message box.
			dialogTitle = _("Error")
			alert(msg, makeAddonWindowTitle(dialogTitle))


class ConfigObjWithoutCommentMarkers(ConfigObj):
	COMMENT_MARKERS = [chr(0xb5)]


class QTInterface (VLCSettings):
	def __init__(self):
		super(QTInterface, self).__init__()
		self._loadRecentFiles()

	def _loadRecentFiles(self):
		from urllib.parse import unquote
		self.recents = {}
		if not self.vlcInitialized:
			return
		qtInterfaceFile = os.path.join(self.vlcSettingsDir, "vlc-qt-interface.ini")
		if not os.path.exists(qtInterfaceFile):
			log.warning("Can find qtInterface ini file: %s" % qtInterfaceFile)
			return
		filesList = []
		timesList = []
		tempList = ""
		src = codecs.open(qtInterfaceFile, "r", "utf_8", errors="replace")
		for line in src:
			tempLine = line.strip()
			if tempLine != "list=@Invalid()" and tempLine.startswith("list="):
				tempList = tempLine[len("list="):].split(", ")
			elif tempLine != "times=@Invalid()" and tempLine.startswith("times="):
				timesList = tempLine[len("times="):].split(", ")
		src.close()
		for item in tempList:
			file = unquote(item)
			filesList.append(file)
		if len(filesList) != len(timesList):
			# error,
			log.warning("Error: number of recent files and time count are different")
			return
		self.firstRecentFile = None
		for index in range(0, len(filesList)):
			f = filesList[index]
			if f[:5] != "file:":
				continue
			p = f[6:]

			if p in self.recents:
				continue
			if index == 0:
				# memorize first recent file (probably current file)
				self.firstRecentFile = p
			self.recents[p] = timesList[index]
		return True


class Vlcrc(VLCSettings):
	def __init__(self):
		self.initialized = False
		super(Vlcrc, self).__init__()
		# get addon settings
		self.localeSettings = LocaleSettings()
		self.vlcrcFile = None
		if not self.vlcInitialized:
			return
		vlcrcFile = os.path.join(self.vlcSettingsDir, "vlcrc")
		if not os.path.exists(vlcrcFile):
			return
		self.vlcrcFile = vlcrcFile
		# read the file
		self.content = self.load()
		if self.content is not None:
			self.initialized = True

	def exist(self):
		return self.vlcrcFile is not None

	def load(self):
		if self.exist() is None:
			return None
		src = codecs.open(self.vlcrcFile, "r", "utf_8", errors="replace")
		lines = []
		for line in src:
			lines.append(line)
		src.close()
		return lines

	def save(self, lines):
		if self.exist() is None:
			return False
		dest = codecs.open(self.vlcrcFile, "w", "utf_8", errors="replace")
		for line in lines:
			dest.write(line)
		dest.close()
		return True

	def _firstPass(self, newVLCKeys):
		if self.content is None:
			return
		# delete vlc key definition which must be modified

		keyNames = list(newVLCKeys.keys())
		newLines = []
		for line in self.content:
			if line.strip() == "" or line[0] in ["#", "["]:
				pass
			else:
				key = line.split("=")[0]
				try:
					key = key.strip()
				except Exception:
					pass
				if key in keyNames:
					# jump this line
					continue
			newLines.append(line)
		return newLines

	def _secondPass(self, lines, newVLCKeys):
		# add new key definition
		keyNames = list(newVLCKeys.keys())
		newLines = []
		for line in lines:
			newLines.append(line)
			if line[0] == "#":
				key = line[1:].split("=")[0]
				try:
					key = key.strip()
				except Exception:
					pass
				if key in keyNames:
					line = "%s=%s\r\n" % (key, newVLCKeys[key])
					newLines.append(line)
					printDebug("VLC Shortcut modification: %s" % line)
		return newLines

	def canUpdateVlcrcFile(self):
		if self.isVLCRunning():
			# Translators: message to inform the user than VLC is running.
			msg = _("You must stop VLC application before modify VLC configuration file")
			# Translators: title of message box.
			dialogTitle = _("Warning")
			alert(msg, makeAddonWindowTitle(dialogTitle))
			return False
		if not self.vlcInitialized:
			# Translators: message to inform the user than VLC is not initialized.
			msg = _("Impossible, VLC application is not installed or initialized")
			# Translators: title of message box.
			dialogTitle = _("Warning")
			alert(msg, makeAddonWindowTitle(dialogTitle))
			return False
		if not self.exist():
			# Translators: message to inform the user than VLC is not initialized.
			msg = _("Error, VLC configuration is not found")
			# Translators: title of message box.
			dialogTitle = _("Warning")
			alert(msg, makeAddonWindowTitle(dialogTitle))
			return False
		return True

	def update(self):
		speech.cancelSpeech()
		# Translators: message to the user.
		speech.speakMessage(_("Please wait"))
		newVLCKeys = self.localeSettings.getVLCKeysToUpdate()
		if newVLCKeys is None:
			# no vlcrc modification
			# Translators: message to user than there is no VLC keys to modify.
			msg = _("There is no key modification to do")
			# Translators: title of message box.
			dialogTitle = _("Information")
			inform(msg, makeAddonWindowTitle(dialogTitle))
			return
		if not self.canUpdateVlcrcFile():
			return
		text = self.getNewVLCKeysHelp()
		if confirm_YesNo(
			# Translators: message to ask the user if he accepts the update.
			text + ". " + _("Are you OK?"),
			# Translators: title of message box.
			_("%s add-on - Confirmation") % self.addon.manifest["summary"]
		) != ReturnCode.YES:
			return
		lines = self._firstPass(newVLCKeys)
		lines = self._secondPass(lines, newVLCKeys)
		dest = os.path.join(self.vlcSettingsDir, "vlcrc.old")
		if os.path.exists(dest):
			os.remove(dest)
		shutil.copy(self.vlcrcFile, dest)
		try:
			shutil.copy(self.vlcrcFile, dest)
		except Exception:
			log.warning("vlcrc file cannot be copied to old file")

		self.save(lines)
		# Translators: message to inform the user than olcrc file has been updated.
		msg = _("VLC configuration file has been updated")
		# Translators: title of message box.
		dialogTitle = _("Information")
		inform(msg, makeAddonWindowTitle(dialogTitle))

	def normalizeKeyToVLC(self, key):
		NVDAKeyToVLCKey = {
			"control": "ctrl",
			"leftArrow": "left",
			"rightArrow": "right",
			"upArro": "up",
			"downArrow": "down"
		}
		newKey = key.split("+")
		for item in NVDAKeyToVLCKey:
			if item in newKey:
				newKey[newKey.index(item)] = NVDAKeyToVLCKey[item]
		return "+".join(newKey)

	def normalizeKeyToNVDA(self, key):
		vlcKeyToNVDAKey = {
			"esc": "Escape",
			"ctrl": "control",
			"left": "leftArrow",
			"right": "rightArrow",
			"up": "upArrow",
			"down": "downArrow",
			"-": "numlock+numpadminus",
		}
		if key == "+":
			return "numlock+numpadplus"
		k = key.replace("++", "+numlock+numpadplus")
		newKey = [x.lower() for x in k.split("+")]
		for item in vlcKeyToNVDAKey:
			if item in newKey:
				newKey[newKey.index(item)] = vlcKeyToNVDAKey[item]
		return "+".join(newKey)

	def getNewVLCKeysHelp(self):
		newVLCKeys = self.localeSettings.getVLCKeysToUpdate()
		if newVLCKeys is None:
			return ""
		vlcKeyNames = list(newVLCKeys.keys())
		# Translators: message to the user.
		text = _("The VLC command keys which will be record in the VLC configuration file are:") + "\r\n"
		for (keyName, msg) in _vlcHotKeyHelp:
			if keyName not in vlcKeyNames:
				continue
			key = self.normalizeKeyToNVDA(newVLCKeys[keyName])
			if len(key) in [0, 1]:
				text = text + "%s %s" % (msg, key) + "\n"
			else:
				gesture = KeyboardInputGesture.fromName(key)
				text = text + "%s %s" % (msg, gesture.displayName) + "\n"
		return text

	def vlcHotKeyHelpText(self):
		text = _("VLC command's keys:") + "\n"
		for (keyName, msg) in _vlcHotKeyHelp:
			if keyName == "":
				text = text + "%s\n" % msg
			else:
				key = self.normalizeKeyToNVDA(self.vlcKeysAssignment[keyName])
				if len(key) in [0, 1]:
					text = text + "%s %s" % (msg, key) + "\n"
				else:
					gesture = KeyboardInputGesture.fromName(key)
					text = text + "%s %s" % (msg, gesture.displayName) + "\n"
		return text

	def _getVlcKeysAssignment(self):

		def getKeyNameAndKey(line):
			tempList = line.replace("\r", "")
			tempList = tempList.replace("\n", "")
			for ch in tempList:
				if ch == "=":
					index = tempList.index(ch)
					keyName = tempList[:index]
					key = tempList[index + 1:]
					if "key-" in keyName:
						if key != "":
							key = self.normalizeKeyToNVDA(key)
						return (keyName, key)
			return (None, None)
		vlcKeysAssignment = _defaultVlcKeysAssignment .copy()
		if self.content is None:
			return vlcKeysAssignment
		keyNames = list(vlcKeysAssignment.keys())
		keys = vlcKeysAssignment
		for line in self.content:
			if line.strip() == "" or line[0] in ["[", ]:
				continue
			elif line[0] == "#":
				line = line[1:]
			(keyName, key) = getKeyNameAndKey(line)
			if keyName is not None and ("key-" in keyName or "global-key-" in keyName):
				if keyName in keyNames:
					keys[keyName] = key
		return keys

	@property
	def vlcKeysAssignment(self):
		if hasattr(self, "_vlcKeysAssignment"):
			return self._vlcKeysAssignment
		self._vlcKeysAssignment = self._getVlcKeysAssignment()
		return self._vlcKeysAssignment

	def getKeyFromName(self, name):
		try:
			key = self.vlcKeysAssignment[name]
			return key.lower()
		except Exception:
			return ""

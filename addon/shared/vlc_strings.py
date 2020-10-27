# shared\vlc_strings.py.
# a part of vlcAccessEnhancement add-on
# Copyright 2018-2020 paulber19
# This file is covered by the GNU General Public License.


import addonHandler
from logHandler import log
import os
import sys
from configobj import ConfigObj, ConfigObjError  # noqa:F401
# ConfigObj 5.1.0 and later integrates validate module.
try:
	from configobj.validate import Validator
except ImportError:
	from validate import Validator
from IAccessibleHandler import accessibleObjectFromEvent, accNavigate
from oleacc import *  # noqa:F403
import ctypes
from vlc_settingsHandler import *  # noqa:F403
from vlc_py3Compatibility import importStringIO
StringIO = importStringIO()


def printDebug(str): return


_curAddon = addonHandler.getCodeAddon()
debugToolsPath = os.path.join(_curAddon.path, "debugTools")
sys.path.append(debugToolsPath)
try:
	# from debug import printDebug, toggleDebugFlag
	pass
except ImportError:
	def prindDebug(msg): return
del sys.path[-1]

# this file manage necessary strings to recognize some objects depending
# of vlc language.
# this strings must be defined in strings-xx.ini file for each vlc language.
# this files are placed in vlcLocale folder.

# main section
ID_LanguageName = "LanguageName"
ID_StringToFindLanguage = "StringToFindLanguage"

# for vlc module
# base title of main window
ID_VLCAppTitle = "VLCAppTitle"
# play button description: second child of third border object
# of first client object
ID_PlayButtonDescription = "PlayButtonDescription"
# pauseThePlayback button description: child of third border object
# of first client object
ID_PauseThePlaybackButtonDescription = "PauseThePlaybackButtonDescription"
# unMute image description :first child of client object.
ID_UnMuteImageDescription = "UnMuteImageDescription"
# normal|loop|repeat check button description
ID_LoopCheckButtonDescription = "LoopCheckButtonDescription"
# Random check button description
ID_RandomCheckButtonDescription = u"RandomCheckButtonDescription"
# title of media information dialog
ID_MediaInformationDialogTitle = u"MediaInformationDialogTitle"


# singleton to store all strings dictionnaries
_stringsDics = None

# confspec definitions
SCTN_Main = "Main"
SCTN_VLC = "vlc.py".split(".")[0]

mainSection = """
[{main}]
{LanguageName} = string(default = "en")
{StringToFindLanguage} = string(default = "Playback Alt+l")
""".format(
	main=SCTN_Main,
	LanguageName=ID_LanguageName,
	StringToFindLanguage=ID_StringToFindLanguage)

_playButtonDefaultDescription = """Play\nif the playlist is empty, open a medium"""

_vlcSection = """
[{module}]
{vlcAppTitle} = string(default = "VLC media player")
{playButtonDescription} =string(default = {playDefault})
{pauseThePlaybackButtonDescription} = string(default = "Pause the playback")
{unMute} = string(default = "Unmute")
{loopCheckButtonDescription} = string(default = "Click to toggle between loop all, loop one and no loop")
{randomCheckButtonDescription} = string(default = "Random")
{mediaInformationDialogTitle} = string(default = "MetaDatasDialogTitle")
""".format(
	module=SCTN_VLC,
	vlcAppTitle=ID_VLCAppTitle,
	playButtonDescription=ID_PlayButtonDescription,
	playDefault="",
	pauseThePlaybackButtonDescription=ID_PauseThePlaybackButtonDescription,
	unMute=ID_UnMuteImageDescription,
	loopCheckButtonDescription=ID_LoopCheckButtonDescription,
	randomCheckButtonDescription=ID_RandomCheckButtonDescription,
	mediaInformationDialogTitle=ID_MediaInformationDialogTitle)

_confSpec = ConfigObj(StringIO("""
	{main}
	{vlc}
	""".format(main=mainSection, vlc=_vlcSection)
	), list_values=False, encoding="UTF-8")
_confSpec.newlines = "\r\n"

_stringsFileBaseName = "strings-"
_stringsIniFilesDirName = "vlcLocale"


def get_stringsIniFilePath(appLanguage):
	if appLanguage == "":
		return None
	_addonDir = addonHandler.getCodeAddon().path
	file = os.path.join(
		_addonDir,
		_stringsIniFilesDirName,
		_stringsFileBaseName + str(appLanguage) + ".ini")
	if not os.path.exists(file):
		log.error("No strings Ini file: {}".format(file))
		return None
	return file


def loadFileConfig(file):
	try:
		conf = ConfigObj(
			file, configspec=_confSpec, indent_type="\t", encoding="UTF-8")
	except ConfigObjErrore:
		return None
	conf.newlines = "\r\n"
	val = Validator()
	result = conf.validate(val)
	if not result:
		return None
	conf.newlines = "\r\n"
	return conf


def getSupportedLanguages():
	printDebug("getSupportedLanguages")
	# set path of strings ini files directory
	currAddon = addonHandler.getCodeAddon()
	stringsIniFilesDir = os.path.join(currAddon.path, _stringsIniFilesDirName)
	# get list of all strings ini files
	stringsIniFilesList = _getStringsIniFilesList(stringsIniFilesDir)
	# search for vlc language
	supportedLanguages = []
	for file in stringsIniFilesList:
		stringsIniFile = os.path.join(stringsIniFilesDir, file)
		conf = loadFileConfig(stringsIniFile)
		if conf is None:
			continue
		lang1 = conf[SCTN_Main]["LanguageName"]
		temp = file.split("-")[-1]
		lang2 = temp.split(".")[0]
		supportedLanguages.append((lang1, lang2))
	return supportedLanguages


def _getStringsIniFilesList(stringsFilesDir):
	itemList = os.listdir(stringsFilesDir)
	FilesList = []
	for item in itemList:
		theFile = os.path.join(stringsFilesDir, item)
		if not os.path.isdir(theFile)\
			and os.path.splitext(theFile)[1] == ".ini"\
			and _stringsFileBaseName in item:
			FilesList.append(item)
	return FilesList


def _getRandomCheckButtonLabel():
	printDebug("vlcStrings: _getRandomCheckButtonLabel")
	hdMain = ctypes.windll.user32.GetForegroundWindow()
	(oIA, childID) = accessibleObjectFromEvent(hdMain, 0, 0)
	(o, childID) = accNavigate(oIA, 0, NAVDIR_FIRSTCHILD)
	while o:
		if o.accRole(0) == ROLE_SYSTEM_WINDOW:
			break

		try:
			(o, childID) = accNavigate(o, 0, NAVDIR_NEXT)
		except:  # noqa:E722
			o = None

	try:

		(o, childID) = accNavigate(o, 0, NAVDIR_LASTCHILD)
		(o, childID) = accNavigate(o, 0, NAVDIR_LASTCHILD)
		(o, childID) = accNavigate(o, 0, NAVDIR_LASTCHILD)
		if o.accRole(0) == ROLE_SYSTEM_CHECKBUTTON:
			return o.accDescription(0)
	except:  # noqa:E722
		log.warning("vlc_strings: cannot find random check button")
	return None


def _loadStringsDic():
	global _stringsDics
	printDebug("vlc_strings: _loadStringsDic")
	if _stringsDics is not None:
		printDebug("_loadStringsDic: allready loaded")
		return
	# get label to identify vlc language
	label = _getRandomCheckButtonLabel()
	if label is None:
		printDebug("Random Check button is not found")
		return
	printDebug("_loadStringsDic: randomCheckButton description= %s" % label)
	printDebug("_loadStringsDic: search vlc language")
	# set path of strings ini files directory
	currAddon = addonHandler.getCodeAddon()
	stringsIniFilesDir = os.path.join(currAddon.path, _stringsIniFilesDirName)
	# get list of all strings ini files
	stringsIniFilesList = _getStringsIniFilesList(stringsIniFilesDir)
	# search for vlc language
	languageFound = False
	for file in stringsIniFilesList:
		stringsIniFile = os.path.join(stringsIniFilesDir, file)
		conf = loadFileConfig(stringsIniFile)
		if conf is None:
			continue
		if conf[SCTN_VLC][ID_RandomCheckButtonDescription] == label:
			# language found
			log.warning("VLCAccessEnhancement: VLC language found= %s" % conf[SCTN_Main][ID_LanguageName])  # noqa:E501
			languageFound = True
			break
	if not languageFound:
		log.warning("_loadStringsDic: no language found")
		return
	_stringsDics = conf.copy()
	printDebug("_loadStringsDic: loaded")


def getString(stringID):
	noneString = "???None???"
	section = "vlc"
	printDebug("vlcStrings: _getString: section = %s, stringID = %s" % (section, stringID))  # noqa:E501
	if _stringsDics is None:
		_loadStringsDic()
		if _stringsDics is None:
			printDebug("VLC_Strings: strings are not loaded")
			return noneString

	if section not in _stringsDics:
		log.warning("getStrings error: not section %s in _stringsDic" % module)
		return noneString
	dic = _stringsDics[section]
	if stringID not in list(dic.keys()):
		log.warning("getStrings error: not string \"%s\" in dic" % stringID)
		return noneString
	return dic[stringID]


def init():
	printDebug("vlcStrings init")
	global _stringsDics
	_stringsDics = None


def terminate():
	printDebug("vlcStrings terminate")
	global _stringsDics
	_stringsDics = None

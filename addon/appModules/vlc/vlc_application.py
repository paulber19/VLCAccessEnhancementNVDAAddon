# appModules\vlc\vlc_application.py.
# a part of vlcAccessEnhancement add-on
# Copyright 2019-2022 paulber19
# This file is covered by the GNU General Public License.


import addonHandler

from logHandler import log
from controlTypes.role import Role
from controlTypes.state import State
import api
import speech
import queueHandler
import ui
import keyboardHandler
import time
import wx
import os
import mouseHandler
import oleacc
import ctypes
from NVDAObjects.IAccessible import getNVDAObjectFromEvent
import winUser
from IAccessibleHandler import accNavigate, accParent
from .vlc_utils import executeWithSpeakOnDemand
import sys

_curAddon = addonHandler.getCodeAddon()
debugToolsPath = os.path.join(_curAddon.path, "debugTools")
sys.path.append(debugToolsPath)
try:
	from appModuleDebug import printDebug
except ImportError:

	def printDebug(msg):
		return
del sys.path[-1]
sharedPath = os.path.join(_curAddon.path, "shared")
sys.path.append(sharedPath)
import vlc_strings
from vlc_strings import getString
from vlc_utils import (
	getSpeechMode, setSpeechMode, setSpeechMode_off,
	leftClick, getTimeInSec, formatTime
)

del sys.path[-1]

addonHandler.initTranslation()

ID_NoPlaylist = 0
ID_AnchoredPlaylist = 1
ID_EmbeddedPlaylist = 2


def getForegroundObject():
	hdMain = ctypes.windll.user32.GetForegroundWindow()
	if not getString(vlc_strings.ID_VLCAppTitle) in winUser.getWindowText(hdMain):
		hdMain = winUser.getWindow(winUser.getWindow(hdMain, 2), 2)
	o = getNVDAObjectFromEvent(hdMain, -4, 0)
	return o


def queueMessage(msg):
	queueHandler.queueFunction(
		queueHandler.eventQueue, ui.message, msg)


class MainWindow (object):
	_curMediaState = None
	_continuePlayback = None
	_volumeState = (None, None)
	_loopState = None

	def __init__(self, vlcrcSettings):
		super(MainWindow, self).__init__()
		self.vlcrcSettings = vlcrcSettings

	@property
	def topNVDAObject(self):
		if hasattr(self, "_topNVDAObject"):
			return self._topNVDAObject
		printDebug("topNVDAObject init")
		oDesktop = api.getDesktopObject()
		for i in range(0, oDesktop.childCount):
			obj = oDesktop.getChild(i)
			if obj.windowClassName == u'Qt5QWindowIcon' and obj.childCount == 7:
				o = obj.getChild(3)
				first = o.firstChild
				if first and first.role == Role.MENUBAR\
					and first.childCount == 8:
					self._topNVDAObject = o
					return o
			if obj == obj.next:
				break
			obj = obj.next
		printDebug("topNVDAObject not found")
		return None

	@property
	def mainPanel(self):
		if hasattr(self, "_mainPanel"):
			return self._mainPanel
		mainPanel = MainPanel(self)
		if mainPanel is not None:
			self._mainPanel = mainPanel
			self.volumeInfos = VolumeInfos(self)

			return mainPanel
		return None

	def getStatusBar(self):
		try:
			statusBar = self.topNVDAObject.firstChild.next
		except Exception:
			statusBar = None
		if statusBar is None:
			log.warning("getStatusBar: status bar not found")
		return statusBar

	def getMediaViewNVDAObject(self):
		mediaInfos = MediaInfos(self)
		return mediaInfos.getViewNVDAObject()

	def reportContinuePlayback(self, continuePlaybackScriptGesture):
		if not self.hasMedia:
			return
		(continuePlayback, msg) = self.mainPanel.getcontinuePlayback()
		if (continuePlayback != self._continuePlayback):
			if continuePlayback:
				if continuePlaybackScriptGesture is not None:
					# Translators: message to user when continue playing is available.
					msg = _("Continue playback %s") % continuePlaybackScriptGesture
				else:
					# Translators: message to user when continue playing is available.
					msg = _("Continue playback %s") % "alt+r"
				queueMessage(msg)
				printDebug("MainWindow: reportContinuePlayback, start = %s" % msg)
			self._continuePlayback = continuePlayback

	def reportMediaStates(self):
		# no state report when appModule is terminated or vlc main window loses focus
		if not self.topNVDAObject.hasFocus:
			return
		(muteState, level) = self.getVolumeMuteStateAndLevel()
		if not self.hasMedia():
			if muteState:
				# Translators: message to the user to say volume is muted.
				queueMessage(_("volume muted"))
			return
		isPlaying = self.isPlaying()
		printDebug("MainWindow: reportMediaStates playing= %s, oldPlaying= %s, mute = %s" % (
			isPlaying, self._curMediaState, muteState))
		if self._curMediaState is not None and (isPlaying == self._curMediaState):
			return
		if muteState:
			# Translators: message to user when volume is muted
			msg = _("volume muted")
			if isPlaying:
				# Translators: message to the user to say playing with muted volume.
				msg = _("Playing,%s") % msg
			else:
				# translators: message to the user to say pause with muted volume.
				msg = _("Pause,%s") % msg
			queueMessage(msg)
		elif not isPlaying:
			# Translators: message to the user to say media is paused.
			queueMessage(_("Pause"))
		self.updateCurMediaState()

	def reportMenubarState(self):
		# no report when appModule is terminated or vlc main window loses focus
		if not self.topNVDAObject.hasFocus:
			return
		menubar = Menubar(self)
		if menubar is None:
			return
		if not menubar.isVisible():
			# Translators: message to user to report menubar is not visible
			queueMessage(_("Menu bar is hidden"))

	def resetMediaStates(self, alsoContinuePlayback=True):
		self._curMediaState = None
		if alsoContinuePlayback:
			self._continuePlayback = None

	def reportMediaName(self):
		mediaInfos = MediaInfos(self)
		mediaName = mediaInfos.getName()
		if mediaName is None:
			# Translators: message to the user to say there is no media.
			queueMessage(_("No media"))
		else:
			queueMessage(mediaName)

	def reportMediaChange(self):
		speech.cancelSpeech()
		self.reportMediaName()
		self.resetMediaStates()
		self.reportMediaStates()

	def reportViewState(self):
		screenSize = wx.GetDisplaySize()
		try:
			delattr(self, "topNVDAObject")
			(x, y, h, w) = self.mainPanel.NVDAObject.location
			if (x, y) == (0, 0) and (h, w) == screenSize:
				# Translators: message to user to report full screen state.
				queueMessage(_("Full screen"))
		except Exception:
			pass

	def hasMedia(self):
		mediaInfos = MediaInfos(self)
		if mediaInfos is None:
			return False
		mediaName = mediaInfos.getName()
		if mediaName is None:
			return False
		return True

	def isPlaying(self):
		mediaInfos = MediaInfos(self)
		if mediaInfos:
			return mediaInfos.isPlaying()

	def getTotalTime(self):
		mediaInfos = MediaInfos(self)
		return mediaInfos.getTotalTime()

	def getElapsedTime(self):
		mediaInfos = MediaInfos(self)
		return mediaInfos.getElapsedTime()

	def sayElapsedTime(self, forced=False):
		if not self.hasMedia():
			return
		(muteState, level) = self.volumeInfos.getMuteAndLevel()
		if not muteState and not forced and self.isPlaying():
			return
		from vlc_addonConfig import _addonConfigManager
		if not forced and not _addonConfigManager.getAutoElapsedTimeReportOption():
			return
		elapsedTime = self.getElapsedTime()
		if elapsedTime:
			# Translators: message to the user to say played duration.
			msg = _("Played duration %s") if forced else "%s"
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				executeWithSpeakOnDemand,
				ui.message,
				msg % formatTime(elapsedTime)
			)

	def sayRemainingTime(self):
		if not self.hasMedia():
			return
		mediaInfos = MediaInfos(self)
		remainingTime = mediaInfos.getRemainingTime()
		# Translators: message to the user to report remaining duration.
		msg = _("Remaining duration %s")
		if remainingTime:
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				executeWithSpeakOnDemand,
				ui.message,
				msg % formatTime(remainingTime)
			)
			return
		# Translators: remaining time is unknown.
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			executeWithSpeakOnDemand,
			ui.message,
			msg % _("unknown")
		)

	def getVolumeMuteStateAndLevel(self):
		return self.volumeInfos.getMuteAndLevel()

	def getSpeedValue(self):
		# speed value is on third child of status bar
		statusBar = StatusBar(self).NVDAObject
		o = statusBar.getChild(2)
		if o and "x" in o.name:
			st1, st, st2 = o.name, "", ""
			sst1 = st1.split(".")
			st2 = sst1[-1]
			if st2[-2] == "0":
				st2 = st2.replace("0", "")
			if st2 == "x":
				st = "".join(sst1[0] + st2)
			else:
				st = "".join(sst1[0] + "." + st2)
			return st
		return ""

	def reportVolumeStateChange(self):
		(muteState, level) = self.volumeInfos.getMuteAndLevel()
		printDebug("MainWindow: reportVolumeStateChange: mute= %s, level= %s" % (muteState, level))
		if (muteState, level) == self._volumeState:
			return
		self._volumeState = (muteState, level)
		if not self.isPlaying() or muteState:
			# Translators: message to the user to report volume level.
			queueMessage(_("Volume: %s") % str(level))
			if muteState:
				# Translators: message to the user to say volume is muted.
				queueMessage(_("Volume mute"))

	def updateCurMediaState(self):
		self._curMediaState = self.isPlaying()

	def togglePlayOrPause(self):
		self.mainPanel.togglePlayPause()
		self.updateCurMediaState()

	def reportLoopStateChange(self):
		speech.cancelSpeech()
		loopState = self.mainPanel.getLoopState()
		if loopState:
			# Translators: message to user to report loop state :
			# repeat all or repeat only current media.
			msg = _("Repeat all") if not self._loopState else _("Repeat only current media")
		else:
			# Translators: message to user to report no repeat state.
			msg = _("No repeat")
		queueMessage(msg)
		self._loopState = loopState

	def reportRandomStateChange(self):
		speech.cancelSpeech()
		randomState = self.mainPanel.getRandomState()
		# Translators: message to user to report random or normal playback state.
		msg = _("Random playback") if randomState else _("Normal playback")
		queueMessage(msg)

	def reportLoopAndRandomStates(self):
		self._loopState = self.mainPanel.getLoopState()
		randomState = self.mainPanel.getRandomState()
		msg = None
		if self._loopState and randomState:
			# Translators: message to user to report repeat and random playback state.
			msg = _("With repeat and random playback")
		elif self._loopState:
			# Translators: message to user to report only repeat playback state
			msg = _("With repeat")
		elif randomState:
			# Translators: message to user to report only random playback state.
			msg = _("With random playback")
		if msg is not None:
			queueMessage(msg)

	def calculatePosition(self, jumpTimeInSec, totalTimeInSec, isPlaying):
		mainWindow = self
		o1 = mainWindow.getMediaViewNVDAObject()
		(x, y, l, h) = o1.location
		iX = (int(x) + 5) + (int(l) - 10) * jumpTimeInSec / totalTimeInSec
		return (iX, int(y) + int(h) / 2)

	def adjustPosition(self, jumpTimeInSec, totalTimeInSec, x, y):
		def moveBy10Sec(count, direction):
			printDebug("MainWindow: moveBy10sec: count= %s, direction = %s" % (count, direction))
			keyToRight = self.vlcrcSettings.getKeyFromName("key-jump+short")
			keyToLeft = self.vlcrcSettings.getKeyFromName("key-jump-short")
			key = keyToRight if direction > 0 else keyToLeft
			d = 0
			if count:
				for i in range(1, count + 1):
					keyboardHandler.KeyboardInputGesture.fromName(key).send()
					d += direction * 10
			return d

		def moveBy3Sec(count, direction):
			printDebug("MainWindow: moveBy3sec: count= %s, direction = %s" % (count, direction))
			keyToRight = self.vlcrcSettings.getKeyFromName("key-jump+extrashort")
			keyToLeft = self.vlcrcSettings.getKeyFromName("key-jump-extrashort")
			key = keyToRight if direction > 0 else keyToLeft
			d = 0
			if count != 0:
				for i in range(1, count + 1):
					keyboardHandler.KeyboardInputGesture.fromName(key).send()
					d += direction * 3
			return d
		printDebug("MainWindow: adjustPosition")
		actionsForOffset = {
			1: ((3, moveBy3Sec, -1), (1, moveBy10Sec, 1)),
			2: ((1, moveBy10Sec, -1), (4, moveBy3Sec, 1)),
			3: ((1, moveBy3Sec, 1),),
			4: ((2, moveBy3Sec, -1), (1, moveBy10Sec, 1)),
			5: ((1, moveBy10Sec, -1), (5, moveBy3Sec, 1)),
			6: ((2, moveBy3Sec, 1),),
			7: ((1, moveBy3Sec, -1), (1, moveBy10Sec, 1)),
			8: ((1, moveBy10Sec, -1), (6, moveBy3Sec, 1)),
			9: ((3, moveBy3Sec, 1),)
		}
		curTimeInSec = getTimeInSec(self.getElapsedTime())
		diff = curTimeInSec - jumpTimeInSec
		direction = 1 if diff < 0 else -1
		diff = abs(diff)
		if diff == 0:
			# nothing to do
			return
		if diff > 20:
			leftClick(x, y)
			time.sleep(0.2)
			api.processPendingEvents()

			curTimeInSec = getTimeInSec(self.getElapsedTime())
			diff = curTimeInSec - jumpTimeInSec
			direction = 1 if diff < 0 else -1
			diff = abs(diff)
		if diff % 10 == 0:
			moveBy10Sec(diff / 10, direction)
			return
		if (diff % 3) == 0:
			moveBy3Sec(diff / 3, direction)
			return
		if curTimeInSec <= 19 and direction > 0\
			or totalTimeInSec - curTimeInSec <= 19 and direction < 0:
			moveBy10Sec(1, direction)
			diff = 10 - diff
			direction = (-1) * direction
		if diff > 9:
			moveBy10Sec(diff / 10, direction)
			diff = diff % 10
			if diff == 0:
				return
		actions = actionsForOffset[diff]
		for action in actions:
			move = action[1]
			count = action[0]
			d = action[2]
			move(count, d * direction)

	def jumpToTime(self, jumpTime, totalTime, startPlaying=False):
		printDebug("MainWindow: jumpToTime")
		mainWindow = self
		speech.cancelSpeech()
		oldSpeechMode = getSpeechMode()
		setSpeechMode_off()
		api.processPendingEvents()
		speech.cancelSpeech()
		if jumpTime is None or jumpTime == 0:
			setSpeechMode(oldSpeechMode)
			# Translators: message to the user to report no time change.
			queueMessage(_("No change"))
			queueHandler.queueFunction(
				queueHandler.eventQueue, mainWindow.sayElapsedTime, True)
			queueHandler.queueFunction(
				queueHandler.eventQueue, mainWindow.reportMediaStates)
			return
		isPlaying = mainWindow.isPlaying()
		curTimeInSec = getTimeInSec(mainWindow.getElapsedTime())
		if type(jumpTime) is int:
			jumpTimeInSec = jumpTime
		else:
			jumpTimeInSec = getTimeInSec(jumpTime)

		if abs(curTimeInSec - jumpTimeInSec) <= 2:
			# we are at time
			setSpeechMode(oldSpeechMode)
			queueHandler.queueFunction(
				queueHandler.eventQueue, mainWindow.sayElapsedTime)
			queueHandler.queueFunction(
				queueHandler.eventQueue, mainWindow.reportMediaStates)
			if not isPlaying and startPlaying:
				mainWindow.togglePlayOrPause()
				return
		if isPlaying:
			# pause playing
			mainWindow.togglePlayOrPause()
			time.sleep(0.2)
		totalTimeInSec = getTimeInSec(totalTime)
		(x, y) = self.calculatePosition(jumpTimeInSec, totalTimeInSec, isPlaying)
		leftClick(int(x), int(y))
		api.processPendingEvents()
		time.sleep(0.2)
		winUser.setCursorPos(int(x), int(y - 20))
		mouseHandler.executeMouseMoveEvent(x, y)
		speech.cancelSpeech()
		setSpeechMode(oldSpeechMode)
		# wait for new time
		api.processPendingEvents()
		i = 20
		newCurTimeInSec = getTimeInSec(mainWindow.getElapsedTime())
		while i > 0 and newCurTimeInSec == curTimeInSec:
			time.sleep(0.05)
			i = i - 1
			if i == 0:
				# time out
				# Translators: message to the user to say that jump is not possible.
				queueMessage(_("Jump is not possible"))
				queueHandler.queueFunction(
					queueHandler.eventQueue, mainWindow.sayElapsedTime)
				queueHandler.queueFunction(
					queueHandler.eventQueue, mainWindow.reportMediaStates)
				printDebug("MainWindow: jump is not completed")
				return

			newCurTimeInSec = getTimeInSec(mainWindow.getElapsedTime())
		if newCurTimeInSec != jumpTimeInSec:
			self.adjustPosition(jumpTimeInSec, totalTimeInSec, x, y)
		if not startPlaying and isPlaying:
			mainWindow.togglePlayOrPause()
			queueHandler.queueFunction(
				queueHandler.eventQueue, mainWindow.reportMediaStates)
			return

		queueHandler.queueFunction(
			queueHandler.eventQueue, mainWindow.sayElapsedTime)
		if startPlaying:
			mainWindow.togglePlayOrPause()
		queueHandler.queueFunction(
			queueHandler.eventQueue, mainWindow.reportMediaStates)


class MediaInfos(object):
	def __init__(self, mainWindow):
		super(MediaInfos, self).__init__()
		self.mainWindow = mainWindow
		self.mainPanelNVDAObject = self.mainWindow.mainPanel.NVDAObject
		self.statusBar = StatusBar(mainWindow).NVDAObject

	@property
	def timesNVDAObject(self):
		if hasattr(self, "_timesNVDAObject") and self._timesNVDAObject is not None:
			return self._timesNVDAObject
		oMain = self.mainPanelNVDAObject
		# try:
		if True:
			for o in oMain.children:
				if o.role == Role.BORDER:
					self._timesNVDAObject = o
					return o
		# except:
		else:
			self._timesNVDAObject = None
		log.warning("ObjectTime not found")
		return self._timesNVDAObject

	def isPlaying(self):
		try:
			oDeb = self.timesNVDAObject.next.IAccessibleObject
			count = oDeb.accChildCount
		except Exception:
			return False
		i = 0
		while i < count:
			o = oDeb.accChild(i)
			i = i + 1
			if o.accRole(0) == oleacc.ROLE_SYSTEM_PUSHBUTTON and getString(
				vlc_strings.ID_PauseThePlaybackButtonDescription) == o.accDescription(0):
				return True
		return False

	def getViewNVDAObject(self):
		return self.timesNVDAObject.getChild(1)

	def getName(self):
		# name of media is the second child of status bar
		if self.statusBar is None:
			return ""
		o = self.statusBar.getChild(1)
		return o.name if o is not None else ""

	def getTotalTime(self):
		# media total time is on forth childof status bar
		try:
			o = self.statusBar.getChild(3)
			t1 = o.name
			st1 = t1.split("/")
			t1 = st1[-1]
			return t1 if t1 != u"--:--" else None
		except Exception:
			return None

	def getCurrentTime(self):
		o = self.timesNVDAObject.getChild(0)
		if o is None or o.name is None:
			log.warning("CurTime object not found or nottime")
			return None
		return o.name

	def getCurrentTimeInSeconds(self):
		t = getTimeInSec(self.timesNVDAObject.getChild(0).name)
		return t

	def getRemainingTime(self):
		totalTime = self.mainWindow.getTotalTime()
		if totalTime is None:
			return None
		t2sec = getTimeInSec(totalTime)
		o1 = self.timesNVDAObject.children[0]
		if o1 is None or o1.name is None:
			return None
		t1 = o1.name
		t1sec = getTimeInSec(t1)
		t3sec = t2sec - t1sec
		if t3sec < 3600:
			st = "".join(str(int(t3sec / 60)) + ":" + str(t3sec % 60))
		if t3sec >= 3600:
			th = int(t3sec / 3600)
			tm = int((t3sec - 3600 * th) / 60)
			if tm < 10:
				stm = "".join("0" + str(tm))
			else:
				stm = str(tm)
			ts = t3sec - 3600 * th - 60 * tm
			if ts < 10:
				sts = "".join("0" + str(ts))
			else:
				sts = str(ts)
			st = "".join(str(th) + ":" + stm + ":" + sts)
		return st

	def getElapsedTime(self):
		o = self.timesNVDAObject.getChild(0)
		if o is None:
			return None
		t1 = o.name
		if t1 is None or t1 == "--:--":
			return None
		return t1


class StatusBar (object):
	def __init__(self, mainWindow):
		super(StatusBar, self).__init__()
		self.topNVDAObject = mainWindow.topNVDAObject

	@property
	def NVDAObject(self):
		if hasattr(self, "_NVDAObject"):
			return self._NVDAObject
		top = self.topNVDAObject
		for o in top.children:
			if o.role == Role.STATUSBAR:
				self._NVDAObject = o
				return o
		log.warning("getStatusBar: status bar not found")
		return None


class VolumeInfos(object):
	def __init__(self, mainWindow):
		printDebug("VolumeInfo: init")
		super(VolumeInfos, self).__init__()
		self.mainPanelNVDAObject = mainWindow.mainPanel.NVDAObject

	@property
	def NVDAObject(self):
		if hasattr(self, "_NVDAObject"):
			return self._NVDAObject
		oMain = self.mainPanelNVDAObject
		try:
			for o in oMain.children:
				if o.role == Role.BORDER:
					self._NVDAObject = o
					return o
		except Exception:
			pass
		log.warning("VolumeInfos Object not found")
		return None

	@property
	def volumeIAObject(self):
		if hasattr(self, "_volumeIAObject"):
			return self._volumeIAObject
		try:
			oDeb = self.NVDAObject.next.IAccessibleObject
		except Exception:
			log.warning("VolumeInfos: getVolumeIAObject exception")
			return None
		count = oDeb.accChildCount
		i = 0
		while i < count:
			o = oDeb.accChild(i)
			i = i + 1
			if o and o.accChildCount:
				if o.accRole(0) == oleacc.ROLE_SYSTEM_CLIENT:
					self._volumeIAObject = o
					return o
		return None

	def getMuteAndLevel(self):
		o = self.volumeIAObject
		label = getString(vlc_strings.ID_UnMuteImageDescription)
		if o is None or len(label) == 0:
			return (None, None)
		muteState = False
		if label in o.accChild(1).accDescription(0):
			muteState = True
		level = o.accChild(2).accValue(0)
		return (muteState, level)


class MainPanel(object):
	def __init__(self, mainWindow):
		printDebug("MainPanel: init")
		super(MainPanel, self).__init__()
		self.topNVDAObject = mainWindow.topNVDAObject
		self.controlPanel = ControlPanel(self)
		self.anchoredPlaylist = AnchoredPlaylist(self)

	@property
	def NVDAObject(self):
		if hasattr(self, "_NVDAObject"):
			return self._NVDAObject
		printDebug("mainPanel: NVDAObject init")
		top = self.topNVDAObject
		if top:
			for o in top.children:
				if o.role == Role.PANE:
					printDebug("mainPanel: NVDAObject found")
					self._NVDAObject = o
					return o
		printDebug("mainPanel NVDAObject not found")
		return None

	def getcontinuePlayback(self):
		try:
			obj = self.NVDAObject.firstChild
			if State.INVISIBLE in obj.states:
				return (False, None)
			return (True, obj.lastChild.name)
		except Exception:
			return (False, None)

	def pushContinuePlaybackButton(self):
		try:
			obj = self.NVDAObject.firstChild.lastChild
			if obj.role == Role.BUTTON:
				obj.IAccessibleObject.accdoDefaultAction(0)
		except Exception:
			pass

	def getLoopState(self):
		return self.controlPanel.getLoopCheckButtonState()

	def getRandomState(self):
		return self.controlPanel.getRandomCheckButtonState()

	def togglePlayPause(self):
		self.controlPanel.clickPlayPauseButton()


__filter_class__ = filter


def filter(*args):
	return [item for item in __filter_class__(*args)]


class ControlPanel(object):
	def __init__(self, mainPanel):
		printDebug("ControlPanel: init")
		super(ControlPanel, self).__init__()
		self.curControlIndex = 0
		if mainPanel.NVDAObject is None:
			return
		self.NVDAObject = mainPanel.NVDAObject.lastChild
		self.IAObject = self.NVDAObject.IAccessibleObject
		self.refreshControls()

	def getLoopCheckButtonState(self):
		oDeb = self.IAObject
		try:
			count = oDeb.accChildCount
		except Exception:
			return False
		i = 0
		while i <= count:
			o = oDeb.accChild(i)
			i = i + 1
			if o and o.accRole(0) == oleacc.ROLE_SYSTEM_CHECKBUTTON and getString(
				vlc_strings.ID_LoopCheckButtonDescription) in o.accDescription(0):
				return True if o.accState(0) & oleacc.STATE_SYSTEM_CHECKED else False
		return False

	def getRandomCheckButtonState(self):
		oDeb = self.IAObject
		try:
			count = oDeb.accChildCount
		except Exception:
			return False
		i = 0
		while i <= count:
			o = oDeb.accChild(i)
			i = i + 1
			if o and o.accRole(0) == oleacc.ROLE_SYSTEM_CHECKBUTTON and getString(
				vlc_strings.ID_RandomCheckButtonDescription) in o.accDescription(0):
				return True if o.accState(0) & oleacc.STATE_SYSTEM_CHECKED else False
				log.warning("random checkButton not found")
		return False

	def getPlayPauseButton(self):
		oDeb = self.IAObject
		count = oDeb.accChildCount
		i = 0
		while i < count:
			o = oDeb.accChild(i)
			i = i + 1
			role = o.accRole(0)
			if role == oleacc.ROLE_SYSTEM_PUSHBUTTON and (
				getString(vlc_strings.ID_PlayButtonDescription) in o.accDescription(0)
				or getString(
					vlc_strings.ID_PauseThePlaybackButtonDescription) in o.accDescription(0)):
				return o
		return None

	def clickPlayPauseButton(self):
		oIA = self.getPlayPauseButton()
		if oIA is None:
			return
		name = oIA.accName(0)
		left, top, width, height = oIA.accLocation(0)
		leftClick(left + int(width / 2), top + int(height / 2))
		# verify if it is done
		if oIA.accName(0) == name:
			return
		# no, so try other thing
		oldSpeechMode = getSpeechMode()
		setSpeechMode_off()
		keyboardHandler.KeyboardInputGesture.fromName("space").send()
		time.sleep(0.1)
		api.processPendingEvents()
		setSpeechMode(oldSpeechMode)

	def clickButton(self, button):
		printDebug("ControlPanel: clickButton")
		left, top, width, height = button.location
		leftClick(int(left + (width / 2)), int(top + (height / 2)))

	def refreshControls(self):
		self.curControlIndex = 0
		self.controls = [api.getForegroundObject(), ]
		self.controls .extend(self.getAllControls())

	def getAllControls(self):
		controls = []
		o = self.NVDAObject
		try:
			controls = filter(lambda c: c.role not in [
				Role.GRIP, Role.BORDER, Role.PANE],
				o.children
				+ o.getChild(0).children
				+ o.getChild(1).children
				+ o.getChild(2).firstChild.children
				+ o.getChild(3).firstChild.children
			)
			# Add mute button
			if State.INVISIBLE not in o.getChild(3).firstChild.states:
				controls.append(o.getChild(3).firstChild)
		except Exception:
			return []
		return filter(
			lambda item: State.INVISIBLE not in item.states
			and State.UNAVAILABLE not in item.states, controls)

	def moveToControl(self, next=True):
		controls = self.controls
		if len(controls) == 1:
			self.refreshControls()
		if len(controls) == 1:
			# TRANSLATORS: Message when there are no controls visible on screen,
			# or the addon can't find them.
			queueMessage(_("There are no controls available"))
			return None
		index = self.curControlIndex + 1 if next else self.curControlIndex - 1
		if index >= len(controls):
			index = 0
		if index < 0:
			index = len(controls) - 1
		control = controls[index]
		if control.name is None or len(control.name) == 0:
			control.name = control.description
		if self.curControlIndex == 0:
			# Translators: message to user to report navigator object in control panel.
			ui.message(_("Control Panel"))
		api.setNavigatorObject(control)
		api.setMouseObject(control)
		speech.speakObject(control)
		self.curControlIndex = index

	def reportCurrentControl(self):
		if self.curControlIndex == 0:
			return
		controls = self.controls
		if len(controls) == 1:
			return
		control = controls[self.curControlIndex]
		# Translators: message to user to report navigator object in control panel.
		wx.CallLater(100, ui.message, _("Control Panel"))
		wx.CallLater(110, speech.speakObject, control)


class Menubar(object):
	def __init__(self, mainWindow):
		printDebug("Menubar: init")
		super(Menubar, self).__init__()
		self.topNVDAObject = mainWindow.topNVDAObject

	@property
	def NVDAObject(self):
		if hasattr(self, "_NVDAObject"):
			return self._NVDAObject
		top = self.topNVDAObject
		for o in top.children:
			if o.role == Role.MENUBAR:
				self._NVDAObject = o
				return o
		return None

	def isVisible(self):
		try:
			return State.INVISIBLE not in self.NVDAObject.states
		except Exception:
			return False


_count = 0


class Playlist(object):
	def __init__(self):
		super(Playlist, self).__init__()
		self.groupButton = None

	def isAlive(self):
		return True if self.NVDAObject else False

	@classmethod
	def isAPlaylist(cls, oIA):
		try:
			if oIA.accRole(0) != oleacc.ROLE_SYSTEM_CLIENT or oIA.accChildCount != 4:
				return False
			(client, childID) = accNavigate(oIA, 0, oleacc.NAVDIR_FIRSTCHILD)
			(buttonMenu, childID) = accNavigate(client, 0, oleacc.NAVDIR_FIRSTCHILD)
			if buttonMenu and buttonMenu.accRole(0) == oleacc.ROLE_SYSTEM_BUTTONMENU:
				return True
		except Exception:
			pass
		return False

	@classmethod
	def getPlaylistID(cls, oIA):
		if not cls.isAPlaylist(oIA):
			return ID_NoPlaylist
		try:
			(parent, childID) = accParent(oIA, 0)
		except Exception:
			return ID_NoPlaylist

		if parent and parent.accRole(0) == oleacc.ROLE_SYSTEM_WINDOW:
			# embedded window playlist
			id = ID_EmbeddedPlaylist
		else:
			# anchored playlist
			id = ID_AnchoredPlaylist
		return id

	def getGroupButtonName(self):
		if self.NVDAObject is None:
			return None
		oIA = self.NVDAObject.IAccessibleObject
		try:
			(client, childID) = accNavigate(oIA, 0, oleacc.NAVDIR_FIRSTCHILD)
			(buttonMenu, childID) = accNavigate(client, 0, oleacc.NAVDIR_FIRSTCHILD)
			(groupButton, childID) = accNavigate(buttonMenu, 0, oleacc.NAVDIR_NEXT)
			if groupButton and groupButton.accRole(0) == oleacc.ROLE_SYSTEM_PUSHBUTTON:
				return groupButton.accName(0)
		except Exception:
			pass
		return None

	def reportGroupButtonName(self):
		name = self.getGroupButtonName()
		if name is None:
			return
		queueMessage(name)


class AnchoredPlaylist(Playlist):
	def __init__(self, mainPanel):
		printDebug("AnchoredPlaylist: init")
		super(AnchoredPlaylist, self).__init__()
		self.mainPanelNVDAObject = mainPanel.NVDAObject

	@property
	def NVDAObject(self):
		if self.mainPanelNVDAObject:
			try:
				NVDAObject = self.mainPanelNVDAObject.getChild(1).getChild(2)
				return NVDAObject
			except Exception:
				pass
		return None

	def isVisible(self):
		if self.NVDAObject is None:
			return False
		if State.INVISIBLE in self.NVDAObject.states:
			return False
		return True

	def reportViewState(self):
		if self.isVisible():
			# Translators: message to user to report state of anchored playlist.
			queueMessage(_("Anchored playlist shown"))
		else:
			# Translators: message to user to report state of anchored playlist.
			queueMessage(_("Anchored playlist hidden"))


class EmbeddedPlaylist(Playlist):

	@property
	def NVDAObject(self):
		if hasattr(self, "_NVDAObject"):
			return self._NVDAObject
		obj = api.getDesktopObject().firstChild
		while obj:
			if obj.windowClassName == u'Qt5QWindowIcon' and obj.childCount == 7:
				o = obj.getChild(3).firstChild
				if o and Playlist.isAPlaylist(o.IAccessibleObject):
					self._NVDAObject = o
					return o
			if obj is None or obj == obj.next:
				break
			obj = obj.next
		return None

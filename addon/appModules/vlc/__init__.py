# appModules\vlc\__init__.py.
# a part of vlcAccessEnhancement add-on
# Copyright 2019-2025 paulber19
# This file is covered by the GNU General Public License.
# some code source comes from VLC add-on written by Javi Dominguez.


import addonHandler
import winUser
from controlTypes.role import Role
from controlTypes.state import State
import api
from scriptHandler import script
import re
import speech
import queueHandler
import ui
import keyboardHandler
from NVDAObjects.IAccessible import IAccessible, qt
from NVDAObjects.behaviors import Dialog
import time
import wx
import os
import oleacc
from inputCore import normalizeGestureIdentifier
import inputCore
try:
	# NVDA >= 2024.1
	speech.speech.SpeechMode.onDemand
	speakOnDemand = {"speakOnDemand": True}
except AttributeError:
	# NVDA <= 2023.3
	speakOnDemand = {}
import sys
from .vlc_goToTime import GoToTimeDialog
from . import vlc_application
from .vlc_application import ID_NoPlaylist, ID_AnchoredPlaylist, ID_EmbeddedPlaylist
from . import vlc_playlist
_curAddon = addonHandler.getCodeAddon()
debugToolsPath = os.path.join(_curAddon.path, "debugTools")
sys.path.append(debugToolsPath)
try:
	from appModuleDebug import AppModuleDebug as AppModule
	from appModuleDebug import printDebug, toggleDebugFlag
except ImportError:
	from appModuleHandler import AppModule as AppModule

	def printDebug(msg):
		return

	def toggleDebugFlag(set=True):
		return
del sys.path[-1]
sharedPath = os.path.join(_curAddon.path, "shared")
sys.path.append(sharedPath)
import vlc_addonConfig
from vlc_utils import (
	mouseClick, MessageBox,
	getTimeInSec, getTimeList, formatTime,
)
from vlc_settingsHandler import (
	Vlcrc,
	jumpDelays, playKeys, movementKeys, muteKeys,
	volumeKeys, speedKeys, normalSpeedKeys, jumpKeys,
)
from vlc_special import makeAddonWindowTitle
from messages import confirm_YesNo, ReturnCode
import vlc_strings
del sys.path[-1]
del sys.modules["vlc_utils"]
del sys.modules["vlc_settingsHandler"]
del sys.modules["vlc_special"]
del sys.modules["messages"]

addonHandler.initTranslation()

_scriptCategory = str(_curAddon.manifest['summary'])


def sendGesture(gesture):
	gesture.send()
	if "numLock" in gesture.modifierNames:
		keyboardHandler.KeyboardInputGesture.fromName("numLock").send()


class InVLCViewWindow(IAccessible):
	scriptCategory = _scriptCategory
	_controlsPaneGestures = {
		"kb:tab": "moveToNextControl",
		"kb:shift+tab": "moveToPreviousControl",
		"kb:enter": "doAction",
	}

	def initOverlayClass(self):
		from vlc_addonConfig import _addonConfigManager
		self._initGestures()

		if not isinstance(self, vlc_playlist.InAnchoredPlaylist) and\
			_addonConfigManager.getPlaybackControlsAccessOption():
			self.bindGestures(self._controlsPaneGestures)

	def _initGestures(self):
		if not hasattr(self.appModule, "vlcrcSettings"):
			printDebug("appModule has no vlcrcSettings")
			return
		scriptGestures = self.appModule.vlcrcSettings .localeSettings .scriptGestures
		for scr in scriptGestures:
			gesture = scriptGestures[scr]
			self.bindGesture(gesture, scr)
		self._initVlcGestures()

	def _initVlcGestures(self):
		gestures = self.appModule.vlcGestures
		self.bindGestures(gestures)

	def event_typedCharacter(self, ch):
		printDebug("InVLCViewWindow event_typedCharacter: hasFocus = %s, name= %s, ch = %s (%s)" % (
			self.hasFocus, self.name, ch, ord(ch)))
		mainWindow = self.appModule.mainWindow
		if ch == self.appModule.vlcrcSettings.getKeyFromName("key-loop"):
			wx.CallAfter(mainWindow.reportLoopStateChange)
		elif ch == self.appModule.vlcrcSettings.getKeyFromName("key-random"):
			wx.CallLater(30, mainWindow.reportRandomStateChange)
		elif ch == self.appModule.vlcrcSettings.getKeyFromName(
			"key-toggle-fullscreen"):
			wx.CallAfter(mainWindow.reportViewState)
		else:
			super(InVLCViewWindow, self).event_typedCharacter(ch)
		controlPanel = mainWindow.mainPanel.controlPanel
		controlPanel.reportCurrentControl()

	def event_statesChange(self):
		printDebug("event_stateChange")
		super(InVLCViewWindow, self).event_statesChange()

	def event_gainFocus(self):
		printDebug("InVLCViewWindow event_gainFocus: role = %s, name = %s" % (self.role, self.name))
		if self.role == Role.PANE and not self.isFocusable:
			# this pane receves focus after playlist removing.
			# Speak foreground window object
			speech.speakObject(self.appModule.mainWindow.topNVDAObject)
		else:
			super(InVLCViewWindow, self).event_gainFocus()
		if not self.hasFocus:
			printDebug("InVLCViewWindow: event_gainFocus: setFocus on object with hasFocus = False")
		mainWindow = self.appModule.mainWindow
		# after anchored playlist hiding , refresh playback controls
		mainWindow.mainPanel.controlPanel.refreshControls()
		queueHandler.queueFunction(
			queueHandler.eventQueue, mainWindow.reportMediaStates)
		queueHandler.queueFunction(
			queueHandler.eventQueue, mainWindow.reportLoopAndRandomStates)
		queueHandler.queueFunction(
			queueHandler.eventQueue, mainWindow.reportMenubarState)
		queueHandler.queueFunction(
			queueHandler.eventQueue, mainWindow.reportViewState)

	def event_loseFocus(self):
		printDebug("InVLCViewWindow: event_loseFocus")

	def hasNoMedia(self):
		mainWindow = self.appModule.mainWindow
		if not mainWindow.hasMedia():
			# Translators: message to the user to say there is no media.
			ui.message(_("No media"))
			return True
		return False

	@script(
		# Translators: Input help mode message for report elapsed time command.
		description=_("Report media's played duration"),
		**speakOnDemand,
	)
	def script_reportElapsedTime(self, gesture):
		if self.hasNoMedia():
			return
		mainWindow = self.appModule.mainWindow
		mainWindow.sayElapsedTime(True)

	@script(
		# Translators: Input help mode message for report total time command.
		description=_("Report media's totalduration"),
		**speakOnDemand,
	)
	def script_reportTotalTime(self, gesture):
		if self.hasNoMedia():
			return
		# Translators: message to the user to report media duration.
		msg = _("Media duration %s")
		mainWindow = self.appModule.mainWindow
		totalTime = mainWindow.getTotalTime()
		if totalTime is None:
			# Translators: media duration is unknown.
			ui.message(msg % _("unknown"))
			return

		ui.message(msg % formatTime(totalTime))

	@script(
		# Translators: Input help mode message for report remaining time command.
		description=_("Report media's remaining durationto be played"),
		**speakOnDemand
	)
	def script_reportRemainingTime(self, gesture):
		if self.hasNoMedia():
			return
		mainWindow = self.appModule.mainWindow
		mainWindow.sayRemainingTime()

	def saySpeed(self, msg=""):
		mainWindow = self.appModule.mainWindow
		ui.message("%s %s" % (msg, mainWindow.getSpeedValue()))

	@script(
		# Translators: Input help mode message for report current speed command.
		description=_("Report current speed"),
		**speakOnDemand,
	)
	def script_reportCurrentSpeed(self, gesture):
		if self.hasNoMedia():
			return
		# Translators: part of message to report speed.
		self.saySpeed(_("Current speed "))

	def _setAndReportSpeed(self, gesture, msg=""):
		if self.hasNoMedia():
			return
		gesture.send()
		wx.CallAfter(speech.cancelSpeech)
		wx.CallAfter(self.saySpeed, msg)

	def script_setAndReportSpeed(self, gesture):
		self._setAndReportSpeed(gesture)

	def script_setAndReportNormalSpeed(self, gesture):
		# Translators: part of message to report speed.
		self._setAndReportSpeed(gesture, _("Back to normal speed"))

	@script(
		# Translators: Input help mode message for go to time command.
		description=_(
			"Display the dialog to set a time and move the playback cursor to this time"),
	)
	def script_goToTime(self, gesture):
		if self.hasNoMedia():
			return
		mainWindow = self.appModule.mainWindow
		currentTime = mainWindow.getElapsedTime()
		totalTime = mainWindow.getTotalTime()
		if currentTime is None or totalTime is None:
			return
		curTime = getTimeList(currentTime)
		totalTime = getTimeList(totalTime)
		wx.CallAfter(GoToTimeDialog.run, curTime, totalTime, mainWindow)

	def isAJumpOutOfMedia(self, gesture):
		mainWindow = self.appModule.mainWindow
		(layout, identifier) = gesture._get_identifiers()
		delay = self.appModule.jumpKeyToDelay[normalizeGestureIdentifier(identifier)]
		totalTime = mainWindow.getTotalTime()
		if totalTime is None:
			return False
		totalTimeList = getTimeList(totalTime)
		totalTimeInSec = int(totalTimeList[0]) * 3600 + int(totalTimeList[1]) * 60 + int(totalTimeList[2])
		currentTime = mainWindow.getElapsedTime()
		curTimeInSec = getTimeInSec(currentTime)
		# Translators: message to the user to say time jump is not possible.
		msg = _("Not available, jump is too big")
		if delay > 0:
			diff = totalTimeInSec - curTimeInSec
			pause = True if ((diff <= 10) or (diff >= delay and diff - delay <= 10))\
				else False
			if pause:
				# to prevent vlc to stop media, we pause the media
				isPlaying = mainWindow.isPlaying()
				if isPlaying:
					mainWindow.togglePlayOrPause()
					queueHandler.queueFunction(
						queueHandler.eventQueue, ui.message, _("Pause"))
			if diff <= abs(delay):
				queueHandler.queueFunction(queueHandler.eventQueue, ui.message, msg)
				mainWindow.sayElapsedTime(True)
				queueHandler.queueFunction(
					queueHandler.eventQueue,
					ui.message,
					# Translators: message to the user to report media duration.
					_("Media duration %s") % formatTime(totalTime))
				return True
		elif delay < 0:
			if curTimeInSec < abs(delay):
				queueHandler.queueFunction(queueHandler.eventQueue, ui.message, msg)
				mainWindow.sayElapsedTime(True)
				return True
		return False

	def script_jumpAndReportTime(self, gesture):
		speech.cancelSpeech()
		if self.hasNoMedia():
			return
		if self.isAJumpOutOfMedia(gesture):
			return
		gesture.send()
		mainWindow = self.appModule.mainWindow
		elapsedTime = mainWindow.getElapsedTime()
		if elapsedTime:
			ui.message( formatTime(elapsedTime))

	def script_sayVolume(self, gesture):
		def speakVolume(level, muteState):
			# Translators: message to the user to report volume level.
			ui.message(_("Volume: %s") % str(level))
			if muteState:
				# Translators: message to the user to say volume is muted.
				ui.message(_("Volume mute"))

		printDebug("InVLCViewWindow: sayVolume")
		mainWindow = self.appModule.mainWindow
		(oldMuteState, oldLevel) = mainWindow.getVolumeMuteStateAndLevel()
		gesture.send()
		time.sleep(0.05)
		from vlc_addonConfig import _addonConfigManager
		(muteState, level) = mainWindow.getVolumeMuteStateAndLevel()
		if self.hasNoMedia():
			speakVolume(level, muteState)
			return
		if not _addonConfigManager.getAutoVolumeLevelReportOption():
			return
		if (muteState, level) == (oldMuteState, oldLevel):
			return

		if not mainWindow.isPlaying() or muteState:
			speakVolume(level, muteState)

	def script_toggleMuteAndReportState(self, gesture):
		def callback():
			speech.cancelSpeech()
			mainWindow = self.appModule.mainWindow
			(muteState, level) = mainWindow.getVolumeMuteStateAndLevel()
			if muteState is None:
				return
			if muteState:
				# Translators: message To the user to report volume is muted.
				ui.message(_("Volume mute"))
			elif not mainWindow.isPlaying():
				# Translators: message to the user to report volume is not muted.
				ui.message(_("volume unmuted"))
		gesture.send()
		wx.CallAfter(callback)

	def script_stopMedia(self, gesture):
		gesture.send()
		wx.CallAfter(speech.cancelSpeech)
		mainWindow = self.appModule.mainWindow
		if not mainWindow.hasMedia():
			mainWindow.resetMediaStates()
			# Translators: message to the user to say the media is stopped.
			wx.CallAfter(ui.message, _("Media stopped"))

	def script_togglePlayAndReportState(self, gesture):
		if gesture.mainKeyName == self.appModule.vlcrcSettings.getKeyFromName(
			"key-stop"):
			self.script_stopMedia(gesture)
			return
		mainWindow = self.appModule.mainWindow
		mainWindow.updateCurMediaState()
		sendGesture(gesture)
		wx.CallAfter(speech.cancelSpeech)
		wx.CallLater(10, mainWindow.reportMediaStates,)

	def script_mediaChange(self, gesture):
		sendGesture(gesture)
		mainWindow = self.appModule.mainWindow
		wx.CallLater(30, mainWindow.reportMediaChange)

	def script_hotKeyHelp(self, gesture):
		helpMsg = []
		# Translators: title of script gesture help.
		helpMsg.append(_("Add-on's Input gestures:"))
		for identifier in self._gestureMap:
			scriptDoc = self._gestureMap[identifier].__doc__
			if scriptDoc:
				(layout, keyName) = keyboardHandler.KeyboardInputGesture.getDisplayTextForIdentifier(identifier)
				helpMsg.append("%s %s" % (scriptDoc, keyName))
		helpMsg.append("")
		vlcHelp = self.appModule.vlcrcSettings.vlcHotKeyHelpText()
		helpMsg.append(vlcHelp)
		text = "\n".join(helpMsg)
		# Translators: title of main window shortcut help window.
		title = makeAddonWindowTitle(_("main window help"))
		wx.CallAfter(MessageBox.run, title, text)

	@script(
		# Translators: Input help mode message for record resume file command.
		description=_("Record current playing position for this media"),
	)
	def script_recordResumeFile(self, gesture):

		def callback():
			mainWindow = self.appModule.mainWindow
			mediaInfos = vlc_application.MediaInfos(mainWindow)
			mediaName = mediaInfos.getName()
			if mediaName is None:
				return
			curTime = getTimeList(mainWindow.getElapsedTime())
			if getTimeInSec(curTime) == 0:
				# Translators: message to user to say media cannot be played.
				ui.message(_("Not available, the media don't be played"))
				return
			from vlc_addonConfig import _addonConfigManager
			if _addonConfigManager.recordFileToResume(curTime):
				# Translators: message to user to say the resume playback time.
				msg = _("Playback of {0} file will be resume at {1}")
				wx.CallLater(
					1500, ui.message, msg.format(mediaName, formatTime(":".join(curTime))))
		if self.hasNoMedia():
			return
		mainWindow = self.appModule.mainWindow
		totalTime = mainWindow.getTotalTime()
		if totalTime is None:
			# Translators: message to user : not available for this media
			ui.message(_("No available for this media"))
			return
		wx.CallAfter(callback)

	@script(
		# Translators: Input help mode message for resume playback command.
		description=_("Resume playback at position recoreded for this media"),
	)
	def script_resumePlayback(self, gesture):
		printDebug("resumePlayback")

		def callback(resumeTime):
			res = confirm_YesNo(
				# Translators: message to ask the user if he want to resume playback.
				_("Do you want to resume Playback at %s?") % formatTime(resumeTime),
				# Translators: title of message box.
				makeAddonWindowTitle(_("Confirmation")),
			)
			if res != ReturnCode.YES:
				return
			mainWindow = self.appModule.mainWindow
			totalTime = getTimeList(mainWindow.getTotalTime())
			jumpTime = getTimeList(resumeTime)
			wx.CallLater(
				200, mainWindow.jumpToTime, jumpTime, totalTime, startPlaying=True)

		if self.hasNoMedia():
			return
		from vlc_addonConfig import _addonConfigManager
		resumeTime = _addonConfigManager.getResumeFileTime()
		if resumeTime is None or resumeTime == 0:
			# Translators: message to user to say no resume time for this media
			ui.message(_("No resume time for this media"))
			return
		wx.CallAfter(callback, resumeTime)

	@script(
		# Translators: Input help mode message for continue playback command.
		description=_("Restart interrupted playback at position recorded by VLC"),
	)
	def script_continuePlayback(self, gesture):
		printDebug("InMainWindow: script_continuePlayback alt+R VLC Command script")
		if self.hasNoMedia():
			return
		mainWindow = self.appModule.mainWindow
		isPlaying = mainWindow.isPlaying()
		if isPlaying:
			mainWindow.togglePlayOrPause()
		mainWindow.mainPanel.pushContinuePlaybackButton()
		time.sleep(0.2)
		mainWindow.resetMediaStates(False)
		mainWindow.sayElapsedTime()
		queueHandler.queueFunction(
			queueHandler.eventQueue, mainWindow.togglePlayOrPause)
		queueHandler.queueFunction(
			queueHandler.eventQueue, mainWindow.reportMediaStates)

	def script_hideShowMenusView(self, gesture):
		gesture.send()
		time.sleep(0.05)
		mainWindow = self.appModule.mainWindow
		menubar = vlc_application.Menubar(mainWindow)
		if menubar.isVisible():
			ui.message(_("Menu bar is shown"))
		else:
			ui.message(_("Menu bar is hidden"))

	def moveToControl(self, next=True):
		mainWindow = self.appModule.mainWindow
		mainPanel = self.appModule.mainWindow.mainPanel
		anchoredPlaylist = mainPanel.anchoredPlaylist
		if anchoredPlaylist.isAlive() and anchoredPlaylist.isVisible():
			obj = anchoredPlaylist.NVDAObject.lastChild
			mouseClick(obj)
			return
		mainWindow.mainPanel.controlPanel.moveToControl(next)

	def script_moveToNextControl(self, gesture):
		self.moveToControl(next=True)

	def script_moveToPreviousControl(self, gesture):
		self.moveToControl(next=False)

	def script_adjustmentsAndEffects(self, gesture):
		def callback():
			obj = api.getDesktopObject().firstChild
			while obj is not None:
				if obj.role == Role.WINDOW and\
					obj.windowClassName == u'Qt5QWindowToolSaveBits':
					obj.setFocus()
					api.setFocusObject(obj)
					break
				obj = obj.next
		gesture.send()
		wx.CallLater(800, callback)

	@script(
		# Translators: Input help mode message for toggle auto volume level report command.
		description=_("Toggle automatic volume level report option")
	)
	def script_toggleAutoVolumeLevelReport(self, gesture):
		from vlc_addonConfig import _addonConfigManager
		_addonConfigManager.toggleAutoVolumeLevelReportOption()

	@script(
		# Translators: Input help mode message for toggle auto elapsed time report command.
		description=_("Toggle automatic elapsed time report option"),
	)
	def script_toggleAutoElapsedTimeReport(self, gesture):
		from vlc_addonConfig import _addonConfigManager
		_addonConfigManager.toggleAutoElapsedTimeReportOption()

	def script_hideShowPlaylist(self, gesture):
		mainPanel = self.appModule.mainWindow.mainPanel
		anchoredPlaylist = mainPanel.anchoredPlaylist
		if anchoredPlaylist.isAlive():
			anchoredPlaylist.reportViewState()
		else:
			embeddedPlaylist = vlc_application.EmbeddedPlaylist()
			ret = embeddedPlaylist.isAlive()
			if not ret:
				ui.message(_("Playlist closed"))

	def getDialog(self):
		# code written by Javi Dominguez and adapted to this add-on
		fg = api.getDesktopObject().firstChild
		obj = fg.simpleNext
		while obj:
			if obj.role == Role.WINDOW and\
				obj.windowClassName == u'Qt5QWindowToolSaveBits':
				if State.INVISIBLE not in obj.states:
					return obj
			obj = obj.simpleNext
		return None

	def focusDialog(self):
		# code written by Javi Dominguez and adapted to this add-on
		dlg = self.getDialog()
		if not dlg:
			return False
		if not dlg.setFocus():
			mouseClick(dlg)
		return True

	def script_doAction(self, gesture):
		# code written by Javi Dominguez and adapted to this add-on
		printDebug("script_doAction")
		obj = api.getNavigatorObject()
		mainWindow = self.appModule.mainWindow
		anchoredPlaylist = mainWindow.mainPanel.anchoredPlaylist
		oldAnchoredPlaylistState = anchoredPlaylist.isVisible()
		controlPanel = mainWindow.mainPanel.controlPanel
		if obj not in controlPanel.controls[1:]:
			gesture.send()
			return
		description = obj.description
		if obj.role not in [Role.BUTTON, Role.GRAPHIC]:
			obj.doAction()

			def finish(obj, description):
				msg = []
				from controlTypes.state import _stateLabels
				for state in obj.states:
					stateLabel = _stateLabels[state]
					msg.append(stateLabel)
				desc = api.getMouseObject().description
				if (
					obj.role == Role.CHECKBOX
					and State.CHECKED not in obj.states
				):
					msg.append(_("unchecked"))
					if desc:
						msg.append(api.getMouseObject().description)
				elif desc and description == desc:
					msg.append(desc)
				if len(msg):
					text = ", ".join(msg)
					ui.message(text)

			wx.CallLater(50, finish, obj, description)
		else:
			api.moveMouseToNVDAObject(obj)
			x, y = winUser.getCursorPos()
			o = api.getDesktopObject().objectFromPoint(x, y)
			if o.description == obj.description:
				controlPanel.clickButton(obj)
				api.processPendingEvents()
				api.moveMouseToNVDAObject(obj)
				o = api.getDesktopObject().objectFromPoint(x, y)
				if description != o.description:
					ui.message(api.getMouseObject().description)
			else:
				pass
		newAnchoredPlaylistState = anchoredPlaylist.isVisible()
		if not oldAnchoredPlaylistState and newAnchoredPlaylistState:
			obj = anchoredPlaylist.NVDAObject
			mouseClick(obj)
			return
		# put focus on new dialog if there is one (like adjustments and effects)
		self.focusDialog()


class VLCMainWindow(InVLCViewWindow):
	def event_foreground(self):
		printDebug("VLCMainWindow: event_foreground")
		if not hasattr(self.appModule, "_mainWindow") or not self.appModule._mainWindow:
			mainWindow = vlc_application.MainWindow(self.appModule)
			if mainWindow.topNVDAObject:
				self.appModule._mainWindow = mainWindow
				printDebug("VLCMainWindow: MainWindow set")
		super(VLCMainWindow, self).event_foreground()

	def event_gainFocus(self):
		printDebug("VLCMainWindow: event_gainFocus: role = %s, name = %s" % (
			self.role, self.name))
		super(VLCMainWindow, self).event_gainFocus()
		if not self.hasFocus:
			printDebug("VLCMainWindow	: event_gainFocus: setFocus on object with hasFocus = False")
			# if anchored playlist is alive, put focus on it
			mainPanel = self.appModule.mainWindow.mainPanel
			anchoredPlaylist = mainPanel.anchoredPlaylist
			if anchoredPlaylist.isAlive() and anchoredPlaylist.isVisible():
				# anchoredPlaylist.NVDAObject.firstChild.setFocus()
				obj = anchoredPlaylist.NVDAObject.lastChild
				mouseClick(obj)


class VLCMainPanel(InVLCViewWindow):
	def _get_name(self):
		return _("Main Panel")


class VLCBehaviorsDialog(Dialog):
	# code source from VLC add-on written by Javi Dominguez
	def _get_description(self):
		return ""

	def event_gainFocus(self):
		super(VLCBehaviorsDialog, self).event_gainFocus()
		# this dialog is necessary the foreground object
		api.setForegroundObject(self)


class VLCQTApplication(qt.Application):
	def _get_description(self):
		return ""

	def event_focusEntered(self):
		printDebug("VLCQTApplication: event_focusEntered")


class VLCSlider(IAccessible):
	# a slider is displayed with 3 ch object:
	# - first: object with role SLIDER and value
	# - nextobject : value in DB
	# - next object: name of slider
	def _get_name(self):
		try:
			return self.next.next.name
		except Exception:
			return super(VLCSlider, self)._get_name()

	def _get_value(self):
		try:
			return self.next.name
		except Exception:
			return super(VLCSlider, self)._get_value()


class VLCComboBox (IAccessible):
	def script_nextItem(self, gesture):
		gesture.send()
		wx.CallAfter(ui.message, self.value)

	def _get_value(self):
		value = super(VLCComboBox, self)._get_value()
		return value if value is not None else _("None")

	def event_valueChange(self):
		pass

	def script_reportItem(self, gesture):
		gesture.send()
		wx.CallAfter(ui.message, self.value)

	__gestures = {
		"kb:downArrow": "reportItem",
		"kb:upArrow": "reportItem",
		"kb:home": "reportItem",
		"kb:end": "reportItem",
	}


class VLCMenuBar(IAccessible):
	def event_gainFocus(self):
		printDebug("VLCMenuBar: event_gainFocus")
		fg = api.getForegroundObject()
		api.setFocusObject(fg)


class VLCSplitButton (IAccessible):
	def event_focusEntered(self):
		printDebug("SplitButton: event_focusEntered")
		pass


class VLCMediaInfos (IAccessible):
	@classmethod
	def isInside(self, obj):
		o = obj.IAccessibleObject
		while o:
			try:
				name = o.accName(0)
				MediaInformationDialogTitle = vlc_strings.getString(
					vlc_strings.ID_MediaInformationDialogTitle)
				if name and (MediaInformationDialogTitle in name):
					return True
			except Exception:
				pass
			try:
				o = o.accParent
			except Exception:
				o = None
		return False

	def _get_name(self):
		name = super(VLCMediaInfos, self)._get_name()
		if self.role != Role.EDITABLETEXT:
			return name
		if name is not None:
			return name
		try:
			previous = self.previous
			if previous and previous.role in [Role.STATICTEXT, ]:
				return previous.name
		except Exception:
			pass
		return None

	def script_nextControl(self, gesture):
		if self.role == Role.EDITABLETEXT\
			and not self.next:
			self.parent.getChild(1).doAction()
		else:
			gesture.send()

	def script_previousControl(self, gesture):
		if self.role == Role.EDITABLETEXT\
			and not self.next:
			self.simplePrevious.simplePrevious.doAction()
		else:
			gesture.send()

	__gestures = {
		"kb:Tab": "nextControl",
		"kb:Shift+Tab": "previousControl"
	}


class AppModule(AppModule):
	vlcrcSettings = None
	vlcGestures = {}
	_trapNextGainFocus = False
	_continuePlayback = (False, None)
	_curTaskTimer = None
	_keyListToScript = (
		(jumpKeys, "jumpAndReportTime"),
		(normalSpeedKeys, "setAndReportNormalSpeed"),
		(speedKeys, "setAndReportSpeed"),
		(volumeKeys, "sayVolume"),
		(muteKeys, "toggleMuteAndReportState"),
		(playKeys, "togglePlayAndReportState"),
		(movementKeys, "mediaChange"),
	)

	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)
		toggleDebugFlag(True)

		self.chooseNVDAObjectOverlayClassesDisabled = False
		self.hasFocus = False
		self.lastFocusedObject = None
		self.initAppModuleTimer = None
		self.foreground = None
		self.initialized = False
		self.vlcrcSettings = Vlcrc()

	def _initAppModule(self):
		self.initAppModuleTimer = None
		if self.initialized:
			printDebug("AppmoduleVLC: initAppModule: appModule already initialized")
			return
		printDebug("AppModule VLC: initAppModule")
		self.vlcrcSettings = Vlcrc()
		if not self.initVLCGestures():
			self.initAppModule()
			return
		if not vlc_strings.init():
			self.initAppModule()
			return
		vlc_addonConfig.initialize(self.vlcrcSettings)
		focus = api.getFocusObject()
		foreground = api.getForegroundObject()
		if isinstance(foreground, InVLCViewWindow):
			foreground.bindGestures(self.vlcGestures)
		if isinstance(focus, InVLCViewWindow):
			focus.bindGestures(self.vlcGestures)

		def giveFocusToVLC():
			api.setFocusObject(foreground)

		wx.CallLater(500, giveFocusToVLC)
		self.initialized = True
		printDebug("AppModule VLC: appModule initialized")

	def initAppModule(self):
		if self.initAppModuleTimer is not None:
			return
		self.initAppModuleTimer = wx.CallLater(500, self._initAppModule)

	def initVLCGestures(self):
		self.vlcGestures = {}
		vlcrcSettings = self.vlcrcSettings
		if vlcrcSettings is None or not vlcrcSettings .initialized:
			printDebug("AppModule VLC: initAppModule: vlcrcSettings not yet initialized")
			return False

		for (keyList, scr) in self._keyListToScript:
			for name in keyList:
				key = vlcrcSettings.getKeyFromName(name)
				if key != "":
					self.vlcGestures["kb:%s" % key] = scr
		self.jumpKeyToDelay = {}
		for keyName in jumpDelays:
			key = vlcrcSettings.getKeyFromName(keyName)
			if key != "":
				identifier = normalizeGestureIdentifier("kb:%s" % key)
				self.jumpKeyToDelay[identifier] = jumpDelays[keyName]
		printDebug("appModuleVLC: initVLCGestures: gestures = %s" % self.vlcGestures)
		return True

	def _inputCaptor(self, gesture):
		def callback():
			time.sleep(0.2)
			o = api.getFocusObject()
			printDebug("appModule VLC inputCaptor callback: %s, hasFocus= %s" % (o.role, o.hasFocus))
			roles = [Role.MENU, Role.MENUITEM, ]
			if (o.role in roles and not o.hasFocus)\
				or o.role == Role.MENUBAR:
				printDebug("click foreground object when focus object is on not focused object")
				self.mainWindow.resetMediaStates()
				mouseClick(api.getForegroundObject(), True, True)
		printDebug("appModule VLC: inputCaptor: key = %s" % (gesture.displayName))
		if not self.initialized:
			wx.CallAfter(self.initAppModule)
		if gesture.mainKeyName in ["escape", "leftAlt"]:
			# when focus is on menu item but menu is not open,
			# these keys change only focused state without event
			# so we need to put focus on menu bar as the menu is opened
			wx.CallAfter(callback)
		return True

	def stopTaskTimer(self):
		if self._curTaskTimer is not None:
			self._curTaskTimer.Stop()
			self._curTaskTimer = None

	def _get_statusBar(self):
		return self.mainWindow.getStatusBar()

	def _get_mainWindow(self):
		if hasattr(self, "_mainWindow") and self._mainWindow is not None:
			return self._mainWindow
		printDebug("try to set mainWindow")
		if not hasattr(self, "vlcrcSettings"):
			return
		mainWindow = vlc_application.MainWindow(self.vlcrcSettings)
		if mainWindow.topNVDAObject:
			self._mainWindow = mainWindow
			printDebug("appModule mainWindow set")
		return mainWindow

	def getNewCls(self, obj, clsList):
		def isInVlcMainWindow(oIA, obj, clsList):
			try:
				name = oIA.accName(0)
				if name and name == api.getDesktopObject().name:
					return False
				if oIA.accRole(0) == oleacc.ROLE_SYSTEM_WINDOW:
					VLCAppTitle = vlc_strings.getString(vlc_strings.ID_VLCAppTitle)
					if VLCAppTitle in name or name == "vlc":
						clsList.insert(0, InVLCViewWindow)
						return True
			except Exception:
				pass
			return False

		def isInsideMediaInfo(oIA, obj, clsList):
			try:
				name = oIA.accName(0)
				MediaInformationDialogTitle = vlc_strings.getString(
					vlc_strings.ID_MediaInformationDialogTitle)
				if name and MediaInformationDialogTitle in name:
					clsList.insert(0, VLCMediaInfos)
					return True
			except Exception:
				pass
			return False

		def isInPlaylist(OIA, obj, clsList):
			if State.INVISIBLE in obj.states:
				return ID_NoPlaylist

			ret = vlc_application.Playlist.getPlaylistID(oIA)
			if not ret:
				return False
			obj.playlist = ret
			if ret == ID_AnchoredPlaylist:
				if obj.role == Role.TREEVIEWITEM:
					columnHeaders = vlc_playlist.getColumnHeaderCount(
						obj.IAccessibleObject.accParent)
					if columnHeaders == 1:
						clsList.insert(0, vlc_playlist.VLCAnchoredGroupTreeViewItem)
					else:
						clsList.insert(0, vlc_playlist.VLCAnchoredPlaylistTreeViewItem)
				elif obj.role == Role.TREEVIEW:
					clsList.insert(0, vlc_playlist.VLCAnchoredPlaylistTreeView)
				elif obj.role == Role.LISTITEM:
					clsList.insert(0, vlc_playlist.VLCAnchoredPlaylistListItem)
				else:
					clsList.insert(0, vlc_playlist.InAnchoredPlaylist)
					if obj.role != Role.EDITABLETEXT:
						clsList.insert(0, InVLCViewWindow)
			elif ret == ID_EmbeddedPlaylist:
				if obj.role == Role.TREEVIEWITEM:
					columnHeaders = vlc_playlist.getColumnHeaderCount(
						obj.IAccessibleObject.accParent)
					if columnHeaders == 1:
						clsList.insert(0, vlc_playlist.VLCEmbeddedGroupTreeViewItem)
					else:
						clsList.insert(0, vlc_playlist.VLCEmbeddedPlaylistTreeViewItem)
				elif obj.role == Role.TREEVIEW:
					clsList.insert(0, vlc_playlist.VLCEmbeddedPlaylistTreeView)
				elif obj.role == Role.LISTITEM:
					clsList.insert(0, vlc_playlist.VLCEmbeddedPlaylistListItem)
				else:
					clsList.insert(0, vlc_playlist.InEmbeddedPlaylist)
			return True
		oIA = obj.IAccessibleObject
		while oIA:
			if isInPlaylist(oIA, obj, clsList):
				return True
			if isInVlcMainWindow(oIA, obj, clsList):
				return True
			if isInsideMediaInfo(oIA, obj, clsList):
				return True
			try:
				oIA = oIA.accParent
			except Exception:
				oIA = None
		return False

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		# printDebug("appModule vlc: chooseNVDAOverlayClass: %s, %s" % (
		# obj.role, obj.name))
		if not isinstance(obj, IAccessible):
			return
		if obj.role == Role.APPLICATION:
			obj.parent = api.getDesktopObject()
			clsList.insert(0, VLCQTApplication)
			return
		roles = [
			Role.MENU, Role.MENUITEM,
			Role.POPUPMENU, Role.CHECKMENUITEM,
			Role.TABLECOLUMNHEADER]
		if obj.role in roles:
			return
		if obj.role == Role.DIALOG and (
			obj.windowClassName == u'Qt5QWindowToolSaveBits'
			or obj.windowClassName == u'Qt5QWindowIcon'):
			clsList.insert(0, VLCBehaviorsDialog)
			return
		if obj.role == Role.MENUBAR:
			clsList.insert(0, VLCMenuBar)
			return
		if obj.role == Role.SLIDER:
			clsList.insert(0, VLCSlider)
			return
		if obj.role == Role.COMBOBOX:
			clsList.insert(0, VLCComboBox)
		elif obj.role == Role.SPLITBUTTON:
			clsList.insert(0, VLCSplitButton)
		if self.chooseNVDAObjectOverlayClassesDisabled:
			printDebug("ChooseOverlayClass disabled")
			return
		oIA = obj.IAccessibleObject
		if obj.windowClassName == u'Qt5QWindowIcon':
			if obj.role == Role.EDITABLETEXT:
				from .vlc_qtEditableText import VLCQTEditableText
				clsList.insert(0, VLCQTEditableText)
			elif obj.role == Role.WINDOW:
				try:
					if oIA.accChild(1).accRole(0) == oleacc.ROLE_SYSTEM_MENUBAR:
						self.initAppModule()
						clsList.insert(0, VLCMainWindow)
						return
				except Exception:
					pass
			elif obj.role == Role.PANE:
				if obj.childCount == 4:
					# perhaps is the main panel
					try:
						if oIA.accParent.accChild(1).accRole(0) == oleacc.ROLE_SYSTEM_MENUBAR:
							clsList.insert(0, VLCMainPanel)
							return
					except Exception:
						pass
					# perhaps is the playlist
					ret = vlc_application.Playlist.getPlaylistID(oIA)
					if ret == ID_EmbeddedPlaylist:
						# embedded window playlist
						clsList.insert(0, vlc_playlist.VLCEmbeddedPlaylist)
						obj.playlist = ret
						return
					elif ret == ID_AnchoredPlaylist:
						# anchored playlist
						clsList.insert(0, vlc_playlist.VLCAnchoredPlaylist)
						obj.playlist = ret
						return
		if not self.initialized:
			return
		try:
			self.getNewCls(obj, clsList)
		except Exception:
			pass

	def event_appModule_gainFocus(self):
		printDebug("appModule VLC: event_appModulegainFocus")
		self.hasFocus = True
		self.lastFocusedObject = None
		self._oldInputCoreManagerCaptureFunc = inputCore.manager._captureFunc
		inputCore.manager._captureFunc = self._inputCaptor
		self.initAppModule()
		self._mainWindow = None
		self._get_mainWindow()

	def event_appModule_loseFocus(self):
		printDebug("appModule VLC: event_appModuleLoseFocus")
		self.stopTaskTimer()
		if hasattr(self, "_oldInputCoreManagerCaptureFunc"):
			inputCore.manager._captureFunc = self._oldInputCoreManagerCaptureFunc
			del self._oldInputCoreManagerCaptureFunc
		if hasattr(self, "curAPIGetStatusBar"):
			api.getStatusBar = self.curAPIGetStatusBar
			delattr(self, "curAPIGetStatusBar")
		self.hasFocus = False

	def terminate(self):
		printDebug("AppModule VLC: terminate")
		self.stopTaskTimer()
		if hasattr(self, "_oldInputCoreManagerCaptureFunc"):
			inputCore.manager._captureFunc = self._oldInputCoreManagerCaptureFunc
			del self._oldInputCoreManagerCaptureFunc
		super(AppModule, self).terminate()

	def event_typedCharacter(self, obj, nextHandler, ch):
		printDebug("appModule VLC: event_typedCharacter: role = %s, name = %s, ch = %s (%s)" % (
			obj.role, obj.name, ch, ord(ch)))
		if not self.hasFocus:
			return
		if ord(ch) == 12:
			# after control+l command
			focus = api.getFocusObject()
			if hasattr(focus, "script_hideShowPlaylist"):
				focus.script_hideShowPlaylist(None)
				return
		nextHandler()

	def event_becomeNavigator(self, obj, nextHandler):
		printDebug("appModule VLC: event_becomeNavigator: %s, %s" % (obj.role, obj.description))
		if obj.description and "<html>" in obj.description:
			# Removes the HTML tags that appear in the
			# description of some objects
			while re.search("<[^(>.*<)]+>([^<]*</style>)?", obj.description):
				obj.description = obj.description.replace(
					re.search("<[^(>.*<)]+>([^<]*</style>)?", obj.description).group(), "")
		nextHandler()

	def event_focusEntered(self, obj, nextHandler):
		printDebug("appModule VLC: event_focusEntered: %s, %s" % (
			obj.role, obj.name))
		if obj.role == Role.APPLICATION and obj.name == "vlc":
			try:
				self.mainWindow.resetMediaStates()
			except Exception:
				pass
			return
		nextHandler()

	def event_foreground(self, obj, nextHandler):
		printDebug("appModule VLC: event_foreground: %s, %s" % (
			obj.role, obj.name))
		self.foreground = obj
		nextHandler()
		self.initAppModule()

	def getContinuePlaybackScriptGesture(self):
		from inputCore import manager
		all = manager.getAllGestureMappings()[_curAddon.manifest['summary']]
		for item in all:
			infos = all[item]
			if infos.scriptName == "continuePlayback":
				gestures = infos.gestures
				if len(gestures):
					return gestures[0].split(":")[1]
		return None

	def event_nameChange(self, obj, nextHandler):
		nextHandler()
		if obj.name == "VLC (Direct3D11 output)":
			self.initAppModule()
			return
		if self.hasFocus:
			continuePlaybackScriptGesture = self.getContinuePlaybackScriptGesture()
			self.mainWindow.reportContinuePlayback(continuePlaybackScriptGesture)

	def event_gainFocus(self, obj, nextHandler):
		printDebug("appModule VLC: event_gainFocus: role = %s, name = %s" % (
			obj.role, obj.name))
		if obj.description and "<html>" in obj.description:
			# Removes the HTML tags that appear in the description of some objects
			while re.search("<[^(>.*<)]+>([^<]*</style>)?", obj.description):
				obj.description = obj.description.replace(
					re.search("<[^(>.*<)]+>([^<]*</style>)?", obj.description).group(), "")
		nextHandler()
		self.lastFocusedObject = obj

	@script(
		# Translators: Input help mode message for hot key help command.
		description=_("Display add-on's help"),
		category=_scriptCategory,
		gesture="kb:nvda+control+h",
	)
	def script_hotKeyHelp(self, gesture):
		obj = api.getFocusObject()
		if hasattr(obj, "script_hotKeyHelp"):
			obj.script_hotKeyHelp(gesture)

	@script(
		# gesture="kb:nvda+control+f9",
	)
	def script_test(self, gesture):
		ui.message("test VLC")
		print("test VLC")

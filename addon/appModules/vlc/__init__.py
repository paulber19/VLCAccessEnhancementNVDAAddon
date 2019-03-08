# appModules/vlc/__init__.py.
# a part of VLC media player add-on
# Copyright 2018 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.


import addonHandler
addonHandler.initTranslation()
from logHandler import log
import winUser
import controlTypes
import textInfos
import api
import appModuleHandler
import speech
import queueHandler
import ui
import keyboardHandler
from NVDAObjects.window import Window
from NVDAObjects.IAccessible import IAccessible, qt
import NVDAObjects.IAccessible
import time
import wx
import gui
import os
import winsound
import eventHandler
import mouseHandler
import oleacc
from inputCore import normalizeGestureIdentifier
import inputCore
import core

_curAddon = addonHandler.getCodeAddon()
import sys
debugToolsPath = os.path.join(_curAddon.path, "debugTools")
sys.path.append(debugToolsPath)
try:
	from debug import printDebug, toggleDebugFlag
except ImportError:
	def prindDebug(msg): return
	def toggleDebugFlag(): return
try:
	import appModuleDebug
	AppModuleDebug = appModuleDebug.AppModuleDebug
except ImportError:
	AppModuleDebug = appModuleHandler.AppModule
del sys.path[-1]
sharedPath = os.path.join(_curAddon.path, "shared")
sys.path.append(sharedPath)
from vlcUtils import *
from vlcSettingsHandler import *
import vlc_special
import vlcStrings
from py3Compatibility import _unicode
del sys.path[-1]
from .vlcGoToTime import GoToTimeDialog
from . import vlcAddonConfig
from . import vlcApplication
_addonSummary = _curAddon.manifest['summary']
_scriptCategory = _unicode(_addonSummary)

def sendGesture(gesture):
	gesture.send()
	if "numLock" in gesture.modifierNames:
		keyboardHandler.KeyboardInputGesture.fromName("numLock").send()

class InVLCViewWindow(NVDAObjects.NVDAObject):
	def initOverlayClass(self):
		#printDebug("MainWindow initOverlayClass:  %s, hasFocus = %s, name = %s" %(controlTypes.roleLabels.get(self.role), self.hasFocus, self.name))
		self.continuePlaybackScript = InVLCViewWindow.script_continuePlayback
		self._initGestures()
		self._initVlcGestures()
	
	def event_typedCharacter(self,ch):
		printDebug( "InVLCViewWindow event_typedCharacter: hasFocus = %s, name= %s, ch = %s"%(self.hasFocus, self.name,ch))
		mainWindow = self.appModule.mainWindow
		if ch == self.appModule.vlcrcSettings.getKeyFromName("key-loop"):
			wx.CallAfter(mainWindow.reportLoopStateChange)
		elif ch == self.appModule.vlcrcSettings.getKeyFromName("key-random"):
			wx.CallAfter(mainWindow.reportRandomStateChange)
		else:
			super(InVLCViewWindow  , self).event_typedCharacter(ch)	
	def event_statesChange(self):
		printDebug ("event_stateChange")
		super(InVLCViewWindow, self).event_statesChange()
	

	def event_gainFocus(self):
		printDebug( "InVLCViewWindow event_gainFocus: role = %s, name = %s"%(controlTypes.roleLabels.get(self.role), self.name))
		super(InVLCViewWindow  , self).event_gainFocus()
		if self.hasFocus == False:
			printDebug ("InViewWindow: event_gainFocus: setFocus on object with hasFocus = False")
			self.setFocus()
		mainWindow = self.appModule.mainWindow
		queueHandler.queueFunction(queueHandler.eventQueue, mainWindow.reportMediaStates)
		queueHandler.queueFunction(queueHandler.eventQueue, mainWindow.reportLoopAndRandomStates)
		
	def _initGestures(self):
		scriptGestures = self.appModule.vlcrcSettings .localeSettings .scriptGestures
		for script in  scriptGestures:
			gesture = scriptGestures[script]
			self.bindGesture(gesture, script)
	
	def _initVlcGestures(self):
		gestures = self.appModule.vlcGestures
		self.bindGestures(gestures)
	
	def hasNoMedia(self):
		mainWindow = self.appModule.mainWindow
		if not mainWindow.hasMedia():
			# Translators: message to the user to say there is no media.
			ui.message(_("No media"))
			return True
		return False
	
	def script_reportElapsedTime(self,gesture):
		if self.hasNoMedia():
			return
		mainWindow = self.appModule.mainWindow
		mainWindow.sayElapsedTime(True)
	# Translators: Input help mode message for  report elapsed time command.
	script_reportElapsedTime.__doc__ = _("Report media's played duration")
	script_reportElapsedTime.category = _scriptCategory
	
	def script_reportTotalTime(self,gesture):
		if self.hasNoMedia():
			return
		# Translators: message to the user to report media duration.
		mainWindow = self.appModule.mainWindow
		ui.message(_("Media duration %s") %formatTime(mainWindow.getTotalTime()))
	# Translators: Input help mode message for report total time command.
	script_reportTotalTime.__doc__ = _("Report media's totalduration")
	script_reportTotalTime.category = _scriptCategory
	
	def script_reportRemainingTime(self,gesture):
		if self.hasNoMedia():
			return
		mainWindow = self.appModule.mainWindow
		mainWindow.sayRemainingTime()
		
	# Translators: Input help mode message for  report remaining time command.
	script_reportRemainingTime.__doc__ = _("Report media's remaining durationto be played")
	script_reportRemainingTime.category = _scriptCategory
	
	def saySpeed(self, msg =""):
		mainWindow = self.appModule.mainWindow
		ui.message("%s %s" %(msg, mainWindow.getSpeedValue()))
	
	def script_reportCurrentSpeed(self,gesture):
		if self.hasNoMedia():
			return
		# Translators:  part of message to report speed.
		self.saySpeed(_("Current speed "))
	# Translators: Input help mode message for  report current speed command.
	script_reportCurrentSpeed.__doc__ = _("Report current speed")
	script_reportCurrentSpeed.category = _scriptCategory
	
	def _setAndReportSpeed(self, gesture, msg = ""):
		if self.hasNoMedia():
			return
		sendGesture(gesture)
		wx.CallAfter(speech.cancelSpeech)
		wx.CallAfter(self.saySpeed,msg)
	
	def script_setAndReportSpeed(self, gesture):
		self._setAndReportSpeed(gesture)
	
	def script_setAndReportNormalSpeed(self, gesture):
		# Translators: part of message to report speed.
		self._setAndReportSpeed(gesture, _("Back to normal speed"))
	
	def script_goToTime(self,gesture):
		if self.hasNoMedia():
			return
		mainWindow = self.appModule.mainWindow
		curTime = getTimeList(mainWindow.getCurrentTime())
		totalTime = getTimeList(mainWindow.getTotalTime())
		wx.CallAfter(GoToTimeDialog.run,curTime, totalTime, mainWindow)
	# Translators: Input help mode message for  go to time command.
	script_goToTime.__doc__ = _("Display the dialog to set a time and move the playback cursor to this time")
	script_goToTime.category = _scriptCategory
	
	def isAJumpOutOfMedia(self, gesture):
		mainWindow = self.appModule.mainWindow
		(layout, identifier) = gesture._get_identifiers()
		delay = self.appModule.jumpKeyToDelay[normalizeGestureIdentifier(identifier)]
		totalTime = getTimeList(mainWindow.getTotalTime())
		totalTimeInSec = int(totalTime[0])*3600  + int(totalTime[1])*60 +int(totalTime[2])
		curTimeInSec = getTimeInSec(mainWindow.getCurrentTime())
		# Translators: message to the user to say  time jump is not possible.
		msg = _("Not available, jump is too big ")
		if delay >0:
			diff = totalTimeInSec - curTimeInSec
			if diff < abs(delay):
				ui.message(msg)
				mainWindow.sayElapsedTime(True)
				# Translators: message to the user to report media duration.
				ui.message(_("Media duration %s") %formatTime(mainWindow.getTotalTime()))
				return True
		
		elif delay <0:
			if curTimeInSec < abs(delay):
				ui.message(msg)
				mainWindow.sayElapsedTime(True)
				return True
				return False
	
	def script_jumpAndReportTime(self,gesture):
		if self.hasNoMedia():
			return
		if self.isAJumpOutOfMedia(gesture):
			return
		else:
			sendGesture(gesture)
			mainWindow = self.appModule.mainWindow
			mainWindow.sayElapsedTime()
	
	def script_sayVolume(self, gesture):
		mainWindow = self.appModule.mainWindow
		(oldMuteState, oldLevel) = mainWindow.getVolumeMuteStateAndLevel()
		sendGesture(gesture)
		(muteState, level) = mainWindow.getVolumeMuteStateAndLevel()
		if (muteState, level)  == (oldMuteState, oldLevel) : return
		if not mainWindow.isPlaying() or muteState :
			# Translators: message to the user to report  volume level.
			speech.speakMessage(_("Volume: %s")%str(level))
			if muteState:
				# Translators: message to the user to say volume is muted.
				speech.speakMessage(_("Volume mute"))
	
	def script_toggleMuteAndReportState(self, gesture):
		def callback():
			mainWindow = self.appModule.mainWindow
			(muteState, level) = mainWindow.getVolumeMuteStateAndLevel()
			if muteState :
				# Translators: message To  the user to report volume is muted.
				speech.speakMessage (_("Volume mute"))
			elif not mainWindow.isPlaying():
				# Translators: message to the user to report volume is not muted.
				speech.speakMessage( _("volume unmuted"))
		
		sendGesture(gesture)
		wx.CallAfter(speech.cancelSpeech)
		wx.CallAfter(callback)
	
	def script_stopMedia(self, gesture):
		sendGesture(gesture)
		wx.CallAfter(speech.cancelSpeech)
		mainWindow = self.appModule.mainWindow
		if not mainWindow.hasMedia():
			mainWindow.resetMediaStates()
			# Translators: message to the user to say the media is stopped.
			wx.CallAfter(speech.speakMessage,_("Media stopped"))
		
	
	def script_togglePlayAndReportState(self, gesture):
		if gesture.mainKeyName  == self.appModule.vlcrcSettings.getKeyFromName("key-stop"):
			self.script_stopMedia(gesture)
			return
		sendGesture(gesture)
		mainWindow = self.appModule.mainWindow
		wx.CallAfter(speech.cancelSpeech)
		wx.CallAfter(mainWindow.reportMediaStates,)
	
	def script_mediaChange(self, gesture):
		sendGesture(gesture)
		mainWindow = self.appModule.mainWindow
		wx.CallAfter(speech.cancelSpeech)
		wx.CallLater(30, mainWindow.reportMediaChange)


	
	def script_hotKeyHelp(self,gesture):
		o = api.getFocusObject()
		helpMsg = []
		# Translators: title of script gesture help.
		helpMsg.append(_("Add-on's Input gestures:"))
		for identifier in self._gestureMap:
			scriptDoc = self._gestureMap[identifier].__doc__
			if scriptDoc:
				(layout, keyName) = keyboardHandler.KeyboardInputGesture.getDisplayTextForIdentifier(identifier)
				helpMsg.append("%s %s" %(scriptDoc, keyName))
		helpMsg.append("")
		vlcHelp = self.appModule.vlcrcSettings.vlcHotKeyHelpText()
		helpMsg.append( vlcHelp)
		text = "\n".join(helpMsg)
		# Translators: title of main window shortcut help window.
		title = _("%s - main window help") %_addonSummary
		wx.CallAfter(MessageBox.run, title, text)
	def script_recordResumeFile(self, gesture):
		def callback():
			mainWindow = self.appModule.mainWindow
			mediaInfos= vlcApplication.MediaInfos(mainWindow)
			mediaName = mediaInfos.getName()
			if mediaName == None:
				return
			curTime = getTimeList(mainWindow.getCurrentTime())
			if getTimeInSec(curTime) == 0:
				# Translators: message to user to say media cannot be played.
				ui.message(_("Not available, the media don't be played"))
				return
			conf = self.appModule.config
			if conf.recordFileToResume(mediaName, curTime):
				# Translators: message to user to say the resume playback time.
				msg = _("Playback of {0} file  will be resume at {1}")
				wx.CallLater(1500, ui.message, msg.format(mediaName, formatTime(":".join(curTime))))
		if self.hasNoMedia():
			return
		wx.CallAfter(callback)
	
	# Translators: Input help mode message for  record resume file command.
	script_recordResumeFile.__doc__ = _("Record current playing position for this media")
	script_recordResumeFile.category = _scriptCategory
	
	def script_resumePlayback(self,gesture):
		printDebug ("resumePlayback")
		def callback(resumeTime):
			res = vlc_special.messageBox(
			# Translators:  message to ask the user if he want to resume playback.
			_("Do you want to resume Playback at %s") %formatTime(resumeTime),
			# Translators: title of message box.
			_("%s - Confirmation")%_addonSummary,
			wx.OK|wx.CANCEL)
			if res == wx.CANCEL:
				return
			mainWindow = self.appModule.mainWindow
			totalTime = getTimeList(mainWindow.getTotalTime())
			jumpTime = getTimeList(resumeTime)
			wx.CallLater(200, mainWindow.jumpToTime, jumpTime, totalTime, startPlaying = True)

		if self.hasNoMedia():
			return
		mainWindow = self.appModule.mainWindow
		mediaInfos= vlcApplication.MediaInfos(mainWindow)
		mediaName = mediaInfos.getName()
		conf = self.appModule.config
		resumeTime = conf.getResumeFileTime(mediaName)
		if resumeTime == None or resumeTime == 0:
			#Translators: message to user to say  no resume time for this media
			ui.message(_("No resume time for this media"))
			return
		wx.CallAfter(callback,resumeTime)
	# Translators: Input help mode message for  resume playback command.
	script_resumePlayback.__doc__ = _("Resume playback at position recoreded for this media")
	script_resumePlayback.category = _scriptCategory

	
	def script_continuePlayback(self, gesture):
		printDebug ("InMainWindow: altRVLCCommand script") 
		if self.hasNoMedia():
			return
		mainWindow = self.appModule.mainWindow
		isPlaying = mainWindow.isPlaying()
		if isPlaying :
			mainWindow.togglePlayOrPause()
		mainWindow.mainPanel.pushContinuePlaybackButton()
		time.sleep(0.2)
		mainWindow.resetMediaStates(False)
		queueHandler.queueFunction(queueHandler.eventQueue,  mainWindow.sayElapsedTime)
		queueHandler.queueFunction(queueHandler.eventQueue, mainWindow.togglePlayOrPause)
		queueHandler.queueFunction(queueHandler.eventQueue, mainWindow.reportMediaStates)
			
	script_continuePlayback.__doc__ = _("Restart interrupted playback at position recorded by VLC")
	script_continuePlayback.category = _scriptCategory
class AppModule(AppModuleDebug):
	_appModuleGestures = {
		"kb:nvda+control+h" : "hotKeyHelp",
		}
	_trapNextGainFocus = False
	_continuePlayback = (False, None)
	_curTaskTimer = None
	_keyListToScript = (
		(jumpKeys , "jumpAndReportTime"),
		(normalSpeedKeys, "setAndReportNormalSpeed"),
		(speedKeys , "setAndReportSpeed" ),
		(volumeKeys , "sayVolume"),
		(muteKeys, "toggleMuteAndReportState"),
		(playKeys , "togglePlayAndReportState"),
		(movementKeys, "mediaChange"),
		)
		
	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)
		#toggleDebugFlag()

		self.hasFocus = False
		self.initialized = False
		self.bindGestures(self._appModuleGestures)
		self.initAppModule()
	
	def initAppModule(self):
		if self.initialized:
			printDebug ("AppmoduleVLC:  initAppModule: appModule already initialized")
			return
		printDebug ("AppModule VLC: initAppModule")
		if not hasattr(self, "vlcrcSettings "):
			self.vlcrcSettings = Vlcrc(_curAddon)
		if self.vlcrcSettings .initialized:
			vlcStrings.init()
			self.initVLCGestures()
			self.config = vlcAddonConfig.AddonConfigManager(self.vlcrcSettings)
			self.initialized = True
			printDebug ("AppModule VLC: appModule initialized")
	
	def _inputCaptor(self, gesture):
		def callback():
			time.sleep(0.2)
			o = api.getFocusObject()
			printDebug ("appModule VLC inputCaptor callback: %s, hasFocus= %s"%(controlTypes.roleLabels.get(o.role), o.hasFocus))
			if o.role in [controlTypes.ROLE_MENU, controlTypes.ROLE_MENUITEM, ]  and not o.hasFocus:
				printDebug ("click foreground object when focus object is on not focused object")
				self.mainWindow.resetMediaStates()
				mouseClick(api.getForegroundObject(), True, True)
		printDebug ("appModule VLC: inputCaptor: key = %s"%(gesture.mainKeyName))
		if not self.initialized:
			wx.CallAfter(self.initAppModule)
		if gesture.mainKeyName in ["escape", "leftAlt"]:
			# when focus is on menu item but menu is not open, these keys change  only focused state without event
			# so we need to put focus on menu bar as the menu is opened
			wx.CallAfter(callback)
		return True
	def  stopTaskTimer(self):
		if self._curTaskTimer is not None:
			self._curTaskTimer.Stop()
			self._curTaskTimer = None

		
	def setStatusBar(self):
		if not hasattr(self, "curAPIGetStatusBar "):
			self.curAPIGetStatusBar = api.getStatusBar
			api.getStatusBar = self.mainWindow.getStatusBar
	
	
		
	def _get_mainWindow(self):
		if hasattr(self, "_mainWindow")and self._mainWindow is not None:
			return self._mainWindow
		printDebug ("try to set mainWindow")
		mainWindow =vlcApplication.MainWindow(self)
		if mainWindow.topNVDAObject:
			printDebug ("MainWindow set")
			self._mainWindow = mainWindow
			self.setStatusBar()
			printDebug ("appModule mainWindow set")
			return self._mainWindow
		return None
	
	def event_appModule_gainFocus(self):
		printDebug("appModule VLC: event_appModulegainFocus")
		inputCore.manager._captureFunc = self._inputCaptor
		if not self.initialized:
			wx.CallAfter(self.initAppModule)
		self.hasFocus = True

	def event_appModule_loseFocus(self):
		printDebug ("appModule VLC: event_appModuleLoseFocus")
		self.stopTaskTimer()
		inputCore.manager._captureFunc = None
		if hasattr(self, "curAPIGetStatusBar"):
			api.getStatusBar = self.curAPIGetStatusBar
			delattr(self, "curAPIGetStatusBar")
		self.hasFocus = False
	
	def terminate(self):
		printDebug("AppModule VLC: terminate")
		self.stopTaskTimer()
		inputCore.manager._captureFunc = None
		if hasattr(self, "curAPIGetStatusBar"):
			api.getStatusBar = self.curAPIGetStatusBar
			delattr(self, "curAPIGetStatusBar")
		super(AppModule, self).terminate()
	
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		#printDebug("appModule vlc: chooseNVDAOverlayClass: %s, %s"%(controlTypes.roleLabels.get(obj.role), obj.name))
		if   not self.initialized:
			#printDebug ("chooseOverllayClass: appModule not initialized")
			return
		if obj.role in [ controlTypes.ROLE_MENU, controlTypes.ROLE_MENUITEM, controlTypes.ROLE_POPUPMENU, controlTypes.ROLE_CHECKMENUITEM]:
			#printDebug ("AppModule VLC: chooseOverlayClass role = %s, name= %s, clsList: %s"%(controlTypes.roleLabels.get(obj.role), obj.name, clsList))
			return
		if not isinstance(obj, NVDAObjects.IAccessible.IAccessible):
			return
		if vlcApplication.MainWindow.inVlcMainWindow(obj):
			#printDebug ("AppModule VLC: chooseOverlayClass insert class InVLCViewWindow , className = %s"%obj.windowClassName)
			clsList.insert(0, InVLCViewWindow)
	
	def event_typedCharacter(self,obj, nextHandler, ch):
		printDebug ("appModule VLC: event_typedCharacter: role = %s, name = %s, ch = %s" %(controlTypes.roleLabels.get(obj.role), obj.name, ch))
		if not self.hasFocus: return
		nextHandler()
	
	def event_focusEntered(self, obj, nextHandler):
		try:
			ret = repr(obj.__class__.__mro__)
		except:
			ret = ""
		printDebug ("appModule VLC: event_focusEntered: %s, %s: %s" %(controlTypes.roleLabels.get(obj.role), obj.name, ret))
		if obj.role == controlTypes.ROLE_APPLICATION and obj.name == "vlc":
			self.mainWindow.resetMediaStates()
			return
		nextHandler()
	def event_foreground(self, obj, nextHandler):
		printDebug ("appModule VLC: event_foreground: %s, %s" %(controlTypes.roleLabels.get(obj.role),obj.name))
		if not self.hasFocus: return
		if not self.initialized:
			wx.CallAfter(self.initAppModule)
		maximizeWindow(obj.windowHandle)
		nextHandler()
	
	def event_nameChange(self, obj, nextHandler):
		printDebug ("appModule VLC: event_nameChange: role = %s, name = %s" %(controlTypes.roleLabels.get(obj.role),obj.name))
		nextHandler()
		if obj.name == "VLC (Direct3D11 output)" and not  self.initialized:
			wx.CallAfter(self.initAppModule)
			return
		if self.hasFocus:
			self.mainWindow.reportContinuePlayback()
		
	
	def initVLCGestures(self):
		printDebug ("appModule VLC: initVLCGestures")
		self.vlcGestures = {}
		for (keyList, script) in self._keyListToScript:
			for name in keyList:
				key = self.vlcrcSettings.getKeyFromName(name)
				if key != "":
					self.vlcGestures["kb:%s" %key] = script
		self.jumpKeyToDelay = {}
		for keyName in jumpDelays:
			key = self.vlcrcSettings.getKeyFromName(keyName)
			if key != "":
				identifier = normalizeGestureIdentifier("kb:%s"%key)
				self.jumpKeyToDelay[identifier] = jumpDelays[keyName]
		printDebug ("appModuleVLC: initVLCGestures: gestures = %s"%self.vlcGestures)

	
	def script_hotKeyHelp(self,gesture):
		obj = api.getFocusObject()
		if hasattr(obj, "script_hotKeyHelp"):
			obj.script_hotKeyHelp(gesture)
	# Translators: Input help mode message for hot key help command.
	script_hotKeyHelp.__doc__ = _("Display add-on's help")
	script_hotKeyHelp.category = _scriptCategory

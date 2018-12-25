# appModules/vlc/vlcApplication.py.
# a part of VLC media player add-on
# Copyright 2018 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
addonHandler.initTranslation()
from logHandler import log
import controlTypes
import textInfos
import api
import speech
import queueHandler
import ui
import keyboardHandler
import time
import wx
import gui
import os
import eventHandler
import mouseHandler
import oleacc
import ctypes
from NVDAObjects.IAccessible import getNVDAObjectFromEvent
import winUser
import vlcAddonConfig
import scriptHandler
_curAddon = addonHandler.getCodeAddon()
import sys
debugToolsPath = os.path.join(_curAddon.path, "debugTools")
sys.path.append(debugToolsPath)
try:
	from debug import printDebug
except ImportError:
	def printDebug (msg): return
del sys.path[-1]
sharedPath = os.path.join(_curAddon.path, "shared")
sys.path.append(sharedPath)
import vlcStrings
from vlcUtils import *
del sys.path[-1]


def getForegroundObject():
	hdMain=ctypes.windll.user32.GetForegroundWindow()
	if not vlcStrings.getString(vlcStrings.ID_VLCAppTitle) in winUser.getWindowText(hdMain):
		hdMain= winUser.getWindow(winUser.getWindow(hdMain,2),2)
	o =getNVDAObjectFromEvent(hdMain,-4,0)
	return o


class MainWindow (object):
	_curMediaState = None
	_continuePlayback = None
	_volumeState = (None, None)
	_loopState = None
	
	def __init__(self, appModule):
		super(MainWindow, self).__init__()
		self.appModule = appModule

	@property
	def topNVDAObject(self):
		if hasattr(self, "_topNVDAObject"):
			return self._topNVDAObject
		printDebug ("MainWindow:  topNVDAObject")
		foreground = getForegroundObject()
		name = foreground.name
		if name and (vlcStrings.getString(vlcStrings.ID_VLCAppTitle) in name or name == "vlc"):
			self._topNVDAObject = foreground
			self.mainPanel = MainPanel(self)
			self.volumeInfos = VolumeInfos(self)
			return foreground
		return None

	
	@classmethod
	def inVlcMainWindow(cls, obj):
		try:
			o = obj.IAccessibleObject
		except:
			log.debugWarning("MainWindow: inVlcMainWindow: no IAccessible object")
			return False
		desktopName = api.getDesktopObject().name
		while o:
			try:
				name = o.accName(0)
				if name and name == api.getDesktopObject().name: break
				if o.accRole(0) == oleacc.ROLE_SYSTEM_WINDOW:
					if vlcStrings.getString(vlcStrings.ID_VLCAppTitle) in name or name == "vlc":
						return True
			except:
				pass
			try:
				o = o.accParent
			except:
				o = None
		return False


	def getStatusBar(self):
		try:
			statusBar =self.topNVDAObject.firstChild.next
		except:
			statusBar = None
		if statusBar is None:
			log.warning( "getStatusBar: status bar not found")
		return statusBar
	"""
	def setStatusBar(self):
		if not hasattr(self.appModule, "curAPIGetStatusBar"):
			self.appModule.curAPIGetStatusBar = api.getStatusBar
			api.getStatusBar = self.getStatusBar
"""	
	def getMediaViewNVDAObject(self):
		mediaInfos = MediaInfos(self)
		return mediaInfos.getViewNVDAObject()


	def giveFocusToViewWindow(self):
		printDebug ("giveFocusToViewWindow")
		self.resetMediaStates()
		obj = self.topNVDAObject
		oldSpeechMode = speech.speechMode
		speech.speechMode = speech.speechMode_off
		mouseClick(obj, True, False)
		time.sleep(0.2)
		obj = api.getFocusObject()
		mouseClick(obj, False, False)
		api.processPendingEvents()
		speech.speechMode = oldSpeechMode
		speech.cancelSpeech()
		wx.CallAfter( self.reportMediaStates)
		wx.CallAfter(self.reportcontinuePlayback)
	def getContinuePlaybackScriptGesture(self):
		focus = api.getFocusObject()
		if not hasattr(focus, "continuePlaybackScript"): return
		continuePlaybackScript = focus.continuePlaybackScript
		from inputCore import manager
		all = manager.getAllGestureMappings()[_curAddon.manifest['summary']]
		for item in all:
			infos = all[item]
			if infos.scriptName == "continuePlayback":
				gestures = infos.gestures
				if len(gestures):
					return gestures[0].split(":")[1]
		return None
	
	def reportContinuePlayback(self):
		if not self.hasMedia:
			return
		(continuePlayback, msg) = self.mainPanel.getcontinuePlayback()
		if (continuePlayback != self._continuePlayback):
			if continuePlayback: 
				continuePlaybackScriptGesture = self.getContinuePlaybackScriptGesture()
				if continuePlaybackScriptGesture is not None:
					# Translators: message to user when continue playing is available.
					msg = _("continue playback %s")%continuePlaybackScriptGesture
					wx.CallAfter(speech.speakMessage,msg)
					printDebug ("Application: reportContinuePlayback, start = %s"%msg)
			self._continuePlayback = continuePlayback

	
	def reportMediaStates(self):
		(muteState, level) = self.getVolumeMuteStateAndLevel()
		if not self.hasMedia():
			if muteState  :
				# Translators: message to the user to say volume is muted.
				speech.speakMessage(_("volume muted"))
			return
		isPlaying = self.isPlaying()
		printDebug ("MainWindow: reportMediaStates playing= %s, oldPlaying= %s, mute = %s" %(isPlaying, self._curMediaState,muteState))
		if self._curMediaState  is not None and (isPlaying == self._curMediaState): return
		if muteState  :
			# Translators: message to user when volume is muted
			msg  = _("volume muted")
			if  isPlaying:
				# Translators: message to the user to say  playing with muted volume.
				speech.speakMessage(_("Playing,%s")%msg)
			else:
				# translators: message to the user to say pause with muted volume.
				speech.speakMessage(_("Pause,%s")%msg)


		elif not isPlaying:
			# Translators: message to the user to say media is paused.
			speech.speakMessage(_("Pause"))
		self._curMediaState = isPlaying
	
	def resetMediaStates(self, alsoContinuePlayback = True):
		self._curMediaState = None
		if alsoContinuePlayback:
			self._continuePlayback = None

	def reportMediaName(self):
		mediaInfos= MediaInfos(self)
		mediaName = mediaInfos.getName()
		if mediaName is None:
			# Translators: message to the user to say there is no media.
			speech.speakMessage( _("No media"))
		else:
			speech.speakMessage(mediaName)
	def reportMediaChange(self):
		speech.cancelSpeech()
		self.reportMediaName()
		self.resetMediaStates()
		self.reportMediaStates()
	
	def hasMedia(self):
		mediaInfos= MediaInfos(self)
		mediaName = mediaInfos.getName()
		if mediaName is None:
			return False
		return True
	
	def isPlaying(self):
		mediaInfos= MediaInfos(self)
		return mediaInfos.isPlaying()
	
	def getTotalTime(self) :
		mediaInfos= MediaInfos(self)
		return mediaInfos.getTotalTime()
		
	def getCurrentTime(self):
		mediaInfos= MediaInfos(self)
		return mediaInfos.getCurrentTime()

	def sayElapsedTime(self, forced = False) :
		if not self.hasMedia():
			return
		(muteState, level) = self.volumeInfos.getMuteAndLevel()
		if not muteState and not forced and self.isPlaying():
			return
		mediaInfos= MediaInfos(self)
		elapsedTime = mediaInfos.getElapsedTime()
		if elapsedTime:
			# Translators: message to the user to say played duration.
			msg = _("Played duration %s") if forced else "%s"
			ui.message(msg % formatTime(elapsedTime))
	
	def sayRemainingTime(self):
		if not self.hasMedia() :
			return
		mediaInfos= MediaInfos(self)
		remainingTime = mediaInfos.getRemainingTime()
		# Translators: message to the user to report  remaining duration.
		ui.message(_("remaining duration %s") %formatTime(remainingTime))


	
	def getVolumeMuteStateAndLevel(self):
		return self.volumeInfos.getMuteAndLevel()
		

	def getSpeedValue(self) :
		# speed value is on third child of status bar
		statusBar = StatusBar(self).NVDAObject
		o = statusBar.getChild(2)
		if o and "x" in o.name :
			st1, st, st2 = o.name, "", ""
			sst1 = st1.split(".")
			st2 = sst1[-1]
			if st2[-2]=="0" :
				st2 = st2.replace("0","")
			if st2 == "x" :
				st = "".join(sst1[0]+st2)
			else :
				st = "".join(sst1[0]+"."+st2)
			return st
		return ""
	
		
	def reportVolumeStateChange(self):
		(muteState, level) = self.volumeInfos.getMuteAndLevel()
		if (muteState, level)  == self._volumeState: return
		self._volumeState = (muteState, level)
		if not self.isPlaying() or muteState :
			# Translators: message to the user to report  volume level.
			ui.message(_("Volume: %s")%str(level))
			if muteState:
				# Translators: message to the user to say volume is muted.
				ui.message(_("Volume mute"))
	
	def togglePlayOrPause(self):
		isPlaying = self.isPlaying()
		self.mainPanel.togglePlayPause()
	
	#def reportLoopStateChange(self):
		#self.mainPanel.buttonsPanel.reportLoopStateChange()
	
	def reportLoopStateChange(self):
		speech.cancelSpeech()
		loopState =  self.mainPanel.getLoopState()
		if loopState :
			# Translators: message to user to report loop state : repeat all or repeat only current media.
			msg = _("repeat all") if not self._loopState else _("repeat only  current media")
		else:
			# Translators: message to user to report no repeat state.
			msg = _("no repeat")
		speech.speakMessage( msg)
		self._loopState = loopState
	def reportRandomStateChange(self):
		speech.cancelSpeech()
		randomState =  self.mainPanel.getRandomState()
		# Translators: message to user to report random or normal playback state.
		msg = _("Random playback") if randomState else _("Normal playback")
		speech.speakMessage(msg)
	
	
	def reportLoopAndRandomStates(self):
		self._loopState =  self.mainPanel.getLoopState()
		randomState = self.mainPanel.getRandomState()
		print "reportLoopAndRandomStates: random= %s, loop= %s"%(self._loopState, randomState)
		msg = None
		if self._loopState and randomState:
			# Translators: message to user to report repeat and random playback state.
			msg = _("With repeat and random playback")
		elif self._loopState :
			# Translators: message to user to report only repeat playback state
			msg = _("With repeat")
		elif  randomState:
			# Translators: message to user to report only random playback state.
			msg = _("With random playback")
		if msg is not None:
			wx.CallAfter(speech.speakMessage, msg)
	def  calculatePosition(self, jumpTimeInSec, totalTimeInSec, isPlaying):
		mainWindow = self
		o1 = mainWindow.getMediaViewNVDAObject()
		(x,y,l,h) = o1.location
		iX=(int(x)+5)+(int(l)-10)*jumpTimeInSec/totalTimeInSec
		return (iX, int(y)+int(h)/2)
	
	def adjustPosition(self, jumpTimeInSec, totalTimeInSec, x, y):
		def moveBy10Sec(count, direction ):
			printDebug ("moveBy10sec: count= %s, direction = %s"%(count, direction))
			keyToRight =  self.appModule.vlcrcSettings.getKeyFromName("key-jump+short")
			keyToLeft = self.appModule.vlcrcSettings.getKeyFromName("key-jump-short")
			key = keyToRight if direction>0 else keyToLeft
			d= 0
			if count:
				for i in range(1, count+1):
					keyboardHandler.KeyboardInputGesture.fromName(key).send()
					d += direction*10
			return d
		
		def moveBy3Sec(count, direction ):
			printDebug ("moveBy3sec: count= %s, direction = %s"%(count, direction))
			keyToRight =  self.appModule.vlcrcSettings.getKeyFromName("key-jump+extrashort" )
			keyToLeft = self.appModule.vlcrcSettings.getKeyFromName("key-jump-extrashort")
			key = keyToRight if direction>0 else keyToLeft
			d= 0
			if count != 0:
				for i in range(1, count+1):
					keyboardHandler.KeyboardInputGesture.fromName(key).send()
					d  += direction*3
			return d
		printDebug ("MainWindow: adjustPosition")		
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
		mainWindow = self.appModule.mainWindow
		curTimeInSec = getTimeInSec(mainWindow.getCurrentTime())
		diff = curTimeInSec -jumpTimeInSec
		direction= 1 if diff <0 else -1
		diff = abs(diff)
		if diff == 0:
			#nothing to do
			return
		if diff >20:
			leftClick(x,y)
			time.sleep(0.2)
			api.processPendingEvents()
			mainWindow = self.appModule.mainWindow
			curTimeInSec = getTimeInSec(mainWindow.getCurrentTime())
			diff = curTimeInSec -jumpTimeInSec
			direction= 1 if diff <0 else -1
			diff = abs(diff)
			
		if diff%10 == 0:
			moveBy10Sec(diff/10, direction)
			return
		if diff%3 == 0:
			moveBy3Sec(diff/3, direction)
			return
		
		if (curTimeInSec <=19  and direction>0
			or totalTimeInSec -curTimeInSec <= 19 and direction <0):
			moveBy10Sec(1,direction)
			diff  = 10 - diff
			direction =  (-1)*direction
		
		if diff > 9:
			moveBy10Sec(diff/10, direction)
			diff = diff%10
			if diff == 0:
				return
		actions = actionsForOffset[diff]
		for action in actions:
			move = action[1]
			count = action[0]
			d = action [2]
			move(count, d*direction)
			
	
	def jumpToTime(self, jumpTime, totalTime, startPlaying = False):
		print "type: %s" %type(jumpTime)
		printDebug ("MainWindow: jumpToTime")
		mainWindow = self
		speech.cancelSpeech()
		oldSpeechMode = speech.speechMode
		speechMode = speech.speechMode_off
		api.processPendingEvents()
		speech.cancelSpeech()
		if jumpTime == None or jumpTime ==0:
			speech.speechMode = oldSpeechMode
			# Translators: message to the user to report no time change.
			queueHandler.queueFunction(queueHandler.eventQueue, speech.speakMessage, _("No change"))
			queueHandler.queueFunction(queueHandler.eventQueue, mainWindow.sayElapsedTime,True)
			queueHandler.queueFunction(queueHandler.eventQueue, mainWindow.reportMediaStates)
			return
		isPlaying = mainWindow.isPlaying()
		curTimeInSec = getTimeInSec(mainWindow.getCurrentTime())
		if type(jumpTime) is int:
			jumpTimeInSec = jumpTime
		else:
			jumpTimeInSec = getTimeInSec(jumpTime)

		if abs(curTimeInSec - jumpTimeInSec) <=2:
			# we are at time
			speech.speechMode = oldSpeechMode
			queueHandler.queueFunction(queueHandler.eventQueue, mainWindow.sayElapsedTime)
			queueHandler.queueFunction(queueHandler.eventQueue, mainWindow.reportMediaStates)
			if not isPlaying and startPlaying:
				mainWindow.togglePlayOrPause()
				return
		if isPlaying:
			# pause playing
			mainWindow.togglePlayOrPause()
			time.sleep(0.2  )
		totalTimeInSec = getTimeInSec(totalTime)
		(x, y)  = self.calculatePosition(jumpTimeInSec, totalTimeInSec, isPlaying)
		leftClick(x,y)
		api.processPendingEvents()
		time.sleep(0.2)
		winUser.setCursorPos(x,y-20)
		mouseHandler.executeMouseMoveEvent(x,y)
		speech.cancelSpeech()
		speech.speechMode = oldSpeechMode
		# wait for new time
		api.processPendingEvents()
		i= 20
		newCurTimeInSec = getTimeInSec(mainWindow.getCurrentTime())
		while  i>0 and newCurTimeInSec == curTimeInSec:
			time.sleep(0.05)
			i = i-1
			if i == 0:
				# time out
				# Translators: message to the user to say that jump is not possible.
				queueHandler.queueFunction(queueHandler.eventQueue,  speech.speakMessage, _("Jump is not possible"))
				queueHandler.queueFunction(queueHandler.eventQueue,  mainWindow.sayElapsedTime)
				queueHandler.queueFunction(queueHandler.eventQueue,  mainWindow.reportMediaStates)
				printDebug ("jump is not completed")
				return

			newCurTimeInSec = getTimeInSec(mainWindow.getCurrentTime())
		if newCurTimeInSec != jumpTimeInSec:
			self.adjustPosition(jumpTimeInSec, totalTimeInSec, x, y)
		if not startPlaying and isPlaying:
			mainWindow.togglePlayOrPause()
			queueHandler.queueFunction(queueHandler.eventQueue, mainWindow.reportMediaStates)
			return

		queueHandler.queueFunction(queueHandler.eventQueue,  mainWindow.sayElapsedTime)
		if startPlaying:
			mainWindow.togglePlayOrPause()
		queueHandler.queueFunction(queueHandler.eventQueue, mainWindow.reportMediaStates)

class MediaInfos(object):
	def __init__(self, mainWindow):
		#printDebug ("MediaInfo")
		super(MediaInfos, self).__init__()
		self.mainWindow = mainWindow
		self.statusBar = StatusBar(self.mainWindow).NVDAObject
	
	@property
	def timesNVDAObject(self):
		if hasattr(self, "_timesNVDAObject")and self._timesNVDAObject is not None:
			return self._timesNVDAObject
		oMain = self.mainWindow.mainPanel.NVDAObject
		try:
			for o in oMain.children:
				if o.role==controlTypes.ROLE_BORDER:
					self._timesNVDAObject = o
					return o
		except:
			self._timesNVDAObject = None
		log.warning("ObjectTime not found")
		return self._timesNVDAObject
	
	def isPlaying(self):
		try:
			oDeb= self.timesNVDAObject.next.IAccessibleObject
		except:
			return False
		count = oDeb.accChildCount
		i= 0
		while i <count:
			o= oDeb.accChild(i)
			i= i+1
			if o.accRole(0) ==oleacc.ROLE_SYSTEM_PUSHBUTTON and vlcStrings.getString(vlcStrings.ID_PauseThePlaybackButtonDescription) == o.accDescription(0):
				return True
		return False
	
	def getViewNVDAObject(self):
		return self.timesNVDAObject.getChild(1)

	def getName(self):
		# name of media is the second child of status bar
		o = self.statusBar.getChild(1)
		return o.name

		
	def getTotalTime(self) :
		# media total time is on forth childof status bar
		o = self.statusBar.getChild(3)
		t1 = o.name
		st1=t1.split("/")
		t1 =st1[-1]
		return t1
	
	def getCurrentTime(self):
		topNVDAObject = self.mainWindow.topNVDAObject
		o = self.timesNVDAObject.getChild(0)
		if o == None  or o.name == None:
			log.warning("CurTime object not found or nottime")
			return None
		return o.name
	def getCurrentTimeInSeconds(self):
		t = getTimeInSec(self.timesNVDAObject.getChild(0).name)
		return t
	
	def getRemainingTime(self):
		t2sec = getTimeInSec(self.mainWindow.getTotalTime())
		o1 = self.timesNVDAObject.children[0]
		t1 = o1.name
		t1sec = getTimeInSec(t1)
		t3sec = t2sec-t1sec
		if t3sec<3600 :
			st = "".join(str(int(t3sec /60))+":"+str(t3sec %60))
		if t3sec>=3600 :
			th = int(t3sec /3600)
			tm =  int((t3sec - 3600*th) /60)
			if tm<10 :
				stm = "".join("0"+str(tm))
			else :
				stm =str(tm)
			ts =   t3sec - 3600*th -60*tm
			if ts<10 :
				sts = "".join("0"+str(ts))
			else :
				sts =str(ts)
			st = "".join(str(th)+":"+stm+":"+sts)
		return st
	def getElapsedTime(self) :
		o = self.timesNVDAObject.getChild(0)
		t1 = o.name
		if getTimeInSec(t1)>=0 and getTimeInSec(t1)<getTimeInSec(self.getTotalTime()):
			return t1
		return None


class StatusBar (object):
	def __init__(self, mainWindow):
		#printDebug ("StatusBar")
		super(StatusBar, self).__init__()
		self.topNVDAObject= mainWindow.topNVDAObject
	@property
	def NVDAObject(self):
		if hasattr(self, "_NVDAObject"):
			return self._NVDAObject
		top=self.topNVDAObject
		for o in top.children:
			if o.role == controlTypes.ROLE_STATUSBAR:
				self._NVDAObject = o
				return o
		log.warning( "getStatusBar: status bar not found")
		return None

class VolumeInfos(object):
	def __init__(self, mainWindow):
		printDebug ("VolumeInfo")
		super(VolumeInfos, self).__init__()
		self.mainWindow = mainWindow
		self.volumeIAObject = self.getVolumeIAObject()
	@property
	def NVDAObject(self):
		if hasattr(self, "_NVDAObject"):
			return self._NVDAObject
		oMain = self.mainWindow.mainPanel.NVDAObject
		try:
			for o in oMain.children:
				if o.role==controlTypes.ROLE_BORDER:
					self._NVDAObject = o
					return o
		except:
			pass
		log.warning("ObjectTime not found")
		return None
	def getVolumeIAObject(self):
		try:
			oDeb = self.NVDAObject.next.IAccessibleObject
		except:
			return None
		count = oDeb.accChildCount
		i= 0
		while i <count:
			o= oDeb.accChild(i)
			i= i+1
			if o and o.accChildCount:
				if o.accRole(0) ==oleacc.ROLE_SYSTEM_CLIENT:
					return o
		return None
	
	def getMuteAndLevel(self):
		o = self.volumeIAObject
		if o:
			muteState = False
			if vlcStrings.getString(vlcStrings.ID_UnMuteImageDescription) in o.accChild(1).accDescription(0):
				muteState = True
			level = o.accChild(2).accValue(0)
			return (muteState, level)
		return (None, None)
		

class MainPanel(object):
	def __init__(self, mainWindow):
		printDebug ("MainPanel")
		super(MainPanel, self).__init__()
		self.mainWindow = mainWindow
		self.buttonsPanel = ButtonsPanel(self)
		
	@property
	def NVDAObject(self):
		top= self.mainWindow.topNVDAObject
		for o in top.children:
			if o.role == controlTypes.ROLE_PANE:
				return o
		return None
	
	def getcontinuePlayback(self):
		try:
			obj = self.NVDAObject.firstChild
			if controlTypes.STATE_INVISIBLE in obj.states:
				return (False, None)
			return (True,  obj.lastChild.name)
		except:
			return (False, None)
	
	def pushContinuePlaybackButton(self):
		try:
			obj = self.NVDAObject.firstChild.lastChild
			if obj.role == controlTypes.ROLE_BUTTON:
				obj.IAccessibleObject.accdoDefaultAction(0)
		except:
			pass
		
	def getLoopState(self):
		return self.buttonsPanel.getLoopCheckButtonState()
	def getRandomState(self):
		return self.buttonsPanel.getRandomCheckButtonState()
	def togglePlayPause(self):
		self.buttonsPanel.clickPlayPauseButton()

class ButtonsPanel(object):
	def __init__(self, mainPanel):
		printDebug ("ButtonsPanel")
		super(ButtonsPanel, self).__init__()	
		self.mainPanel = mainPanel
		self.NVDAObject = mainPanel.NVDAObject.lastChild
		self.IAObject = self.NVDAObject.IAccessibleObject

	
	def getLoopCheckButtonState(self):
		oDeb= self.IAObject
		count = oDeb.accChildCount
		i= 0
		while i <= count:
			o= oDeb.accChild(i)
			i= i+1
			if o and o.accRole(0) ==oleacc.ROLE_SYSTEM_CHECKBUTTON and vlcStrings.getString(vlcStrings.ID_LoopCheckButtonDescription) in o.accDescription(0):
				return True if o.accState(0)  & oleacc.STATE_SYSTEM_CHECKED else False
		return False
	
	def getRandomCheckButtonState(self):
		oDeb= self.IAObject
		count = oDeb.accChildCount
		i= 0
		while i <=count:
			o= oDeb.accChild(i)
			i= i+1
			if o and o.accRole(0) ==oleacc.ROLE_SYSTEM_CHECKBUTTON and vlcStrings.getString(vlcStrings.ID_RandomCheckButtonDescription) in o.accDescription(0):
				return True if o.accState(0)  & oleacc.STATE_SYSTEM_CHECKED else False
				log.warning("random checkButton not found")
		return False
	def getPlayPauseButton(self):
		oDeb= self.IAObject
		count = oDeb.accChildCount
		i= 0
		while i <count:
			o= oDeb.accChild(i)
			i= i+1
			role = o.accRole(0)
			if ( role ==oleacc.ROLE_SYSTEM_PUSHBUTTON and vlcStrings.getString(vlcStrings.ID_PlayButtonDescription) in o.accDescription(0)
				or role ==oleacc.ROLE_SYSTEM_PUSHBUTTON and vlcStrings.getString(vlcStrings.ID_PauseThePlaybackButtonDescription ) in o.accDescription(0)):
					return o
		return None
	
	def clickPlayPauseButton(self):
		"""
		oDeb= self.IAObject
		count = oDeb.accChildCount
		i= 0
		while i <count:
			o= oDeb.accChild(i)
			i= i+1
			role = o.accRole(0)
			if ( role ==oleacc.ROLE_SYSTEM_PUSHBUTTON and vlcStrings.getString(vlcStrings.ID_PlayButtonDescription) in o.accDescription(0)
				or role ==oleacc.ROLE_SYSTEM_PUSHBUTTON and vlcStrings.getString(vlcStrings.ID_PauseThePlaybackButtonDescription ) in o.accDescription(0)):
		"""
		o = self.getPlayPauseButton()
		if o is None: return
		name = o.accName(0)
		left,top,width,height = o.accLocation(0)
		leftClick (left+(width/2),top+(height/2))
		# verify if it is done
		if o.accName(0) == name: return
		#no, so try other thing
		oldSpeechMode = speech.speechMode
		speech.speechMode = speech.speechMode_off
		keyboardHandler.KeyboardInputGesture.fromName("space").send()
		time.sleep(0.1)
		api.processPendingEvents()
		speech.speechMode= oldSpeechMode
	

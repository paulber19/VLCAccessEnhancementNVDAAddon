# shared/vlcUtils.py.
# a part of VLC media player add-on
# Copyright 2018 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
addonHandler.initTranslation()
from logHandler import log
import winUser
import api
import keyboardHandler
import time
import wx
import config
import characterProcessing

def PutWindowOnForeground(hwnd, sleepNb  = 10, sleepTime  = 0.1):
	winUser.setForegroundWindow(hwnd)
	try:
		winUser.setForegroundWindow(hwnd)
	except:
		pass
	for i in [sleepTime]*(sleepNb-1):
		time.sleep(i)
		if winUser.getForegroundWindow() == hwnd:
			return True
	# last chance
	keyboardHandler.KeyboardInputGesture.fromName("alt+Tab").send()
	keyboardHandler.KeyboardInputGesture.fromName("alt+Tab").send()
	time.sleep(sleepTime)
	if winUser.getForegroundWindow() == hwnd:
		return True
	return False

def formatTime(sTime) :
	# Translators: no comment.
	msgOne = _("one")
	# Translators: no comment.
	msgOneMinute = _("one minute")
	time = []
	for i in sTime.split(":"):
		time.append(int(i))
	if (len(time) in [2,3]) and time[0] == 0:
		time = time[1:]
	msg = ""
	saySeconds = False
	if len(time) == 3 :
		#hours, minuts, seconds
		if time[0] == 0:
			pass
		elif time[0] == 1:
			# Translators: no comment.
			msg = _("one hour")
		else:
			# Translators: message to user to say hours 's number.
			msg = _("%s hours")%str(time[0])
			
		time = time[1:]
	if len(time) == 2:
		#minuts, seconds
		if msg == "" :
			#no hours
			if time[0] == 0:
				saySeconds = True
			elif time[0] == 1:
				msg =  msgOneMinute
			else:
				# Translators: message to user to say minutes 's number.
				msg = _("%s minuts") %str(time[0])
		else:
			#with hours
			if time[0] == 0:
				saySeconds = True
			elif time[0] == 1:
				#one minute
				if time[1] == 0:
					#no second
					msg = "%s %s" %(msg, msgOne)
				else:
					msg =  "%s %s" %(msg, msgOneMinute)
			else:
				#many minuts
				if time[1] == 0:
					# non second
					msg = "%s %s" %(msg, str(time[0]))
				else:
					# Translators: Message to user to say hours and minutes.
					msg = "%s %s" %(msg, _("%s minuts"%str(time[0])))
		time = time[1:]
	if  time[0] == 1:
		#one second
		if msg== "":
			# Translators: no comment.
			msg = _("one second")
		else:
			if saySeconds:
								# Translators: message to user to say hour, minute with seconds.
				msg = "%s %s" %(msg, _("%s seconds")%msgOne)
			else:
				# Translators: message to user to say hour, minute with one second.
				msg = "%s %s" %( msg,msgOne)
	elif time[0] != 0:
		#some seconds
		if msg == "":
			# only seconds
			# Translators: message to user to say  only seconds.
			msg = _("%s seconds") %str(time[0])
		else:
			if saySeconds:
				# Translators: message to user to say hour, minute and seconds
				msg = "%s %s" %(msg, _("%s seconds") %str(time[0]))
			else:
				msg = "%s %s" %(msg,str(time[0]))
	elif msg == "" and time[0] == 0:
		# Translators: no comment.
		msg = _("0 second")
	return msg
		
def getTimeInSec(theTime):

	if isinstance(theTime, basestring):
		if "--:--" in theTime:
			return 0
		
		timeList=getTimeList(theTime)
		
	else:
		timeList = theTime
	
	return int(timeList[0])*3600 +int(timeList[1])*60 +int(timeList[2])
		
def getTimeInMinutes( sTime) :
	timeList=getTimeList(sTime)
	iMinu = 0
	if int(timeList[2]) >30 :
		iMinu = 1
	iMinu = iMinu+int(timeList[1])+int(timeList[0])*60
	return iMinu
def getTimeList( timeString):
	""" convert time in the form hh:mm:ss to a string list of three elements: hours, minutes, seconds """

	timeList = timeString.split(":")
	timeList.reverse()
	t = ["0", "0", "0"]
	i = 2
	for s in timeList:
		t[i] = str(int(s))
		i= i-1
	
	return t
def getTimeString( timeList):
	""" convert time  to time string with the form hh:mm:ss"""


	return "{0}:{1}:{2}" .format(timeList[0].zfill(2),timeList[1].zfill(2), timeList[2].zfill(2))

	
def leftClick (x,y):
	winUser.setCursorPos(x,y)
	winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
	winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
	
	
# winuser.h constant
SC_MAXIMIZE     = 0xF030
WS_MAXIMIZE         = 0x01000000
WM_SYSCOMMAND = 0x112

def maximizeWindow(hWnd):
	winUser.sendMessage (hWnd, WM_SYSCOMMAND, SC_MAXIMIZE,0)

def mouseClick(obj, rightButton=False, twice = False):
	api.moveMouseToNVDAObject(obj)
	api.setMouseObject(obj)
	if not rightButton :
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
		if twice:
			time.sleep(0.1)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
	
	else:
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTUP,0,0,None,None)
		if twice:
			time.sleep(0.1)
			winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTDOWN,0,0,None,None)
			winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTUP,0,0,None,None)


class MessageBox(wx.Dialog):
	def __init__(self, parent, ID, title, helpMessage, closeIfInactive):
		super(MessageBox, self).__init__(parent, ID,title )
		self.oldSymbolLevel = config.conf["speech"]["symbolLevel"]
		config.conf["speech"]["symbolLevel"] = characterProcessing.SYMLVL_ALL
		# Translators: message shown in dialog to  close window.
		self.helpMessage = "%s\r\n%s" %(helpMessage, _("Hit Escape key to close the window"))
		self.closeIfInactive = closeIfInactive
		self.destroyed = False
		self.doGui()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.HORIZONTAL)
		box = wx.StaticBox(self,-1,"")
		taskSizer = wx.StaticBoxSizer(box,wx.HORIZONTAL)
		textControl = wx.TextCtrl(self,-1,style =wx.TE_MULTILINE|wx.TE_READONLY,size=(530,490))
		textControl.SetValue(self.helpMessage)
		textControl.SetFocus()
		taskSizer.Add(textControl, wx.ALL|wx.EXPAND,wx.ALIGN_CENTRE, 5)
		mainSizer.Add(taskSizer,flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTRE, border=5 )
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# the events
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.Bind(wx.EVT_CHAR_HOOK, self.onOutputChar)
		self.Bind(wx.EVT_ACTIVATE, self.onActivate)
	def onActivate(self, evt):
		if  evt.GetActive():
			config.conf["speech"]["symbolLevel"] = characterProcessing.SYMLVL_ALL
		else:
			config.conf["speech"]["symbolLevel"] = self.oldSymbolLevel

	def onClose(self, evt):
		self.Destroy()
		evt.Skip()
			
	def onOutputChar(self, evt):
		key = evt.GetKeyCode()
		if key in (wx.WXK_RETURN,wx.WXK_NUMPAD_ENTER,wx.WXK_SPACE,wx.WXK_ESCAPE) :
			self.Close()
		evt.Skip()
	@classmethod
	def run(cls,  title, msg):
		d = cls(None,wx.ID_ANY, title,msg, True)
		d.CentreOnScreen()
		d.Show(True)
		PutWindowOnForeground(d.GetHandle(), 5, 0.2)

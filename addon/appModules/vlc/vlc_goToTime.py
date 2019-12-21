# appModules\vlc\vlc_goToTime.py.
# a part of vlcAccessEnhancement add-on
# Copyright 2019 paulber19
#This file is covered by the GNU General Public License.


import addonHandler
addonHandler.initTranslation()
import wx
import gui
import ui
import os
import sys
_curAddon = addonHandler.getCodeAddon()
sharedPath = os.path.join(_curAddon.path, "shared")
sys.path.append(sharedPath)
from vlc_utils import PutWindowOnForeground
from vlc_special import makeAddonWindowTitle
del sys.path[-1]

class GoToTimeDialog(wx.Dialog):
	def __init__(self, parent, ID, curTime , totalTime, mainWindow):
		self.mainWindow = mainWindow
		self.destroyed = False
		# Translators:  title of go to time dialog.
		title= makeAddonWindowTitle(_("Go to time"))
		super(GoToTimeDialog, self).__init__(parent, ID , title , size = (290, 130))
		self.curTime = curTime
		self.totalTime = totalTime
		self.timer = None
		self.jumpTime = None
		self.doGui()
	
	def doGui(self):
		hoursList, minutesList, secondesList = self.initMaxs(self.curTime[0], self.curTime[1], self.curTime[2])
		mainSizer = wx.GridBagSizer ( 2, 3 )
		#mainSizer = wx.GridBagSizer ( 0, 0 )

		# hours
# Translators: label of hours  combobox of go to time dialog.
		hoursLabel=wx.StaticText(self,-1,label=_("hours:"))
		self.hoursCB = wx.ComboBox(self, -1, self.curTime[0],size = wx.DefaultSize,choices = hoursList[:], style = wx.CB_DROPDOWN, name = "HoursNumber")
		self.hoursCB.SetStringSelection(self.curTime[0])
		hoursSizer=wx.BoxSizer(wx.VERTICAL)
		hoursSizer.Add(hoursLabel)
		hoursSizer.Add(self.hoursCB, flag=wx.LEFT|wx.TOP, border=5)
		mainSizer.Add(hoursSizer, (0,0), (1,1))
		#minutes
		# Translators: minute label of combobox of go to time dialog.
		minutesLabel=wx.StaticText(self,-1,label=_("Minutes:"))
		self.minutesCB = wx.ComboBox(self, -1, self.curTime[1],size = wx.DefaultSize,choices = minutesList[:], style = wx.CB_DROPDOWN, name = "minutesNumber")
		self.minutesCB.SetStringSelection(self.curTime[1])
		minutesSizer=wx.BoxSizer(wx.VERTICAL)
		minutesSizer.Add(minutesLabel)
		minutesSizer.Add(self.minutesCB, flag=wx.LEFT|wx.TOP, border=5)
		mainSizer.Add(minutesSizer, (0,1), (1,1))
		#secondes
		# Translators: second label of combobox of go to time dialog.
		secondesLabel=wx.StaticText(self,-1,label=_("Secondes:"))
		self.secondesCB = wx.ComboBox(self, -1, self.curTime[2],size = wx.DefaultSize,choices = secondesList[:], style = wx.CB_DROPDOWN, name = "secondesNumber")
		self.secondesCB.SetStringSelection(self.curTime[2])
		secondesSizer=wx.BoxSizer(wx.VERTICAL)
		secondesSizer.Add(secondesLabel)
		secondesSizer.Add(self.secondesCB, flag=wx.LEFT|wx.TOP, border=5)
		mainSizer.Add(secondesSizer, (0,2), (1,1))
		# goto button
		# Translators: label of go to button.
		self.goToButton= wx.Button(self,-1,label= _("&Go to time"))
		self.goToButton.Bind(wx.EVT_BUTTON, self.onGoToButton)
		self.goToButton.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		self.goToButton.SetDefault()
		mainSizer.Add ( self.goToButton,  ( 1, 0) ,flag=wx.LEFT|wx.TOP, border=15)
		# Translators: label of cancel button.
		self.cancelButton =  wx.Button(self,-1,label= _("&Cancel"))
		self.cancelButton.Bind(wx.EVT_BUTTON,self.onCancelButton)
		self.cancelButton.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		mainSizer.Add ( self.cancelButton, ( 1, 1),flag=wx.LEFT|wx.TOP, border=15)
		mainSizer.AddGrowableRow(1)
		self.SetSizerAndFit(mainSizer)
		self.hoursCB.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		self.hoursCB.Bind(wx.EVT_TEXT, self.onHoursTextChange)
		self.hoursCB.Bind(wx.EVT_SET_FOCUS, self.onComboBox)
		self.minutesCB.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		self.minutesCB.Bind(wx.EVT_SET_FOCUS, self.onComboBox)
		self.minutesCB.Bind(wx.EVT_TEXT, self.onMinutesTextChange)
		self.secondesCB.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		self.secondesCB.Bind(wx.EVT_SET_FOCUS, self.onComboBox)
		self.secondesCB.Bind(wx.EVT_TEXT, self.onSecondesTextChange)
		self.onComboBox(0)
		self.Bind(wx.EVT_ACTIVATE, self.onActivate)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.SetEscapeId(wx.ID_CLOSE)
	
	def initMaxs(self, curHour, curMinute, curSeconde):
		def maximize(timeList):
			t= timeList[:]
			r= 5
			if int(t[2]) < r:
				t[1] = str(int(t[1])-1)
				t[2] =str(60 - (r - int(t[2])))
			else:
				t[2] = str(int(t[2]) - r)
			return t
		
		nbList = []
		i = 59
		while i >=0:
			nbList.append(str(i))
			i= i-1
		maxTotalTime = maximize(self.totalTime)
		#hours
		max = nbList.index(maxTotalTime[0])
		hoursList = nbList[max:]
		#minutes
		max =  nbList.index(maxTotalTime[1])
		if int(curHour) < int(maxTotalTime[0]
			or int(curSeconde) < int(maxTotalTime[2])):
			max = 0

		minutesList = nbList[max:]
		#secondes
		max =  nbList.index(maxTotalTime[2])
		if (int(curHour) < int(maxTotalTime[0])
			or int(curMinute) < int(maxTotalTime[1])):
			max = 0
		#secondesMax =nbList.index(str(max))
		secondesList = nbList[max:]
		return hoursList, minutesList, secondesList
	
	def setSelection(self, cb, value):
		cb.SetStringSelection(value)
		cb.SetInsertionPointEnd()
		try:
			# for wxPython 4
			cb.SetTextSelection(0,cb.GetLastPosition())
		except:
			# for wxPython 3
			cb.SetMark(0,cb.GetLastPosition())
	
	def textHasChanged(self, cb, curTime):
		waitTime = 800
		if self.timer!= None:
			self.timer.Stop()
			self.timer = None
		text = cb.GetValue()
		valid = True if text in cb.GetStrings() else False
		if valid and len(text) ==1:
			self.timer = wx.CallLater(waitTime,self.setSelection, cb, text)
		elif valid and len(text) == 2:
			self.timer = wx.CallLater(waitTime,self.setSelection, cb, text)
		else:
			self.timer = wx.CallLater(waitTime,self.setSelection, cb, curTime)

	
	def onHoursTextChange(self, evt):
		self.textHasChanged(self.hoursCB, self.curTime[0])
		evt.Skip()
	def onMinutesTextChange(self, evt):
		self.textHasChanged(self.minutesCB, self.curTime[1])
		evt.Skip()
	
	def onSecondesTextChange(self, evt):
		self.textHasChanged(self.secondesCB, self.curTime[2])
		evt.Skip()
	
	def onComboBox(self, evt):
		hoursList, minutesList, secondesList = self.initMaxs(self.hoursCB.GetValue(), self.minutesCB.GetValue(), self.secondesCB.GetValue())
		hour, minute, seconde = self.hoursCB.GetStringSelection(), self.minutesCB.GetStringSelection(), self.secondesCB.GetStringSelection()
		if self.hoursCB.GetItems()[:] != hoursList[:]:
			self.hoursCB.Clear()
			self.hoursCB.SetItems(hoursList)
			hour = hour if hour in hoursList else hoursList[0]
			self.hoursCB.SetStringSelection(hour)
		if self.minutesCB.GetItems()[:] != minutesList[:]:
			self.minutesCB.Clear()
			self.minutesCB.SetItems(minutesList)
			minute = minute if minute in minutesList else minutesList[0]
			self.minutesCB.SetStringSelection(minute)
			
		if self.secondesCB.GetItems()[:] != secondesList[:]:
			self.secondesCB.Clear()
			self.secondesCB.SetItems(secondesList)
			seconde = seconde if seconde in secondesList else secondesList[0]
			self.secondesCB.SetStringSelection(seconde)
		if evt:
			evt.Skip()
	
	def onClose(self, evt):
		self.Destroy()
		self.destroyed = True
		evt.Skip()
	
	def doClose(self):
		self.Close()
	
	def onActivate(self, evt):
		if not self.destroyed and not evt.GetActive():
			self.Close()
		evt.Skip()
	
	def onKeyDown(self, evt):
		key = evt.GetKeyCode()
		if key == wx.WXK_ESCAPE:
			self.doClose()
			return
		evt.Skip()
	
	def onGoToButton(self,event):
		if self.timer:
			self.timer.Notify()
			self.timer.Stop()
			self.timer= None
		self.jumpTime = [self.hoursCB.GetValue(), self.minutesCB.GetValue(), self.secondesCB.GetValue()]
		if self.jumpTime == self.curTime:
			self.jumpTime = None
		
		wx.CallAfter(self.mainWindow.jumpToTime,self.jumpTime, self.totalTime, True)
		self.Close()

	
	def onCancelButton(self, evt):
		self.Close()
		evt.Skip()
	@classmethod
	def run(cls,  curTime, totalTime, obj):
		d = cls(None,wx.ID_ANY, curTime, totalTime, obj)
		d.SetSize((290, 130))
		d.CentreOnScreen()
		d.Show(True)
		PutWindowOnForeground(d.GetHandle(), 5, 0.2)

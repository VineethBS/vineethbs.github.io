#!/usr/bin/python

"""
Thakali Vidya 0.0.2
"""

# imports for gui
import wx
import wx.calendar as wxc
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

# other imports
import pickle
import os
import time

# START : class definitions for the task management system
class Schedule:
    def __init__(self, deadline = 0, schedule = 0, recur = 0, reminder = 0):
	self.deadLine = deadline
	self.schedule = schedule
	self.recur = recur
	self.reminder = reminder

class Task:
    def __init__(self, name, color = "White", priority = 1):
	self.name = name
	self.color = color
	self.priority = priority
	self.schedule = Schedule(deadline = 0, schedule = 0, recur = 0, reminder = 0)
	# saves the list of times when we have worked on this task, a list of (type, start, stop) times in seconds since epoch
	# type indicates whether it is work or break
	self.worktimes = []
	self.completed = False

class ListOfTasks:
    def __init__(self, name, color = 'White'):
	self.name = name
	self.color = color
	self.ListOfTasks = [];

    def addTask(self, name, color, priority, deadline, schedule, recur, reminder):
	self.ListOfTasks.append(Task(name))
	tempIndex = len(self.ListOfTasks) - 1
	self.ListOfTasks[tempIndex].color = color
	self.ListOfTasks[tempIndex].priority = priority
	self.ListOfTasks[tempIndex].schedule.schedule = schedule
	self.ListOfTasks[tempIndex].schedule.deadline = deadline
	self.ListOfTasks[tempIndex].schedule.reminder = reminder
	self.ListOfTasks[tempIndex].schedule.recur = recur

    def editTaskName(self, index, name):
	self.ListOfTasks[index].name = name

    def getTaskName(self, index):
	return self.ListOfTasks[index].name

    def editTaskColor(self, index, color):
	self.ListOfTasks[index].color = color

    def getTaskColor(self, index):
	return self.ListOfTasks[index].color

    def editTaskPriority(self, index, priority):
	self.ListOfTasks[index].priority = priority

    def getTaskPriority(self, index):
	return self.ListOfTasks[index].priority

    def editTaskSchedule(self, index, deadline, schedule, recur, reminder):
	self.ListOfTasks[index].schedule.recur = recur
	self.ListOfTasks[index].schedule.deadline = deadline
	self.ListOfTasks[index].schedule.reminder = reminder
	self.ListOfTasks[index].schedule.schedule = schedule

    def getTaskRecurrence(self, index):
	return self.ListOfTasks[index].schedule.recur

    def getTaskDeadline(self, index):
	return self.ListOfTasks[index].schedule.deadline

    def getTaskReminder(self, index):
	return self.ListOfTasks[index].schedule.reminder

    def getTaskSchedule(self, index):
	return self.ListOfTasks[index].schedule.schedule

    def removeTask(self, index):
	tempList = [];
	for ind, task in enumerate(self.ListOfTasks):
	    if not ind == index:
		tempList.append(task);
	self.ListOfTasks = tempList;

class ListOfListOfTasks:
    def __init__(self):
	self.ListOfListOfTasks = []

    def addListOfTasks(self, name, color):
	self.ListOfListOfTasks.append(ListOfTasks(name, color))

    def getListOfTasksName(self, index):
	return self.ListOfListOfTasks[index].name

    def getListOfTasksColor(self, index):
	return self.ListOfListOfTasks[index].color

    def setListOfTasksName(self, index, name):
	self.ListOfListOfTasks[index].name = name

    def setListOfTasksColor(self, index, color):
	self.ListOfListOfTasks[index].color = color

    def removeListOfTasks(self, index):
	tempList = []
	for ind, listoftasks in enumerate(self.ListOfListOfTasks):
	    if not ind == index:
		tempList.append(listoftasks)
	self.ListOfListOfTasks = tempList
# END : class definitions for the task management system

# START : wxpython GUI class definitions

class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent, dsize):
	wx.ListCtrl.__init__(self, parent, -1, size = dsize, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
	ListCtrlAutoWidthMixin.__init__(self)	
	
class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent, dsize):
        wx.ListCtrl.__init__(self, parent, -1, size = dsize, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

# dialog for list manipulation base class
class ListBase(wx.Dialog):
    global COLORCHOICES
    def __init__(self, parent, titlemessage, dialogsize, listname, listcolour):
	wx.Dialog.__init__(self, parent, id = wx.ID_ANY, title = titlemessage, size = dialogsize)

	# the basic elements for list manipulation
	self.mainpanel = wx.Panel(self, id = wx.ID_ANY)
	self.listnamelabel = wx.StaticText(self.mainpanel, id = wx.ID_ANY, label = "Name :", size = (100, 25))
	self.listcolourlabel = wx.StaticText(self.mainpanel, id = wx.ID_ANY, label = "Colour :", size = (100, 25))
	self.listName = wx.TextCtrl(self.mainpanel, id = wx.ID_ANY, size = (200, 25))
	self.listColour = wx.Choice(self.mainpanel, id = wx.ID_ANY, choices = COLORCHOICES)
	self.Ok = wx.Button(self.mainpanel, id = wx.ID_ANY, label = "Ok")
	self.Cancel = wx.Button(self.mainpanel, id = wx.ID_ANY, label = "Cancel")

	# binding
	self.Bind(wx.EVT_BUTTON, self.onOk, self.Ok)
	self.Bind(wx.EVT_BUTTON, self.onCancel, self.Cancel)

	# layout
	self.mainsizer = wx.BoxSizer(wx.VERTICAL)
	self.namesizer = wx.BoxSizer(wx.HORIZONTAL)
	self.coloursizer = wx.BoxSizer(wx.HORIZONTAL)
	self.buttonsizer = wx.BoxSizer(wx.HORIZONTAL)

	self.mainsizer.Add(self.namesizer, flag = wx.EXPAND)
	self.mainsizer.Add(self.coloursizer, flag = wx.EXPAND)
	self.mainsizer.Add((-1,20))
	self.mainsizer.Add(self.buttonsizer)

	self.mainpanel.SetSizer(self.mainsizer)

	self.namesizer.Add(self.listnamelabel)
	self.namesizer.Add(self.listName, flag = wx.EXPAND)

	self.coloursizer.Add(self.listcolourlabel, flag = wx.ALIGN_CENTER)
	self.coloursizer.Add(self.listColour, flag = wx.ALIGN_CENTER)

	self.buttonsizer.Add((60,-1))
	self.buttonsizer.Add(self.Ok)
	self.buttonsizer.Add(self.Cancel)

    def onOk(self,event):
	self.clickedOk = True
	self.Show(False)

    def onCancel(self,event):
	self.clickedOk = False
	self.Show(False)

# base class for all task manipulation jobs
class TaskBase(wx.Dialog):
    global COLORCHOICES, RECURCHOICES, REMINDERCHOICES

    def __init__(self, parent, titlemessage, dialogsize, task):
	wx.Dialog.__init__(self, parent, id = wx.ID_ANY, title = titlemessage, size = dialogsize)

	# basic elements of task manipulation
	self.mainpanel = wx.Panel(self, id = wx.ID_ANY)
	self.taskname = wx.StaticText(self.mainpanel, id = wx.ID_ANY, label = "Name :", size = (50,25))
	self.taskName = wx.TextCtrl(self.mainpanel, id = wx.ID_ANY, size = (200,25))
	self.taskcolour = wx.StaticText(self.mainpanel, id = wx.ID_ANY, label = "Colour :", size = (50,25))
	self.taskColour = wx.Choice(self.mainpanel, id = wx.ID_ANY, choices = COLORCHOICES, size = (100, 25))
	self.taskpriority = wx.StaticText(self.mainpanel, id = wx.ID_ANY, label = "Priority :", size = (50,25))
	self.taskPriority = wx.SpinCtrl(self.mainpanel, id = wx.ID_ANY, size = (100,25))

	self.deadlineradio = wx.CheckBox(self.mainpanel, id = wx.ID_ANY, label = "Task has deadline ?")
	self.deadlinedate = wxc.CalendarCtrl(self.mainpanel, id = wx.ID_ANY, size = (270, 180))

	self.scheduleradio = wx.CheckBox(self.mainpanel, id = wx.ID_ANY, label = "Task is scheduled ?")
	self.scheduledates = wxc.CalendarCtrl(self.mainpanel, id = wx.ID_ANY, size = (270, 180))
	self.schedulerecurrence = wx.StaticText(self.mainpanel, id = wx.ID_ANY, label = "Recurrence :")
	self.scheduleRecurrence = wx.Choice(self.mainpanel, id = wx.ID_ANY, choices = RECURCHOICES, size = (100,25))
	self.schedulereminder = wx.StaticText(self.mainpanel, id = wx.ID_ANY, label = "Reminder :")
	self.scheduleReminder = wx.Choice(self.mainpanel, id = wx.ID_ANY, choices = REMINDERCHOICES, size = (100,25))

	self.Ok = wx.Button(self.mainpanel, id = wx.ID_ANY, label = "Ok")
	self.Cancel = wx.Button(self.mainpanel, id = wx.ID_ANY, label = "Cancel")

	# layout

	self.mainsizer = wx.BoxSizer(wx.VERTICAL)
	self.namesizer = wx.BoxSizer(wx.HORIZONTAL)
	self.coloursizer = wx.BoxSizer(wx.HORIZONTAL)
	self.prioritysizer = wx.BoxSizer(wx.HORIZONTAL)
	self.deadlinesizer = wx.BoxSizer(wx.HORIZONTAL)
	self.schedulesizer = wx.BoxSizer(wx.VERTICAL)
	self.buttonsizer = wx.BoxSizer(wx.HORIZONTAL)

	self.mainsizer.Add(self.namesizer, flag = wx.EXPAND)
	self.mainsizer.Add(self.coloursizer, flag = wx.EXPAND)
	self.mainsizer.Add(self.prioritysizer, flag = wx.EXPAND)
	self.mainsizer.Add((-1,20))
	self.mainsizer.Add(self.deadlinesizer, flag = wx.EXPAND)
	self.mainsizer.Add(self.schedulesizer, flag = wx.EXPAND)
	self.mainsizer.Add((-1,20))
	self.mainsizer.Add(self.buttonsizer, flag = wx.EXPAND)

	self.mainpanel.SetSizer(self.mainsizer)

	self.namesizer.Add(self.taskname)
	self.namesizer.Add(self.taskName, flag = wx.EXPAND)

	self.coloursizer.Add(self.taskcolour)
	self.coloursizer.Add(self.taskColour, flag = wx.EXPAND)

	self.prioritysizer.Add(self.taskpriority)
	self.prioritysizer.Add(self.taskPriority, flag = wx.EXPAND)

	self.deadlinesizer.Add(self.deadlineradio)
	self.deadlinesizer.Add(self.deadlinedate)

	self.schedulesub1sizer = wx.BoxSizer(wx.HORIZONTAL)
	self.schedulesub2sizer = wx.BoxSizer(wx.HORIZONTAL)
	self.schedulesub3sizer = wx.BoxSizer(wx.HORIZONTAL)

	self.schedulesub1sizer.Add(self.scheduleradio)
	self.schedulesub1sizer.Add(self.scheduledates)
	self.schedulesub2sizer.Add(self.schedulerecurrence)
	self.schedulesub2sizer.Add(self.scheduleRecurrence)
	self.schedulesub3sizer.Add(self.schedulereminder)
	self.schedulesub3sizer.Add(self.scheduleReminder)

	self.schedulesizer.Add(self.schedulesub1sizer)
	self.schedulesizer.Add(self.schedulesub2sizer)
	self.schedulesizer.Add(self.schedulesub3sizer)

	self.buttonsizer.Add(self.Ok)
	self.buttonsizer.Add(self.Cancel)

	# binding
	self.Bind(wx.EVT_BUTTON, self.onOk, self.Ok)
	self.Bind(wx.EVT_BUTTON, self.onCancel, self.Cancel)
	self.Bind(wx.EVT_CHECKBOX, self.onDeadlineCheck, self.deadlineradio)
	self.Bind(wx.EVT_CHECKBOX, self.onScheduleCheck, self.scheduleradio)
		  
    def onDeadlineCheck(self, event):
	if self.deadlineradio.Value == True:
	    self.deadlinedate.Enable()
	else:
	    self.deadlinedate.Disable()

    def onScheduleCheck(self, event):
	if self.scheduleradio.Value == True:
	    self.scheduledates.Enable()
	    self.schedulerecurrence.Enable()
	    self.scheduleRecurrence.Enable()
	    self.schedulereminder.Enable()
	    self.scheduleReminder.Enable()
	else:
	    self.scheduledates.Disable()
	    self.schedulerecurrence.Disable()
	    self.scheduleRecurrence.Disable()
	    self.schedulereminder.Disable()
	    self.scheduleReminder.Disable()
    
    def onOk(self,event):
	self.clickedOk = True
	self.Show(False)

    def onCancel(self,event):
	self.clickedOk = False
	self.Show(False)

# preferences for the timer
class TimerPref(wx.Dialog):
    global WORKTIME, SBTIME, BBTIME
    def __init__(self, parent, titlemessage, dialogsize):
	wx.Dialog.__init__(self, parent, id = wx.ID_ANY, title = titlemessage, size = dialogsize)

	# basic elements
	self.mainpanel = wx.Panel(self, id = wx.ID_ANY)
	self.worktime = wx.StaticText(self.mainpanel, id = wx.ID_ANY, label = "Task duration", pos = (10, 10))
	self.smallbreaktime = wx.StaticText(self.mainpanel, id = wx.ID_ANY, label = "Small break duration", pos = (10, 80))
	self.bigbreaktime = wx.StaticText(self.mainpanel, id = wx.ID_ANY, label = "Big break duration", pos = (10, 140))
	self.Ok = wx.Button(self.mainpanel, id = wx.ID_ANY , label = "Ok", pos = (10, 200))
	self.workTime = wx.Slider(self.mainpanel, id = wx.ID_ANY, value = WORKTIME, minValue = 5, maxValue = 60, pos = (10, 30), size = (250, 35), style = wx.SL_LABELS)
	self.smallbreakTime = wx.Slider(self.mainpanel, id = wx.ID_ANY, value = SBTIME, minValue = 1, maxValue = 15, pos = (10, 100), size = (250,35), style = wx.SL_LABELS)
	self.bigbreakTime = wx.Slider(self.mainpanel, id = wx.ID_ANY, value = BBTIME, minValue = 5, maxValue = 60, pos = (10, 160), size = (250,35), style = wx.SL_LABELS)

	# binding
	self.Bind(wx.EVT_BUTTON, self.onOk, self.Ok)

    def onOk(self, event):
	self.Show(False)

# timer
class TimerDisplay(wx.Dialog):
    def __init__(self, parent, titlemessage, timermax = 25):
	wx.Dialog.__init__(self,parent, id = wx.ID_ANY, title = titlemessage)
		
	self.mainpanel = wx.Panel(self, id = wx.ID_ANY)
	self.gauge = wx.Gauge(self.mainpanel, id = wx.ID_ANY, size = (500, 100))
	self.gauge.SetRange(timermax)
	self.timeremaining = wx.StaticText(self.mainpanel, id = wx.ID_ANY, size = (100, 50))
	self.timeremaining.SetFont(wx.Font(36, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
	self.timer = wx.Timer(self)
	self.Bind(wx.EVT_TIMER, self.updateGauge, self.timer)
	self.Bind(wx.EVT_CLOSE, self.onClose, self)
	self.Show(False)	

    def startTimer(self, timermax):
	global ONEMINUTE
	self.timer.Start(ONEMINUTE)
	self.gauge.SetRange(timermax)
	self.mins = timermax
	self.gauge.SetValue(self.mins)
	self.timeremaining.SetLabel(str(self.mins) + ":00")
		
	if (self.GetParent()).menuDoFullScreen.IsChecked():
	    self.SetSize(wx.DisplaySize())
	    (w,h) = wx.DisplaySize()
	    self.gauge.MoveXY(w/2 - 250, h/2 - 50)
	    self.timeremaining.MoveXY(w/2 - 35, h/2 - 25 + 100)
	    self.mainpanel.SetBackgroundColour("black")
	    self.ShowFullScreen(True, wx.FULLSCREEN_ALL)
	    self.timeremaining.SetForegroundColour("darkgray")
	    self.gauge.SetBackgroundColour("gray")
	else:
	    self.SetSize((500, 400))
	    self.gauge.MoveXY(0, 10)
	    self.timeremaining.MoveXY(250 - 45, 200 - 25 + 50)
	self.ShowModal()
	
    def updateGauge(self, event):
	self.mins = self.mins - 1
	self.gauge.SetValue(self.mins)
	self.timeremaining.SetLabel(str(self.mins) + ":00")
	if self.mins == 0:
	    wx.Sound.PlaySound("good.wav")
	    self.Show(False)
	    self.timer.Stop()
	    
    def onClose(self, event):
	self.timer.Stop()
	self.Show(False)

# task work tracker
class ListWorkTracker(wx.Dialog):
    def __init__(self, parent):
	wx.Dialog.__init__(self, parent, title = "List Time Tracker", size = (670, 300))
	
	self.mainpanel = wx.Panel(self, id = wx.ID_ANY)
	self.mainreport = wx.ListCtrl(self.mainpanel, id = wx.ID_ANY, style = wx.LC_REPORT, size = (670, 300))
	self.mainreport.InsertColumn(0, "Task")
	self.mainreport.InsertColumn(1, "Type")
	self.mainreport.InsertColumn(2, "Start")
	self.mainreport.InsertColumn(3, "End")
	
	self.mainreport.SetColumnWidth(0, 200)
	self.mainreport.SetColumnWidth(1, 50)
	self.mainreport.SetColumnWidth(2, 200)
	self.mainreport.SetColumnWidth(3, 200)
	
    def reportTimes(self, listoftasks):
	self.mainreport.DeleteAllItems()
	tempos = 0
	for task in listoftasks.ListOfTasks:
	    self.mainreport.InsertStringItem(tempos, task.name)
	    tempfirst = 1
	    for worktuple in task.worktimes:
		if not tempfirst == 1:
		    self.mainreport.InsertStringItem(tempos, "")
		
		tempfirst = 0
		self.mainreport.SetStringItem(tempos, 1, str(worktuple[0]))
		self.mainreport.SetStringItem(tempos, 2, time.ctime(worktuple[1]))
		self.mainreport.SetStringItem(tempos, 3, time.ctime(worktuple[2]))
		tempos += 1
	
	self.Center()
	self.Show(True)


class TaskWorkTracker(wx.Dialog):
    def __init__(self, parent):
	wx.Dialog.__init__(self, parent, title = "Task Time Tracker", size = (470, 300))
	
	self.mainpanel = wx.Panel(self, id = wx.ID_ANY)
	self.mainreport = wx.ListCtrl(self.mainpanel, id = wx.ID_ANY, style = wx.LC_REPORT, size = (470, 300))
	self.mainreport.InsertColumn(0, "Type")
	self.mainreport.InsertColumn(1, "Start")
	self.mainreport.InsertColumn(2, "End")
	
	self.mainreport.SetColumnWidth(0, 50)
	self.mainreport.SetColumnWidth(1, 200)
	self.mainreport.SetColumnWidth(2, 200)
	
    def reportTimes(self, task):
	self.mainreport.DeleteAllItems()
	tempos = 0
	for worktuple in task.worktimes:
	    self.mainreport.InsertStringItem(tempos, str(worktuple[0]))
	    self.mainreport.SetStringItem(tempos, 1, time.ctime(worktuple[1]))
	    self.mainreport.SetStringItem(tempos, 2, time.ctime(worktuple[2]))
	    tempos += 1
	
	self.Center()
	self.Show(True)
    
    
# the main frame for our application
class MainFrame(wx.Frame):
    global PROGRAMNAME, PROGRAMVER, FS
    def __init__(self):
	# initialize frame
	wx.Frame.__init__(self, None, id = wx.ID_ANY, title = PROGRAMNAME + " " + PROGRAMVER, size = (700, 610))

	# setup the menu

	# program menu
	self.menuProgram = wx.Menu()
	# items in program menu
	self.menuProgramSave = self.menuProgram.Append(wx.ID_ANY, "&Save")
	self.menuProgramSaveas = self.menuProgram.Append(wx.ID_ANY, "Save as")
	self.menuProgramLoad = self.menuProgram.Append(wx.ID_ANY,"&Load")
	self.menuProgram.AppendSeparator()
	self.menuProgramExit = self.menuProgram.Append(wx.ID_EXIT,"E&xit")
	# binding menu items
	self.Bind(wx.EVT_MENU, self.onSave, self.menuProgramSave)
	self.Bind(wx.EVT_MENU, self.onSaveas, self.menuProgramSaveas)
	self.Bind(wx.EVT_MENU, self.onLoad, self.menuProgramLoad)
	self.Bind(wx.EVT_MENU, self.onExit, self.menuProgramExit)
	
	# Import menu
	self.menuImport = wx.Menu()
	self.menuImportNew = self.menuImport.Append(wx.ID_ANY, "Import as New")
	self.menuImportAppend = self.menuImport.Append(wx.ID_ANY, "Import and Append")
	# binding
	self.Bind(wx.EVT_MENU, self.onImportNew, self.menuImportNew)
	self.Bind(wx.EVT_MENU, self.onImportAppend, self.menuImportAppend)
	
	# List menu
	self.menuList = wx.Menu()
	# items in the Task menu
	self.menuListNew = self.menuList.Append(wx.ID_ANY, "New List")
	self.menuListEdit = self.menuList.Append(wx.ID_ANY, "Edit List")
	self.menuListDelete = self.menuList.Append(wx.ID_ANY, "Delete List")
	self.menuList.AppendSeparator()
	self.menuListTrack = self.menuList.Append(wx.ID_ANY,"Track List")
	# binding list items
	self.Bind(wx.EVT_MENU, self.onNewList, self.menuListNew)
	self.Bind(wx.EVT_MENU, self.onEditList, self.menuListEdit)
	self.Bind(wx.EVT_MENU, self.onDeleteList, self.menuListDelete)
	self.Bind(wx.EVT_MENU, self.onTrackList, self.menuListTrack)

	# Task menu
	self.menuTask = wx.Menu()
	# items in the list menu
	self.menuTaskView = self.menuTask.Append(wx.ID_ANY,"View Task")
	self.menuTaskNew = self.menuTask.Append(wx.ID_ANY, "New Task")
	self.menuTaskEdit = self.menuTask.Append(wx.ID_ANY, "Edit Task")
	self.menuTaskDelete = self.menuTask.Append(wx.ID_ANY, "Delete Task")
	self.menuTaskCopy = self.menuTask.Append(wx.ID_ANY, "Copy Task")
	self.menuTaskPaste = self.menuTask.Append(wx.ID_ANY, "Paste Task")
	self.menuTask.AppendSeparator()
	self.menuTaskTrack = self.menuTask.Append(wx.ID_ANY,"Track Task")
	# binding list items
	self.Bind(wx.EVT_MENU, self.onViewTask, self.menuTaskView)
	self.Bind(wx.EVT_MENU, self.onNewTask, self.menuTaskNew)
	self.Bind(wx.EVT_MENU, self.onEditTask, self.menuTaskEdit)
	self.Bind(wx.EVT_MENU, self.onDeleteTask, self.menuTaskDelete)
	self.Bind(wx.EVT_MENU, self.onCopyTask, self.menuTaskCopy)
	self.Bind(wx.EVT_MENU, self.onPasteTask, self.menuTaskPaste)
	self.Bind(wx.EVT_MENU, self.onTrackTask, self.menuTaskTrack)

	# Do menu
	self.menuDo = wx.Menu()
	# items in the Do menu
	self.menuDoStartW = self.menuDo.Append(wx.ID_ANY,"Start Work")
	self.menuDoStartSB = self.menuDo.Append(wx.ID_ANY,"Start Small Break")
	self.menuDoStartBB = self.menuDo.Append(wx.ID_ANY,"Start Big Break")
	self.menuDo.AppendSeparator()
	self.menuDoPref = self.menuDo.Append(wx.ID_ANY,"Preferences")
	self.menuDoFullScreen = self.menuDo.Append(wx.ID_ANY,"Full screen timer", kind = wx.ITEM_CHECK)
	self.menuDoFullScreen.Check(FS)
	
	# binding
	self.Bind(wx.EVT_MENU, self.onStartW, self.menuDoStartW)
	self.Bind(wx.EVT_MENU, self.onStartSB, self.menuDoStartSB)
	self.Bind(wx.EVT_MENU, self.onStartBB, self.menuDoStartBB)
	self.Bind(wx.EVT_MENU, self.onPref, self.menuDoPref)

	# Help menu
	self.menuHelp = wx.Menu()
	# items
	self.menuHelpAbout = self.menuHelp.Append(wx.ID_ABOUT, "About Thakali Vidya")
	# binding
	self.Bind(wx.EVT_MENU, self.onAbout, self.menuHelpAbout)

	# now setup the menubar
	self.menuBar = wx.MenuBar()
	self.menuBar.Append(self.menuProgram, "Program")
	self.menuBar.Append(self.menuImport, "Import")
	self.menuBar.Append(self.menuList, "List")
	self.menuBar.Append(self.menuTask, "Task")
	self.menuBar.Append(self.menuDo, "Do")
	self.menuBar.Append(self.menuHelp, "Help")
	self.SetMenuBar(self.menuBar)

	# the toolbar
	self.toolBar = wx.ToolBar(self, style=wx.TB_HORIZONTAL|wx.TB_3DBUTTONS|wx.TB_TEXT|wx.TB_NOICONS|wx.TB_HORZ_LAYOUT|wx.TB_HORZ_TEXT)
	self.SetToolBar(self.toolBar);
	# add elements to the toolbar
	self.toolBarSave = self.toolBar.AddLabelTool(wx.ID_ANY, "Save", wx.NullBitmap)
	self.toolBarLoad = self.toolBar.AddLabelTool(wx.ID_ANY, "Load", wx.NullBitmap)
	self.toolBar.AddSeparator()
	self.toolBarAddList = self.toolBar.AddLabelTool(wx.ID_ANY, "NL", wx.NullBitmap)
	self.toolBarEditList = self.toolBar.AddLabelTool(wx.ID_ANY, "EL", wx.NullBitmap)
	self.toolBarDeleteList = self.toolBar.AddLabelTool(wx.ID_ANY, "DL", wx.NullBitmap)
	self.toolBar.AddSeparator()
	self.toolBarViewTask = self.toolBar.AddLabelTool(wx.ID_ANY, "V", wx.NullBitmap)
	self.toolBarNewTask = self.toolBar.AddLabelTool(wx.ID_ANY, "N", wx.NullBitmap)
	self.toolBarEditTask = self.toolBar.AddLabelTool(wx.ID_ANY, "E", wx.NullBitmap)
	self.toolBarDeleteTask = self.toolBar.AddLabelTool(wx.ID_ANY, "D", wx.NullBitmap)
	self.toolBarCopyTask = self.toolBar.AddLabelTool(wx.ID_ANY, "C", wx.NullBitmap)
	self.toolBarPasteTask = self.toolBar.AddLabelTool(wx.ID_ANY, "P", wx.NullBitmap)
	self.toolBar.AddSeparator()
	self.toolBarStartW = self.toolBar.AddLabelTool(wx.ID_ANY, "SW", wx.NullBitmap)
	self.toolBarStartSB = self.toolBar.AddLabelTool(wx.ID_ANY, "SSB", wx.NullBitmap)
	self.toolBarStartBB = self.toolBar.AddLabelTool(wx.ID_ANY, "SBB", wx.NullBitmap)
	# binding
	self.Bind(wx.EVT_TOOL, self.onSave, self.toolBarSave)
	self.Bind(wx.EVT_TOOL, self.onLoad, self.toolBarLoad)
	self.Bind(wx.EVT_TOOL, self.onNewList, self.toolBarAddList)
	self.Bind(wx.EVT_TOOL, self.onEditList, self.toolBarEditList)
	self.Bind(wx.EVT_TOOL, self.onDeleteList, self.toolBarDeleteList)
	self.Bind(wx.EVT_TOOL, self.onViewTask, self.toolBarViewTask)
	self.Bind(wx.EVT_TOOL, self.onNewTask, self.toolBarNewTask)
	self.Bind(wx.EVT_TOOL, self.onEditTask, self.toolBarEditTask)
	self.Bind(wx.EVT_TOOL, self.onDeleteTask, self.toolBarDeleteTask)
	self.Bind(wx.EVT_TOOL, self.onCopyTask, self.toolBarCopyTask)
	self.Bind(wx.EVT_TOOL, self.onPasteTask, self.toolBarPasteTask)
	self.Bind(wx.EVT_TOOL, self.onStartW, self.toolBarStartW)
	self.Bind(wx.EVT_TOOL, self.onStartSB, self.toolBarStartSB)
	self.Bind(wx.EVT_TOOL, self.onStartBB, self.toolBarStartBB)
	
	# show the toolbar
	self.toolBar.Realize()

	# setup a panel
	self.mainpanel = wx.Panel(self, id = wx.ID_ANY)

	# setup the two list controls for goal list and task list
	self.goalList = AutoWidthListCtrl(self.mainpanel, dsize = (250, 500))
	self.taskList = CheckListCtrl(self.mainpanel, dsize = (250, 500))
	
	self.goalList.InsertColumn(0, "List", width = 300)
	
	self.taskList.InsertColumn(0, "Task", width = 250)
	self.taskList.InsertColumn(1, "Priority", width = 20)
	
	# binding
	self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onGoalListSelect, self.goalList)
	self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onGoalListSelect, self.goalList)
	
	self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onTaskStartWork, self.taskList)

	# setup the textbox for entering commands
	self.commandText = wx.StaticText(self.mainpanel, id = wx.ID_ANY, label = "Command :")
	self.commandBox = wx.TextCtrl(self.mainpanel, id = wx.ID_ANY, size = (300,25), style = wx.TE_PROCESS_ENTER)
	# binding for the commandbox
	self.Bind(wx.EVT_TEXT_ENTER, self.onCommandEnter, self.commandBox)

	# sizers for layout
	self.mainsizer = wx.BoxSizer(wx.VERTICAL)
	self.listsizer = wx.BoxSizer(wx.HORIZONTAL)
	self.commandsizer = wx.BoxSizer(wx.HORIZONTAL)

	self.mainsizer.Add(self.listsizer, flag = wx.EXPAND)
	self.mainsizer.Add(self.commandsizer, flag = wx.EXPAND)
	self.mainpanel.SetSizer(self.mainsizer)

	self.listsizer.Add(self.goalList, flag = wx.EXPAND, proportion = 1)
	self.listsizer.Add(self.taskList, flag = wx.EXPAND, proportion = 1)
	self.commandsizer.Add(self.commandText, flag = wx.ALIGN_CENTER)
	self.commandsizer.Add(self.commandBox, proportion = 1, flag = wx.EXPAND)

	# a status bar
	self.CreateStatusBar()
	
	# window close
	self.Bind(wx.EVT_CLOSE, self.onExit, self)

	# now create the other dialogs

	self.NewListDialog = ListBase(self, "Add new list", (300,150), "", "")
	self.EditListDialog = ListBase(self, "Edit list", (300,150), "", "")

	self.ViewTaskDialog = TaskBase(self, "View task", (480, 570), "")
	self.NewTaskDialog = TaskBase(self, "Add new task", (480, 570), "")
	self.EditTaskDialog = TaskBase(self, "Edit task", (480, 570), "")

	self.TimerPrefDialog = TimerPref(self, "Edit timer preferences", (300, 250))
	
	self.TaskTimer = TimerDisplay(self, "Task Timer")
	self.SmallBreakTimer = TimerDisplay(self, "Small Break Timer")
	self.BigBreakTimer = TimerDisplay(self,"Big Break Timer")
	
	self.TaskTracker = TaskWorkTracker(self)
	self.ListTracker = ListWorkTracker(self)

	# Finally show the frame
	self.Show(True)


    # handlers
    def onImportNew(self, event):
	global goalList
	
	dlg = wx.FileDialog(self, "Import as New", "", "", "*.otl", wx.OPEN)
	if dlg.ShowModal() == wx.ID_OK:
	    # note that once the file has been loaded it becomes the savefile
	    tempfilename = dlg.GetFilename()
	    tempdir = dlg.GetDirectory()
	    temppath = os.path.join(tempdir, tempfilename)
	    tempfile = open(temppath, "r")
	    importdata = tempfile.readlines()
	    tempfile.close()
	    
	    goalList = 0
	    goalList = ListOfListOfTasks()
	    
	    currentlistoftasks = 0
	    currentlistindex = len(goalList.ListOfListOfTasks)
	    for textline in importdata:
		textline = textline.replace("\n","")
		if not textline == "":
		    if not list(textline)[0] == '\t':
			goalList.addListOfTasks(textline, "White")
			currentlistoftasks = goalList.ListOfListOfTasks[currentlistindex]
			currentlistindex += 1
		    else:
			textline = textline[1:len(textline)]
			currentlistoftasks.addTask(textline, "White", 0, 0, 0, 0, 0)
	    self.refreshLists()	    
    
    def onImportAppend(self, event):
	global goalList
	dlg = wx.FileDialog(self, "Import as New", "", "", "*.otl", wx.OPEN)
	if dlg.ShowModal() == wx.ID_OK:
	    # note that once the file has been loaded it becomes the savefile
	    tempfilename = dlg.GetFilename()
	    tempdir = dlg.GetDirectory()
	    temppath = os.path.join(tempdir, tempfilename)
	    tempfile = open(temppath, "r")
	    importdata = tempfile.readlines()
	    tempfile.close()
	    
	    currentlistoftasks = 0
	    currentlistindex = len(goalList.ListOfListOfTasks)
	    for textline in importdata:
		textline = textline.replace("\n","")
		if not textline == "":
		    if not list(textline)[0] == '\t':
			goalList.addListOfTasks(textline, "White")
			currentlistoftasks = goalList.ListOfListOfTasks[currentlistindex]
			currentlistindex += 1
		    else:
			textline = textline[1:len(textline)]
			currentlistoftasks.addTask(textline, "White", 0, 0, 0, 0, 0)
	    self.refreshLists()
					
	
    def onTaskStartWork(self, event):
	global DUMMY
	self.onStartW(DUMMY)
    
    def getselections(self, listctrlobj):
	tempselection = listctrlobj.GetNextSelected(-1)
	tempname = listctrlobj.GetItem(tempselection, 0).GetText()
	return [tempselection, tempname]
    
    def onGoalListSelect(self, event):
	[tempselection, tempname] = self.getselections(self.goalList)
	# get all the list names from the goalList
	listofnames = [goalList.ListOfListOfTasks[i].name for i in range(0,len(goalList.ListOfListOfTasks))]
	# find out the actual index in the goalList
	tempindex = listofnames.index(tempname)
	
	self.taskList.DeleteAllItems()
	
	# now update the list of tasks
	if not len(goalList.ListOfListOfTasks[tempindex].ListOfTasks) == 0:
	    tempnamelist = [goalList.ListOfListOfTasks[tempindex].ListOfTasks[i].name for i in range(0, len(goalList.ListOfListOfTasks[tempindex].ListOfTasks))]
	    tempprioritylist = [goalList.ListOfListOfTasks[tempindex].ListOfTasks[i].priority for i in range(0, len(goalList.ListOfListOfTasks[tempindex].ListOfTasks))]
	    tempcolorlist = [goalList.ListOfListOfTasks[tempindex].ListOfTasks[i].color for i in range(0, len(goalList.ListOfListOfTasks[tempindex].ListOfTasks))]
	    for i in range(0, len(tempnamelist)):
		self.taskList.InsertStringItem(i, tempnamelist[i])
		self.taskList.SetStringItem(i, 1, str(tempprioritylist[i]))
		self.taskList.SetItemBackgroundColour(i, tempcolorlist[i])
		
    def onCommandEnter(self, event):
	global DUMMY
	command = self.commandBox.GetValue()
	self.commandBox.SetValue("")
	command = command.replace("\n","").strip()

	if command == "save" or command == "Save" or command == "s":
	    self.onSave(DUMMY)
	elif command == "load" or command == "Load" or command == "l":
	    self.onLoad(DUMMY)
	elif command == "exit" or command == "Exit":
	    self.onExit(DUMMY)
	elif command == "nl":
	    self.onNewList(DUMMY)
	elif command == "el":
	    self.onEditList(DUMMY)
	elif command == "dl":
	    self.onDeleteList(DUMMY)
	elif command == "v":
	    self.onViewTask(DUMMY)
	elif command == "n":
	    self.onNewTask(DUMMY)
	elif command == "e":
	    self.onEditTask(DUMMY)
	elif command == "d":
	    self.onDeleteTask(DUMMY)
	elif command == "c":
	    self.onCopyTask(DUMMY)
	elif command == "p":
	    self.onPasteTask(DUMMY)
	elif command == "sw":
	    self.onStartW(DUMMY)
	elif command == "ssb":
	    self.onStartSB(DUMMY)
	elif command == "sbb":
	    self.onStartBB(DUMMY)
	else:
	    # if we have not found a valid command - show our indignance
	    self.commandBox.SetBackgroundColour("Pink")

    def onSave(self,event):
	global goalList, SAVEDIR, SAVEFILENAME, SAVEFILENAMESET_FLAG
	# note that we only ask if the filename has not been set
	if SAVEFILENAMESET_FLAG == 0:
	    dlg = wx.FileDialog(self, "Choose a save file", "", SAVEFILENAME, "*.pickle", wx.SAVE)
	    if dlg.ShowModal() == wx.ID_OK:
		SAVEFILENAMESET_FLAG = 1;
		SAVEFILENAME = dlg.GetFilename()
		SAVEDIR = dlg.GetDirectory()
		dlg.Destroy()
		
	if SAVEFILENAMESET_FLAG == 1:
	    temppath = os.path.join(SAVEDIR, SAVEFILENAME)
	    tempfile = open(temppath, "wb")
	    pickle.dump(goalList, tempfile)
	    tempfile.close()

    def onSaveas(self,event):
	global goalList, SAVEDIR, SAVEFILENAME, SAVEFILENAMESET_FLAG
	dlg = wx.FileDialog(self, "Choose a save file", "", SAVEFILENAME, "*.pickle", wx.SAVE)
	if dlg.ShowModal() == wx.ID_OK:
	    SAVEFILENAMESET_FLAG = 1;
	    SAVEFILENAME = dlg.GetFilename()
	    SAVEDIR = dlg.GetDirectory()
	    temppath = os.path.join(SAVEDIR, SAVEFILENAME)
	    tempfile = open(temppath, "wb")
	    pickle.dump(goalList, tempfile)
	    tempfile.close()
	dlg.Destroy()

    def onLoad(self, event):
	global goalList, SAVEDIR, SAVEFILENAME, SAVEFILENAMESET_FLAG
	dlg = wx.FileDialog(self, "Load", "", "", "*.pickle", wx.OPEN)
	if dlg.ShowModal() == wx.ID_OK:
	    # note that once the file has been loaded it becomes the savefile
	    SAVEFILENAMESET_FLAG = 1;	    
	    SAVEFILENAME = dlg.GetFilename()
	    SAVEDIR = dlg.GetDirectory()
	    temppath = os.path.join(SAVEDIR, SAVEFILENAME)
	    tempfile = open(temppath, "rb")
	    goalList = pickle.load(tempfile)
	    tempfile.close()
	dlg.Destroy()
	self.refreshLists()
	
    def refreshLists(self):
	self.goalList.DeleteAllItems()
	self.taskList.DeleteAllItems()
	
	if not len(goalList.ListOfListOfTasks) == 0:
	    for listind, tasklist in enumerate(goalList.ListOfListOfTasks):
		self.goalList.InsertStringItem(listind, tasklist.name)
		self.goalList.SetItemBackgroundColour(listind, tasklist.color)
	    # only update the task list for the last list loaded
	    if not len(tasklist.ListOfTasks) == 0:
		for taskind, task in enumerate(tasklist.ListOfTasks):
		    self.taskList.InsertStringItem(taskind, task.name)
		    self.taskList.SetStringItem(taskind, 1, str(task.priority))
		    self.taskList.SetItemBackgroundColour(taskind, task.color)
	
    def onExit(self,event):
	# will save preferences here
	tempfile = open(DEFAULTPREFFILE, "w")
	tempfile.write(str(self.TimerPrefDialog.workTime.Value) + "\n")
	tempfile.write(str(self.TimerPrefDialog.smallbreakTime.Value) + "\n")
	tempfile.write(str(self.TimerPrefDialog.bigbreakTime.Value) + "\n")
	tempfile.write(str(self.menuDoFullScreen.IsChecked()) + "\n")
	tempfile.close()
	self.Destroy()

    def findgoalListSelection(self):
	[tempselection, tempname] = self.getselections(self.goalList)
	if not tempselection == -1:
	    # get all the list names from the goalList
	    listofnames = [goalList.ListOfListOfTasks[i].name for i in range(0,len(goalList.ListOfListOfTasks))]
	    # find out the actual index in the goalList
	    tempindex = listofnames.index(tempname)
	    return [tempselection, tempname, listofnames, tempindex]
	else:
	    return [-1, -1, -1, -1]
	    
    def findtaskListSelection(self, tempindex):
	[temptaskselection, temptaskname] = self.getselections(self.taskList) # a task also has to be selected
	if not temptaskselection == -1:
	    # get all the tasks from the tasklist
	    listoftasknames = [goalList.ListOfListOfTasks[tempindex].ListOfTasks[i].name for i in range(0, len(goalList.ListOfListOfTasks[tempindex].ListOfTasks))]
	    # find out the actual index of the task
	    temptaskindex = listoftasknames.index(temptaskname)
	    return [temptaskselection, temptaskname, listoftasknames, temptaskindex]
	else:
	    return [-1,-1,-1,-1]
    
    def onNewList(self,event):
	self.NewListDialog.listName.Value = ""
	self.NewListDialog.ShowModal()
	if self.NewListDialog.clickedOk:
	    # get the values from the dialog
	    tempname = self.NewListDialog.listName.Value
	    if not tempname.strip() == "":
		tempcolor = self.NewListDialog.listColour.Selection
		tempcolor = COLORCHOICES[tempcolor]
		# add to internal data structure
		goalList.addListOfTasks(tempname, tempcolor)
		# add to guilist
		tempind = self.goalList.GetItemCount()
		self.goalList.InsertStringItem(tempind, tempname)
		self.goalList.SetItemBackgroundColour(tempind, tempcolor)
		
    def onEditList(self,event):
	[tempselection, tempname, listofnames, tempindex] = self.findgoalListSelection()
	if not tempselection == -1:
	    # set the initial values in the dialog
	    self.EditListDialog.listName.Value = tempname
	    self.EditListDialog.listColour.Selection = COLORCHOICES.index(goalList.ListOfListOfTasks[tempindex].color)
	    self.EditListDialog.ShowModal()
	    # now set the new values
	    if self.EditListDialog.clickedOk:
		goalList.ListOfListOfTasks[tempindex].name = self.EditListDialog.listName.Value
		tempcolor = self.EditListDialog.listColour.Selection
		tempcolor = COLORCHOICES[tempcolor]
		goalList.ListOfListOfTasks[tempindex].color = tempcolor
		self.goalList.SetStringItem(tempselection, 0, self.EditListDialog.listName.Value)
		self.goalList.SetItemBackgroundColour(tempselection, COLORCHOICES[self.EditListDialog.listColour.Selection])
		
    def onDeleteList(self,event):
	[tempselection, tempname, listofnames, tempindex] = self.findgoalListSelection()
	if not tempselection == -1:
	    # delete from goal list
	    goalList.removeListOfTasks(tempindex)
	    # delete from the gui
	    self.goalList.DeleteItem(tempselection)
	    # also delete the corresponding task from the gui
	    self.taskList.DeleteAllItems()
		
    def onTrackList(self,event):
	[tempselection, tempname, listofnames, tempindex] = self.findgoalListSelection()
	if not tempselection == -1:
	    currentList = goalList.ListOfListOfTasks[tempindex]
	    self.ListTracker.reportTimes(currentList)	
	    
    def onViewTask(self,event):
	[tempselection, tempname, listofnames, tempindex] = self.findgoalListSelection()
	if not tempselection == -1:
	    [temptaskselection, temptaskname, listoftasknames, temptaskindex] = self.findtaskListSelection(tempindex)
	    if not temptaskselection == -1:
		currentTask = goalList.ListOfListOfTasks[tempindex].ListOfTasks[temptaskindex]
		self.ViewTaskDialog.taskName.Value = currentTask.name
		self.ViewTaskDialog.taskColour.Selection = COLORCHOICES.index(currentTask.color)
		self.ViewTaskDialog.taskPriority.Value = currentTask.priority
		if currentTask.schedule.deadline == 0:
		    self.ViewTaskDialog.deadlineradio.Value = False
		else:
		    self.ViewTaskDialog.deadlineradio.Value = True
		if currentTask.schedule.schedule == 0:
		    self.ViewTaskDialog.scheduleradio.Value = False
		else:
		    self.ViewTaskDialog.scheduleradio.Value = True
		    
		self.ViewTaskDialog.ShowModal()

    def onNewTask(self,event):
	[tempselection, tempname, listofnames, tempindex] = self.findgoalListSelection()
	if not tempselection == -1:	
	    # make sure that the deadline, schedule, reminder and recur controls are properly enabled or disabled
	    self.NewTaskDialog.deadlineradio.Value = False
	    self.NewTaskDialog.scheduleradio.Value = False
	    self.NewTaskDialog.deadlinedate.Disable()
	    self.NewTaskDialog.scheduledates.Disable()
	    self.NewTaskDialog.schedulerecurrence.Disable()
	    self.NewTaskDialog.scheduleRecurrence.Disable()
	    self.NewTaskDialog.schedulereminder.Disable()
	    self.NewTaskDialog.scheduleReminder.Disable()
	    
	    self.NewTaskDialog.ShowModal()
	    
	    if self.NewTaskDialog.clickedOk:
		temptaskname = self.NewTaskDialog.taskName.Value
		if not tempname.strip() == "":
		    tempcolor = self.NewTaskDialog.taskColour.Selection
		    tempcolor = COLORCHOICES[tempcolor]
		    temppriority = self.NewTaskDialog.taskPriority.GetValue()
		    
		    if self.NewTaskDialog.deadlineradio.Value == False:
			tempdeadline = 0
		    else:
			tempdeadline = 1
		    
		    if self.NewTaskDialog.scheduleradio.Value == False:
			tempschedule = 0
		    else:
			tempschedule = 1
		    
		    # now add the task to the list
		    goalList.ListOfListOfTasks[tempindex].addTask(temptaskname, tempcolor, temppriority, tempdeadline, tempschedule, 0, 0)
		    
		    # add to the the gui
		    tempind = self.taskList.GetItemCount()
		    self.taskList.InsertStringItem(tempind, temptaskname)
		    self.taskList.SetStringItem(tempind, 1, str(temppriority))
		    self.taskList.SetItemBackgroundColour(tempind, tempcolor)

    def onEditTask(self,event):
	[tempselection, tempname, listofnames, tempindex] = self.findgoalListSelection()
	if not tempselection == -1:
	    [temptaskselection, temptaskname, listoftasknames, temptaskindex] = self.findtaskListSelection(tempindex)
	    if not temptaskselection == -1:	    
		# now set the values in the EditTaskDialog
		currentTask = goalList.ListOfListOfTasks[tempindex].ListOfTasks[temptaskindex]
		self.EditTaskDialog.taskName.Value = currentTask.name
		self.EditTaskDialog.taskColour.Selection = COLORCHOICES.index(currentTask.color)
		self.EditTaskDialog.taskPriority.Value = currentTask.priority
		if currentTask.schedule.deadline == 0:
		    self.EditTaskDialog.deadlineradio.Value = False
		else:
		    self.EditTaskDialog.deadlineradio.Value = True
		    
		if currentTask.schedule.schedule == 0:
		    self.EditTaskDialog.scheduleradio.Value = False
		else:
		    self.EditTaskDialog.scheduleradio.Value = True
		
		self.EditTaskDialog.ShowModal()
		
		if self.EditTaskDialog.clickedOk:
		    temptaskname = self.EditTaskDialog.taskName.Value
		    if not temptaskname.strip() == "":
		        tempcolor = self.EditTaskDialog.taskColour.Selection
		        tempcolor = COLORCHOICES[tempcolor]
		        temppriority = self.EditTaskDialog.taskPriority.GetValue()
			
			if self.EditTaskDialog.deadlineradio.Value == False:
			    tempdeadline = 0
			else:
			    tempdeadline = 1
			    
			if self.EditTaskDialog.scheduleradio.Value == False:
			    tempschedule = 0
			else:
			    tempschedule = 1
			    
			currentTask.name = temptaskname
			currentTask.color = tempcolor
			currentTask.priority = temppriority
			
			# edit internal structure
			goalList.ListOfListOfTasks[tempindex].editTaskSchedule(temptaskindex, tempdeadline, tempschedule, 0, 0)
			
			# change gui name
			self.taskList.SetStringItem(temptaskselection, 0, temptaskname)
			self.taskList.SetStringItem(temptaskselection, 1, str(temppriority))
			self.taskList.SetItemBackgroundColour(temptaskselection, tempcolor)
    	
    def onDeleteTask(self,event):
	# a list has to be selected first
	[tempselection, tempname, listofnames, tempindex] = self.findgoalListSelection()
	if not tempselection == -1:
	    [temptaskselection, temptaskname, listoftasknames, temptaskindex] = self.findtaskListSelection(tempindex)
	    if not temptaskselection == -1:
		# remove from the internal data structure
		goalList.ListOfListOfTasks[tempindex].removeTask(temptaskindex)
		# remove from the gui
		self.taskList.DeleteItem(temptaskselection)
	
    def onCopyTask(self,event):
	global COPYFLAG, COPYTASK
	[tempselection, tempname, listofnames, tempindex] = self.findgoalListSelection()
	if not tempselection == -1:
	    [temptaskselection, temptaskname, listoftasknames, temptaskindex] = self.findtaskListSelection(tempindex)
	    if not temptaskselection == -1:
		COPYFLAG = 1
		COPYTASK = goalList.ListOfListOfTasks[tempindex].ListOfTasks[temptaskindex]
	    
    def onPasteTask(self,event):
	global COPYFLAG, COPYTASK
	if COPYFLAG == 1:
	    [tempselection, tempname, listofnames, tempindex] = self.findgoalListSelection()
	    if not tempselection == -1:
		goalList.ListOfListOfTasks[tempindex].addTask(COPYTASK.name, COPYTASK.color, COPYTASK.priority, COPYTASK.schedule.deadline, COPYTASK.schedule.schedule, COPYTASK.schedule.reminder, COPYTASK.schedule.recur)
		tempind = self.taskList.GetItemCount()
		self.taskList.InsertStringItem(tempind, COPYTASK.name)
		self.taskList.SetStringItem(tempind, 1, COPYTASK.priority)
		self.taskList.SetItemBackgroundColour(tempind, COPYTASK.color)
					    
    def onTrackTask(self,event):
	[tempselection, tempname, listofnames, tempindex] = self.findgoalListSelection()
	if not tempselection == -1:
	    [temptaskselection, temptaskname, listoftasknames, temptaskindex] = self.findtaskListSelection(tempindex)
	    if not temptaskselection == -1:
		currentTask = goalList.ListOfListOfTasks[tempindex].ListOfTasks[temptaskindex]
		self.TaskTracker.reportTimes(currentTask)	
    
    def onStartW(self,event):
	[tempselection, tempname, listofnames, tempindex] = self.findgoalListSelection()
	if not tempselection == -1:
	    [temptaskselection, temptaskname, listoftasknames, temptaskindex] = self.findtaskListSelection(tempindex)
	    if not temptaskselection == -1:
		tempstart = time.time()
		self.TaskTimer.startTimer(self.TimerPrefDialog.workTime.Value)
		tempstop = time.time()
		goalList.ListOfListOfTasks[tempindex].ListOfTasks[temptaskindex].worktimes.append(["w", tempstart, tempstop])
    
    def onStartSB(self,event):
	[tempselection, tempname, listofnames, tempindex] = self.findgoalListSelection()
	if not tempselection == -1:
	    [temptaskselection, temptaskname, listoftasknames, temptaskindex] = self.findtaskListSelection(tempindex)
	    if not temptaskselection == -1:
		tempstart = time.time()
		self.SmallBreakTimer.startTimer(self.TimerPrefDialog.smallbreakTime.Value)
		tempstop = time.time()
		goalList.ListOfListOfTasks[tempindex].ListOfTasks[temptaskindex].worktimes.append(["b", tempstart, tempstop])
    
    def onStartBB(self,event):
	[tempselection, tempname, listofnames, tempindex] = self.findgoalListSelection()
	if not tempselection == -1:
	    [temptaskselection, temptaskname, listoftasknames, temptaskindex] = self.findtaskListSelection(tempindex)
	    if not temptaskselection == -1:
		tempstart = time.time()
		self.BigBreakTimer.startTimer(self.TimerPrefDialog.bigbreakTime.Value)
		tempstop = time.time()
		goalList.ListOfListOfTasks[tempindex].ListOfTasks[temptaskindex].worktimes.append(["b", tempstart, tempstop])		
	    
    def onPref(self,event):
	self.TimerPrefDialog.ShowModal()

    def onAbout(self, event):
	dlg = wx.MessageDialog(self, "A task manager with time boxing, version 0.0.1", "About Thakali Vidya", wx.OK)
	dlg.ShowModal()
	dlg.Destroy()

# END : wxpython GUI class definitions

# START : Global variables and settings

PROGRAMNAME = "Thakali Vidya"
PROGRAMVER = "0.0.1"
DUMMY = 0;
COLORCHOICES = ["White", "Lightgray", "Lightblue", "Lightgreen", "Lightyellow", "Gray",  "Blue", "Pink", "Red", "Green", "Yellow"]
RECURCHOICES = ["None", "Daily", "Weekly", "Fortnightly", "Monthly", "Yearly"]
REMINDERCHOICES = ["None", "1 min", "5 mins", "10 mins", "15 mins", "20 mins", "25 mins", "30 mins", "1 hr"]

TIMETEMPLATE = ['year','month','date','hour','min'];

SAVEDIR = "."
SAVEFILENAME = "goals.pickle"
SAVEFILENAMESET_FLAG = 0

COPYFLAG = 0
COPYTASK = 0

DEFAULTPREFFILE = "tvidyapref"

ONEMINUTE = 60 * 1000 # in milliseconds

# END : Global variables and settings

goalList = ListOfListOfTasks()

app = wx.App()

# getting user preferences
userpref = open(DEFAULTPREFFILE, "r").readlines()
userpref = [u.replace("\n","") for u in userpref]
WORKTIME = int(userpref[0])
SBTIME = int(userpref[1])
BBTIME = int(userpref[2])
if userpref[3] == "False":
    FS = False
else:
    FS = True
    
mainframe = MainFrame()
app.MainLoop()

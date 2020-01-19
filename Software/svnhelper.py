#!/usr/bin/python

import wx
import pickle, os, sys
import commands

buttonFieldWidth = 25
svnHelperDirectory = "/home/vineeth"
svnHelperFile = ".svnhelper.pickle"

class SvnShow(wx.Dialog):
    def __init__(self, parent, title, message):
        wx.Dialog.__init__(self, parent, title = title, size = (400, 200))
        self.mainpanel = wx.Panel(self, id = wx.ID_ANY)
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainpanel.SetSizer(self.mainsizer)

        self.messageText = wx.TextCtrl(self.mainpanel, id = wx.ID_ANY, style = wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY)
        self.messageText.SetValue(message)
        self.buttonOk = wx.Button(self.mainpanel, id = wx.ID_ANY, label = "Ok")
        self.mainsizer.Add(self.messageText, flag = wx.EXPAND, proportion = 1)
        self.mainsizer.Add(self.buttonOk)

        self.Bind(wx.EVT_BUTTON, self.onOk, self.buttonOk)

    def onOk(self, event):
        self.Show(False)
    
class SvnMessageEditor(wx.Dialog):
    def __init__(self, parent, project):
        wx.Dialog.__init__(self, parent, title = "Check in message for " + project, size = (400, 200))
        self.mainpanel = wx.Panel(self, id = wx.ID_ANY)
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainpanel.SetSizer(self.mainsizer)

        self.messageText = wx.TextCtrl(self.mainpanel, id = wx.ID_ANY, style = wx.TE_MULTILINE|wx.HSCROLL)
        self.buttonOk = wx.Button(self.mainpanel, id = wx.ID_ANY, label = "Ok")
        self.mainsizer.Add(self.messageText, flag = wx.EXPAND, proportion = 1)
        self.mainsizer.Add(self.buttonOk)

        self.Bind(wx.EVT_BUTTON, self.onOk, self.buttonOk)
        self.message = ""
    
    def onOk(self, event):
        self.message = self.messageText.GetValue()
        self.Show(False)

class MainFrame(wx.Frame):

    def __init__(self, programTitle, programVersion):
        self.projectList = []

        wx.Frame.__init__(self, None, id = wx.ID_ANY, title = programTitle + " " + programVersion)

        self.Bind(wx.EVT_CLOSE, self.onExit, self)

        self.menubar = wx.MenuBar()
        self.menu = wx.Menu()
        self.menubar.Append(self.menu, "Project")

        self.menuAddProject = self.menu.Append(wx.ID_ANY, "&Add project")
        self.menuDeleteProject = self.menu.Append(wx.ID_ANY, "&Delete project(s)")
        self.menuSaveProject = self.menu.Append(wx.ID_ANY, "&Save current list")
        self.menuExit = self.menu.Append(wx.ID_ANY, "E&xit")

        self.Bind(wx.EVT_MENU, self.onAddProject, self.menuAddProject)
        self.Bind(wx.EVT_MENU, self.onDeleteProject, self.menuDeleteProject)
        self.Bind(wx.EVT_MENU, self.saveProject, self.menuSaveProject)
        self.Bind(wx.EVT_MENU, self.onExit, self.menuExit)

        self.SetMenuBar(self.menubar)

        self.mainPanel = wx.Panel(self, id = wx.ID_ANY)
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainPanel.SetSizer(self.mainSizer)

        self.projectListBox = wx.ListBox(self.mainPanel, id = wx.ID_ANY, style = wx.LB_MULTIPLE)
        self.mainSizer.Add(self.projectListBox, flag = wx.EXPAND, proportion = 1)
        self.buttonSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.buttonSizer, flag = wx.EXPAND, proportion = 1)
        
        self.buttonAddProject = wx.Button(self.mainPanel, id = wx.ID_ANY, label = "Add project".ljust(buttonFieldWidth))
        self.buttonDeleteProject = wx.Button(self.mainPanel, id = wx.ID_ANY, label = "Delete project(s)".ljust(buttonFieldWidth))
        self.Bind(wx.EVT_BUTTON, self.onAddProject, self.buttonAddProject)
        self.Bind(wx.EVT_BUTTON, self.onDeleteProject, self.buttonDeleteProject)
        
        self.buttonSizer.Add(self.buttonAddProject)
        self.buttonSizer.Add(self.buttonDeleteProject)
        
        self.checkboxSelectAll = wx.CheckBox(self.mainPanel, id = wx.ID_ANY, label = "Select all projects".ljust(buttonFieldWidth))
        self.buttonSizer.Add(self.checkboxSelectAll)

        self.buttonUpdateProject = wx.Button(self.mainPanel, id = wx.ID_ANY, label = "Update project(s)".ljust(buttonFieldWidth))
        self.buttonCheckinProject = wx.Button(self.mainPanel, id = wx.ID_ANY, label = "Check-in project(s)".ljust(buttonFieldWidth))
        self.Bind(wx.EVT_BUTTON, self.onUpdate, self.buttonUpdateProject)
        self.Bind(wx.EVT_BUTTON, self.onCheckin, self.buttonCheckinProject)

        self.buttonSvnStatus = wx.Button(self.mainPanel, id = wx.ID_ANY, label = "Status".ljust(buttonFieldWidth))
        self.buttonSvnLog = wx.Button(self.mainPanel, id = wx.ID_ANY, label = "Log".ljust(buttonFieldWidth))
        self.buttonSvnDiff = wx.Button(self.mainPanel, id = wx.ID_ANY, label = "Diff".ljust(buttonFieldWidth))
        self.Bind(wx.EVT_BUTTON, self.onStatus, self.buttonSvnStatus)
        self.Bind(wx.EVT_BUTTON, self.onLog, self.buttonSvnLog)
        self.Bind(wx.EVT_BUTTON, self.onDiff, self.buttonSvnDiff)

        self.buttonSizer.Add(self.buttonUpdateProject)
        self.buttonSizer.Add(self.buttonCheckinProject)
        self.buttonSizer.Add(self.buttonSvnStatus)
        self.buttonSizer.Add(self.buttonSvnLog)
        self.buttonSizer.Add(self.buttonSvnDiff)
    
        self.loadProject()
        self.loadProjectList()

        self.Show(True)

    def onStatus(self, event):
        if self.checkboxSelectAll.GetValue():
            selections = range(0, self.projectListBox.GetCount())
        else:
            selections = self.projectListBox.GetSelections()

        currDir = os.getcwd()
        for s in selections:
            p = self.projectListBox.GetString(s)
            os.chdir(p)
            status, out = commands.getstatusoutput("svn status")
            svnShow = SvnShow(self, p, out)
            svnShow.ShowModal()

        os.chdir(currDir)

    def onLog(self, event):
        if self.checkboxSelectAll.GetValue():
            selections = range(0, self.projectListBox.GetCount())
        else:
            selections = self.projectListBox.GetSelections()

        currDir = os.getcwd()
        for s in selections:
            p = self.projectListBox.GetString(s)
            os.chdir(p)
            status, out = commands.getstatusoutput("svn log")
            svnShow = SvnShow(self, p, out)
            svnShow.ShowModal()

        os.chdir(currDir)

    def onDiff(self, event):
        if self.checkboxSelectAll.GetValue():
            selections = range(0, self.projectListBox.GetCount())
        else:
            selections = self.projectListBox.GetSelections()

        currDir = os.getcwd()
        for s in selections:
            p = self.projectListBox.GetString(s)
            os.chdir(p)
            status, out = commands.getstatusoutput("svn diff")
            svnShow = SvnShow(self, p, out)
            svnShow.ShowModal()

        os.chdir(currDir)

    def onUpdate(self, event):
        if self.checkboxSelectAll.GetValue():
            selections = range(0, self.projectListBox.GetCount())
        else:
            selections = self.projectListBox.GetSelections()

        currDir = os.getcwd()
        for s in selections:
            p = self.projectListBox.GetString(s)
            os.chdir(p)
            status, out = commands.getstatusoutput("svn update")
            dlg = wx.MessageBox(out, caption = "SVN Update Message for " + p, style = wx.OK)

        os.chdir(currDir)

    def onCheckin(self, event):
        if self.checkboxSelectAll.GetValue():
            selections = range(0, self.projectListBox.GetCount())
        else:
            selections = self.projectListBox.GetSelections()

        currDir = os.getcwd()
        for s in selections:
            p = self.projectListBox.GetString(s)
            os.chdir(p)
            svnMessEd = SvnMessageEditor(self, p)
            svnMessEd.ShowModal()
            status, out = commands.getstatusoutput("svn ci -m \"" + svnMessEd.message + "\"")
            dlg = wx.MessageBox(out, caption = "SVN Checkin Message for " + p, style = wx.OK)

        os.chdir(currDir)

    def loadProject(self):
        try:
            print os.path.join(svnHelperDirectory, svnHelperFile)
            projFile = open(os.path.join(svnHelperDirectory, svnHelperFile), "rb")
            self.projectList = pickle.load(projFile)
            projFile.close()
        except IOError:
            print "x"
            pass

    def loadProjectList(self):
        for p in self.projectList:
            self.projectListBox.InsertItems([p], 0)

    def onAddProject(self, event):
        dlg = wx.DirDialog(self, "Add SVN working copy", "", wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            project = dlg.GetPath()
            self.projectList.append(project)
            self.projectListBox.InsertItems([project], 0)

    def onDeleteProject(self, event):
        selections = self.projectListBox.GetSelections()
        try:
            s = selections[0]
            p = self.projectListBox.GetString(s)
            self.projectList.remove(p)
            self.projectListBox.Delete(s)
        except IndexError:
            pass

    def saveProject(self):
        try:
            projFile = open(os.path.join(svnHelperDirectory, svnHelperFile), "wb")
            pickle.dump(self.projectList, projFile)
            projFile.close()
        except IOError:
            sys.exit(-1)

    def onExit(self, event):
        self.saveProject()
        self.Destroy()
        

programTitle = "SVN Helper"
programVersion = "0.1"

app = wx.App()

mainframe = MainFrame(programTitle, programVersion)
app.MainLoop()

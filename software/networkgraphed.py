#!/usr/bin/python2.7

PROGRAM_TITLE = "Network Graph Editor"

MIN_SCALE = 1
MAX_SCALE = 5

TOOL_NONE = 0
TOOL_NODE = 1
TOOL_EDGE = 2

TOOL_NAMES = ["None", "Node", "Edge"]

DEFAULT_NODE_WIDTH = 50
DEFAULT_NODE_HEIGHT = 50
DEFAULT_NODE_LINE_WIDTH = 1
DEFAULT_NODE_FILL_COLOR = "SKY BLUE"
DEFAULT_NODE_TEXT_SIZE = 20

DEFAULT_EDGE_WIDTH = 2
DEFAULT_EDGE_COLOR = "DARK GREEN"

NODE_SELECTION_OFFSET = 0
NODE_SELECTION_LINE_WIDTH = 2
NODE_SELECT_COLOR = "DARK BLUE"

E_0_NODE = 0
E_1_NODE = 1

EDGE_NODE_1 = "DARK RED"
EDGE_NODE_2 = "DARK GREEN"

BIG_VALUE = 10000

ENDL = "\n"

from wx.lib.floatcanvas import NavCanvas, FloatCanvas, Resources
import wx

import math
class Node:
    def __init__(self, name, pos, width, height):
        self.name = name
        self.pos = pos
        self.width = width
        self.height = height
        
        self.neighbours = []
    
    def hit_test(self, coords):
        x = coords[0]
        y = coords[1]
        
        if x >= self.pos[0] and x <= self.pos[0] + width and y >= self.pos[1] - height and y <= self.pos[1]:
            return True
        else:
            return False
    
    def add_neighbour(self, N):
        flag = True
        for n in self.neighbours:
            if N.name == n.name:
                flag = False
                break
        if flag:
            self.neighbours.append(N)
        
class Network_Graph_Ed(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent = None, 
                          id = wx.ID_ANY, 
                          title = PROGRAM_TITLE)
                          
        
        self.splitter_window = wx.SplitterWindow(self, id = wx.ID_ANY, style = wx.SP_3D)

        self.nav_canvas = NavCanvas.NavCanvas(self.splitter_window, BackgroundColor = "DARK GRAY")
        self.canvas = self.nav_canvas.Canvas
        self.canvas.InitAll()
        self.canvas.MinScale = MIN_SCALE
        self.canvas.MaxScale = MAX_SCALE

        self.properties_panel = wx.Panel(self.splitter_window, id = wx.ID_ANY)

        self.splitter_window.SplitVertically(self.nav_canvas, self.properties_panel)
        
        self.tool_bar = self.nav_canvas.ToolBar
        self.tool_bar.AddSeparator()

        self.select_node = wx.Button(self.tool_bar, wx.ID_ANY, "Node")
        self.select_edge = wx.Button(self.tool_bar, wx.ID_ANY, "Edge")
        self.select_none = wx.Button(self.tool_bar, wx.ID_ANY, "No Tool")

        self.tool_bar.AddSeparator()
        self.gen_outputfile = wx.Button(self.tool_bar, wx.ID_ANY, "Generate output")

        self.tool_bar.AddControl(self.select_node)
        self.tool_bar.AddControl(self.select_edge)
        self.tool_bar.AddControl(self.select_none)
        self.tool_bar.AddControl(self.gen_outputfile)

        self.CreateStatusBar()
        
        self.canvas.Bind(FloatCanvas.EVT_LEFT_DOWN, self.on_click)

        self.select_node.Bind(wx.EVT_BUTTON, self.on_select_node)
        self.select_edge.Bind(wx.EVT_BUTTON, self.on_select_edge)
        self.select_none.Bind(wx.EVT_BUTTON, self.on_select_none)
        self.gen_outputfile.Bind(wx.EVT_BUTTON, self.on_gen_outputfile)
        
        self.node_number = 0
        
        self.selected_tool = TOOL_NODE
        
        self.nodes_in_graph = {}
        self.edges_in_graph = {}
        
        self.last_selected = None
        
        self.selection_rectangle = None
        
        self.set_tool_on_status()
        
        self.init_edge_selection()
        
        self.Show(True)

            


    def on_click(self, event):
        if self.selected_tool == TOOL_NODE:
            self.add_new_node(event)
        elif self.selected_tool == TOOL_NONE:
            if not self.last_selected == None:
                self.canvas.RemoveObject(self.selection_rectangle)
                self.last_selected = None
                self.canvas.Draw()
    
    def on_select_node(self, event):
        self.flush_edge_selection()
        self.selected_tool = TOOL_NODE
        self.set_tool_on_status()
    
    def on_select_edge(self, event):
        self.flush_edge_selection()
        self.selected_tool = TOOL_EDGE
        self.set_tool_on_status()
    
    def on_select_none(self, event):
        self.flush_edge_selection()
        self.selected_tool = TOOL_NONE
        self.set_tool_on_status()
    
    def add_new_node(self, event):
        x = event.Coords[0]
        y = event.Coords[1]
        
        new_node = Node(self.node_number, (x, y), DEFAULT_NODE_WIDTH, DEFAULT_NODE_HEIGHT)
        self.nodes_in_graph[self.node_number] = new_node
        
        R = self.canvas.AddRectangle((x, y), (DEFAULT_NODE_WIDTH, DEFAULT_NODE_HEIGHT), 
                                     LineWidth = DEFAULT_NODE_LINE_WIDTH, FillColor = DEFAULT_NODE_FILL_COLOR)
        R.Name = self.node_number
        R.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.on_node_hit)
        
        self.canvas.AddText(str(self.node_number), (x + DEFAULT_NODE_WIDTH/3, y + DEFAULT_NODE_HEIGHT * 0.75), Size = DEFAULT_NODE_TEXT_SIZE)
        
        self.node_number += 1
        
        self.canvas.Draw()
    
    def add_new_edge(self):
        
        def distance(pair):
            (x1, y1) = pair[0]
            (x2, y2) = pair[1]
            
            d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            return d
        
        n1 = self.new_edge_node_1
        n2 = self.new_edge_node_2
        x1 = n1.pos[0]
        w1 = n1.width
        h1 = n1.height
        y1 = n1.pos[1]
        
        x2 = n2.pos[0]
        w2 = n2.width
        h2 = n2.height
        y2 = n2.pos[1]
        
        p1 = [(x1, y1), (x1 + w1, y1), (x1, y1 + h1), (x1 + w1, y1 + h1)]
        
        p2 = [(x2, y2), (x2 + w2, y2), (x2, y2 + h2), (x2 + w2, y2 + h2)]
        
        p = [(a, b) for a in p1 for b in p2]
        
        d = [math.floor(distance(x) * BIG_VALUE) for x in p]
        
        pts = p[d.index(min(d))]
        
        self.canvas.AddArrowLine(pts, LineWidth = DEFAULT_EDGE_WIDTH, LineColor = DEFAULT_EDGE_COLOR)
        
        self.new_edge_node_1.add_neighbour(self.new_edge_node_2)
        
        
    
    def on_node_hit(self, obj):

        if not self.last_selected == None:
            self.canvas.RemoveObject(self.selection_rectangle)
            self.last_selected = None

        if self.selected_tool == TOOL_NONE or self.selected_tool == TOOL_NODE:
            selected_node = self.nodes_in_graph[obj.Name]
            self.draw_selection_node(selected_node)
            self.last_selected = selected_node

        elif self.selected_tool == TOOL_EDGE:
            if self.new_edge_status == E_0_NODE:
                selected_node = self.nodes_in_graph[obj.Name]
                self.draw_selection_node_1(selected_node)
                self.new_edge_node_1 = selected_node
                self.new_edge_status = E_1_NODE
                
            elif self.new_edge_status == E_1_NODE:
                selected_node = self.nodes_in_graph[obj.Name]
                self.draw_selection_node_2(selected_node)
                self.new_edge_node_2 = selected_node
                
                self.add_new_edge()
                
                self.flush_edge_selection()
                
                
    
    def draw_selection_node(self, selected_node, type_of_sel = NODE_SELECT_COLOR):
        x = selected_node.pos[0]
        y = selected_node.pos[1]
        
        w = selected_node.width
        h = selected_node.height
        
        self.selection_rectangle = self.canvas.AddRectangle((x - NODE_SELECTION_OFFSET, y - NODE_SELECTION_OFFSET), 
                                                            (w + NODE_SELECTION_OFFSET, h + NODE_SELECTION_OFFSET), 
                                                            LineWidth = NODE_SELECTION_LINE_WIDTH, LineColor = type_of_sel)

        self.canvas.Draw()
        
        
    
    def draw_selection_node_1(self, selected_node, type_of_sel = EDGE_NODE_1):
        x = selected_node.pos[0]
        y = selected_node.pos[1]
        
        w = selected_node.width
        h = selected_node.height
        
        self.edge_node_1_rect = self.canvas.AddRectangle((x - NODE_SELECTION_OFFSET, y - NODE_SELECTION_OFFSET), 
                                                            (w + NODE_SELECTION_OFFSET, h + NODE_SELECTION_OFFSET), 
                                                            LineWidth = NODE_SELECTION_LINE_WIDTH, LineColor = type_of_sel)

        self.canvas.Draw()
        
        
    def draw_selection_node_2(self, selected_node, type_of_sel = EDGE_NODE_2):
        x = selected_node.pos[0]
        y = selected_node.pos[1]
        
        w = selected_node.width
        h = selected_node.height
        
        self.edge_node_2_rect = self.canvas.AddRectangle((x - NODE_SELECTION_OFFSET, y - NODE_SELECTION_OFFSET), 
                                                            (w + NODE_SELECTION_OFFSET, h + NODE_SELECTION_OFFSET), 
                                                            LineWidth = NODE_SELECTION_LINE_WIDTH, LineColor = type_of_sel)

        self.canvas.Draw()
        
        
    
    def set_tool_on_status(self):
        self.SetStatusText("Tool selected : " + TOOL_NAMES[self.selected_tool])
    
    def init_edge_selection(self):
            self.new_edge_node_1 = None
            self.new_edge_node_2 = None
            self.new_edge_status = E_0_NODE
            self.edge_node_1_rect = None
            self.edge_node_2_rect = None
    def flush_edge_selection(self):
        if not (self.edge_node_1_rect == None or self.edge_node_2_rect == None):
            self.canvas.RemoveObject(self.edge_node_1_rect)
            self.canvas.RemoveObject(self.edge_node_2_rect)
         
            self.canvas.Draw()
            
        self.init_edge_selection()
    
    def on_gen_outputfile(self, event):
        save_file = wx.FileDialog(self, "Save output file", ".",
                                  "netconfig.txt", "*.txt", 
                                  wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        
        if save_file.ShowModal() == wx.ID_CANCEL:
            return -1
            
        else:
            filename = save_file.GetPath()
            f = open(filename, "w")
            
            f.write(str(len(self.nodes_in_graph)))
            f.write(ENDL)
            
            for n in self.nodes_in_graph.values():
                for neighbour in n.neighbours:
                    f.write(str(n.name) + " " + str(neighbour.name))
                    f.write(ENDL)
                    
            f.close()
            
if __name__ == "__main__":
    app = wx.App()
    Network_Graph_Ed()
    app.MainLoop()    



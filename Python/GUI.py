import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib 
matplotlib.use('TkAgg')
import pandas as pd
import PySimpleGUI as sg
import serial.tools.list_ports
from random import randint
from matplotlib.animation import FuncAnimation
import Support_Package as sp
from functools import partial
import time
from tkinter import messagebox

serial_ports =  list(serial.tools.list_ports.comports())
baud_rates = [9600, 14400, 19200, 28800, 38400, 57600, 115200]
points = ["Needs Setup",]
global ser
Serial_object = None

def draw_figure(canvas, figure):
   figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
   figure_canvas_agg.draw()
   figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1, anchor='center')
   return figure_canvas_agg

sg.theme('DarkBlue3')   # Add a touch of color

#Setup Column
Setup = sg.Text('Setup', justification='center', font=("Helvetica", 20), expand_x=True)
Port_text = sg.Text('Select port and Baud:')
Port_Dropdown = sg.DropDown(values = serial_ports, key = '-PORTS_LISTBOX-', expand_x=True)
Baud_Dropdown = sg.DropDown(values = baud_rates, key = '-BAUD_LISTBOX-', expand_x=True)
Port_button = sg.Button('Connect', key = "-ARDUINO_CONNECT-")
Data_text = sg.Text('Choose Data Points:')
Data_listbox = sg.Listbox(values = points, expand_y = True,expand_x=True, key = '-DATA_POINTS_LIST-',select_mode="multiple", no_scrollbar = False, enable_events=True)
file_text = sg.Text("Choose a file")
file_input = sg.Input("File Path Goes Here", key = "-FILE_INPUT-", size=(12,1), enable_events=True, expand_x=True)
browse = sg.FileBrowse(file_types=(("Comma Seperated Values", '*.csv'),), enable_events=True, key='-FILE_BROWSE-')

#Control Column
Control = sg.Text('Control', justification='center', font=("Helvetica", 20), expand_x=True) 
Start_button = sg.Button('Start',size=(7,1), pad = (30, 0), key = "-START-")
Stop_button = sg.Button('Pause', size = (7,1), pad = (30, 0), key = '-PAUSE-')
save_file_text = sg.Input("Name of trial", key ='-save_file_text-', size=(12,1), enable_events=True, expand_x=True)
Save_button = sg.Button('Save Data', size = (20,1), key = "-SAVE_DATA-")

#Graphs Column
Graphs = sg.Text('Graphs', justification='center', font=("Helvetica", 20), expand_x=True)
GraphX_text = sg.Text('X-Axis: ')
GraphX_Dropdown = sg.DropDown(values = points, expand_x=True, key = '-GRAPH_X-', enable_events=True)
Graph_vs_text = sg.Text('vs.')
GraphY_text = sg.Text('Y-Axis: ')
GraphY_Dropdown = sg.DropDown(values = points, expand_x=True, key = '-GRAPH_Y-', enable_events=True)
Graph_slider = sg.Slider(range = (10,400), default_value = 50, orientation = 'h', size = (10,15), key = 'slider', expand_x=True, enable_events=True)

Setup_Col = sg.Column([[Setup], [Port_text, Port_Dropdown,Baud_Dropdown, Port_button], [Data_text,Data_listbox], [file_text, file_input, browse]], element_justification= 'left', expand_x=True)
Control_Col = sg.Column([[Control], [Start_button, Stop_button], [save_file_text],[Save_button]], expand_x=True, element_justification='center', vertical_alignment='top')
Graphs_Col = sg.Column([[Graphs], [GraphX_text, GraphX_Dropdown, Graph_vs_text, GraphY_text, GraphY_Dropdown], [Graph_slider]], expand_x=True, element_justification='center', vertical_alignment='top')


layout = [ 
        [sg.Canvas(size=(800, 330), key='-CANVAS-', expand_x=True, expand_y=True)], #canvas for graph
        [Setup_Col, Control_Col, Graphs_Col],
]        


# create empty lists for the x and y data
x = []
y = []
running_df = pd.DataFrame()

fig, ax = plt.subplots(1,2)
fig.tight_layout(pad=3.0)
plt.subplots_adjust(wspace = .5)
graph_0_x = points[0]
graph_0_y = points[0]
recent = 50

data_dict = {}
start_time = 0

def animate(x, i):
    new = sp.get_data(ser, True)
    
    for key in data_dict.keys():
        if key == "Time(s)":
            data_dict[key].append(new[key]/1000)
        else:
            data_dict[key].append(new[key])
    
    x = data_dict[graph_0_x]
    y = data_dict[graph_0_y]
    current = time.time() - start_time
    
    print(x,y)
    
    ax[0].clear()
    ax[0].set_title("All Data")
    ax[0].set_xlabel(graph_0_x)
    ax[0].set_ylabel(graph_0_y)
    ax[0].plot(x, y)
    ax[0].set_xlim([0,max(x)+4])
    ax[0].set_ylim([0,max(y)+ 5])
    
    ax[1].clear()
    ax[1].set_title("Recent Data")
    ax[1].set_xlabel(graph_0_x)
    ax[1].set_ylabel(graph_0_y)    
    ax[1].plot(x, y)
    ax[1].set_ylim([0,max(y)+ 5])
    if max(x)+4  < recent:
        ax[1].set_xlim([0,max(x)+4])
    else:
        ax[1].set_xlim([x[-recent], x[-1]])


def animate_start():
    ax[0].clear()
    ax[0].set_title("All Data")
    ax[0].set_xlabel(graph_0_x)
    ax[0].set_ylabel(graph_0_y)
    
    ax[1].clear()
    ax[1].set_title("Recent Data")
    ax[1].set_xlabel(graph_0_x)
    ax[1].set_ylabel(graph_0_y)    

running_df = pd.DataFrame(columns = points)
ani = FuncAnimation(fig, func =partial(animate, x), interval=1, repeat=False, init_func=animate_start,)
window = sg.Window('Data Collection', layout, finalize=True, resizable=True, element_justification='center')
fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
ani.pause()

def save(trial_name, df, file_name):
    sp.write_append([trial_name,], file_name)
    sp.write_append(list(df.columns), file_name)
    sp.write_append(df, file_name)
    print("Saving Data")
    

Serial_object = None
while True:    
    event, values = window.read()
    if event == sg.WIN_CLOSED: # if user closes window
        print('program close')
        break
    
    if event == "-START-":
        ani.resume()
        start_time = time.time()
         
    if event == "-PAUSE-":
        ani.pause()
        
    if event == "-ARDUINO_CONNECT-":

        port = values['-PORTS_LISTBOX-']
        port = port.device
        baud = values['-BAUD_LISTBOX-']      
        Connected, ser = sp.Connect(baud, port) # returns true if connected and false if not
        temp_dict = sp.get_data(ser, False)
        data_dict = temp_dict
        points.clear()
        for key in data_dict.keys():
            points.append(key)
            data_dict[key] = []
        window.Element('-DATA_POINTS_LIST-').update(points)
        window.Element('-GRAPH_X-').update(values = points)
        window.Element('-GRAPH_Y-').update(values = points)

            
    if event == 'slider':
        recent = int(values['slider'])
        
    if event == '-SAVE_DATA-':
        if file_input.get() == "File Path Goes Here":
            messagebox.showerror('Application Error', 'Error: This button/field needs setup')
        try:
            trial_name = values['-save_file_text-']
            file = values['-FILE_INPUT-']
            save(trial_name, running_df, file)
        except:
            messagebox.showerror('Application Error', 'Error: This button/field needs setup')
        
    if event == '-GRAPH_X-':
        graph_0_x = values['-GRAPH_X-']
            
    if event == '-GRAPH_Y-':
        graph_0_y = values['-GRAPH_Y-']
    
    if event == '-DATA_POINTS_LIST-':
        print(values['-DATA_POINTS_LIST-'])
        running_df = pd.DataFrame(columns = list(values['-DATA_POINTS_LIST-']))
        
    
window.close()
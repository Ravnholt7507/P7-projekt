from tkinter import *
import vector_based.prediction as prediction
import vector_based.plot as plot
import vector_based.map as map
from PIL import ImageTk, Image 
import webbrowser
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import cartopy.crs as ccrs
import cartopy
import cartopy.feature as cfeature


# Main window setup
root = Tk()
root.title("Ship Path Prediction")
canvas = Canvas(root, width = 300, height = 300)
sideframe = Frame(root, width = 300, height = 300)
rightSideframe = Frame(root, width = 300, height = 300)
canvas.pack(side=RIGHT, fill=BOTH, expand=1)
sideframe.pack(side=LEFT, fill=BOTH, expand=0)
sideframe.pack(side=RIGHT, fill=BOTH, expand=0)
sideframe.grid_columnconfigure(2, weight=1)
sideframe.grid_rowconfigure(100, weight=1)

# Data setup
df = pd.read_csv("data/boats.csv")
MMSI = df['MMSI'].unique()

def Take_input():
    save_settingstxt()
    errorLabel.grid_forget()
    clear()
    while True:
        try:
            input = mmsiEntryBox.get()
            if(int(input) in MMSI):
                if(nnVar.get() == 1):
                    if(nnChoiceCheckVar.get() == 1):
                        blegh = 1
                    if(nnChoiceCheckVar2.get() == 1):
                        blegh = 1
                    if(nnChoiceCheckVar3.get() == 1):
                        blegh = 1
                    elif(nnChoiceCheckVar.get() == 0 and nnChoiceCheckVar2.get() == 0 and nnChoiceCheckVar3.get() == 0):
                        print("Error: No neural network variant selected")
                        errorLabel.grid(row=16, column=0, sticky=W, padx=10, pady=2)
                        break
                if(vectorVar.get() == 1):
                    prediction.predict(input)
                    plot.plot()
                    plot.actualToPred()
                    plot.worldMapPlot()
                    map.plot()
                    mapButton.grid(row=0, column=0)
                    plot1.grid(row=0, column=1)
                    plot2.grid(row=0, column=2)
                    plot3.grid(row=0, column=3)
                    output.grid(row=1, column=1, sticky=W, padx=10, pady=2)
                    output.delete(1.0, END)
                    output.insert(END, "Output appears here")
                    mapButton.invoke()
                if(compShipsVar.get() == 1):
                    multiListbox_select(0)
                elif(vectorVar.get() == 0 and nnVar.get() == 0):
                    print("Error: No prediction method selected")
                    errorLabel.grid(row=16, column=0, sticky=W, padx=10, pady=2)
                    break 
                break
            else:
                print("Error: MMSI not found")
                errorLabel.grid(row=16, column=0, sticky=W, padx=10, pady=2)
                break
        except ValueError:
            print("Error: MMSI not found")
            errorLabel.grid(row=16, column=0, sticky=W, padx=10, pady=2)
            break
    
def focus_out_entry_box(widget, widget_text):
    if widget['fg'] == 'Black' and len(widget.get()) == 0:
        widget.delete(0, END)
        widget['fg'] = 'Grey'
        widget.insert(0, widget_text)

def focus_in_entry_box(widget):
    if widget['fg'] == 'Grey':
        widget['fg'] = 'Black'
        widget.delete(0, END)

def listbox_select(event):
    print('Listbox selection: ', mmsiListbox.get(mmsiListbox.curselection()))
    
    mmsiEntryBox.delete(0, END)
    mmsiEntryBox.insert(0, mmsiListbox.get(mmsiListbox.curselection()))

def multiListbox_select(event):
    # Get the indices of all the selected items
    selectedIndices = multiListbox.curselection()
    selectedItems = []
    # Loop over the selected indices and get the values of the selected items
    for index in selectedIndices:
        selectedItems.append(multiListbox.get(index))
    print(selectedItems)

def nerualNetworkChoices(var):
    if var == 1:
        nnVariantLabel.grid(row=6, column=0, sticky=W, padx=10, pady=2)
        nnChoiceCheck.grid(row=7, column=0, sticky=W, padx=10, pady=2)
        nnChoiceCheck2.grid(row=8, column=0, sticky=W, padx=10, pady=2)
        nnChoiceCheck3.grid(row=9, column=0, sticky=W, padx=10, pady=2)
    else:
        nnVariantLabel.grid_forget()
        nnChoiceCheck.grid_forget()
        nnChoiceCheck2.grid_forget()
        nnChoiceCheck3.grid_forget()
        nnChoiceCheckVar.set(0)
        nnChoiceCheckVar2.set(0)
        nnChoiceCheckVar3.set(0)

def show_multi_listbox(var):
    if var == 1:
        multiListboxLabel.grid(row=12, column=0, sticky=W, padx=10, pady=2)
        multiListbox.grid(row=13, column=0, sticky=W, padx=10, pady=2)
    if var == 0:
        multiListboxLabel.grid_forget()
        multiListbox.grid_forget()
        multiListbox.selection_clear(0, END)
        
def clear():
    with open('data/predictions.csv', 'w') as fp:
        fp.truncate()
        
def load_settingstxt():
    #load settings.txt
    with open('settings.txt', 'r') as f:
        settings = f.readlines()

    for i in range(len(settings)):
        settings[i] = int(settings[i].split('=')[1].replace('\n', ''))
        
    if settings[0] == 1:
        mmsiEntryBox.delete(0, END)
        mmsiEntryBox.insert(0, settings[0])
    if settings[1] == 1:
        vectorCheck.select()
    if settings[2] == 1:
        nnCheck.select()
        nerualNetworkChoices(1)
    if settings[3] == 1:
        nnChoiceCheck.select()
    if settings[4] == 1:
        nnChoiceCheck2.select()
    if settings[5] == 1:
        nnChoiceCheck3.select()
    
    return settings

def save_settingstxt():
    #get settings
    settings = []
    settings.append('selectedMMSI='+mmsiEntryBox.get()+str('\n'))
    settings.append('vectorCheck='+str(vectorVar.get())+str('\n'))
    settings.append('NNCheck='+str(nnVar.get())+str('\n'))
    settings.append('NN1Check='+str(nnChoiceCheckVar.get())+str('\n'))
    settings.append('NN2Check='+str(nnChoiceCheckVar2.get())+str('\n'))
    settings.append('NN3Check='+str(nnChoiceCheckVar3.get())+str('\n'))
    #save settings.txt
    with open('settings.txt', 'w') as f:
        f.writelines(settings)

chosen = None
def raised_button(button_object):
    global chosen

    if chosen: # previously clicked
        chosen.configure(relief=RAISED, state=ACTIVE)
    chosen = button_object
    button_object.configure(relief=SUNKEN, state=DISABLED)

def stop():
    global chosen

    chosen = None

    mapButton.configure(relief=RAISED, state=ACTIVE)
    plot1.configure(relief=RAISED, state=ACTIVE)
    plot2.configure(relief=RAISED, state=ACTIVE)
    plot3.configure(relief=RAISED, state=ACTIVE)

def showBackForw():
    backward.grid(row=3, column=0)
    forward.grid(row=3, column=2)

def backOrForw():
    blegh = 1
    
def getListOfFiles():
    Files = []
    for file_path in os.listdir('Figures'):
        if file_path.endswith('.png'):
            Files.append(file_path)

show_plot = False
def showFigure(path):
    fig = plot.Load_plot(path)
    plt.figure(figsize=(12,6))
    figure = FigureCanvasTkAgg(fig , master =imagebox)
    toolbar_frame = Frame(imagebox)
    
    global show_plot
    if show_plot:
        figure.get_tk_widget().grid_forget()
        toolbar_frame.destroy()
    
    figure.draw()
    toolbar_frame = Frame(toolBox)
    toolbar = NavigationToolbar2Tk(figure, toolbar_frame)
    toolbar_frame.grid(row=0, column=0)
    figure.get_tk_widget().grid(row=0, column=0)
    
    show_plot = True

def worldMap(master):
    fig,ax = plt.subplots()
    ccrs.PlateCarree()
    plt.axes(projection=ccrs.PlateCarree())

    names = np.array(list("ABCDEFGHIJKLMNO"))
    norm = plt.Normalize(1,4)
    cmap = plt.cm.RdYlGn
    c = np.random.randint(1,5,size=10000)


    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.add_feature(cartopy.feature.OCEAN)
    ax.add_feature(cartopy.feature.LAND, edgecolor='black')
    ax.add_feature(cartopy.feature.LAKES, edgecolor='black')
    ax.add_feature(cartopy.feature.RIVERS)
    ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, color = 'None')
    df = pd.read_csv("data/boats.csv")
    sc = plt.scatter(df['LON'], df['LAT'], s=0.1, c='red', marker='*', transform=ccrs.PlateCarree())
    plt.tight_layout()
    
    annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind):
        pos = sc.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        df = pd.read_csv("data/boats.csv")
        text = 'Vessel: {}'.format(df['VesselName'].iloc[ind["ind"][0]]) + '\n' + 'MMSI: {}'.format(df['MMSI'].iloc[ind["ind"][0]]) + '\n' + 'Latitude: {}'.format(df['LAT'].iloc[ind["ind"][0]]) + '\n' + 'Longitude: {}'.format(df['LON'].iloc[ind["ind"][0]]) + '\n' + 'BaseDateTime: {}'.format(df['BaseDateTime'].iloc[ind["ind"][0]]) + '\n' + 'SOG: {}'.format(df['SOG'].iloc[ind["ind"][0]]) + '\n' + 'COG: {}'.format(df['COG'].iloc[ind["ind"][0]]) + '\n' + 'Heading: {}'.format(df['Heading'].iloc[ind["ind"][0]])
        annot.set_text(text)
        annot.get_bbox_patch().set_facecolor(cmap(norm(c[ind["ind"][0]])))
        annot.get_bbox_patch().set_alpha(0.4)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = sc.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    global cId
    cId = fig.canvas.mpl_connect("motion_notify_event", hover)

    figure = FigureCanvasTkAgg(fig , master =master)
    toolbar_frame = Frame(master)
    
    global show_plot
    if show_plot:
        figure.get_tk_widget().grid_forget()
        toolbar_frame.destroy()
    
    figure.draw()
    toolbar_frame = Frame(toolBox)
    toolbar = NavigationToolbar2Tk(figure, toolbar_frame)
    toolbar_frame.grid(row=0, column=0)
    figure.get_tk_widget().grid(row=0, column=0)
    show_plot = True

# widgets
mmsiEntryBox = Entry(sideframe, font='Arial 18', fg='Grey')
mmsiEntryBox.insert(0, 'Enter MMSI')
mmsiEntryBox.bind("<FocusIn>", lambda args: focus_in_entry_box(mmsiEntryBox))
mmsiEntryBox.bind("<FocusOut>", lambda args: focus_out_entry_box(mmsiEntryBox, 'Enter MMSI'))
availableMMsis = Variable(sideframe, MMSI.tolist())
availableMMsisLabel = Label(sideframe, text ="Available MMSI's")
mmsiListbox = Listbox(sideframe, height=5, listvariable=availableMMsis, selectmode='single')
predMethodLabel = Label(sideframe, text="Prediction Methods")
nnVar = IntVar()
nnCheck = Checkbutton(sideframe, text="Neural Network", variable=nnVar, command=lambda: nerualNetworkChoices(nnVar.get()))
nnVariantLabel = Label(sideframe, text="Select one or more variants below")
nnChoiceCheckVar = IntVar()
nnChoiceCheck = Checkbutton(sideframe, text="CNN", variable=nnChoiceCheckVar)
nnChoiceCheckVar2 = IntVar()
nnChoiceCheck2 = Checkbutton(sideframe, text="LSTM", variable=nnChoiceCheckVar2)
nnChoiceCheckVar3 = IntVar()
nnChoiceCheck3 = Checkbutton(sideframe, text="RNN", variable=nnChoiceCheckVar3)
vectorVar = IntVar()
vectorCheck = Checkbutton(sideframe, text="Vector Based", variable=vectorVar)
additionalOptionsLabel = Label(sideframe, text="Additional Options")
compShipsVar = IntVar()
compShipsCheck = Checkbutton(sideframe, text="Compare to other ships", variable=compShipsVar, command=lambda: show_multi_listbox(compShipsVar.get()))
multiListboxLabel = Label(sideframe, text="select one or more from the list below")
multiListbox = Listbox(sideframe, height=5, listvariable=availableMMsis, selectmode='multiple')
buttonFrame = Frame(sideframe)
predButton = Button(buttonFrame, text="Predict", command=lambda: Take_input())
clearButton = Button(buttonFrame, text="Clear predictions", command=lambda: clear())
errorLabel = Label(sideframe, text="Error: You seem to have fucked up!", fg='red')
canvasFrame = Frame(canvas)
imagebox = Label(canvas)
toolBox = Frame(canvas)
output = Text(canvas, width=50, height=33, bg="light yellow")
mapButton = Button(canvasFrame, text='Map', command=lambda: [raised_button(button_object=mapButton), worldMap(imagebox)])
plot1 = Button(canvasFrame, text='Act & Pred', command=lambda: [raised_button(button_object=plot1), showFigure('figures/actVsPred.obj')])
plot2 = Button(canvasFrame, text='Act -> Pred', command=lambda: [raised_button(button_object=plot2), showFigure('figures/predPlotArrows.obj')])
plot3 = Button(canvasFrame, text='Collisions', command=lambda: [raised_button(button_object=plot3), showBackForw()])
backward = Button(canvasFrame, text='Previous Image')
forward = Button(canvasFrame, text='Next Image')


# grid, some widgets are hidden by default
availableMMsisLabel.grid(row=0, column=0, sticky=W, padx=10, pady=2)
mmsiListbox.grid(row=1, column=0, sticky=W, padx=10, pady=2)
mmsiEntryBox.grid(row=2, column=0, padx=10, pady=10)
predMethodLabel.grid(row=3, column=0, sticky=W, padx=10, pady=2)
vectorCheck.grid(row=4, column=0, sticky=W, padx=10, pady=2)
nnCheck.grid(row=5, column=0, sticky=W, padx=10, pady=2)
additionalOptionsLabel.grid(row=10, column=0, sticky=W, padx=10, pady=2)
compShipsCheck.grid(row=11, column=0, sticky=W, padx=10, pady=2)
buttonFrame.grid(row=14, column = 0)
predButton.grid(row=0, column=0)
clearButton.grid(row=0, column=1)
canvasFrame.grid(row=0, column=0)
imagebox.grid(row=1, column=0)
toolBox.grid(row=2, column=0)

# bindings for when a listbox item is selected
mmsiListbox.bind('<<ListboxSelect>>', listbox_select)
multiListbox.bind('<<ListboxSelect>>', multiListbox_select)

load_settingstxt()

# mainloop for window
root.mainloop()
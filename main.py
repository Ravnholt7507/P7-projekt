from tkinter import *
import vector_based.prediction as prediction
import vector_based.plot as plot
import vector_based.map as map
from PIL import ImageTk, Image 
import webbrowser
import pandas as pd

import numpy as np


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
                    else:
                        print("Error: No neural network variant selected")
                        errorLabel.grid(row=16, column=0, sticky=W, padx=10, pady=2)
                        break
                if(vectorVar.get() == 1):
                    prediction.predict(input)
                    plot.actualToPred()
                    map.plot()
                    show_image("Figures/predPlotArrows.png")
                    webMapButton.grid(row=0, column=0)
                    zoomButton.grid(row=0, column=1)
                    output.grid(row=1, column=1, sticky=W, padx=10, pady=2)
                    output.delete(1.0, END)
                    output.insert(END, "Output appears here")
                if(compShipsVar.get() == 1):
                    multiListbox_select(0)
                break
            else:
                print("Error: MMSI not found")
                errorLabel.grid(row=16, column=0, sticky=W, padx=10, pady=2)
                break
        except ValueError:
            print("Error: MMSI not found")
            errorLabel.grid(row=16, column=0, sticky=W, padx=10, pady=2)
            break
      
def show_image(imagefile):
    image = ImageTk.PhotoImage(file=imagefile)
    imagebox.config(image=image)
    imagebox.image = image

def openURL():
    webbrowser.open_new('map.html')
    
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
output = Text(canvas, width=50, height=33, bg="light yellow")
webMapButton = Button(canvasFrame, text="Open Map", command=lambda: openURL())
zoomButton = Button(canvasFrame, text="Open Zoomable Plot", command=lambda: plot.Load_plot('Figures/predPlotArrows.obj'))

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

# bindings for when a listbox item is selected
mmsiListbox.bind('<<ListboxSelect>>', listbox_select)
multiListbox.bind('<<ListboxSelect>>', multiListbox_select)

load_settingstxt()

# mainloop for window
root.mainloop()
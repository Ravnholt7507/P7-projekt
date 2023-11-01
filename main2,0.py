from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
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
import datetime
import pickle

df = pd.read_csv("data/boats.csv")
MMSI = df['MMSI'].unique()
plotSelected = None
showPlot = False
GlobalBackground = None

class inputFrame(Frame):
    def __init__(self, parent, output_frame, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.output_frame = output_frame
        
        #Widgets
        self.availableMMsisLabel = Label(self, text ="Available MMSI's")
        self.availableMMsis = Variable(self, MMSI.tolist())
        self.mmsiTree = ttk.Treeview(self, height=5, columns=('c1', 'c2'), show='headings')
        self.mmsiEntryBox = Entry(self, font='arial 18', fg='grey')
        self.mmsiEntryBox.insert(0, 'Enter MMSI')
        self.mmsiEntryBox.bind("<FocusIn>", lambda args: self.focus_in_entry_box(self.mmsiEntryBox))
        self.mmsiEntryBox.bind("<FocusOut>", lambda args: self.focus_out_entry_box(self.mmsiEntryBox, 'Enter MMSI'))
        self.predMethodLabel = Label(self, text="Prediction Methods")
        self.nnVar = IntVar()
        self.nnCheck = Checkbutton(self, text="Neural Network", variable=self.nnVar, command=lambda: self.nerualNetworkChoices(self.nnVar.get()))
        self.nnVariantLabelFrame = LabelFrame(self, text="Neural Network Variants")
        self.nnVariantLabel = Label(self.nnVariantLabelFrame, text="Select one or more variants below")
        self.nnChoiceCheckVar = IntVar()
        self.nnChoiceCheck = Checkbutton(self.nnVariantLabelFrame, text="CNN", variable=self.nnChoiceCheckVar)
        self.nnChoiceCheckVar2 = IntVar()
        self.nnChoiceCheck2 = Checkbutton(self.nnVariantLabelFrame, text="LSTM", variable=self.nnChoiceCheckVar2)
        self.nnChoiceCheckVar3 = IntVar()
        self.nnChoiceCheck3 = Checkbutton(self.nnVariantLabelFrame, text="RNN", variable=self.nnChoiceCheckVar3)
        self.vectorVar = IntVar()
        self.vectorCheck = Checkbutton(self, text="Vector Based", variable=self.vectorVar)
        self.additionalOptionsLabel = Label(self, text="Additional Options")
        self.compShipsVar = IntVar()
        self.compShipsCheck = Checkbutton(self, text="Compare to other ships", variable=self.compShipsVar, command=lambda: self.show_multi_listbox(self.compShipsVar.get()))
        self.multiListboxLabel = Label(self, text="select one or more from the list below")
        self.multiListbox = Listbox(self, height=5, listvariable=self.availableMMsis, selectmode='multiple')
        self.buttonFrame = Frame(self)
        self.predButton = Button(self.buttonFrame, text="Predict", command=lambda: self.predict())
        self.errorLabel = Label(self, text="Error: You seem to have fucked up!", fg='red')

        #Widget Placement
        self.availableMMsisLabel.grid(row=0, column=0, sticky=W, padx=10, pady=2)
        self.mmsiTree.grid(row=1, column=0, sticky=W, padx=10, pady=2)
        self.mmsiEntryBox.grid(row=2, column=0, sticky=W, padx=10, pady=10)
        self.predMethodLabel.grid(row=3, column=0, sticky=W, padx=10, pady=2)
        self.nnCheck.grid(row=4, column=0, sticky=W, padx=10, pady=2)
        self.nnVariantLabelFrame.grid(row=5, column=0, sticky=W, padx=10, pady=2)
        self.nnVariantLabel.grid(row=6, column=0, sticky=W, padx=10, pady=2)
        self.nnChoiceCheck.grid(row=7, column=0, sticky=W, padx=10, pady=2)
        self.nnChoiceCheck2.grid(row=8, column=0, sticky=W, padx=10, pady=2)
        self.nnChoiceCheck3.grid(row=9, column=0, sticky=W, padx=10, pady=2)
        self.vectorCheck.grid(row=10, column=0, sticky=W, padx=10, pady=2)
        self.additionalOptionsLabel.grid(row=11, column=0, sticky=W, padx=10, pady=2)
        #self.compShipsCheck.grid(row=12, column=0, sticky=W, padx=10, pady=2)
        #self.multiListboxLabel.grid(row=13, column=0, sticky=W, padx=10, pady=2)
        self.buttonFrame.grid(row=14, column=0, sticky=W, padx=10, pady=2)
        self.predButton.grid(row=0, column=0, sticky=W, padx=10, pady=2)
        
        self.nerualNetworkChoices(self.nnVar.get())
        self.constructTree()
        self.multiListbox.bind('<<ListboxSelect>>', self.multiListbox_select)
        self.mmsiTree.bind('<<TreeviewSelect>>', self.treeSelect)

    def constructTree(self):
        self.mmsiTree.column("# 1", width=125, anchor='w')
        self.mmsiTree.heading("# 1", text="Vessel")
        self.mmsiTree.column("# 2", width=100, anchor='w')
        self.mmsiTree.heading("# 2", text="MMSI")
        
        for ship in MMSI:
            self.mmsiTree.insert("", "end", values=(df.loc[df['MMSI'] == ship, 'VesselName'].iloc[0], ship))

    def treeSelect(self, event):
        print('Treeview selection: ', self.mmsiTree.item(self.mmsiTree.selection())['values'][1])
        self.mmsiEntryBox.delete(0, END)
        self.mmsiEntryBox.insert(0, self.mmsiTree.item(self.mmsiTree.selection())['values'][1])
        
    def focus_out_entry_box(self, widget, widget_text):
        if widget['fg'] == 'Black' and len(widget.get()) == 0:
            widget.delete(0, END)
            widget['fg'] = 'Grey'
            widget.insert(0, widget_text)

    def focus_in_entry_box(self, widget):
        if widget['fg'] == 'Grey':
            widget['fg'] = 'Black'
            widget.delete(0, END)
            
    def nerualNetworkChoices(self, var):
        if var == 1:
            self.nnVariantLabelFrame.grid(row=5, column=0, sticky=W, padx=10, pady=2)
            self.nnVariantLabel.grid(row=6, column=0, sticky=W, padx=10, pady=2)
            self.nnChoiceCheck.grid(row=7, column=0, sticky=W, padx=10, pady=2)
            self.nnChoiceCheck2.grid(row=8, column=0, sticky=W, padx=10, pady=2)
            self.nnChoiceCheck3.grid(row=9, column=0, sticky=W, padx=10, pady=2)
        else:
            self.nnVariantLabelFrame.grid_forget()
            self.nnVariantLabel.grid_forget()
            self.nnChoiceCheck.grid_forget()
            self.nnChoiceCheck2.grid_forget()
            self.nnChoiceCheck3.grid_forget()
            self.nnChoiceCheckVar.set(0)
            self.nnChoiceCheckVar2.set(0)
            self.nnChoiceCheckVar3.set(0)
    
    def multiListbox_select(self, event):
        # Get the indices of all the selected items
        selectedIndices = self.multiListbox.curselection()
        selectedItems = []
        # Loop over the selected indices and get the values of the selected items
        for index in selectedIndices:
            selectedItems.append(self.multiListbox.get(index))
        print(selectedItems)

    def predict(self):
        self.errorLabel.grid_forget()
        GlobalBackground.clear()
        self.output_frame.clearOutput()
        GlobalBackground.saveSettings()
        while True:
            try:
                input = self.mmsiEntryBox.get()
                if(int(input) in MMSI):
                    if(self.nnVar.get() == 1):
                        if(self.nnChoiceCheckVar.get() == 1):
                            blegh = 1
                        if(self.nnChoiceCheckVar2.get() == 1):
                            blegh = 1
                        if(self.nnChoiceCheckVar3.get() == 1):
                            blegh = 1
                        elif(self.nnChoiceCheckVar.get() == 0 and self.nnChoiceCheckVar2.get() == 0 and self.nnChoiceCheckVar3.get() == 0):
                            print("Error: No neural network variant selected")
                            self.errorLabel.grid(row=16, column=0, sticky=W, padx=10, pady=2)
                            break
                    if(self.vectorVar.get() == 1):
                        prediction.predict(input)
                        intvOutput = prediction.predict_intv()
                        self.output_frame.showOutput('Vector Based\n')
                        for i in range(len(intvOutput)):
                            self.output_frame.showOutput(intvOutput[i])
                        GlobalBackground.simpLogger()
                        plot.plot()
                        plot.actualToPred()
                    if(self.compShipsVar.get() == 1):
                        self.multiListbox_select(0)
                    elif(self.vectorVar.get() == 0 and self.nnVar.get() == 0):
                        print("Error: No prediction method selected")
                        self.errorLabel.grid(row=16, column=0, sticky=W, padx=10, pady=2)
                        break 
                    break
                else:
                    print("Error: MMSI not found")
                    self.errorLabel.grid(row=16, column=0, sticky=W, padx=10, pady=2)
                    break
            except:
                print("Error: MMSI not found")
                self.errorLabel.grid(row=16, column=0, sticky=W, padx=10, pady=2)
                break

class plotFrame(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.buttonFrame = Frame(self)
        self.imagebox = Label(self)
        self.toolBox = Frame(self)
        self.mapButton = Button(self.buttonFrame, text='Map', command=lambda: [self.raised_button(self.mapButton), self.worldMap(True)])
        self.plot1 = Button(self.buttonFrame, text='Act & Pred', command=lambda: [self.raised_button(self.plot1), self.worldMap(False), self.showFigure('figures/actVsPred.obj')])
        self.plot2 = Button(self.buttonFrame, text='Act -> Pred', command=lambda: [self.raised_button(self.plot2), self.worldMap(False), self.showFigure('figures/predPlotArrows.obj')])
        self.plot3 = Button(self.buttonFrame, text='Collisions', command=lambda: [self.raised_button(self.plot3), self.worldMap(False), self.showBackForw()])
                
        self.buttonFrame.grid(row=0, column=0, sticky=W, padx=10, pady=2)
        self.mapButton.grid(row=0, column=0, sticky=W, padx=10, pady=2)
        self.plot1.grid(row=0, column=1, sticky=W, padx=10, pady=2)
        self.plot2.grid(row=0, column=2, sticky=W, padx=10, pady=2)
        self.plot3.grid(row=0, column=3, sticky=W, padx=10, pady=2)
        self.imagebox.grid(row=1, column=0, sticky=W, padx=10, pady=2)
        self.toolBox.grid(row=2, column=0, sticky=W, padx=10, pady=2)

        self.mapButton.invoke()

    def raised_button(self, button_object):
        global plotSelected
        if plotSelected: # previously clicked
            plotSelected.configure(relief=RAISED, state=ACTIVE)
        plotSelected = button_object
        button_object.configure(relief=SUNKEN, state=DISABLED)

    def stop(self):
        global plotSelected
        plotSelected = None
        self.mapButton.configure(relief=RAISED, state=ACTIVE)
        self.plot1.configure(relief=RAISED, state=ACTIVE)
        self.plot2.configure(relief=RAISED, state=ACTIVE)
        self.plot3.configure(relief=RAISED, state=ACTIVE)
        
    def showFigure(self, path):
        fig = plot.Load_plot(path)
        plt.figure(figsize=(12,6))
        figure = FigureCanvasTkAgg(fig , master =self.imagebox)
        toolbar_frame = Frame(self.imagebox)
        
        global showPlot
        if showPlot:
            figure.get_tk_widget().grid_forget()
            toolbar_frame.destroy()
        
        figure.draw()
        toolbar_frame = Frame(self.toolBox)
        toolbar = NavigationToolbar2Tk(figure, toolbar_frame)
        toolbar_frame.grid(row=0, column=0)
        figure.get_tk_widget().grid(row=0, column=0)
        showPlot = True
        plt.clf()
                
    def worldMap(self, toPlotOrNotToPlot):
            fig,ax = plt.subplots()
            ccrs.PlateCarree()
            plt.axes(projection=ccrs.PlateCarree())

            norm = plt.Normalize(1,4)
            cmap = plt.cm.RdYlGn
            c = np.random.randint(1,5,size=757757)

            fig = plt.figure(figsize=(12, 6))
            ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
            ax.add_feature(cartopy.feature.OCEAN)
            ax.add_feature(cartopy.feature.LAND, edgecolor='black')
            ax.add_feature(cartopy.feature.LAKES, edgecolor='black')
            ax.add_feature(cartopy.feature.RIVERS)
            ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, color = 'None')
            ax.margins(5,5)
            sc = plt.scatter(df['LON'], df['LAT'], s=0.1, c='red', marker='*', transform=ccrs.PlateCarree())
            plt.tight_layout()
            plt.savefig('figures/map.png')
            with open('Figures/map.obj', 'wb') as f:
                pickle.dump(fig, f)
            annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
            annot.set_visible(False)

            def update_annot(ind):
                pos = sc.get_offsets()[ind["ind"][0]]
                annot.xy = pos
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
            def deactivate():
                fig.canvas.mpl_disconnect(cId)
                plt.clf()

            cId = fig.canvas.mpl_connect("motion_notify_event", hover)

            figure = FigureCanvasTkAgg(fig , master =self.imagebox)
            toolbar_frame = Frame(self.toolBox)
            
            global showPlot
            if showPlot:
                figure.get_tk_widget().grid_forget()
                toolbar_frame.destroy()
            
            if toPlotOrNotToPlot:
                figure.draw()
            toolbar_frame = Frame(self.toolBox)
            toolbar = NavigationToolbar2Tk(figure, toolbar_frame)
            toolbar_frame.grid(row=0, column=0)
            figure.get_tk_widget().grid(row=0, column=0)
            showPlot = True

            if not toPlotOrNotToPlot:
                deactivate()

class outputFrame(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.outputLabel = Label(self, text="Output")
        self.outputText = Text(self, height=40, width=50)
        self.outputText.configure(state='disabled')
        
        self.outputLabel.grid(row=0, column=0, sticky=W, padx=10, pady=2)
        self.outputText.grid(row=1, column=0, sticky=W, padx=10, pady=2)
        
    def showOutput(self, output):
        self.outputText.configure(state='normal')
        self.outputText.insert(END, output)
        self.outputText.configure(state='disabled')
        
    def clearOutput(self):
        self.outputText.configure(state='normal')
        self.outputText.delete('1.0', END)
        self.outputText.configure(state='disabled')
        
class BackgroundFunctionality():
    def __init__(self, parent, output_frame, input_frame, *args, **kwargs):
        self.parent = parent
        self.output_frame = output_frame
        self.input_frame = input_frame
        self.loadSettings()

        self.parent.outputFrame.showOutput('Can we remove global variables, pretty please?')
    def simpLogger(self):
        text = self.output_frame.outputText.get('1.0', END)
        with open('log.txt', 'a') as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n')
            f.write(text)
        
    def loadSettings(self):
        
        while True:
            try:
                with open('settings.txt', 'r') as f:
                    settings = f.readlines()

                for i in range(len(settings)):
                    settings[i] = int(settings[i].split('=')[1].replace('\n', ''))                    
                if settings[0] == 1:
                    self.input_frame.mmsiEntryBox.delete(0, END)
                    self.input_frame.mmsiEntryBox.insert(0, settings[0])
                if settings[1] == 1:
                    self.input_frame.vectorCheck.select()
                if settings[2] == 1:
                    self.input_frame.nnCheck.select()
                    self.input_frame.nerualNetworkChoices(1)
                if settings[3] == 1:
                    self.input_frame.nnChoiceCheck.select()
                if settings[4] == 1:
                    self.input_frame.nnChoiceCheck2.select()
                if settings[5] == 1:
                    self.input_frame.nnChoiceCheck3.select()
                break
            except:
                self.input_frame.errorLabel.configure(text='Error: Your settings file seems to be fucked')
                self.input_frame.errorLabel.grid(row=16, column=0, sticky=W, padx=10, pady=2)
                break
        
    def saveSettings(self):
        #get settings
        settings = []
        settings.append('selectedMMSI='+self.input_frame.mmsiEntryBox.get()+str('\n'))
        settings.append('vectorCheck='+str(self.input_frame.vectorVar.get())+str('\n'))
        settings.append('NNCheck='+str(self.input_frame.nnVar.get())+str('\n'))
        settings.append('NN1Check='+str(self.input_frame.nnChoiceCheckVar.get())+str('\n'))
        settings.append('NN2Check='+str(self.input_frame.nnChoiceCheckVar2.get())+str('\n'))
        settings.append('NN3Check='+str(self.input_frame.nnChoiceCheckVar3.get())+str('\n'))
        #save settings.txt
        with open('settings.txt', 'w') as f:
            f.writelines(settings)

    def clear(self):
        with open('data/predictions.csv', 'w') as fp:
            fp.truncate()

class MenuBar(Menu):
    def __init__(self, parent, *args, **kwargs ):
        self.parent = parent
        super().__init__(parent)
        
        self.settingsCheck = False
        
        programMenu = Menu(self, tearoff=False)
        settingsMenu = Menu(self, tearoff=False)
        helpMenu = Menu(self, tearoff=False)

        self.add_cascade(label="SMAT",underline=0, menu=programMenu)
        self.add_cascade(label="Settings",underline=0, menu=settingsMenu)
        self.add_cascade(label="Help",underline=0, menu=helpMenu)
        
        programMenu.add_command(label="Exit", underline=0, command=self.quit)

        settingsMenu.add_checkbutton(label="Autosave Options", underline=0)
        settingsMenu.add_command(label="Settings", underline=0, command=self.openSettings)
        
        helpMenu.add_command(label="About", underline=0)
        helpMenu.add_command(label="Help", underline=0)
        helpMenu.add_command(label="Github", underline=0)

    def openSettings(self):
        if self.settingsCheck == False:
            self.settingsCheck = True
            settingsWindow = SettingsWindow(self.parent)
            settingsWindow.mainloop()

class SettingsWindow(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.settingsWindow = Toplevel()
        self.settingsWindow.title("Settings")
        self.settingsWindow.resizable(False, False)
        self.focus_set()
        self.settingsWindow.protocol("WM_DELETE_WINDOW", self.onClose)
    
        self.settingsLabel = Label(self.settingsWindow, text="Settings")
        self.cleanseLabel = Label(self.settingsWindow, text="Cleanse")
        self.cleanseCheckVar = IntVar()
        self.cleanseCheck = Checkbutton(self.settingsWindow, text="Cleanse", variable=self.cleanseCheckVar)
        self.aisPathLabel = Label(self.settingsWindow, text="AIS Path")
        self.aisPathEntry = Entry(self.settingsWindow, font='arial 14', fg='grey')
        self.aisPathEntry.insert(0, 'Enter AIS Path')
        self.aisPathBtt = Button(self.settingsWindow, text="Browse", command=lambda: self.browse('ais'))
        self.cleanAisPath = Label(self.settingsWindow, text="Clean AIS Path")
        self.cleanAisPathEntry = Entry(self.settingsWindow, font='arial 14', fg='grey')
        self.cleanAisPathEntry.insert(0, 'Enter Clean AIS Path')
        self.cleanAisPathBtt = Button(self.settingsWindow, text="Browse", command=lambda: self.browse('cleanAis'))
        self.predPathLabel = Label(self.settingsWindow, text="Prediction Path")
        self.predPathEntry = Entry(self.settingsWindow, font='arial 14', fg='grey')
        self.predPathEntry.insert(0, 'Enter Prediction Path')
        self.predPathBtt = Button(self.settingsWindow, text="Browse", command=lambda: self.browse('pred'))
        self.saveFiguresLabel = Label(self.settingsWindow, text="Save Figures")
        self.saveFiguresCheckVar = IntVar()
        self.saveFiguresCheck = Checkbutton(self.settingsWindow, text="Save Figures", variable=self.saveFiguresCheckVar)

        self.settingsLabel.grid(row=0, column=0, sticky=N, padx=10, pady=2)
        self.cleanseLabel.grid(row=1, column=0, sticky=N, padx=10, pady=2)
        self.cleanseCheck.grid(row=2, column=0, sticky=N, padx=10, pady=2)
        self.aisPathLabel.grid(row=3, column=0, sticky=N, padx=10, pady=2)
        self.aisPathEntry.grid(row=4, column=0, sticky=N, padx=10, pady=2)
        self.aisPathBtt.grid(row=4, column=1, sticky=N, padx=10, pady=2)
        self.cleanAisPath.grid(row=6, column=0, sticky=N, padx=10, pady=2)
        self.cleanAisPathEntry.grid(row=7, column=0, sticky=N, padx=10, pady=2)
        self.cleanAisPathBtt.grid(row=7, column=1, sticky=N, padx=10, pady=2)
        self.predPathLabel.grid(row=9, column=0, sticky=N, padx=10, pady=2)
        self.predPathEntry.grid(row=10, column=0, sticky=N, padx=10, pady=2)
        self.predPathBtt.grid(row=10, column=1, sticky=N, padx=10, pady=2)
        self.saveFiguresLabel.grid(row=12, column=0, sticky=N, padx=10, pady=2)
        self.saveFiguresCheck.grid(row=13, column=0, sticky=N, padx=10, pady=2)
           
    def browse(self, file):
        filename = fd.askopenfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file == 'ais':
            self.aisPathEntry.delete(0, END)
            self.aisPathEntry.insert(0, filename) 
        elif file == 'cleanAis':
            self.cleanAisPathEntry.delete(0, END)
            self.cleanAisPathEntry.insert(0, filename)
        elif file == 'pred':
            self.predPathEntry.delete(0, END)
            self.predPathEntry.insert(0, filename)

    def onClose(self):
        self.parent.settingsCheck = False
        self.settingsWindow.destroy()

class MainApplication(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.menuBar = MenuBar(self)
        self.parent.config(menu=self.menuBar)
        self.plotFrame = plotFrame(self)
        self.plotFrame.grid(row=0, column=1, sticky=NSEW)
        self.outputFrame = outputFrame(self)
        self.outputFrame.grid(row=0, column=2, sticky=NSEW)
        self.inputFrame = inputFrame(self, output_frame=self.outputFrame)
        self.inputFrame.grid(row=0, column=0, sticky=NSEW)
        self.background = BackgroundFunctionality(self, output_frame=self.outputFrame, input_frame=self.inputFrame)
        global GlobalBackground
        GlobalBackground = self.background
        
        
if __name__ == "__main__":
    root = Tk()
    #root.title("Super Mega Awesome AIS Prediction Tool 3000 (SMAAPT3K)")
    root.title("Super Mega AIS Tool - Series 0 (SMAT-S0)")
    root.resizable(False, False)
    
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
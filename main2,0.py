from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import tkinter.messagebox as msg
import vector_based.prediction as prediction
import vector_based.plot as plot
import vector_based.map as map
from PIL import ImageTk, Image 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import datetime
import pickle
import webbrowser
# Please ignore the squiggly lines below, they are there to make the code look pretty
import cartopy.crs as ccrs
import cartopy
import cartopy.feature as cfeature
import sv_ttk
# Please ignore the squiggly lines above, they are there to make the code look pretty

class inputFrame(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.availShips = None

        #Widgets
        self.availableMMsisLabel = ttk.Label(self, text ="Available MMSI's")
        self.availableMMsis = Variable(self)
        self.mmsiTree = ttk.Treeview(self, height=5, columns=('c1', 'c2'), show='headings')
        self.mmsiEntryBox = ttk.Entry(self, font='arial 14')
        self.mmsiEntryBox.insert(0, 'Enter MMSI')
        self.mmsiEntryBox.bind("<FocusIn>", lambda args: self.focus_in_entry_box(self.mmsiEntryBox))
        self.mmsiEntryBox.bind("<FocusOut>", lambda args: self.focus_out_entry_box(self.mmsiEntryBox, 'Enter MMSI'))
        self.predMethodLabel = ttk.Label(self, text="Prediction Methods")
        self.nnVar = IntVar()
        self.nnCheck = ttk.Checkbutton(self, text="Neural Network", variable=self.nnVar, command=lambda: self.nerualNetworkChoices(self.nnVar.get()))
        self.nnVariantLabelFrame = ttk.LabelFrame(self, text="Neural Network Variants")
        self.nnVariantLabel = ttk.Label(self.nnVariantLabelFrame, text="Select one or more variants below")
        self.nnChoiceCheckVar = IntVar()
        self.nnChoiceCheck = ttk.Checkbutton(self.nnVariantLabelFrame, text="CNN", variable=self.nnChoiceCheckVar)
        self.nnChoiceCheckVar2 = IntVar()
        self.nnChoiceCheck2 = ttk.Checkbutton(self.nnVariantLabelFrame, text="LSTM", variable=self.nnChoiceCheckVar2)
        self.nnChoiceCheckVar3 = IntVar()
        self.nnChoiceCheck3 = ttk.Checkbutton(self.nnVariantLabelFrame, text="RNN", variable=self.nnChoiceCheckVar3)
        self.vectorVar = IntVar()
        self.vectorCheck = ttk.Checkbutton(self, text="Vector Based", variable=self.vectorVar)
        self.additionalOptionsLabel = ttk.Label(self, text="Additional Options")
        self.compShipsVar = IntVar()
        self.compShipsCheck = ttk.Checkbutton(self, text="Compare to other ships", variable=self.compShipsVar, command=lambda: self.show_multi_listbox(self.compShipsVar.get()))
        self.multiListboxLabel = ttk.Label(self, text="select one or more from the list below")
        self.multiListbox = Listbox(self, height=5, listvariable=self.availableMMsis, selectmode='multiple')
        self.buttonFrame = ttk.Frame(self)
        self.predButton = ttk.Button(self.buttonFrame, text="Predict", command=lambda: self.predict())
        self.errorLabel = ttk.Label(self, text="Error: You seem to have fucked up!")

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
        #self.additionalOptionsLabel.grid(row=11, column=0, sticky=W, padx=10, pady=2)
        #self.compShipsCheck.grid(row=12, column=0, sticky=W, padx=10, pady=2)
        #self.multiListboxLabel.grid(row=13, column=0, sticky=W, padx=10, pady=2)
        self.buttonFrame.grid(row=14, column=0, sticky=W, padx=10, pady=2)
        self.predButton.grid(row=0, column=0, sticky=W, padx=10, pady=2)

        self.multiListbox.bind('<<ListboxSelect>>', self.multiListbox_select)
        self.mmsiTree.bind('<<TreeviewSelect>>', self.treeSelect)

    def ready(self):
            self.parent.background.loadSettings()
            self.availShips = self.parent.background.getData('data/boats.csv')
            self.nerualNetworkChoices(self.nnVar.get())
            self.constructTree()

    def constructTree(self):
        self.mmsiTree.column("# 1", width=135, anchor='w')
        self.mmsiTree.heading("# 1", text="Vessel")
        self.mmsiTree.column("# 2", width=90, anchor='w')
        self.mmsiTree.heading("# 2", text="MMSI")
        
        for ship in self.availShips['MMSI'].unique():
            self.mmsiTree.insert("", "end", values=(self.availShips.loc[self.availShips['MMSI'] == ship, 'VesselName'].iloc[0], ship))

    def treeSelect(self, event):
        print('Treeview selection: ', self.mmsiTree.item(self.mmsiTree.selection())['values'][1])
        self.mmsiEntryBox.delete(0, END)
        self.mmsiEntryBox.insert(0, self.mmsiTree.item(self.mmsiTree.selection())['values'][1])
        
    def focus_out_entry_box(self, widget, widget_text):
        widget.delete(0, END)
        widget.insert(0, widget_text)

    def focus_in_entry_box(self, widget):
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
        selectedIndices = self.multiListbox.curselection()
        selectedItems = []
        for index in selectedIndices:
            selectedItems.append(self.multiListbox.get(index))
        print(selectedItems)

    def predict(self):
        self.errorLabel.grid_forget()
        self.parent.background.clearPredCsv()
        self.parent.background.saveSettings()
        #self.parent.outputFrame.clearOutput()
        while True:
            try:
                input = self.mmsiEntryBox.get()
                if(int(input) in self.availShips['MMSI'].unique()):
                    if(self.nnVar.get() == 1):
                        if(self.nnChoiceCheckVar.get() == 1):
                            self.parent.outputFrame.showOutput('CNN Based has yet to be implemented\n', True, 'error')
                        if(self.nnChoiceCheckVar2.get() == 1):
                            self.parent.outputFrame.showOutput('LSTM Based has yet to be implemented\n', True, 'error')
                        if(self.nnChoiceCheckVar3.get() == 1):
                            self.parent.outputFrame.showOutput('RNN Based has yet to be implemented\n', True, 'error')
                        elif(self.nnChoiceCheckVar.get() == 0 and self.nnChoiceCheckVar2.get() == 0 and self.nnChoiceCheckVar3.get() == 0):
                            self.parent.outputFrame.showOutput('Error: No neural network variant selected\n', True, 'error')
                            break
                    if(self.vectorVar.get() == 1):
                        prediction.predict(input)
                        intvOutput = prediction.predict_intv()
                        self.parent.outputFrame.showOutput('Vector Based\n', True)
                        self.parent.outputFrame.showOutput(intvOutput, False)
                        self.parent.background.simpLogger()
                        plot.plot()
                        plot.actualToPred()
                    if(self.compShipsVar.get() == 1):
                        self.multiListbox_select(0)
                    elif(self.vectorVar.get() == 0 and self.nnVar.get() == 0):
                        self.parent.outputFrame.showOutput('Error: No prediction method selected\n', True, 'error')
                        break 
                    break
            except:
                self.parent.outputFrame.showOutput('Prediction encountered an exception\n', True, 'error')
                break

class plotFrame(Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.showPlot = False
        
        #Widgets
        self.buttonFrame = ttk.Frame(self)
        self.imageboxLabel = ttk.Label(self, text="Map")
        self.imagebox = ttk.Label(self)
        self.imagebox.configure(background='black')
        self.toolBox = ttk.Frame(self)
        self.mapButton = ttk.Button(self.buttonFrame, text='Map', command=lambda: [self.worldMap(True), self.imageboxLabel.configure(text='Map')])
        self.plot1 = ttk.Button(self.buttonFrame, text='Act & Pred', command=lambda: [self.worldMap(False), self.showFigure('figures/actVsPred.obj'), self.imageboxLabel.configure(text='Actual vs Predicted')])
        self.plot2 = ttk.Button(self.buttonFrame, text='Act -> Pred', command=lambda: [self.worldMap(False), self.showFigure('figures/predPlotArrows.obj'), self.imageboxLabel.configure(text='Actual to Predicted')])
        self.plot3 = ttk.Button(self.buttonFrame, text='Collisions', command=lambda: [self.worldMap(False), self.showBackForw()])
        
        #Widget Placement        
        self.buttonFrame.grid(row=0, column=0, sticky=N, padx=10, pady=2)
        self.mapButton.grid(row=0, column=0, sticky=W, padx=10, pady=2)
        self.plot1.grid(row=0, column=1, sticky=W, padx=10, pady=2)
        self.plot2.grid(row=0, column=2, sticky=W, padx=10, pady=2)
        self.plot3.grid(row=0, column=3, sticky=W, padx=10, pady=2)
        self.imageboxLabel.grid(row=1, column=0, sticky=N, padx=10, pady=2)
        self.imagebox.grid(row=2, column=0, sticky=W, padx=10, pady=2)
        self.toolBox.grid(row=3, column=0, sticky=W, padx=10, pady=2)

    def showFigure(self, path):
        fig = plot.Load_plot(path)
        plt.figure(figsize=(12,6))
        figure = FigureCanvasTkAgg(fig , master =self.imagebox)
        toolbar_frame = Frame(self.imagebox)
        
        if self.showPlot:
            figure.get_tk_widget().grid_forget()
            toolbar_frame.destroy()
        
        figure.draw()
        toolbar_frame = Frame(self.toolBox)
        toolbar = self.CustomToolbar(figure, toolbar_frame)
        toolbar_frame.grid(row=0, column=0)
        figure.get_tk_widget().grid(row=0, column=0)
        self.showPlot = True
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
            ax.margins(666,666)
            sc = plt.scatter(self.parent.inputFrame.availShips['LON'], self.parent.inputFrame.availShips['LAT'], s=0.1, c='red', marker='*', transform=ccrs.PlateCarree())
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
                text = 'Vessel: {}'.format(self.parent.inputFrame.availShips['VesselName'].iloc[ind["ind"][0]]) + '\n' + 'MMSI: {}'.format(self.parent.inputFrame.availShips['MMSI'].iloc[ind["ind"][0]]) + '\n' + 'Latitude: {}'.format(self.parent.inputFrame.availShips['LAT'].iloc[ind["ind"][0]]) + '\n' + 'Longitude: {}'.format(self.parent.inputFrame.availShips['LON'].iloc[ind["ind"][0]]) + '\n' + 'BaseDateTime: {}'.format(self.parent.inputFrame.availShips['BaseDateTime'].iloc[ind["ind"][0]]) + '\n' + 'SOG: {}'.format(self.parent.inputFrame.availShips['SOG'].iloc[ind["ind"][0]]) + '\n' + 'COG: {}'.format(self.parent.inputFrame.availShips['COG'].iloc[ind["ind"][0]]) + '\n' + 'Heading: {}'.format(self.parent.inputFrame.availShips['Heading'].iloc[ind["ind"][0]])
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
            
            if self.showPlot:
                figure.get_tk_widget().grid_forget()
                toolbar_frame.destroy()
            
            if toPlotOrNotToPlot:
                figure.draw()
            toolbar_frame = Frame(self.toolBox)
            toolbar = self.CustomToolbar(figure, toolbar_frame)
            toolbar_frame.grid(row=0, column=0)
            figure.get_tk_widget().grid(row=0, column=0)
            self.showPlot = True

            if not toPlotOrNotToPlot:
                deactivate()

    class CustomToolbar(NavigationToolbar2Tk):    
        def __init__(self, canvas, parent):
            self.toolitems = (
                ('Home', 'Reset original view', 'home', 'home'),
                ('Back', 'Back to previous view', 'back', 'back'),
                ('Forward', 'Forward to next view', 'forward', 'forward'),
                ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
                ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
                (None, None, None, None),
                ('Save', 'Save the figure', 'filesave', 'save_figure'),
                )
            super().__init__(canvas, parent)

class outputFrame(Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        #Widgets
        self.outputLabel = ttk.Label(self, text="Console")
        self.outputText = Text(self, height=40, width=50)
        self.outputText.configure(state='disabled')
        self.outputText.tag_configure('time', foreground='green')
        self.outputText.tag_configure('error', foreground='red')
        
        #Widget Placement
        self.outputLabel.grid(row=0, column=0, sticky=N, padx=10, pady=2)
        self.outputText.grid(row=1, column=0, sticky=NSEW, padx=10, pady=2)
        
    def showOutput(self, output, showTime, *args):
        self.outputText.configure(state='normal')
        if showTime:
            self.outputText.insert(END, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n', 'time' )
        for i in range (len(output)):
            if args:
                self.outputText.insert(END, output[i], 'error')
            else:
                self.outputText.insert(END, output[i])
        self.outputText.insert(END, '\n')
        self.outputText.see(END)
        self.outputText.configure(state='disabled')
        
    def clearOutput(self):
        self.outputText.configure(state='normal')
        self.outputText.delete('1.0', END)
        self.outputText.configure(state='disabled')
        
class BackgroundFunctionality():
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent

    def simpLogger(self):
        text = self.parent.outputFrame.outputText.get('1.0', END)
        with open('log.txt', 'a') as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n')
            f.write(text)
        
    def loadSettings(self, *args): 
        while True:
            try:
                with open('settings.txt', 'r') as f:
                    settings = f.readlines()
                for i in range(len(settings)):
                    settings[i] = int(settings[i].split('=')[1].replace('\n', ''))                    
                if settings[0] == 1:
                    self.parent.inputFrame.vectorCheck.state(['selected'])
                    self.parent.inputFrame.vectorVar.set(1)
                if settings[1] == 1:
                    self.parent.inputFrame.nnCheck.state(['selected'])
                    self.parent.inputFrame.nnVar.set(1)
                    self.parent.inputFrame.nerualNetworkChoices(1)
                    if settings[2] == 1:
                        self.parent.inputFrame.nnChoiceCheck.state(['selected'])
                        self.parent.inputFrame.nnChoiceCheckVar.set(1)
                    if settings[3] == 1:
                        self.parent.inputFrame.nnChoiceCheck2.state(['selected'])
                        self.parent.inputFrame.nnChoiceCheckVar2.set(1)
                    if settings[4] == 1:
                        self.parent.inputFrame.nnChoiceCheck3.state(['selected'])
                        self.parent.inputFrame.nnChoiceCheckVar3.set(1)
                break
            except:
                self.parent.outputFrame.showOutput('Error: Your settingsfile seems to be fucked\n')
                self.parent.inputFrame.errorLabel.grid(row=16, column=0, sticky=W, padx=10, pady=2)
                break
        
    def saveSettings(self):
        #get settings
        settings = []
        settings.append('vectorCheck='+str(self.parent.inputFrame.vectorVar.get())+str('\n'))
        settings.append('NNCheck='+str(self.parent.inputFrame.nnVar.get())+str('\n'))
        settings.append('NN1Check='+str(self.parent.inputFrame.nnChoiceCheckVar.get())+str('\n'))
        settings.append('NN2Check='+str(self.parent.inputFrame.nnChoiceCheckVar2.get())+str('\n'))
        settings.append('NN3Check='+str(self.parent.inputFrame.nnChoiceCheckVar3.get())+str('\n'))
        #save settings.txt
        with open('settings.txt', 'w') as f:
            f.writelines(settings)

    def clearPredCsv(self):
        with open('data/predictions.csv', 'w') as fp:
            fp.truncate()

    def getData(self, filePath):
        df = pd.read_csv(filePath)
        return df
        
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

        settingsMenu.add_checkbutton(label="Remember selections", underline=0)
        settingsMenu.add_command(label="Additonal settings", underline=0, command=self.openSettings)
        
        helpMenu.add_command(label="About", underline=0)
        helpMenu.add_command(label="Help", underline=0)
        helpMenu.add_command(label="Github", underline=0, command=lambda: webbrowser.open_new('https://github.com/Ravnholt7507/P7-projekt'))

    def openSettings(self):
        print('On Open: ', self.settingsCheck)
        if self.settingsCheck == False:
            self.settingsCheck = True
            settingsWindow = SettingsWindow(self.parent)
            settingsWindow.bind("<Destroy>", lambda args: self.onClose())
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
    
        self.cleanseLabel = ttk.Label(self.settingsWindow, text="Cleanse")
        self.cleanseCheckVar = IntVar()
        self.cleanseCheck = ttk.Checkbutton(self.settingsWindow, text="Cleanse", variable=self.cleanseCheckVar)
        self.aisPathLabel = ttk.Label(self.settingsWindow, text="AIS Path")
        self.aisPathEntry = ttk.Entry(self.settingsWindow, font='arial 14')
        self.aisPathEntry.insert(0, 'Enter AIS Path')
        self.aisPathBtt = ttk.Button(self.settingsWindow, text="Browse", command=lambda: self.browse('ais'))
        self.cleanAisPath = ttk.Label(self.settingsWindow, text="Clean AIS Path")
        self.cleanAisPathEntry = ttk.Entry(self.settingsWindow, font='arial 14')
        self.cleanAisPathEntry.insert(0, 'Enter Clean AIS Path')
        self.cleanAisPathBtt = ttk.Button(self.settingsWindow, text="Browse", command=lambda: self.browse('cleanAis'))
        self.predPathLabel = ttk.Label(self.settingsWindow, text="Prediction Path")
        self.predPathEntry = ttk.Entry(self.settingsWindow, font='arial 14')
        self.predPathEntry.insert(0, 'Enter Prediction Path')
        self.predPathBtt = ttk.Button(self.settingsWindow, text="Browse", command=lambda: self.browse('pred'))
        self.saveFiguresLabel = ttk.Label(self.settingsWindow, text="Save Figures")
        self.saveFiguresCheckVar = IntVar()
        self.saveFiguresCheck = ttk.Checkbutton(self.settingsWindow, text="Save Figures", variable=self.saveFiguresCheckVar)

        self.cleanseLabel.grid(row=1, column=0, sticky=W, padx=10, pady=2)
        self.cleanseCheck.grid(row=2, column=0, sticky=W, padx=10, pady=2)
        self.aisPathLabel.grid(row=3, column=0, sticky=W, padx=10, pady=2)
        self.aisPathEntry.grid(row=4, column=0, sticky=W, padx=10, pady=2)
        self.aisPathBtt.grid(row=4, column=1, sticky=W, padx=10, pady=2)
        self.cleanAisPath.grid(row=6, column=0, sticky=W, padx=10, pady=2)
        self.cleanAisPathEntry.grid(row=7, column=0, sticky=W, padx=10, pady=2)
        self.cleanAisPathBtt.grid(row=7, column=1, sticky=W, padx=10, pady=2)
        self.predPathLabel.grid(row=9, column=0, sticky=W, padx=10, pady=2)
        self.predPathEntry.grid(row=10, column=0, sticky=W, padx=10, pady=2)
        self.predPathBtt.grid(row=10, column=1, sticky=W, padx=10, pady=2)
        self.saveFiguresLabel.grid(row=12, column=0, sticky=W, padx=10, pady=2)
        self.saveFiguresCheck.grid(row=13, column=0, sticky=W, padx=10, pady=2)
           
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
        print('onclose: ' + str(self.parent.settingsCheck))
        self.settingsWindow.destroy()

class MainApplication(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.background = BackgroundFunctionality(self)
        self.menuBar = MenuBar(self)
        self.parent.config(menu=self.menuBar)
        self.inputFrame = inputFrame(self)
        self.inputFrame.grid(row=0, column=0, sticky=NSEW)
        self.plotFrame = plotFrame(self)
        self.plotFrame.grid(row=0, column=1, sticky=NSEW)
        self.outputFrame = outputFrame(self)
        self.outputFrame.grid(row=0, column=2, sticky=NSEW)
        self.inputFrame.ready()
        self.plotFrame.mapButton.invoke()

if __name__ == "__main__":    
    root = Tk()
    icon = Image.open('icon.png')
    photo = ImageTk.PhotoImage(icon)
    root.iconphoto(True, photo)
    #root.title("Super Mega Awesome AIS Prediction Tool 3000 (SMAAPT3K)")
    root.title("Super Mega AIS Tool - Series 0 (SMAT-S0)")
    root.resizable(False, False)
    sv_ttk.set_theme("light")
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
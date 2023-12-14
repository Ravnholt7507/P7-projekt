from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import tkinter.messagebox as msg
import vector_based.prediction as prediction
#import all_collisions as all_collisions
from PIL import ImageTk, Image 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection
import matplotlib.collections
import seaborn as sns
import mplcursors
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
            self.availShips = self.parent.background.getData('data/output.csv')
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
                        self.parent.outputFrame.showOutput('Vector Based\n', True)
                        prediction.predict(input, 'data/boats.csv')
                        #intvOutput = prediction.predict_intv()
                        self.parent.outputFrame.showOutput('Placeholder', False)
                        self.parent.background.simpLogger()
                        #self.parent.plotFrame.worldMap(True, 'data/predictions.csv')
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
        self.map = None

        #Widgets
        self.buttonFrame = ttk.Frame(self)
        self.imageboxLabel = ttk.Label(self, text="Map")
        self.imagebox = ttk.Label(self)
        self.imagebox.configure(background='black')
        self.toolBox = ttk.Frame(self)
        self.drawActualBtt = ttk.Button(self.buttonFrame, text='Draw Actual Path', command=lambda: self.map.scatterActual())
        self.drawPredBtt = ttk.Button(self.buttonFrame, text='Draw Predicted Path', command=lambda: self.map.drawPredictedPath())
        self.heatMapBtt = ttk.Button(self.buttonFrame, text='Heatmap', command=lambda: self.map.heatMap())
        #self.collisionsBtt = ttk.Button(self.buttonFrame, text='Collisions', command=lambda: self.map.collissions())
        self.zoomPredBtt = ttk.Button(self.buttonFrame, text='Zoom to Point', command=lambda: self.map.zoomToPred())
        self.resetMapBtt = ttk.Button(self.buttonFrame, text='Reset Map', command=lambda: self.map.reset())
        self.demo2btt = ttk.Button(self.buttonFrame, text='Live Demo', command=lambda: self.map.liveDemoClassBased())
        self.updateLiveDemoBtt = ttk.Button(self.buttonFrame, text='Update Live Demo', command=lambda: self.map.updateLiveDemo())        
        
        #Widget Placement        
        self.buttonFrame.grid(row=0, column=0, sticky=N, padx=10, pady=2)
        self.drawActualBtt.grid(row=0, column=0, sticky=W, padx=10, pady=2)
        self.drawPredBtt.grid(row=0, column=1, sticky=W, padx=10, pady=2)
        self.heatMapBtt.grid(row=0, column=2, sticky=W, padx=10, pady=2)
        #self.collisionsBtt.grid(row=0, column=3, sticky=W, padx=10, pady=2)       
        self.zoomPredBtt.grid(row=0, column=4, sticky=W, padx=10, pady=2)
        self.resetMapBtt.grid(row=0, column=5, sticky=W, padx=10, pady=2)
        self.demo2btt.grid(row=0, column=7, sticky=W, padx=10, pady=2)
        self.updateLiveDemoBtt.grid(row=1, column=7, sticky=W, padx=10, pady=2)
        
        self.imagebox.grid(row=1, column=0, sticky=W, padx=10, pady=2)
        self.imagebox.columnconfigure(0, weight=1)
        self.imagebox.rowconfigure(0, weight=1)
        self.toolBox.grid(row=2, column=0, sticky=W, padx=10, pady=2)

    class CustomToolbar(NavigationToolbar2Tk):    
        def __init__(self, canvas, parent):
            self.toolitems = (
                #('Home', 'Reset original view', 'home', 'home'),
                #('Back', 'Back to previous view', 'back', 'back'),
                #('Forward', 'Forward to next view', 'forward', 'forward'),
                ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
                ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
                (None, None, None, None),
                ('Save', 'Save the figure', 'filesave', 'save_figure'),
                )
            super().__init__(canvas, parent)

    class worldMap(Frame):
        def __init__(self, parent, *args, **kwargs):
            self.parent = parent
            
            self.fig,self.ax = plt.subplots()
            self.plt = plt
            self.sns = sns
            
            self.ActDf = self.parent.parent.inputFrame.availShips
            
            ccrs.PlateCarree()
            self.plt.axes(projection=ccrs.PlateCarree())

            self.norm = plt.Normalize(1,4)
            self.cmap = plt.cm.RdYlGn
            self.c = np.random.randint(1,5,size=757757)

            self.fig = plt.figure(figsize=(12, 6))
            
            self.ax = self.fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
            self.ax.add_feature(cartopy.feature.OCEAN)
            self.ax.add_feature(cartopy.feature.LAND, edgecolor='black')
            self.ax.add_feature(cartopy.feature.LAKES, edgecolor='black')
            self.ax.add_feature(cartopy.feature.RIVERS)
            self.ax.margins(666666666,66666666)
            self.first = None
            self.last = None
            self.remainder = None
            self.FLRhold = []
            self.predPath = None
            self.hMap = None
            self.max_cluster = 16
            self.intSecPoints = []
            self.liveData = None
            self.collissionsData = None
            self.demoStep = 0
            self.liveDemoCurrent = None
            self.liveDemoCurrentPred = None
            self.liveDemoThresholdCicles = []
            self.boats = []
            self.boatLocations = [[],[]]
            self.predictedBoatLocations = [[],[]]
            self.patches = []
            self.patchCollection = None
            self.lineCollection = None
            self.paths = []
            self.pathCollection = None
            self.demoDF = pd.DataFrame(columns=['BaseDateTime','MMSI','LAT','LON','SOG','COG','VesselName','predictedLAT','predictedLON','locationThresholdLAT','locationThresholdLON','radiusThreshold','thresholdExceeded','currentModel'])
            self.intersections = []
            self.intersectionsScatter = None
            self.intersectionsLines = []
            self.collisionCircles = []
            self.patchCollection2 = None
            self.pathCollection2 = None
            
            self.plt.tight_layout()
            self.legendHandles = []
            self.legendLabels = []
            self.plt.legend()
            
            self.annotConId = None
            self.liveDemoAnnotConId = None
            self.removeAnot = None
            self.zoomConId = self.fig.canvas.mpl_connect('scroll_event',self.zoom_factory(self.ax, 1.5))
            self.pickConId = self.fig.canvas.mpl_connect('pick_event', self.onPick)
            
            self.figure = FigureCanvasTkAgg(self.fig , master =self.parent.imagebox)
            self.toolbar_frame = Frame(self.parent.toolBox)
            self.toolbar = self.parent.CustomToolbar(self.figure, self.toolbar_frame)
            self.toolbar_frame.grid(row=0, column=0)
            self.figure.get_tk_widget().grid(row=0, column=0)
            
        """ def annotate(self, sel):
            index = sel.index
            text = None
            if sel.artist == self.first:
                text = 'Vessel: {}'.format(self.FLRhold[0].iloc[index]['VesselName']) + '\n' + 'MMSI: {}'.format(self.FLRhold[0].iloc[index]['MMSI']) + '\n' + 'Latitude: {}'.format(self.FLRhold[0].iloc[index]['LAT']) + '\n' + 'Longitude: {}'.format(self.FLRhold[0].iloc[index]['LON']) + '\n' + 'BaseDateTime: {}'.format(self.FLRhold[0].iloc[index]['BaseDateTime']) + '\n' + 'SOG: {}'.format(self.FLRhold[0].iloc[index]['SOG']) + '\n' + 'COG: {}'.format(self.FLRhold[0].iloc[index]['COG']) + '\n' + 'Heading: {}'.format(self.FLRhold[0].iloc[index]['Heading'])
            elif sel.artist == self.last:
                text = 'Vessel: {}'.format(self.FLRhold[1].iloc[index]['VesselName']) + '\n' + 'MMSI: {}'.format(self.FLRhold[1].iloc[index]['MMSI']) + '\n' + 'Latitude: {}'.format(self.FLRhold[1].iloc[index]['LAT']) + '\n' + 'Longitude: {}'.format(self.FLRhold[1].iloc[index]['LON']) + '\n' + 'BaseDateTime: {}'.format(self.FLRhold[1].iloc[index]['BaseDateTime']) + '\n' + 'SOG: {}'.format(self.FLRhold[1].iloc[index]['SOG']) + '\n' + 'COG: {}'.format(self.FLRhold[1].iloc[index]['COG']) + '\n' + 'Heading: {}'.format(self.FLRhold[1].iloc[index]['Heading'])
            elif sel.artist == self.remainder:
                text = 'Vessel: {}'.format(self.FLRhold[2].iloc[index]['VesselName']) + '\n' + 'MMSI: {}'.format(self.FLRhold[2].iloc[index]['MMSI']) + '\n' + 'Latitude: {}'.format(self.FLRhold[2].iloc[index]['LAT']) + '\n' + 'Longitude: {}'.format(self.FLRhold[2].iloc[index]['LON']) + '\n' + 'BaseDateTime: {}'.format(self.FLRhold[2].iloc[index]['BaseDateTime']) + '\n' + 'SOG: {}'.format(self.FLRhold[2].iloc[index]['SOG']) + '\n' + 'COG: {}'.format(self.FLRhold[2].iloc[index]['COG']) + '\n' + 'Heading: {}'.format(self.FLRhold[2].iloc[index]['Heading'])
            sel.annotation.set_text(text) """
            
        def annotate(self, sel):
            index = sel.index
            text = None
            if sel.artist == self.first:
                text = 'Vessel: {}'.format(self.FLRhold[0].iloc[index]['VesselName']) + '\n' + 'MMSI: {}'.format(self.FLRhold[0].iloc[index]['MMSI']) + '\n' + 'Latitude: {}'.format(self.FLRhold[0].iloc[index]['LAT']) + '\n' + 'Longitude: {}'.format(self.FLRhold[0].iloc[index]['LON']) + '\n' + 'BaseDateTime: {}'.format(self.FLRhold[0].iloc[index]['BaseDateTime']) + '\n' + 'SOG: {}'.format(self.FLRhold[0].iloc[index]['SOG']) + '\n' + 'COG: {}'.format(self.FLRhold[0].iloc[index]['COG']) + '\n' + 'Current Model: {}'.format(self.FLRhold[0].iloc[index]['currentModel'])
            elif sel.artist == self.last:
                text = 'Vessel: {}'.format(self.FLRhold[1].iloc[index]['VesselName']) + '\n' + 'MMSI: {}'.format(self.FLRhold[1].iloc[index]['MMSI']) + '\n' + 'Latitude: {}'.format(self.FLRhold[1].iloc[index]['LAT']) + '\n' + 'Longitude: {}'.format(self.FLRhold[1].iloc[index]['LON']) + '\n' + 'BaseDateTime: {}'.format(self.FLRhold[1].iloc[index]['BaseDateTime']) + '\n' + 'SOG: {}'.format(self.FLRhold[1].iloc[index]['SOG']) + '\n' + 'COG: {}'.format(self.FLRhold[1].iloc[index]['COG']) + '\n' + 'Current Model: {}'.format(self.FLRhold[1].iloc[index]['currentModel'])
            elif sel.artist == self.remainder:
                text = 'Vessel: {}'.format(self.FLRhold[2].iloc[index]['VesselName']) + '\n' + 'MMSI: {}'.format(self.FLRhold[2].iloc[index]['MMSI']) + '\n' + 'Latitude: {}'.format(self.FLRhold[2].iloc[index]['LAT']) + '\n' + 'Longitude: {}'.format(self.FLRhold[2].iloc[index]['LON']) + '\n' + 'BaseDateTime: {}'.format(self.FLRhold[2].iloc[index]['BaseDateTime']) + '\n' + 'SOG: {}'.format(self.FLRhold[2].iloc[index]['SOG']) + '\n' + 'COG: {}'.format(self.FLRhold[2].iloc[index]['COG']) + '\n' + 'Current Model: {}'.format(self.FLRhold[2].iloc[index]['currentModel'])
            sel.annotation.set_text(text)

        def zoom_factory(self, ax,base_scale = 2.):
            def zoom_fun(event):
                # get the current x and y limits
                cur_xlim = ax.get_xlim()
                cur_ylim = ax.get_ylim()
                cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
                cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
                xdata = event.xdata # get event x location
                ydata = event.ydata # get event y location
                if event.button == 'up':
                    # deal with zoom in
                    scale_factor = 1/base_scale
                elif event.button == 'down':
                    # deal with zoom out
                    scale_factor = base_scale
                else:
                    # deal with something that should never happen
                    scale_factor = 1
                    print(event.button)
                # set new limits
                ax.set_xlim([xdata - cur_xrange*scale_factor,
                            xdata + cur_xrange*scale_factor])
                ax.set_ylim([ydata - cur_yrange*scale_factor,
                            ydata + cur_yrange*scale_factor])
                plt.draw() # force re-draw

            fig = ax.get_figure() # get the figure of interest
            # attach the call back
            fig.canvas.mpl_connect('scroll_event',zoom_fun)

            #return the function
            return zoom_fun
    
        def onPick(self, event):
            if event.mouseevent.button == 1:
                print(event)
                ind = None
                if event.artist == self.first:
                    print('first')
                    ind = event.ind[0]
                    mmsi = self.FLRhold[0].iloc[ind]['MMSI']
                elif event.artist == self.last:
                    print('last')
                    ind = event.ind[0]
                    mmsi = self.FLRhold[1].iloc[ind]['MMSI']
                elif event.artist == self.remainder:
                    print('remainder')
                    ind = event.ind[0]
                    mmsi = self.FLRhold[2].iloc[ind]['MMSI']
                print(mmsi)
                self.parent.parent.inputFrame.mmsiEntryBox.delete(0, END)
                self.parent.parent.inputFrame.mmsiEntryBox.insert(0, mmsi)

        def scatterActual(self):
            if self.first == None and self.last == None and self.remainder == None:
                self.FLRhold.append(self.ActDf.groupby('MMSI', as_index=False).first())
                self.FLRhold.append(self.ActDf.groupby('MMSI', as_index=False).last())
                self.FLRhold.append(self.ActDf.groupby('MMSI', as_index=False).apply(lambda x: x.iloc[1:-1]))
                self.first = plt.scatter(self.FLRhold[0]['LON'], self.FLRhold[0]['LAT'], marker='o', color='green', linewidth=3, transform=ccrs.PlateCarree(), picker=True)
                self.last = plt.scatter(self.FLRhold[1]['LON'], self.FLRhold[1]['LAT'], marker='o', color='red', linewidth=3, transform=ccrs.PlateCarree(), picker = True)
                self.remainder = plt.scatter(self.FLRhold[2]['LON'], self.FLRhold[2]['LAT'], s=0.1, c='purple', marker='*', linewidths=2, transform=ccrs.PlateCarree(), picker = True)
                self.annotConId = mplcursors.cursor([self.first, self.last, self.remainder], hover=True)
                self.annotConId.connect("add", self.annotate)
                if self.predPath != None:
                    self.drawPredictedPath()
                    self.drawPredictedPath()
                self.legendHandles.append(self.first), self.legendLabels.append('First')
                self.legendHandles.append(self.last), self.legendLabels.append('Last')
                self.legendHandles.append(self.remainder), self.legendLabels.append('Remainder')
                self.ax.legend(self.legendHandles, self.legendLabels)
                self.plt.draw()

            else:
                self.first.remove()
                self.last.remove()
                self.remainder.remove()
                self.annotConId.remove()
                self.fig.canvas.mpl_disconnect(self.annotConId)
                self.legendHandles.remove(self.first), self.legendLabels.remove('First')
                self.legendHandles.remove(self.last), self.legendLabels.remove('Last')
                self.legendHandles.remove(self.remainder), self.legendLabels.remove('Remainder')
                self.ax.legend(self.legendHandles, self.legendLabels)
                self.first = None
                self.last = None
                self.remainder = None
                self.annotConId = None
                self.plt.draw()

        def drawPredictedPath(self):
            if self.predPath == None:
                predDf = self.parent.parent.background.getData('data/predictions.csv')
                self.predPath = plt.scatter(predDf['LON'], predDf['LAT'], s=0.1, c='blue', marker='*', linewidths=5, transform=ccrs.PlateCarree())
                self.legendHandles.append(self.predPath), self.legendLabels.append('Predicted')
                self.ax.legend(self.legendHandles, self.legendLabels)
                self.plt.draw()
            else:
                self.predPath.remove()
                self.legendHandles.remove(self.predPath), self.legendLabels.remove('Predicted')
                self.ax.legend(self.legendHandles, self.legendLabels)
                self.predPath = None
                self.plt.draw()

        def heatMap(self):
            #semi functional
            if self.hMap == None:
                df = self.parent.parent.background.getData('data/output.csv')
                self.hMap = sns.kdeplot(data = df, x="LON", y="LAT", cmap='Reds', fill=True, bw_method=0.1)
                self.hMap.collections[0].set_alpha(0)
                self.hMap = sns.kdeplot(data = df, x="LON", y="LAT", cmap='Reds', fill=True, bw_method=0.1)
                self.hMap.collections[0].set_alpha(0)
                self.plt.draw()
            else:
                self.__init__(self.parent)
        
        def collissions(self):
            if self.intSecPoints == []:
                if self.max_cluster == None:
                    self.max_cluster = all_collisions.all_collisions()            
                ship_data = pd.read_csv('data/ship_data.csv')
                cluster_data = ship_data[ship_data['cluster'] == self.max_cluster]
                cluster_data = cluster_data.reset_index(drop=True)
                self.intSecPoints.append(plt.scatter(cluster_data['LON'], cluster_data['LAT'], color='red', marker='*'))
                self.intSecPoints.append(plt.scatter(cluster_data['pred_lon'], cluster_data['pred_lat'], color='green', marker='*'))

                # Plot points from intersection_points.csv where the last column is 0
                intersection_points = pd.read_csv('data/intersection_points.csv', header=None)
                intersection_points.columns = ['LON', 'LAT', 'cluster', 'id','time_diff']
                intersection_points = intersection_points[intersection_points['cluster'] == self.max_cluster]
                intersection_points = intersection_points[intersection_points['id'] == 0]
                self.intSecPoints.append(plt.scatter(intersection_points['LON'], intersection_points['LAT'], color='purple', marker='*'))
                
                # Plot points from intersection_points.csv where the last column is 1
                intersection_points = pd.read_csv('data/intersection_points.csv', header=None)
                intersection_points.columns = ['LON', 'LAT', 'cluster', 'id', 'time_diff']
                intersection_points = intersection_points[intersection_points['cluster'] == self.max_cluster]
                intersection_points = intersection_points[intersection_points['id'] == 1]
                self.intSecPoints.append(plt.scatter(intersection_points['LON'], intersection_points['LAT'], color='black', marker='*'))
                self.legendHandles.append(self.intSecPoints[0]), self.legendLabels.append('Actual')
                self.legendHandles.append(self.intSecPoints[1]), self.legendLabels.append('Predicted')
                self.legendHandles.append(self.intSecPoints[2]), self.legendLabels.append('Actual Collision')
                self.legendHandles.append(self.intSecPoints[3]), self.legendLabels.append('Predicted Collision')
                self.ax.legend(self.legendHandles, self.legendLabels)
                self.plt.draw()
            else:
                for plot in self.intSecPoints:
                    plot.remove()
                self.legendHandles.remove(self.intSecPoints[0]), self.legendLabels.remove('Actual')
                self.legendHandles.remove(self.intSecPoints[1]), self.legendLabels.remove('Predicted')
                self.legendHandles.remove(self.intSecPoints[2]), self.legendLabels.remove('Actual Collision')
                self.legendHandles.remove(self.intSecPoints[3]), self.legendLabels.remove('Predicted Collision')
                self.ax.legend(self.legendHandles, self.legendLabels)
                self.intSecPoints = []
                self.plt.draw()
        
        def liveDemoClassBased(self):
            if self.liveDemoCurrent == None:
                self.liveData = self.parent.parent.background.getData('data/output.csv')
                self.collissionsData = self.parent.parent.background.getData('data/vector_colissions.csv')
                self.liveData = self.liveData.groupby('MMSI', as_index=False)
                templist = []
                for name, group in self.liveData:
                    boat = self.Boat(self, group)
                    self.boats.append(boat)    
                    for i in range (len(boat.actualPoints)):
                        self.boatLocations[0].append(boat.actualPoints[i][0])
                        self.boatLocations[1].append(boat.actualPoints[i][1])
                        self.predictedBoatLocations[0].append(boat.predPoints[i][0])
                        self.predictedBoatLocations[1].append(boat.predPoints[i][1])
                        templist.append(boat.group.iloc[0])    
                    circlePlt = plt.Circle(boat.circle[0], boat.circle[1])
                    self.patches.append(circlePlt)
                    mmsi_value = boat.group.iloc[0]['MMSI']
                    filtered_data1 = self.collissionsData.query("`time1` < `time2` and `MMSI1` == @mmsi_value")
                    filtered_data2 = self.collissionsData.query("`time1` > `time2` and `MMSI2` == @mmsi_value")                
                    boat.collisions = pd.concat([filtered_data1, filtered_data2])
                    if boat.collisions.empty == False:
                        time = boat.group.iloc[boat.demoStep-1]['BaseDateTime']
                        filtered_df = boat.collisions[(boat.collisions['time1'] == time) | (boat.collisions['time2'] == time)]
                        line_segments1 = list(zip(zip(boat.collisions['lat1'], boat.collisions['lon1']), zip(boat.collisions['vlat1'], boat.collisions['vlon1'])))
                        line_segments2 = list(zip(zip(boat.collisions['lat2'], boat.collisions['lon2']), zip(boat.collisions['vlat2'], boat.collisions['vlon2'])))
                        self.intersectionsLines.extend(line_segments1 + line_segments2)
                        intersection_points = list(zip(filtered_df['intersectionLat'], filtered_df['intersectionLon']))
                        self.intersections.extend(intersection_points)
                self.demoDF = pd.DataFrame(templist)                
                coll = matplotlib.collections.PatchCollection(self.patches, facecolors='none', edgecolors='black')
                self.patchCollection = self.ax.add_collection(coll)
                self.liveDemoCurrent = plt.scatter(self.boatLocations[0], self.boatLocations[1], color='red', marker='.', linewidths=1)
                self.liveDemoCurrentPred = plt.scatter(self.predictedBoatLocations[0], self.predictedBoatLocations[1], color='green', marker='.', linewidths=1)
                interSecLc = LineCollection(self.intersectionsLines, colors='purple', linewidths=1)
                self.pathCollection2 = self.ax.add_collection(interSecLc)
                self.intersectionsScatter = plt.scatter([x[0] for x in self.intersections], [x[1] for x in self.intersections], color='purple', marker='*', linewidths=1)

                self.legendHandles.append(self.liveDemoCurrent), self.legendLabels.append('Actual')
                self.legendHandles.append(self.liveDemoCurrentPred), self.legendLabels.append('Predicted')
                self.legendHandles.append(self.intersectionsScatter), self.legendLabels.append('Collisions')
                self.ax.legend(self.legendHandles, self.legendLabels)
                #self.liveDemoAnnotConId = mplcursors.cursor([self.liveDemoCurrent, self.liveDemoCurrentPred], hover=True)
                #self.liveDemoAnnotConId.connect("add", self.annotateLiveDemo)
                self.plt.draw()
        
        def updateLiveDemo(self):
            self.liveDemoCurrent.remove()
            self.boatLocations = [[],[]]
            self.predictedBoatLocations = [[],[]]
            self.patches = []
            self.patchCollection.remove()
            self.liveDemoCurrentPred.remove()
            self.liveDemoAnnotConId.remove()
            self.liveDemoAnnotConId = None
            if self.pathCollection != None:
                self.paths = []
                self.pathCollection.remove()
            if self.pathCollection2 != None:
                self.intersectionsLines = []
                self.pathCollection2.remove()
                self.intersectionsScatter.remove()
                self.intersections = []
            for boat in self.boats:
                boat.update()
                for i in range (len(boat.actualPoints)):
                    self.boatLocations[0].append(boat.actualPoints[i][0])
                    self.boatLocations[1].append(boat.actualPoints[i][1])
                    self.predictedBoatLocations[0].append(boat.predPoints[i][0])
                    self.predictedBoatLocations[1].append(boat.predPoints[i][1])
                circlePlt = plt.Circle(boat.circle[0], boat.circle[1])
                self.patches.append(circlePlt)
                self.paths.append(boat.actualPoints)
                if boat.collisions.empty == False:
                    time = boat.group.iloc[boat.demoStep-1]['BaseDateTime']
                    filtered_df = boat.collisions[(boat.collisions['time1'] == time) | (boat.collisions['time2'] == time)]
                    line_segments1 = list(zip(zip(boat.collisions['lat1'], boat.collisions['lon1']), zip(boat.collisions['vlat1'], boat.collisions['vlon1'])))
                    line_segments2 = list(zip(zip(boat.collisions['lat2'], boat.collisions['lon2']), zip(boat.collisions['vlat2'], boat.collisions['vlon2'])))
                    self.intersectionsLines.extend(line_segments1 + line_segments2)
                    intersection_points = list(zip(filtered_df['intersectionLat'], filtered_df['intersectionLon']))
                    self.intersections.extend(intersection_points)
            coll = matplotlib.collections.PatchCollection(self.patches, facecolors='none', edgecolors='black')
            self.patchCollection = self.ax.add_collection(coll)
            lc = matplotlib.collections.LineCollection(self.paths, colors='red', linewidths=1)
            self.pathCollection = self.ax.add_collection(lc)
            self.liveDemoCurrent = plt.scatter(self.boatLocations[0], self.boatLocations[1], color='red', marker='.', linewidths=1)
            self.liveDemoCurrentPred = plt.scatter(self.predictedBoatLocations[0], self.predictedBoatLocations[1], color='green', marker='.', linewidths=1)
            interSecLc = LineCollection(self.intersectionsLines, colors='purple', linewidths=1)
            self.pathCollection2 = self.ax.add_collection(interSecLc)
            self.intersectionsScatter = plt.scatter([x[0] for x in self.intersections], [x[1] for x in self.intersections], color='purple', marker='*', linewidths=1)
            self.liveDemoAnnotConId = mplcursors.cursor([self.liveDemoCurrent, self.liveDemoCurrentPred], hover=True)
            self.liveDemoAnnotConId.connect("add", self.annotateLiveDemo)
            self.plt.draw()
        
        class Boat():
            def __init__(self, parent, group):
                self.parent = parent
                self.group = group
                self.collisions = []
                self.demoStep = 0
                self.circle = None
                self.circlePlot = None
                self.actualPoints = []
                self.predPoints = []
                self.group["radiusThreshold"] = self.group["radiusThreshold"] / 111.32
                self.circle = ([[self.group.iloc[self.demoStep]["locationThresholdLON"], self.group.iloc[self.demoStep]["locationThresholdLAT"]], self.group.iloc[self.demoStep]["radiusThreshold"]])
                self.circlePlot = self.parent.plt.Circle(self.circle[0], self.circle[1])
                self.firstPoint = [self.group.iloc[self.demoStep]["LON"], self.group.iloc[self.demoStep]["LAT"]]
                self.firstPredPoint = [self.group.iloc[self.demoStep]["predictedLON"], self.group.iloc[self.demoStep]["predictedLAT"]]
                self.actualPoints.append(self.firstPoint)
                self.predPoints.append(self.firstPredPoint)
                self.demoStep = self.demoStep + 1
            
            def update(self):
                if self.demoStep < len(self.group):
                    if self.group.iloc[self.demoStep]["thresholdExceeded"] == False:
                        point = [self.group.iloc[self.demoStep]["LON"], self.group.iloc[self.demoStep]["LAT"]]
                        predPoint = [self.group.iloc[self.demoStep]["predictedLON"], self.group.iloc[self.demoStep]["predictedLAT"]]
                        self.actualPoints.append(point)
                        self.predPoints.append(predPoint)
                        self.demoStep = self.demoStep + 1
                    else:
                        self.actualPoints = []
                        self.predPoints = []
                        point = [self.group.iloc[self.demoStep]["LON"], self.group.iloc[self.demoStep]["LAT"]]
                        predPoint = [self.group.iloc[self.demoStep]["predictedLON"], self.group.iloc[self.demoStep]["predictedLAT"]]
                        self.actualPoints.append(point)
                        self.predPoints.append(predPoint)
                        if self.circle != ([[self.group.iloc[self.demoStep]["locationThresholdLON"], self.group.iloc[self.demoStep]["locationThresholdLAT"]], self.group.iloc[self.demoStep]["radiusThreshold"]]):
                            self.circle = ([[self.group.iloc[self.demoStep]["locationThresholdLON"], self.group.iloc[self.demoStep]["locationThresholdLAT"]], self.group.iloc[self.demoStep]["radiusThreshold"]])
                        self.demoStep = self.demoStep + 1

        def annotateLiveDemo(self, sel):
            index = sel.index
            text = None
            if sel.artist == self.liveDemoCurrent:
                text = 'Vessel: {}'.format(self.demoDF.iloc[index]['VesselName']) + '\n' + 'MMSI: {}'.format(self.demoDF.iloc[index]['MMSI']) + '\n' + 'Latitude: {}'.format(self.demoDF.iloc[index]['LAT']) + '\n' + 'Longitude: {}'.format(self.demoDF.iloc[index]['LON']) + '\n' + 'BaseDateTime: {}'.format(self.demoDF.iloc[index]['BaseDateTime']) + '\n' + 'SOG: {}'.format(self.demoDF.iloc[index]['SOG']) + '\n' + 'COG: {}'.format(self.demoDF.iloc[index]['COG'])
            elif sel.artist == self.liveDemoCurrentPred:
                text = 'Predicted point' + '\n' + 'Vessel: {}'.format(self.demoDF.iloc[index]['VesselName']) + '\n' + 'MMSI: {}'.format(self.demoDF.iloc[index]['MMSI']) + '\n' + 'Latitude: {}'.format(self.demoDF.iloc[index]['predictedLAT']) + '\n' + 'Longitude: {}'.format(self.demoDF.iloc[index]['predictedLON']) + '\n' + 'BaseDateTime: {}'.format(self.demoDF.iloc[index]['BaseDateTime']) + '\n' + 'SOG: {}'.format(self.demoDF.iloc[index]['SOG']) + '\n' + 'COG: {}'.format(self.demoDF.iloc[index]['COG'])
            sel.annotation.set_text(text)
  
        def zoomToPred(self):
            if self.predPath != None:
                """ self.drawPredictedPath()
                self.ax.margins(1,1)
                #self.scatterActual()
                self.plt.draw() """
                self.plt.xlim(self.predDf['LON'].min(), self.predDf['LON'].max())
                self.plt.ylim(self.predDf['LAT'].min(), self.predDf['LAT'].max())
                self.plt.draw()

        def reset(self):
            self.__init__(self.parent)
            self.plt.draw()

    def ready(self):
        self.map = self.worldMap(self)

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
        settingsMenu.add_command(label="Additional settings 2", underline=0, command=lambda: self.open())
        
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

    def open(self):
        print(self.parent.settingsWindowtest)
        if not self.parent.settingsWindowtest:
            self.parent.settingsWindowtest = settingWindow2(self.parent)

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

class settingWindow2(Frame):
    def __init__(self, parent, *args, **kwargs):
        Toplevel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.settingsWindow = Toplevel()
        self.settingsWindow.title("Settings")
        self.settingsWindow.resizable(False, False)
        self.focus_set()

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
        self.settingsWindowtest = None
        self.inputFrame.ready()
        #self.plotFrame.worldMap(True)
        self.plotFrame.ready()

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
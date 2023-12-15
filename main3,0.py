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

        self.collisionsVar = IntVar()
        self.circlesVar = IntVar()
        self.annotationsVar = IntVar()

        #Widgets
        self.inputLabel = Label(self, text="Map Functionality", font=("Helvetica", 16))
        self.buttonFrame1 = ttk.Frame(self, width=100)
        self.demoButton = ttk.Button(self.buttonFrame1, text='Prepare Demo', command=lambda: self.parent.plotFrame.map.loadBoats())
        self.stepFrame = ttk.Frame(self.buttonFrame1)
        self.stepBackButton = ttk.Button(self.stepFrame, text='Step Back')
        self.stepforwardButton = ttk.Button(self.stepFrame, text='Step Forward', command=lambda: self.parent.plotFrame.map.demo())
        self.progressBarFrame = ttk.Frame(self.buttonFrame1)
        self.progressBar = ttk.Progressbar(self.progressBarFrame, orient=HORIZONTAL, length=100, mode='determinate')
        self.progressLabel3 = ttk.Label(self.progressBarFrame, text='Loading boats...')
        self.showCollisionsButton = ttk.Checkbutton(self.buttonFrame1, text='Show Collisions', variable=self.collisionsVar, onvalue=1, offvalue=0, command=lambda: self.parent.plotFrame.map.showCollisions())
        self.circlesButton = ttk.Checkbutton(self.buttonFrame1, text='Show Threshold Circles', variable=self.circlesVar, onvalue=1, offvalue=0, command=lambda: self.parent.plotFrame.map.showThresholdCircles())
        self.annotationsButton = ttk.Checkbutton(self.buttonFrame1, text='Show Annotations', variable=self.annotationsVar, onvalue=1, offvalue=0, command=lambda: self.parent.plotFrame.map.showAnnotations())
        self.heatmapButton = ttk.Button(self.buttonFrame1, text='Heatmap', command=lambda: self.parent.plotFrame.map.heatMap())
        self.resetZoomButton = ttk.Button(self.buttonFrame1, text='Reset Zoom')
        self.resetMapButton = ttk.Button(self.buttonFrame1, text='Reset Map/Demo', command=lambda: self.parent.plotFrame.map.resetZoom())
        
        #Widget Placement
        self.inputLabel.grid(row=0, column=0, sticky=NSEW)
        self.buttonFrame1.grid(row=1, column=0, sticky=NSEW)
        self.demoButton.grid(row=0, column=0, sticky=NSEW, padx=10, pady=2)
        self.stepFrame.grid(row=0, column=0, sticky=NSEW, padx=10, pady=2)
        self.stepBackButton.grid(row=0, column=0, sticky=NSEW)
        self.stepforwardButton.grid(row=0, column=1, sticky=NSEW)
        self.progressBarFrame.grid(row=1, column=0, sticky=NSEW, padx=10, pady=2)
        self.progressBar.grid(row=0, column=1, sticky=NSEW, padx=10, pady=2)
        self.progressLabel3.grid(row=1, column=1, sticky=NSEW)
        self.showCollisionsButton.grid(row=2, column=0, sticky=NSEW, padx=10, pady=2)
        self.circlesButton.grid(row=3, column=0, sticky=NSEW, padx=10, pady=2)
        self.annotationsButton.grid(row=4, column=0, sticky=NSEW, padx=10, pady=2)
        self.heatmapButton.grid(row=5, column=0, sticky=NSEW, padx=10, pady=2)
        self.resetZoomButton.grid(row=6, column=0, sticky=NSEW, padx=10, pady=2) 
        self.resetMapButton.grid(row=7, column=0, sticky=NSEW, padx=10, pady=2)
        
    def ready(self):
        self.showCollisionsButton.invoke()
        self.circlesButton.invoke()
        self.annotationsButton.invoke()
        
        self.showCollisionsButton['state'] = 'disabled'
        self.circlesButton['state'] = 'disabled'
        self.annotationsButton['state'] = 'disabled'
        self.heatmapButton['state'] = 'disabled'
        self.resetZoomButton['state'] = 'disabled'
        self.resetMapButton['state'] = 'disabled'
        
        self.progressBarFrame.grid_remove()
        self.stepFrame.grid_remove()

class plotFrame(Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.map = None
        self.boats = []

        #Widgets
        self.imagebox = ttk.Label(self)
        self.imagebox.configure(background='black')
        self.toolBox = ttk.Frame(self)

        #Widget Placement
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
            
            #General plot setup
            self.fig,self.ax = plt.subplots()
            self.plt = plt
            self.sns = sns
            self.plt.axes(projection=ccrs.PlateCarree())
            self.fig = plt.figure(figsize=(12, 6))
            self.ax = self.fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
            self.ax.add_feature(cartopy.feature.OCEAN)
            self.ax.add_feature(cartopy.feature.LAND, edgecolor='black')
            self.ax.add_feature(cartopy.feature.LAKES, edgecolor='black')
            self.ax.add_feature(cartopy.feature.RIVERS)
            self.ax.margins(666666666,66666666)

            #live demo attributes
            self.liveData = None
            self.collissionsData = None
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
            self.collisionsScatter = None
            self.demoStep = 0
            
            self.hMap = None
            
            #additonal plot setup
            self.plt.tight_layout()
            self.legendHandles = []
            self.legendLabels = []
            self.plt.legend()
            self.plt.legend().set_visible(False)
            self.liveDemoAnnotConId = None
            self.zoomConId = self.fig.canvas.mpl_connect('scroll_event',self.zoom_factory(self.ax, 1.5))
            self.figure = FigureCanvasTkAgg(self.fig , master =self.parent.imagebox)
            self.toolbar_frame = Frame(self.parent.toolBox)
            self.toolbar = self.parent.CustomToolbar(self.figure, self.toolbar_frame)
            self.toolbar_frame.grid(row=0, column=0)
            self.figure.get_tk_widget().grid(row=0, column=0)

        def loadBoats(self):
            if self.parent.boats == []:
                self.parent.parent.outputFrame.showOutput(['Loading boats...'], True)
                liveData = pd.read_csv('data/output.csv')
                liveData = liveData.groupby('MMSI', as_index=False)
                collisionData = pd.read_csv('data/vector_colissions.csv')
                self.parent.parent.inputFrame.demoButton['state'] = 'disabled'
                self.parent.parent.inputFrame.progressBarFrame.grid()
                self.parent.parent.inputFrame.progressBar['maximum'] = len(liveData)
                for name, group in liveData:
                    boat = self.Boat(self, group)
                    self.parent.boats.append(boat)
                    mmsi_value = boat.data.iloc[0]['MMSI']
                    filtered_data1 = collisionData.query("`time1` < `time2` and `MMSI1` == @mmsi_value")
                    filtered_data2 = collisionData.query("`time1` > `time2` and `MMSI2` == @mmsi_value")
                    boat.collisions = pd.concat([filtered_data1, filtered_data2])
                    self.parent.parent.inputFrame.progressBar['value'] = self.parent.parent.inputFrame.progressBar['value'] + 1
                    self.parent.parent.inputFrame.progressBar.update()
                    self.parent.parent.inputFrame.progressLabel3['text'] = 'Loading boat {} of {}'.format(int(self.parent.parent.inputFrame.progressBar['value']), int(self.parent.parent.inputFrame.progressBar['maximum']))
            self.parent.parent.inputFrame.progressBar['value'] = 0
            self.parent.parent.inputFrame.progressBarFrame.grid_remove()
            self.parent.parent.inputFrame.demoButton.configure(text = 'Start Demo', command=lambda: self.demo())
            self.parent.parent.inputFrame.demoButton['state'] = 'normal'


        class Boat():
            def __init__(self, parent, group):
                self.parent = parent
                self.data = group
                #line below is for testing purposes
                self.data["radiusThreshold"] = self.data["radiusThreshold"] / 111.32
                self.currentStep = 0
                self.currentRow = None
                self.currentPredPoint = None
                self.currentThreshold = []
                self.pdReset = pd.DataFrame(columns=['BaseDateTime','MMSI','LAT','LON','SOG','COG','predictedLAT','predictedLON','locationThresholdLAT','locationThresholdLON','radiusThreshold','thresholdExceeded','currentModel','VesselName'])
                self.rowsInThreshhold = self.pdReset
                self.pointsInThresholdPred = self.pdReset
                self.collisions = []

            def stepForward(self):
                if self.currentStep < len(self.data):
                    if self.data.iloc[self.currentStep]["thresholdExceeded"] == False:
                        self.currentRow = self.data.iloc[self.currentStep]
                        self.rowsInThreshhold.loc[len(self.rowsInThreshhold)] = self.currentRow
                        self.currentThreshold = ([[self.data.iloc[self.currentStep]["locationThresholdLON"], self.data.iloc[self.currentStep]["locationThresholdLAT"]], self.data.iloc[self.currentStep]["radiusThreshold"]])
                        
                    elif self.data.iloc[self.currentStep]["thresholdExceeded"] == True:
                        self.currentRow = self.data.iloc[self.currentStep]
                        #delete all rows in self.rowsInThreshhold
                        self.rowsInThreshhold = pd.DataFrame(columns=self.rowsInThreshhold.columns)
                        self.rowsInThreshhold.loc[len(self.rowsInThreshhold)] = self.currentRow
                        self.currentThreshold = ([[self.data.iloc[self.currentStep]["locationThresholdLON"], self.data.iloc[self.currentStep]["locationThresholdLAT"]], self.data.iloc[self.currentStep]["radiusThreshold"]])
                    self.currentStep = self.currentStep + 1
            
        def demo(self):
            self.parent.parent.inputFrame.stepBackButton['state'] = 'disabled'
            self.parent.parent.inputFrame.stepforwardButton['state'] = 'disabled'
            if self.demoStep == 0:
                self.parent.parent.outputFrame.showOutput(['Starting demo...'], True)
                self.parent.parent.inputFrame.demoButton.grid_remove()
                self.parent.parent.inputFrame.stepFrame.grid()
            if self.demoStep != 0:
                self.parent.parent.outputFrame.showOutput(['Stepping forward...'], True)
                self.liveDemoCurrent.remove()
                self.liveDemoCurrent = None
                self.liveDemoCurrentPred.remove()
                self.liveDemoCurrentPred = None
                self.collisionsScatter.remove()
                self.collisionsScatter = None
                if self.liveDemoAnnotConId != None:
                    self.liveDemoAnnotConId.remove()
                    self.liveDemoAnnotConId = None
                if self.pathCollection != None:
                    self.pathCollection.remove()
                    self.pathCollection = None
                    self.intersectionsLines = []
                    self.patchCollection.remove()
                    self.patchCollection = None
            templist = pd.DataFrame(columns=['BaseDateTime','MMSI','LAT','LON','SOG','COG','predictedLAT','predictedLON','locationThresholdLAT','locationThresholdLON','radiusThreshold','thresholdExceeded','currentModel','VesselName'])
            patches = []
            boatLocations = [[],[]]
            predictedBoatLocations = [[],[]]
            intersectionLines = []
            intersections = []
            self.parent.parent.inputFrame.progressBarFrame.grid()
            self.parent.parent.inputFrame.progressBar['maximum'] = len(self.parent.boats)
            for boat in self.parent.boats:
                boat.stepForward()
                boatLocations[0].extend(boat.rowsInThreshhold['LON'].tolist())
                boatLocations[1].extend(boat.rowsInThreshhold['LAT'].tolist())
                predictedBoatLocations[0].extend(boat.rowsInThreshhold['predictedLON'].tolist())
                predictedBoatLocations[1].extend(boat.rowsInThreshhold['predictedLAT'].tolist())
                templist = pd.concat([templist, boat.rowsInThreshhold], ignore_index=True)
                patches.append(plt.Circle(boat.currentThreshold[0], boat.currentThreshold[1]))
                if boat.collisions.empty == False:
                    time = boat.currentRow['BaseDateTime']
                    mmsi = boat.currentRow['MMSI']
                    filtered_df = boat.collisions[((boat.collisions['time1'] == time) & (boat.collisions['MMSI1'] == mmsi)) | ((boat.collisions['time2'] == time) & (boat.collisions['MMSI2'] == mmsi))]
                    if filtered_df.empty == False:
                        intersectionLines.extend(list(zip(zip(filtered_df['lat1'], filtered_df['lon1']), zip(filtered_df['vlat1'], filtered_df['vlon1']))) + list(zip(zip(filtered_df['lat2'], filtered_df['lon2']), zip(filtered_df['vlat2'], filtered_df['vlon2']))))
                        intersection_points = list(zip(filtered_df['intersectionLat'], filtered_df['intersectionLon']))
                        intersections.extend(intersection_points)
                        #for each row in filtered_df
                        for index, row in filtered_df.iterrows():
                            if row['time1'] == time and row['MMSI1'] == mmsi:
                                self.parent.parent.outputFrame.showOutput('-'*50, False)
                                self.parent.parent.outputFrame.showOutput(['Collision detected between MMSI {} and MMSI {} at time {}!'.format(row['MMSI1'], row['MMSI2'], row['time1'])], False)
                                #print coordinates of collision
                                self.parent.parent.outputFrame.showOutput(['Collision coordinates: {}, {}'.format(row['intersectionLat'], row['intersectionLon'])], False)
                                self.parent.parent.outputFrame.showOutput('-'*50, False)
                            elif row['time2'] == time and row['MMSI2'] == mmsi:
                                self.parent.parent.outputFrame.showOutput('-'*50, False)
                                self.parent.parent.outputFrame.showOutput(['Collision detected between MMSI {} and MMSI {} at time {}!'.format(row['MMSI1'], row['MMSI2'], row['time2'])], False)
                                self.parent.parent.outputFrame.showOutput(['Collision coordinates: {}, {}'.format(row['intersectionLat'], row['intersectionLon'])], False)
                                self.parent.parent.outputFrame.showOutput('-'*50, False)

                self.parent.parent.inputFrame.progressBar['value'] = self.parent.parent.inputFrame.progressBar['value'] + 1
                self.parent.parent.inputFrame.progressBar.update()
                self.parent.parent.inputFrame.progressLabel3['text'] = 'Boat {} of {} stepping'.format(int(self.parent.parent.inputFrame.progressBar['value']), int(self.parent.parent.inputFrame.progressBar['maximum']))
            self.parent.parent.inputFrame.progressBar['value'] = 0
            self.parent.parent.inputFrame.progressBarFrame.grid_remove()
            self.demoDF = templist
            self.liveDemoCurrent = plt.scatter(boatLocations[0], boatLocations[1], color='red', marker='.', linewidths=1)
            self.liveDemoCurrentPred = plt.scatter(predictedBoatLocations[0], predictedBoatLocations[1], color='green', marker='.', linewidths=1)
            self.collisionsScatter = plt.scatter([x[0] for x in intersections], [x[1] for x in intersections], color='purple', marker='*', linewidths=1)
            lc = matplotlib.collections.LineCollection(intersectionLines, colors='purple', linewidths=1)
            pc = matplotlib.collections.PatchCollection(patches, facecolors='none', edgecolors='black')
            self.pathCollection = self.ax.add_collection(lc)
            self.patchCollection = self.ax.add_collection(pc)
            if self.demoStep == 0:
                self.legendHandles.append(self.liveDemoCurrent), self.legendLabels.append('Actual')
                self.legendHandles.append(self.liveDemoCurrentPred), self.legendLabels.append('Predicted')
                self.legendHandles.append(self.collisionsScatter), self.legendLabels.append('Collisions')
                self.ax.legend(self.legendHandles, self.legendLabels)
                self.parent.parent.inputFrame.showCollisionsButton['state'] = 'normal'
                self.parent.parent.inputFrame.circlesButton['state'] = 'normal'
                self.parent.parent.inputFrame.annotationsButton['state'] = 'normal'
                self.parent.parent.inputFrame.heatmapButton['state'] = 'normal'
            self.liveDemoAnnotConId = mplcursors.cursor(self.liveDemoCurrent, hover=True)
            self.liveDemoAnnotConId.connect("add", self.annotateLiveDemo)
            self.plt.draw()
            self.demoStep = self.demoStep + 1
            self.showCollisions()
            self.showThresholdCircles()
            self.showAnnotations()
            self.parent.parent.inputFrame.stepBackButton['state'] = 'normal'
            self.parent.parent.inputFrame.stepforwardButton['state'] = 'normal'
        
        def showCollisions(self):
            if self.parent.parent.inputFrame.collisionsVar.get() == 1:
                if self.pathCollection != None:
                    self.pathCollection.set_visible(True)
                    self.collisionsScatter.set_visible(True)
                    self.plt.draw()
            else:
                self.pathCollection.set_visible(False)
                self.collisionsScatter.set_visible(False)
                self.plt.draw()
        def showThresholdCircles(self):
            if self.parent.parent.inputFrame.circlesVar.get() == 1:
                if self.patchCollection != None:
                    self.patchCollection.set_visible(True)
                    self.plt.draw()
            else:
                self.patchCollection.set_visible(False)
                self.plt.draw()
        
        def showAnnotations(self):
            if self.parent.parent.inputFrame.annotationsVar.get() == 1:
                if self.liveDemoAnnotConId == None:
                    self.liveDemoAnnotConId = mplcursors.cursor(self.liveDemoCurrent, hover=True)
                    self.liveDemoAnnotConId.connect("add", self.annotateLiveDemo)
                    self.plt.draw()
            else:
                if self.liveDemoAnnotConId != None:
                    self.liveDemoAnnotConId.remove()
                    self.liveDemoAnnotConId = None
                    self.plt.draw()
           
        def heatMap(self):
            if self.hMap == None:
                df = self.demoDF.groupby('MMSI', as_index=False)
                df = df.apply(lambda x: x.sort_values(['BaseDateTime'], ascending=True))
                df = df.reset_index(drop=True)
                df = df.groupby('MMSI').tail(1)
                self.hMap = sns.kdeplot(data = df, x="LON", y="LAT", cmap='Reds', fill=True, bw_method=0.1)
                self.hMap.collections[0].set_alpha(0)   
                self.plt.draw()
            else:
                print('removing heatmap')
                self.hMap.remove()
                self.plt.draw()

        def annotateLiveDemo(self, sel):
            index = sel.index
            text = None
            if sel.artist == self.liveDemoCurrent:
                text = 'Vessel: {}'.format(self.demoDF.iloc[index]['VesselName']) + '\n' + 'MMSI: {}'.format(self.demoDF.iloc[index]['MMSI']) + '\n' + 'Latitude: {}'.format(self.demoDF.iloc[index]['LAT']) + '\n' + 'Longitude: {}'.format(self.demoDF.iloc[index]['LON']) + '\n' + 'BaseDateTime: {}'.format(self.demoDF.iloc[index]['BaseDateTime']) + '\n' + 'SOG: {}'.format(self.demoDF.iloc[index]['SOG']) + '\n' + 'COG: {}'.format(self.demoDF.iloc[index]['COG'])
            elif sel.artist == self.liveDemoCurrentPred:
                text = 'Predicted point' + '\n' + 'Vessel: {}'.format(self.demoDF.iloc[index]['VesselName']) + '\n' + 'MMSI: {}'.format(self.demoDF.iloc[index]['MMSI']) + '\n' + 'Latitude: {}'.format(self.demoDF.iloc[index]['predictedLAT']) + '\n' + 'Longitude: {}'.format(self.demoDF.iloc[index]['predictedLON']) + '\n' + 'BaseDateTime: {}'.format(self.demoDF.iloc[index]['BaseDateTime']) + '\n' + 'SOG: {}'.format(self.demoDF.iloc[index]['SOG']) + '\n' + 'COG: {}'.format(self.demoDF.iloc[index]['COG'])
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
  
        def resetZoom(self):
            if self.predPath != None:
                """ self.drawPredictedPath()
                self.ax.margins(1,1)
                #self.scatterActual()
                self.plt.draw() """
                self.plt.xlim(66666666666)
                self.plt.ylim(66666666666)
                self.plt.draw()

        def resetWorldmap(self):
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
        self.outputText = Text(self, height=37, width=50)
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

class MainApplication(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.inputFrame = inputFrame(self)
        self.inputFrame.configure(width=300)
        self.inputFrame.grid(row=0, column=0, sticky=NSEW)
        self.plotFrame = plotFrame(self)
        self.plotFrame.grid(row=0, column=1, sticky=NSEW)
        self.outputFrame = outputFrame(self)
        self.outputFrame.grid(row=0, column=2, sticky=NSEW)
        self.plotFrame.ready()
        self.inputFrame.ready()

if __name__ == "__main__":    
    root = Tk()
    icon = Image.open('icon.png')
    photo = ImageTk.PhotoImage(icon)
    root.iconphoto(True, photo)
    root.title("Super Mega AIS Tool - Series 0 (SMAT-S0)")
    root.resizable(False, False)
    sv_ttk.set_theme("light")
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
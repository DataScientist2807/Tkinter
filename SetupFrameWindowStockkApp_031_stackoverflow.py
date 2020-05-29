# -*- coding: utf-8 -*-
"""
Created on Sun May 17 11:21:57 2020

@author: Marcel
"""

import tkinter as tk
from tkinter import Tk, Frame, Menu, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import os
import pandas as pd
import json 
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
from datetime import datetime
import time
import matplotlib.animation as animation
import matplotlib.ticker as mticker
import numpy as np
import threading
from multiprocessing import Process
import multiprocessing
###############################################################
####### LOAD DATA
###############################################################

     


def convert_ticks_to_ohlc(df, df_column, timeframe):
    data_frame = df[df_column].resample(timeframe).ohlc()
    return data_frame


     
valInterval = "5Min"
valCandles = 30
valValueSim = 0


class StockApp(Frame):

    def __init__(self):
        super().__init__()

        Process(target=self.initiate_mastergrid()).start()
        Process(target=self.init_menuBar()).start()
        Process(target=self.initFrames()).start()
        Process(target=self.main_frame()).start()
 
    
    def initiate_mastergrid(self):
        # Configure the grid
        self.master.grid_rowconfigure(1, weight=4)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)
        self.master.grid_columnconfigure(3, weight=1)
        

    def initialize_mainchart(self):
        self.figmain = plt.figure(figsize=(20,5), dpi=80)
        dataPlot2 = FigureCanvasTkAgg(self.figmain, master=self.mainFrame)
        self.am2 = plt.subplot2grid((4,5), (1,0), rowspan=2, colspan=5)
        self.am1 = plt.subplot2grid((4,5), (0,0), rowspan=1, colspan=5, facecolor="#F0F0F0", sharex=self.am2)
        self.am3 = plt.subplot2grid((4,5), (3,0), rowspan=1, colspan=5, sharex=self.am2)
        self.am2.yaxis.tick_right() # Price, Indicator and Volume Labels on the right
        self.am1.yaxis.tick_right() # Price, Indicator and Volume Labels on the right
        self.am3.yaxis.tick_right() # Price, Indicator and Volume Labels on the right
        
        plt.setp(self.am2.get_xticklabels(), visible=False)
        plt.setp(self.am1.get_xticklabels(), visible=False)
        plt.tight_layout(pad=0, w_pad=-1, h_pad=-1)
        
        plt.ion() # Necessary to animate plot
        dataPlot2.draw()
        dataPlot2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            
    
    
    def load_data(self):
        global tick_data
        os.chdir("C:\\Trainings\\Python\\Tkinter\\StockApp\\SampleData")
        tick_data = pd.read_csv("EURUSD-2019_01_01-2019_02_01.csv",
                        index_col=["time"], 
                        usecols=["time", "ask", "bid"],
                        parse_dates=["time"])
        print("Data has been loaded")
    

    def clear_axes(self, axes):
        axes.clear() # - Clear the chart
        

    def update_chart(self, candle_data):
            
        candlestick_ohlc(self.am2, candle_data, width=(15*0.5)/(24*60), 
                         colorup='#075105', 
                         colordown='#AF141A')
                         
        for label in self.am2.xaxis.get_ticklabels():
            label.set_rotation(45)
        self.am2.xaxis.set_major_locator(mticker.MaxNLocator(10))
        self.am2.grid(True)
        plt.grid(False)
        plt.xlabel('Candle count')
        plt.ylabel('Price')
        plt.title('Candlestick chart simulation')
        plt.subplots_adjust(left=0.09, bottom=0.20, right=0.94, 
                            top=0.90, wspace=0.2, hspace=0)
        self.figmain.canvas.draw() # - Draw on the chart
            
        
    def candlestick_simulation(self, tick_data, time_frame, candle_window):
        
        candlestick_data = convert_ticks_to_ohlc(tick_data, 
                                                 "ask", 
                                                 "15Min").dropna()
        
        print("Converts tick to ohlc")
        
        
        candlestick_data = candlestick_data.reset_index()
        
        dvalues = candlestick_data[['open', 'high', 'low', 'close']].values.tolist()
        pdates = mdates.date2num(candlestick_data.time)
        ohlc = [[pdates[i]] + dvalues[i] for i in range(len(pdates))]
 
        print("Converted ohlc")
        
        self.ohlc_animate(ohlc)
        
        
        print("Start animation")
        
    def ohlc_animate(self, ohlclist):
        
        emptyOHLC = []
        
        for i in range(0, 20):
            
            valuesOHLC = ohlclist[i]
            
            emptyOHLC = emptyOHLC + [valuesOHLC]
        
            p_update = Process(target=self.update_chart(emptyOHLC))
            p_update.start()
            p_update.join()
            
            #self.update_chart(emptyOHLC)
            
            print("Sleep 3 seconds")
            
            time.sleep(3.0)
            
            self.clear_axes(self.am2)
            
        
    def start_simulation(self):
        
        Process(target=self.candlestick_simulation(tick_data, valInterval, valCandles)).start()
        print("Start Simulation")
        
        
    def main_frame(self):
        global dataB
        
        
        Process(target=self.initialize_mainchart()).start()
        print("Main Frame initialised")
        
        Process(target=self.load_data()).start()
        print(len(tick_data))
        

    def initFrames(self):
        
    
        self.mainFrame = Frame(self.master,bd=1, relief="sunken") #whatever
        self.mainFrame.grid(row=1, column=1, columnspan=2, sticky="nsew", padx=1, pady=1)

    def init_menuBar(self):
             
        menubar = Menu(self.master)
        self.master.config(menu=menubar)

        # Add menu items
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        indicator_menu = Menu(menubar, tearoff=0)
        indicator_menu.add_command(label="EURUSD", command=lambda: self.start_simulation())
        file_menu.add_cascade(label="Interval", menu=indicator_menu)

def main():

    app = StockApp()
    app.master.title("Stock App 2020 by datascience2807@gmail.com")
    width_value = app.master.winfo_screenwidth()
    height_value = app.master.winfo_screenheight()
    app.master.geometry("%dx%d+0+0" % (width_value,height_value))
    app.mainloop()

if __name__ == '__main__':
    pool = multiprocessing.Pool()
    threading.Thread(target=main()).start()

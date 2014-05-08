# -*- coding: utf-8 -*-
'''This file implements the menu frame of the GUI for the ivctrack module
'''
__author__ = ' De Almeida Luis <ldealmei@ulb.ac.be>'

#------generic imports------
from Tkinter import *
import tkFileDialog

#-------local imports------
from TrackingFrame import TrackingFrame
from PlotFrame import PlotFrame
from AniFrame import AniFrame
from MeasFrameV3 import MeasFrameV3



class MainFrame(Frame):
    
    """Main menu frame : The user can either start a new tracking or view results from previous trackings
        The .zip file which contains the image sequences is linked to the menu window and can only be modified from there"""
    def __init__(self,win):
        Frame.__init__(self,win,width=700,height=700)
        self.pack()
        
        self.track_frame=None
        self.plot_frame=None
        self.meas_frame=None
        self.ani_frame=None
        
        self.menu_buttons=[]
        
        self.datazip_filename=""
        
        self.file_opt={}
        self.file_opt['filetypes'] =  [('ZIP file','.zip')]
        self.file_opt['defaultextension'] ='.zip'
        self.file_opt['title'] = 'Select a zipped sequence file'
        
        
        #----------------------------------------------------GUI IMPLEMENTATION-----------------------------------------

        self.track_button=Button(self,text='Start Tracking',command=lambda : self.track())
        self.track_button.pack(fill='both')
        self.menu_buttons.append(self.track_button)
        
        self.plot_button=Button(self,text='Plot Results',command=lambda : self.plot())
        self.plot_button.pack(fill='both')
        self.menu_buttons.append(self.plot_button)

        self.meas_button=Button(self,text='Measurements',command=lambda : self.measurements())
        self.meas_button.pack(fill='both')
        self.menu_buttons.append(self.meas_button)
        
        self.ani_button=Button(self,text='Player',command=lambda : self.play())
        self.ani_button.pack(fill='both')
        self.menu_buttons.append(self.ani_button)
        
        self.zip_var=StringVar()
        self.change_zip_button=Button(self,textvariable=self.zip_var,command= lambda : self.change_zip())
        self.menu_buttons.append(self.change_zip_button)
        
        self.quit_button=Button(self,text='Quit',command=win.quit)
        self.quit_button.pack(fill='both')
        self.menu_buttons.append(self.quit_button)
    
        self.back_button=Button(self,text='Back',command = lambda : self.back())

        #------------------------------------------------------END-------------------------------------------------------------

    
    def back(self):
        """Return to the menu window.  """
        try :
            self.track_frame.pack_forget()
            self.track_frame=None
        except:
            pass
        try :
            self.plot_frame.pack_forget()
            self.plot_frame=None
        except:
            pass
        try :
            self.meas_frame.pack_forget()
            self.meas_frame=None
        except:
            pass
        try:
            self.ani_frame.pack_forget()
            self.ani_frame=None
        except:
            pass

        self.back_button.pack_forget()
        for button in self.menu_buttons:
            button.pack(fill='both')

    def track(self):
        """Method that transits from the menu to the tracking frame """
        if self.datazip_filename=="":
            self.change_zip()

        self.track_frame=TrackingFrame(win,self.datazip_filename)

        self.track_frame.pack()
        
        for button in self.menu_buttons:
            button.pack_forget()
        
        self.back_button.pack(side='bottom')

    def plot(self):
        """Method that transits from the menu to the plotting frame """

        if self.datazip_filename=="":
            self.change_zip()
        
        self.plot_frame=PlotFrame(win,self.datazip_filename)
        
        self.plot_frame.pack()
            
        for button in self.menu_buttons:
            button.pack_forget()
            
        self.back_button.pack(side='bottom')

    def measurements(self):
        """Method that transits from the menu to the frame that displays multiple measures"""

        if self.datazip_filename=="":
            self.change_zip()
        self.meas_frame=MeasFrameV3(win,self.datazip_filename)

        self.meas_frame.pack()
        
        for button in self.menu_buttons:
            button.pack_forget()
        
        self.back_button.pack(side='bottom')

    def play(self):
        """Method that transits from the menu to the frame that plays the tracking and allows to save it to .mp4"""
        if self.datazip_filename=="":
            self.change_zip()
        
        self.ani_frame=AniFrame(win,self.datazip_filename)
        
        self.ani_frame.pack()
    
        for button in self.menu_buttons:
            button.pack_forget()
        
        self.back_button.pack(side='bottom')

    def change_zip(self):
        """Method that allows the user to change the current sequence ZIP file """
        self.datazip_filename=tkFileDialog.askopenfilename(**self.file_opt)
        try:
            self.zip_var.set("Change Zip File ({})".format(self.datazip_filename.rsplit('/')[-1]))
        except AttributeError:
            pass


if __name__== '__main__':
    
    win=Tk()
    win.wm_title('IVCTrack GUI')
    root=MainFrame(win)
    root.mainloop()

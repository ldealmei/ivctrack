# -*- coding: utf-8 -*-
'''This file implements the frame offering various tools to graphicaly observe the results of the analysis.
'''
__author__ = ' De Almeida Luis <ldealmei@ulb.ac.be>'

#------generic imports------
from Tkinter import *
import tkFileDialog

#------specific imports------
import matplotlib
matplotlib.use('Tkagg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.cm as cm

#------ivctrack toolbox imports------
from hdf5_read import get_hdf5_data
from reader import ZipSource,Reader




class PlotFrame(Frame):
    """Frame that allows the user to view the results of the tracking trough different kinds of graphic representations. """
    
    def __init__(self,win,zip_filename):
        Frame.__init__(self,win,width=700,height=700)
        
        self.frame=0
        self.file_opt={}
        self.file_opt['filetypes'] =  [('HDF5 file','.hdf5')]
        self.file_opt['defaultextension'] ='.hdf5'
        self.file_opt['title'] = 'Select a HDF5 file'
        
        self.feat=[]
        self.data = []
        
        #----------------------------------------------------GUI IMPLEMENTATION-----------------------------------------
        self.file_var=StringVar()
        self.file_var.set('HDF5 File: ')
        self.file_lbl=Label(self,textvariable=self.file_var)
        self.file_lbl.grid(row=0,column=1,columnspan=2)
        
        self.file_browse_button=Button(self,text='Browse',command=self.ask_open_and_load_file)
        self.file_browse_button.grid(row=0,column=3)
    
        self.plot_to_do=StringVar()
        self.plot_to_do.trace('w',self.plot)
        
        #------differen plot possibilities------
        self.xy_radbut=Radiobutton(self,text='X-Y Plot',variable=self.plot_to_do,value='xy')
        self.xy_radbut.grid(column=0,row=1,sticky='W')
        
        self.xf_radbut=Radiobutton(self,text='X-Frame Plot',variable=self.plot_to_do,value='xf')
        self.xf_radbut.grid(column=0,row=2,sticky='W')
        
        self.yf_radbut=Radiobutton(self,text='Y-Frame Plot',variable=self.plot_to_do,value='yf')
        self.yf_radbut.grid(column=0,row=3,sticky='W')
        
        self.relxy_radbut=Radiobutton(self,text='relX-relY Plot',variable=self.plot_to_do,value='relxy')
        self.relxy_radbut.grid(column=0,row=4,sticky='W')
        
        self.cell_shape_radbut=Radiobutton(self,text='Cell Shape',variable=self.plot_to_do,value='cellshape')
        self.cell_shape_radbut.grid(column=0,row=5,sticky='W')
        
        self.next_frame_button=Button(self,text='Next',command=lambda : self.change_frame(1))
        self.prev_frame_button=Button(self,text='Previous',command=lambda : self.change_frame(-1))
        self.lbl=StringVar()
        self.lbl.set('Frame {}'.format(self.frame+1))
        self.frame_lbl=Label(self,textvariable=self.lbl)
        
        #-----Configuration of the tracking canvas------        
        self.f=plt.figure()
        self.a=self.f.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.f, master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=1,row=1,rowspan=5,columnspan=3)
        
        #------------------------------------------------------END-------------------------------------------------------------

        #------import of the zip file & update of the canvas------

        self.datazip_filename=zip_filename
        self.reader = Reader(ZipSource(self.datazip_filename))
        self.bgs = []
        for i in self.reader.range():
            self.bgs.append(self.reader.getframe())
            try:
                self.reader.next()
            except IndexError:
                pass
    
    def plot(self,*args):
        """Plots a graph according to the option selected.
        """
        
        self.f.clf()
        self.a=self.f.add_subplot(111)
        
        self.next_frame_button.grid_forget()
        self.prev_frame_button.grid_forget()
        self.frame_lbl.grid_forget()
        
        legend_needed=True
        leg=[]
        cellnr=1
        for d in self.data:
            t=d['center']
            leg.append('Cell nr {} ({},{})'.format(cellnr,int(t[0,0]),int(t[0,1])))
            cellnr+=1
        
        if self.plot_to_do.get() =='xy':
            for d in self.data:
                t=d['center']
                self.a.plot(t[:,0],t[:,1])
            self.a.set_xlabel('x')
            self.a.set_ylabel('y')
            
        elif self.plot_to_do.get() =='xf':
            for d in self.data:
                f=d['frames']
                t=d['center']
                self.a.plot(f,t[:,0])
            self.a.set_xlabel('frame')
            self.a.set_ylabel('x')

        elif self.plot_to_do.get() =='yf':
            for d in self.data:
                f=d['frames']
                t=d['center']
                self.a.plot(f,t[:,1])
            self.a.set_xlabel('frame')
            self.a.set_ylabel('y')

        elif self.plot_to_do.get() =='relxy':
            for d in self.data :
                t=d['center']
                self.a.plot(t[:,0]-t[0,0],t[:,1]-t[0,1])
            self.a.set_xlabel('$x_{rel}$')
            self.a.set_ylabel('$y_{rel}$')
            self.a.axvline(x=0,color='grey')
            self.a.axhline(y=0,color='grey')

        elif self.plot_to_do.get() =='cellshape':
            self.next_frame_button.grid(column=3,row=6)
            self.prev_frame_button.grid(column=1,row=6)
            self.frame_lbl.grid(column=2,row=6)
            legend_needed=False
            self.plot_cell_shapes()

        if legend_needed:
            l=self.a.legend(leg)
            l.draggable()
        
        self.canvas.show()

    def plot_cell_shapes(self):
        """Plots the results of the tracking on the frames of the sequence. Allowing a visual verification of a good execution of the tracking algorithm.
        """
        for d in self.data:
            t=d['halo']
            self.a.plot(t[self.frame,:,0],t[self.frame,:,1],'o')
            t=d['soma']
            self.a.plot(t[self.frame,:,0],t[self.frame,:,1])
            self.a.set_xlabel('x')
            self.a.set_ylabel('y')
            self.a.set_xlim(0,len(self.bgs[self.frame][0,:]))
            self.a.set_ylim(len(self.bgs[self.frame][:,0]),0)
            self.a.imshow(self.bgs[self.frame],cmap=cm.gray)

    def change_frame(self,A):
        """Allows to slide through the sequence.
        """
        if ( (A>0 and self.frame+A<self.reader.N()) or (A<0 and self.frame+A>=0) ):
            self.frame+=A
            self.lbl.set('Frame {}'.format(self.frame+1))
            self.a.cla()
            self.plot_cell_shapes()
            self.canvas.show()


    def ask_open_and_load_file(self):
        
        self.hdf5_filename=tkFileDialog.askopenfilename(**self.file_opt)
        self.file_var.set('HDF5 File: {}'.format(self.hdf5_filename))
        
        self.feat,self.data=get_hdf5_data(self.hdf5_filename,fields=['center','halo','soma'])

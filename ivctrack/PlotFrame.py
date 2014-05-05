# -*- coding: utf-8 -*-

#A faire :

from Tkinter import *
import matplotlib
matplotlib.use('Tkagg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt

from hdf5_read import get_hdf5_data
from reader import ZipSource,Reader
import matplotlib.cm as cm

import tkFileDialog


class PlotFrame(Frame):
    """Frame that allows the user to view the results of the tracking trough diferent kinds of graphic representations """
    
    def __init__(self,win,zip_filename):
        Frame.__init__(self,win,width=700,height=700)
        #self.pack(fill='both')#A DEGAGER
        
        self.frame=0
        self.file_opt={}
        self.file_opt['filetypes'] =  [('HDF5 file','.hdf5')]
        self.file_opt['defaultextension'] ='.hdf5'
        self.file_opt['title'] = 'Select a HDF5 file'
        
        self.feat=[]
        self.data = []
        
        self.file_var=StringVar()
        self.file_var.set('HDF5 File: ')
        self.file_lbl=Label(self,textvariable=self.file_var)
        self.file_lbl.grid(row=0,column=1,columnspan=2)
        
        self.file_browse_button=Button(self,text='Browse',command=self.ask_open_and_load_file)
        self.file_browse_button.grid(row=0,column=3)
        
        self.f=plt.figure()
        self.a=self.f.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.f, master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=1,row=1,rowspan=5,columnspan=3)
    
        self.plot_to_do=StringVar()
        self.plot_to_do.trace('w',self.plot)
        
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
        
        #Clear de la figure sinon problème d'autoscale à cause de imshow().. Solution peut etre un peu drastique
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
            
                
        if self.plot_to_do.get() =='xf':
            for d in self.data:
                f=d['frames']
                t=d['center']
                self.a.plot(f,t[:,0])
            self.a.set_xlabel('frame')
            self.a.set_ylabel('x')

        if self.plot_to_do.get() =='yf':
            for d in self.data:
                f=d['frames']
                t=d['center']
                self.a.plot(f,t[:,1])
            self.a.set_xlabel('frame')
            self.a.set_ylabel('y')


        if self.plot_to_do.get() =='relxy':
            for d in self.data :
                t=d['center']
                self.a.plot(t[:,0]-t[0,0],t[:,1]-t[0,1])
            self.a.set_xlabel('$x_{rel}$')
            self.a.set_ylabel('$y_{rel}$')
            self.a.axvline(x=0,color='grey')
            self.a.axhline(y=0,color='grey')

        if self.plot_to_do.get() =='cellshape':
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
        if ( (A>0 and self.frame+A<self.reader.N()) or (A<0 and self.frame+A>=0) ):
            self.frame+=A
            self.lbl.set('Frame {}'.format(self.frame+1))
            self.a.cla()
            self.plot_cell_shapes()
            self.canvas.show()

#if self.frame==0 :
#           self.prev_frame_button.config(state="disabled")
#       elif self.frame==self.reader.N()-1:
#           self.next_frame_button.config(state="disabled")
#      else :
#           self.next_frame_button.config(state="normal")
#           self.prev_frame_button.config(state="normal")


    def ask_open_and_load_file(self):
        
        self.hdf5_filename=tkFileDialog.askopenfilename(**self.file_opt)
        self.file_var.set('HDF5 File: {}'.format(self.hdf5_filename))
        
        self.feat,self.data=get_hdf5_data(self.hdf5_filename,fields=['center','halo','soma'])


if __name__== '__main__':
    
    win=Tk()
    win.wm_title('IVCTrack GUI')
    c=PlotFrame(win)
    c.mainloop()

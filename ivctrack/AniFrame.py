# -*- coding: utf-8 -*-
'''This file implements a frame allowing to verify the tracking through an animation (which can be saved).
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
import matplotlib.animation as anim

#------ivctrack toolbox imports------
from reader import ZipSource,Reader
from hdf5_read import get_hdf5_data

class AniFrame(Frame):
    """Frame displaying the results of the tracking as a video, and allowing to save it. Will NOT work if FFmpeg is not installed."""

    def __init__(self,win,zip_filename):
        Frame.__init__(self,win)
        
        self.feat=[]
        self.data = []

        #----------------------------------------------------GUI IMPLEMENTATION-----------------------------------------

        self.file_var=StringVar()
        self.file_var.set('HDF5 File: ')
        self.file_lbl=Label(self,textvariable=self.file_var)
        self.file_lbl.grid(row=0,column=2,columnspan=2)
        
        self.file_browse_button=Button(self,text='Browse',command=self.ask_open_and_load_file)
        self.file_browse_button.grid(row=0,column=4)
        
        self.soma_var=BooleanVar()
        self.soma_check=Checkbutton(self,text='Soma',variable=self.soma_var)
        self.soma_check.grid(column=0,row=1,columnspan=2)
        
        self.halo_var=BooleanVar()
        self.halo_check=Checkbutton(self,text='Halo',variable=self.halo_var)
        self.halo_check.grid(column=0,row=2,columnspan=2)
        
        self.trajectory_var=BooleanVar()
        self.trajectory_check=Checkbutton(self,text='Trajectory',variable=self.trajectory_var)
        self.trajectory_check.grid(column=0,row=3,columnspan=2)

        self.play_button = Button(master=self, text='Preview',command=lambda:(self.play()))

        self.save_button=Button(self,text='Save as..',command=lambda :(self.save()))
        
        self.dpi_lbl=Label(self,text='Resolution (DPI)')
        self.var_dpi=IntVar()
        self.var_dpi.set(200)
        self.dpi_entry=Entry(self,textvariable=self.var_dpi)
        
        #-----Configuration of the tracking canvas------        
        self.f=plt.figure()
        self.a=self.f.add_subplot(111)

        self.frame_text=self.a.text(10,20,'')

        self.canvas = FigureCanvasTkAgg(self.f, master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(row=1,column=2,rowspan=3,columnspan=3)
        
        #------------------------------------------------------END-------------------------------------------------------------

    
        #------import of the zip file & update of the canvas------
        self.datazip_filename = zip_filename
        
        self.reader = Reader(ZipSource(self.datazip_filename))
        self.bg=self.reader.getframe()
        
        self.im = self.a.imshow(self.bg,cmap=cm.gray)
        
        self.a.set_xlim(0,len(self.bg[0,:]))
        self.a.set_ylim(len(self.bg[:,0]),0)
        
        #------MP4 writer------
        self.writer=anim.writers['ffmpeg']
        self.writer=self.writer(fps=5)


    def ask_open_and_load_file(self):
        self.file_opt={}
        self.file_opt['filetypes'] =  [('HDF5 file','.hdf5')]
        self.file_opt['defaultextension'] ='.hdf5'
        self.file_opt['title'] = 'Select a HDF5 file'
        
        self.hdf5_filename=tkFileDialog.askopenfilename(**self.file_opt)
        self.file_var.set('HDF5 File: {}'.format(self.hdf5_filename))
        
        self.feat,self.data=get_hdf5_data(self.hdf5_filename,fields=['center','halo','soma'])
        self.halo=[]
        self.soma=[]
        self.trajectory=[]
        
        for k in range(len(self.data)):
            self.halo.append(self.a.plot([],[],'o'))
            self.soma.append(self.a.plot([],[]))
            self.trajectory.append(self.a.plot([],[]))
        
        self.play_button.grid(row=4,column=1)
        self.save_button.grid(row=4,column=0)
        self.dpi_lbl.grid(column=2,row=4)
        self.dpi_entry.grid(column=3,row=4)

    
    def play(self):
        
        self.cell_ani = anim.FuncAnimation(fig=self.f, func=self.update_img,init_func=self.init_im,frames=self.reader.N(),blit=False)
        self.canvas.show()
        self.play_button.grid_forget()

    def save(self):
        """Exports the animation to a MP4 file.
        """
        self.file_opt={}
        self.file_opt['filetypes'] =  [('MP4 files','.mp4')]
        self.file_opt['defaultextension'] ='.mp4'
        self.file_opt['title'] = 'Save sequence as..'
        
        soma=self.soma_var.get()
        halo=self.halo_var.get()
        trajectory=self.trajectory_var.get()
        
        self.mp4_filename=tkFileDialog.asksaveasfilename(**self.file_opt)
    
        with self.writer.saving(self.f,self.mp4_filename,self.var_dpi.get()):
            self.reader.rewind()
            for i in range(self.reader.N()):
                print "Grabing frame ",i

                self.bg=self.reader.getframe()
                self.im.set_data(self.bg)
                try:
                    self.reader.next()
                except IndexError:
                    pass
                if halo:
                    self.plot_halo(i)
                if soma:
                    self.plot_soma(i)
                if trajectory:
                    self.plot_trajectory(i)
                
                self.frame_text.set_text(i)

                self.writer.grab_frame()
        print "Video correctly saved as ", self.mp4_filename
    

    def update_img(self,frame):
        
        self.reader.moveto(frame)
        self.bg=self.reader.getframe()
        
        self.im.set_data(self.bg)

        if self.halo_var.get():
            self.plot_halo(frame)
        elif not self.halo_var.get():
            for k in range(len(self.data)):
                self.halo[k][0].set_data([],[])
        
        if self.soma_var.get():
            self.plot_soma(frame)
        elif not self.soma_var.get():
            for k in range(len(self.data)):
                self.soma[k][0].set_data([],[])
        
        if self.trajectory_var.get():
            self.plot_trajectory(frame)
        elif not self.trajectory_var.get():
            for k in range(len(self.data)):
                self.trajectory[k][0].set_data([],[])
                        
        self.frame_text.set_text(frame)

    def init_im(self):
        pass

    def plot_halo(self,i):
        k=0
        for d in self.data:
            t=d['halo']
            x=t[i,:,0]
            y=t[i,:,1]
            self.halo[k][0].set_data(x,y)
            k+=1

    def plot_soma(self,i):
        k=0
        for d in self.data:
            t=d['soma']
            x=t[i,:,0]
            y=t[i,:,1]
            self.soma[k][0].set_data(x,y)
            k+=1

    def plot_trajectory(self,i):
        k=0
        for d in self.data:
            t=d['center']
            x=t[0:i,0]
            y=t[0:i,1]
            self.trajectory[k][0].set_data(x,y)
            k+=1

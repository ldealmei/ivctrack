# -*- coding: utf-8 -*-
'''This file implements the frame displaying various measures related to the movement of the cells.
'''
__author__ = ' De Almeida Luis <ldealmei@ulb.ac.be>'
#------generic imports------
from Tkinter import *

#------specfic imports------
import matplotlib
matplotlib.use('Tkagg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkFileDialog
import matplotlib.cm as cm

#------ivctrack toolbox imports------
from hdf5_read import get_hdf5_data
from measurement import speed_feature_extraction,filter,scaling_exponent,relative_direction_distribution
from reader import ZipSource,Reader


class MeasFrameV3(Frame):
    """Frame allowing a deeper trajectory analysis, based on the measurement module of the ivctrack toolbox. """
    
    def __init__(self,win, zip_filename):
        Frame.__init__(self,win,width=700,height=700)
        
        self.file_opt={}
        self.file_opt['filetypes'] =  [('HDF5 file','.hdf5')]
        self.file_opt['defaultextension'] ='.hdf5'
        self.file_opt['title'] = 'Select a HDF5 file'
        
        self.c_feat=[]
        self.c_data = []
        
        self.button_list=[]

        #----------------------------------------------------GUI IMPLEMENTATION-----------------------------------------

        self.file_var=StringVar()
        self.file_var.set('HDF5 File: ')
        self.file_lbl=Label(self,textvariable=self.file_var)
        self.file_lbl.grid(row=0,column=1+0)
        
        self.file_browse_button=Button(self,text='Browse',command=self.ask_open_and_load_file)
        self.file_browse_button.grid(row=0,column=1+1)

        #-----Configuration of the tracking canvas------        
        self.f=plt.figure()
        self.a=self.f.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.f, master=self)
        self.canvas.get_tk_widget().grid(column=1+0,row=1,columnspan=2)
        
        #------------------------------------------------------END-------------------------------------------------------------

        #------import of the zip file & update of the canvas------
        self.datazip_filename=zip_filename
        self.reader = Reader(ZipSource(self.datazip_filename))
        self.bg=self.reader.getframe()
        
        self.a.set_xlim(0,len(self.bg[0,:]))
        self.a.set_ylim(len(self.bg[:,0]),0)

        self.a.imshow(self.bg,cmap=cm.gray)

        self.canvas.show()

    def ask_open_and_load_file(self):
        
        self.hdf5_filename=tkFileDialog.askopenfilename(**self.file_opt)
        self.file_var.set('HDF5 File: {}'.format(self.hdf5_filename))
    
    
        self.c_feat,self.c_data=get_hdf5_data(self.hdf5_filename,fields=['center','halo','soma'])
        feat_name, self.measures=speed_feature_extraction(self.c_data)


        self.a.cla()
        self.a.set_xlim(0,len(self.bg[0,:]))
        self.a.set_ylim(len(self.bg[:,0]),0)
        self.a.imshow(self.bg,cmap=cm.gray)
        
        for cell in self.c_data:
            t=cell['halo']
            self.a.plot(t[0,:,0],t[0,:,1],'ko')
            t=cell['soma']
            self.a.plot(t[0,:,0],t[0,:,1],'k')
            self.a.set_xlabel('x')
            self.a.set_ylabel('y')
       
        self.set_frame()
        
        self.canvas.show()

    def set_frame(self):
    
        self.nrcells=len(self.c_data)
        
        if (len(self.button_list)>0):
            for button in self.button_list:
                button.grid_forget()
                del button
    
        self.features_list=[]
        self.values_list=[]
        self.units_list=[]
        
        self.button_rel_dir_list=[]
        self.button_lin_fit_list=[]
        
        #----------------------------------------------------GUI IMPLEMENTATION-----------------------------------------
    
        self.file_lbl.grid(row=0,column=1+0,columnspan=2*self.nrcells-1)
        self.file_browse_button.grid(row=0,column=1+2*self.nrcells-1)
        self.canvas.get_tk_widget().grid(column=1+0,row=1,columnspan=2,rowspan=8)
       
        features=['Path Length', 'Average Speed', 'MRDO','Hull Surface','Hull Distance','Hull Density','Hull Relative Distance' ]
        
        for feat in features:
            self.features_list.append(Label(self,text=feat))
            self.values_list.append(Label(self))

        units=['px','px/frame','px/frame','px^2','px','/','/']

        for unit in units:
            self.units_list.append(Label(self,text=unit))
        
        self.plotLinFit_button=Button(self,text='Linear Fitting Plot',command = self.plotLinFit)
        self.plotRelDir_button=Button(self,text='Relative Direction Plot',command = self.plotRelDir)

        self.global_meas_button=Button(self,text='Global Measures',command=self.plotGlobMeas)
        self.global_meas_button.grid(column=0,row=4)
        
        
        self.cell_list=Listbox(self)
        for cell in range(self.nrcells):
            self.cell_list.insert('end','Cell {}'.format(cell+1))
        
        self.cell_list.bind('<Double-Button-1>',self.show_meas)
        self.cell_list.bind('<Key>',self.show_meas)

        self.cell_list.grid(column=0,row=1,rowspan=3)
        #------------------------------------------------------END-------------------------------------------------------------


    def show_meas(self,event):
        """Displays general measures of the selected cell.
        """
        cell_nr=int(self.cell_list.get('active').rsplit(' ')[-1])-1

        self.highlight_selected_cell(cell_nr)
        
        self.cell_lbl=Label(self,text='Cell {} ({},{})'.format(cell_nr+1,int(self.c_data[cell_nr]['center'][0,0]),int(self.c_data[cell_nr]['center'][0,1])))
        self.cell_lbl.grid(column=1+2,row=1,columnspan=2)

        for lbl in self.features_list :
            lbl.grid(row=2+(self.features_list).index(lbl),column=1+2, sticky='W')
        for lbl in self.units_list :
            lbl.grid(row=2+(self.units_list).index(lbl),column=1+2+2, sticky='W')
        
        i=0
        for lbl in self.values_list :
            lbl.config(text=round(self.measures[cell_nr][i],5))
            lbl.grid(row=2+(self.values_list).index(lbl),column=1+2+1, sticky='W')
            i+=1

        self.plotLinFit_button.grid(row=10,column=1+2)
        self.plotRelDir_button.grid(row=10,column=1+2+1)


    def plotRelDir(self):
        """Executes the 'relative_directio_distribution' function of the measurement module frm the ivctrack toolbox.
        """
        cell = int(self.cell_list.get('active').rsplit(' ')[-1])-1
        
        self.highlight_selected_cell(cell)

        d=self.c_data[cell]
        xy = d['center']
        fxy = filter(xy,sigma=1.)
        R,V,Theta,Rtot,clip_dtheta,rho = relative_direction_distribution(fxy,verbose=True)#2nd figure (polar)

    def plotLinFit(self):
        """Executes the 'scaling_exponent' function of the measurement module from the ivctrack toolbox.
        """
        cell = int(self.cell_list.get('active').rsplit(' ')[-1])-1

        self.highlight_selected_cell(cell)

        d=self.c_data[cell]
        xy = d['center']
        fxy = filter(xy,sigma=1.)
        se,se_err = scaling_exponent(fxy,verbose=True)#First figure(lin fit)
    
    def plotGlobMeas(self):
        fig=plt.figure()
        a_scat=fig.add_subplot(121)
        a_hist=fig.add_subplot(122)

        a_scat.cla()
        a_hist.cla()
        
        a_scat.scatter(self.measures[:,1],self.measures[:,3])
        a_scat.set_xlabel('avg speed')
        a_scat.set_ylabel('hull surface')
        
        a_hist.hist(self.measures[:,1:4])
        a_hist.legend(['avg','mrdo','hull surface'])
        
        fig.show()
    
    def highlight_selected_cell(self,cell_nr):
        """Highlights the cell selected in the listbox to allow a visual localisation of the studied cell.
        """
        self.a.cla()
        self.a.set_xlim(0,len(self.bg[0,:]))
        self.a.set_ylim(len(self.bg[:,0]),0)
        self.a.imshow(self.bg,cmap=cm.gray)
        
        i=0
        for cell in self.c_data:
            if i==cell_nr:
                t=cell['halo']
                self.a.plot(t[0,:,0],t[0,:,1],'wo')
                t=cell['soma']
                self.a.plot(t[0,:,0],t[0,:,1],'w')
            else:
                t=cell['halo']
                self.a.plot(t[0,:,0],t[0,:,1],'ko')
                t=cell['soma']
                self.a.plot(t[0,:,0],t[0,:,1],'k')
            self.a.set_xlabel('x')
            self.a.set_ylabel('y')
            i+=1
        
        self.canvas.show()

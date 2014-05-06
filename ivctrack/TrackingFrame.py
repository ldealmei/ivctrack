# -*- coding: utf-8 -*-

#A faire:


from Tkinter import *
import matplotlib
matplotlib.use('Tkagg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from reader import ZipSource,Reader
import matplotlib.cm as cm
import tkFileDialog
import tkMessageBox
import os
import matplotlib.animation as anim

from hdf5_read import get_hdf5_data
from cellmodel import Cell,test_experiment,import_marks

class TrackingFrame(Frame):

    """Tracking frame :Allows to :_manually select the cells to track OR/AND import a .csv file containing the coordinates of previous marks. The marks used for the tracking are automatically saved under "selected_marks.csv"
                                  _set the parameters of the tracking and save them or load previously saved parameters
                                  _set the direction of the tracking"""

    def __init__(self,win,zip_filename):
        Frame.__init__(self,win,width=700,height=700)
        #self.pack(fill='both')#A DEGAGER
        
        #Parametres(N,radius,.. et direction du tracking)
        self.params_lbl=Label(self,text='Parametres:')
        self.params_lbl.grid(row=1,column=0,sticky='W')

        self.p1_lbl=Label(self,text='N')
        self.p1_lbl.grid(column=1,row=1, sticky='W')
        self.var_N=IntVar()
        self.var_N.set(12)
        self.p1_entry=Entry(self,textvariable=self.var_N)
        self.p1_entry.grid(column=2,row=1)
        
        self.p2_lbl=Label(self,text='halo radius')
        self.p2_lbl.grid(column=1,row=2, sticky='W')
        self.var_hrad=IntVar()
        self.var_hrad.set(20)
        self.p1_entry=Entry(self,textvariable=self.var_hrad)
        self.p1_entry.grid(column=2,row=2)
        
        self.p3_lbl=Label(self,text='soma radius')
        self.p3_lbl.grid(column=1,row=3, sticky='W')
        self.var_somrad=IntVar()
        self.var_somrad.set(15)
        self.p1_entry=Entry(self,textvariable=self.var_somrad)
        self.p1_entry.grid(column=2,row=3)
        
        self.p4_lbl=Label(self,text='exp halo')
        self.p4_lbl.grid(column=1,row=4, sticky='W')
        self.var_hexp=IntVar()
        self.var_hexp.set(15)
        self.p1_entry=Entry(self,textvariable=self.var_hexp)
        self.p1_entry.grid(column=2,row=4)
        
        self.p5_lbl=Label(self,text='exp soma')
        self.p5_lbl.grid(column=1,row=5, sticky='W')
        self.var_somexp=IntVar()
        self.var_somexp.set(2)
        self.p1_entry=Entry(self,textvariable=self.var_somexp)
        self.p1_entry.grid(column=2,row=5)
        
        self.p6_lbl=Label(self,text='niter')
        self.p6_lbl.grid(column=1,row=6, sticky='W')
        self.var_niter=IntVar()
        self.var_niter.set(5)
        self.p1_entry=Entry(self,textvariable=self.var_niter)
        self.p1_entry.grid(column=2,row=6)
        
        self.p7_lbl=Label(self,text='alpha')
        self.p7_lbl.grid(column=1,row=7, sticky='W')
        self.var_alpha=DoubleVar()
        self.var_alpha.set(.75)
        self.p1_entry=Entry(self,textvariable=self.var_alpha)
        self.p1_entry.grid(column=2,row=7)
        
        self.load_param_button=Button(self,text='Load params',command=self.load_param)
        self.load_param_button.grid(row=8,column=1)

        self.dir_lbl=Label(self,text='Direction:')
        self.dir_lbl.grid(row=9,sticky='W')
        
        self.f=plt.figure()
        self.a=self.f.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.f, master=self)
        self.canvas.get_tk_widget().grid(column=3,row=1,rowspan=11,columnspan=3)

        self.radValue=StringVar()
        self.radValue.set('fwd')
        self.radValue.trace('w',self.change_bg)
        self.fwd_radbut=Radiobutton(self,text='Forward',variable=self.radValue,value='fwd')
        self.fwd_radbut.grid(column=1,row=9,sticky='W')
        self.rev_radbut=Radiobutton(self,text='Reverse',variable=self.radValue,value='rev')
        self.rev_radbut.grid(column=1,row=10,sticky='W')

        self.saveas_lbl=Label(self,text='Save as ')
        self.saveas_lbl.grid(column=0,row=11,sticky='W')
        
        self.hdf5_filename=StringVar()
        self.saveas_entry=Entry(self,textvariable=self.hdf5_filename)
        self.saveas_entry.grid(column=1,row=11)
        
        self.save_as_button=Button(self,text='Save as',command=self.browse)
        self.save_as_button.grid(row=11,column=2)
        
        self.create_folder = IntVar()
        self.create_folder.set(1)
        self.create_folder_checkbutton = Checkbutton(self,text='Create Folder',variable=self.create_folder)
        self.create_folder_checkbutton.grid(row=12, column=1)
        

        #Boutons pour quitter ou lancer le tracking

        self.reset_button=Button(self,text='Reset',command=self.reset)
        self.reset_button.grid(row=12,column=2)

        self.track_button=Button(self,text='Track!',command=self.track)
        self.track_button.grid(row=12,column=4,columnspan=1)
        
        
        #Boutons pour charger/sauver les .csv
        
        self.import_csv_button=Button(self,text='Import marks (.csv)',command=self.load_csv)
        self.import_csv_button.grid(row=12,column=3)
        
        cid=self.f.canvas.mpl_connect('button_release_event', self.onclick)
        self.marks=[]
    
        #Import of the zip file
        
        self.datazip_filename=zip_filename
        self.reader = Reader(ZipSource(self.datazip_filename))
        self.bg=self.reader.getframe()
        
        self.a.set_xlim(0,len(self.bg[0,:]))
        self.a.set_ylim(len(self.bg[:,0]),0)

        self.frame_text=self.a.text(10,20,'')

        self.im = self.a.imshow(self.bg,cmap=cm.gray)
        
        self.canvas.show()
    
        self.static_halo=[]
        self.static_soma=[]
    
        self.halo=[]
        self.soma=[]
        self.trajectory=[]
        
        self.halo.append(self.a.plot([],[],'o'))
        self.soma.append(self.a.plot([],[]))
        self.trajectory.append(self.a.plot([],[]))

    def onclick(self,event):
        
        self.params = {'N':self.var_N.get(),'radius_halo':self.var_hrad.get(),'radius_soma':self.var_somrad.get(),'exp_halo':self.var_hexp.get(),'exp_soma':self.var_somexp.get(),'niter':self.var_niter.get(),'alpha':self.var_alpha.get()}
    
        #Tracking sur la frame affichee
        c=Cell(event.xdata,event.ydata,**self.params)
        c.update(self.bg)
        
        halo=c.rec()[1]
        soma=c.rec()[2]
        self.static_halo.append(self.a.plot(halo[:,0],halo[:,1],'o'))
        self.static_soma.append(self.a.plot(soma[:,0],soma[:,1]))
        self.canvas.show()
        
        if self.radValue.get()=='fwd':
            self.marks.append( (c.rec()[0][0],c.rec()[0][1],0) )
        elif self.radValue.get()=='rev':
            self.marks.append( (c.rec()[0][0],c.rec()[0][1],self.reader.N()-1) )

        self.halo.append(self.a.plot([],[],'o'))
        self.soma.append(self.a.plot([],[]))
        self.trajectory.append(self.a.plot([],[]))

    def reset(self):
        #Parametres par defaut
        self.var_N.set(12)
        self.var_alpha.set(.75)
        self.var_niter.set(5)
        self.var_hrad.set(20)
        self.var_somrad.set(15)
        self.var_somexp.set(2)
        self.var_hexp.set(15)
        self.hdf5_filename.set('')

        #Enlever les marques deja faites
        self.marks=[]
        self.a.cla()
        self.a.set_xlim(0,len(self.bg[0,:]))
        self.a.set_ylim(len(self.bg[:,0]),0)
        self.reader.rewind()
        self.bg=self.reader.getframe()
        self.im = self.a.imshow(self.bg,cmap=cm.gray)
        self.canvas.show()
    
        self.static_halo=[]
        self.static_soma=[]
        
        self.halo=[]
        self.soma=[]
        self.trajectory=[]
        
        self.halo.append(self.a.plot([],[],'o'))
        self.soma.append(self.a.plot([],[]))
        self.trajectory.append(self.a.plot([],[]))
    

    def track(self):
        import csv
        import numpy as np

        if self.hdf5_filename.get() == "" or self.marks==[]:
            tkMessageBox.showerror("Track settings incomplete","Either a filename has not been defined or no cells have been selected. Please verify your settings.")
            self.saveas_entry.set
        else:
            
            #If the user wants a folder reuniting all files related to a single tracking or not
            if (self.create_folder.get()):
                foldername = self.hdf5_filename.get()
                filename = foldername +'/tracks.hdf5'
                self.marks_filename = foldername + '/marks.csv'
                param_filename = foldername + '/params.json'
                os.mkdir(foldername)

            else :
                filename = self.hdf5_filename.get() + '.hdf5'
                self.marks_filename = 'selected_marks.csv'

            csvmarks=np.asarray(self.marks)

            marksfile=open(self.marks_filename, 'wb')
            csvwriter=csv.writer(marksfile, delimiter=',')
            
            #enregistrement des marques effectuees manuellement
            for c in csvmarks:
                csvwriter.writerow([c[0]] + [c[1]] + [int(c[2])])
            marksfile.close()
            
            test_experiment(datazip_filename=self.datazip_filename,marks_filename=self.marks_filename,hdf5_filename=filename,dir=self.radValue.get(),params=self.params)
            
            if (self.create_folder.get()):
                self.save_param(param_filename)
                self.save_mp4(self.hdf5_filename.get())

    def save_mp4(self,foldername):
        
        self.feat,self.data=get_hdf5_data(foldername + '/tracks.hdf5',fields=['center','halo','soma'])
                
        for k in range(len(self.static_halo)):
            self.static_halo[k][0].set_data([],[])
            self.static_soma[k][0].set_data([],[])
        
        writer = anim.writers['ffmpeg']
        writer = writer(fps=5)
        
        with writer.saving(self.f,foldername + '/vid.mp4',200):
            self.reader.rewind()
            print "Saving to video... ",
            for i in range(self.reader.N()):
                
                self.bg=self.reader.getframe()
                self.im.set_data(self.bg)
                try:
                    self.reader.next()
                except IndexError:
                    pass
                
                self.plot_halo(i)
                self.plot_soma(i)
                self.plot_trajectory(i)
                
                self.frame_text.set_text(i)
                
                writer.grab_frame()
            print "Video correctly saved as "#, foldername +'/vid.mp4'

        self.reset()

    def change_bg(self,*args):
        if self.radValue.get()=='fwd':
            self.bg=self.reader.rewind()
        elif self.radValue.get()=='rev':
            self.bg=self.reader.ff()
        
        self.a.imshow(self.bg,cmap=cm.gray)
        self.canvas.show()

    def load_csv(self):
        #Enlever les marques deja faites
        self.marks=[]
        self.a.cla()
        self.a.set_xlim(0,len(self.bg[0,:]))
        self.a.set_ylim(len(self.bg[:,0]),0)
        self.a.imshow(self.bg,cmap=cm.gray)
        self.canvas.show()
        
        self.params = {'N':self.var_N.get(),'radius_halo':self.var_hrad.get(),'radius_soma':self.var_somrad.get(),'exp_halo':self.var_hexp.get(),'exp_soma':self.var_somexp.get(),'niter':self.var_niter.get(),'alpha':self.var_alpha.get()}
        
        self.file_opt={}
        self.file_opt['filetypes'] =  [('CSV file','.csv')]
        self.file_opt['defaultextension'] ='.csv'
        self.file_opt['title'] = 'Select a csv file with the marks'
        
        self.marks=list(import_marks(tkFileDialog.askopenfilename(**self.file_opt)))

        for i in range(len(self.marks)):
            c=Cell(self.marks[i][0],self.marks[i][1],**self.params)
            c.update(self.bg)
                
            halo=c.rec()[1]
            soma=c.rec()[2]
            self.static_halo.append(self.a.plot(halo[:,0],halo[:,1],'o'))
            self.static_soma.append(self.a.plot(soma[:,0],soma[:,1]))
        self.canvas.show()

    def browse(self):
        self.file_opt={}
        #self.file_opt['filetypes'] =  [('HDF5 File','.hdf5')]
        #self.file_opt['defaultextension'] ='.hdf5'
        self.file_opt['title'] = 'Save as...'

        self.hdf5_filename.set(tkFileDialog.asksaveasfilename(**self.file_opt))

    def save_param(self,filename):
        import json

        s = json.dumps(self.params)
        fid = open(filename,'w+t')
        fid.write(s)
        del fid
        print 'parameters saved in ',filename

    def load_param(self):
        import json
        file_opt={}
        file_opt['filetypes'] =  [('JSON files','.json')]
        file_opt['defaultextension'] ='.json'
        file_opt['title'] = "Choose parameters' file"

        self.param_filename=tkFileDialog.askopenfilename(**file_opt)

        self.params=json.loads(open(self.param_filename).read())
        
        self.var_N.set(self.params['N'])
        self.var_alpha.set(self.params['alpha'])
        self.var_niter.set(self.params['niter'])
        self.var_hrad.set(self.params['radius_halo'])
        self.var_somrad.set(self.params['radius_soma'])
        self.var_somexp.set(self.params['exp_soma'])
        self.var_hexp.set(self.params['exp_halo'])
    
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


if __name__== '__main__':
    
    win=Tk()
    win.wm_title('IVCTrack GUI')
    c=TrackingFrame(win)
    c.mainloop()

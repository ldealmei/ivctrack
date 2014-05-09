GUI Tools for ivctrack Module
=============================

This Python module adds a GUI to the ivctrack module, which is in-vitro cell tracking toolbox.

This document gives additional info regarding the GUI. Please refer to https://github.com/odebeir/ivctrack for a description of the original toolbox.

Dependencies
============

Ivctrack module and its dependencies

FFmpeg for video recording
Download links can be found at http://www.ffmpeg.org/documentation.html


Getting started
===========
Once the ivctrack module is correctly installed, execute the Mainwindow.py script.

The Menu consists of 4 buttons : 
	Start Tracking
	Plot Results
	Measurements
	Player

The user should have downloaded the zip sequences described in the ivctrack README. None of the following can be done without a sequence to analyse.

Start Tracking
--------------
Allows you to interactively select the cells to track and start the analysis.
The output files are :
	tracks.hdf5 : contains the results of the analysis
	marks.csv : contains the marks of the analysed cells
	features.csv : contains speed features deduced from the tracking
	vid.mp4 : is a video of the tracking. Allows to verify the tracking
	params.json : contains the parameters of the analysis

Rem : The user can decide to only generate the tracks file by uncheking 'Create Folder'

Plot Results
------------
Plots tracking results

Measurements
------------
Visual display of the measures issued by the measurement module of the ivctrack toolbox

Player
------
Gives a preview of the tracking througout the sequence.
This preview can be exported to an MP4 file 

Warning
=======
It is advised to terminate the application after executing a tracking. A bug in the measurements frame may terminate the application unexpectedly and damage the .hdf5 file.
By terminating and relaunching the program, the integrity of the file will be assured, however the bug may still occur. 
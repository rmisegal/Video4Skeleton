# Import required Libraries
from tkinter import *
from PIL import Image, ImageTk
import cv2
import datetime
import os
import glob
import sys
import logging
import time
import shutil

from OpenPoseManager import OpenPoseClass
import GlobalVars as glb

global all_vertexes_dist_matrix_np


# logger = logging.getLogger(__name__)
glb.logger = logging.getLogger('LibertyLogger')
glb.logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
glb.logger.addHandler(ch)


# log to file
# file_handler = logging.FileHandler('logfile.log')
# formatter    = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
# file_handler.setFormatter(formatter)

# add file handler to logger
# logger.addHandler(file_handler)
# # Logs
# logger.debug('A debug message')
# logger.info('An info message')
# logger.warning('Something is not right.')
# logger.error('A Major error has happened.')
# logger.critical('Fatal error. Cannot continue')
# logging.basicConfig(level=logging.DEBUG,
#                         format='(%(threadName)-9s) %(message)s',)
def calculateSkeleton(op,working_mode='SNAP_FROM_LIVE'):
    global all_vertexes_dist_matrix_np

    if working_mode=='SNAP_FROM_LIVE':
        last_snaped_image = newest_file_in_folder(op.FULL_IN_LOG_IMG_FOLDER)
        shutil.copy(last_snaped_image, op.SNAPSHOT_TMP_IMAGE_NAME)
        glb.logger.debug(f'Copy last snaped image to OpenPose: shutil.copy({last_snaped_image}, {OpenPose.SNAPSHOT_TMP_IMAGE_NAME})')
    elif working_mode=='DEMO_IMAGE':
        shutil.copy(op.FULL_PATH_DEMO_IMG, op.SNAPSHOT_TMP_IMAGE_NAME)
        glb.logger.debug(f'Process buildin DEMO image : shutil.copy({op.FULL_PATH_DEMO_IMG}, {op.SNAPSHOT_TMP_IMAGE_NAME})')
    else:
        glb.logger.debug(f'RAMI ERROR: No such working_mode={working_mode} there fore set it to SNAP_FROM_LIVE')
        working_mode = 'DEMO_IMAGE'
        shutil.copy(op.FULL_PATH_DEMO_IMG, op.SNAPSHOT_TMP_IMAGE_NAME)
        glb.logger.debug(f'Process buildin DEMO image : shutil.copy({op.FULL_PATH_DEMO_IMG}, {op.SNAPSHOT_TMP_IMAGE_NAME})')

    OpenPose.Run()
    body_vertexes_df = op.op_json_to_df(OpenPose.JSON_TMP_FILE)
    all_vertexes_dist_matrix_np = op.generate_ditance_np_matrix(body_vertexes_df)

def takeSnapshot(op):
    # grab the current timestamp and use it to construct the
    # output path
    global cv2image
    glb.logger.debug("Try to take snapshot")
    ts = datetime.datetime.now()
    filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
    p = os.path.sep.join((outputPath, filename))
    # save the file
    cv2.imwrite(p, cv2image.copy())
    glb.logger.debug("[INFO] saved {}".format(p))

    calculateSkeleton(op,'SNAP_FROM_LIVE')

# Define function to show frame
def show_frames():
    global cv2image
    # Get the latest frame and convert into Image
    cv2image = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2RGB)
    img = Image.fromarray(cv2image)
    # Convert image to PhotoImage
    imgtk = ImageTk.PhotoImage(image=img)
    label.imgtk = imgtk
    label.configure(image=imgtk)
    # Repeat after an interval to capture continiously
    label.after(20, show_frames)

#Find the newest file in  the folder
def newest_file_in_folder(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)


OpenPose=OpenPoseClass('C:/24D/LibertySnapshot')
#OpenPose.PROGRAM_RUNNING_MODE='SNAP_FROM_LIVE'
outputPath = OpenPose.FULL_IN_LOG_IMG_FOLDER

# Create an instance of TKinter Window or frame
win = Tk()
# Set the size of the window
win.geometry("645x545")
# create a button, that when pressed, will take the current
# frame and save it to file
# btn = Button(win, text="Snapshot",command=takeSnapshot)
btn = Button(win, text="Snapshot!",
             command=lambda myOp=OpenPose : takeSnapshot(myOp))
             #command=takeSnapshot)
btn.grid(row=1, column=0)

btn_prev = Button(win, text="Measure Demo Image",
             command=lambda myOp=OpenPose, myMode='DEMO_IMAGE' : calculateSkeleton(myOp,myMode))
btn_prev.grid(row=2, column=0)

# Create a Label to capture the Video frames
label = Label(win)
label.grid(row=0, column=0)
cap = cv2.VideoCapture(0)

show_frames()
win.mainloop()

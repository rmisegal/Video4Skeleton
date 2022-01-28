# Import required Libraries
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfile

import numpy as np
from PIL import Image, ImageTk
import cv2
import datetime
import os
import glob
import sys
import logging
import time
import shutil
import FormGUI as frm

from OpenPoseManager import OpenPoseClass
import GlobalVars as glb


global all_vertexes_dist_matrix_np

def create_logger():
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

def browseFiles():
    #file = filedialog.askopenfile(initialdir = OpenPose.FULL_PATH_CONFIG_FOLDER, title = 'Select file', filetypes=[('Image Files', '*.jpg')])
    filename = filedialog.askopenfilename(initialdir=OpenPose.FULL_PATH_CONFIG_FOLDER,
                                          title="Select a File",
                                          filetypes=(('Image Files',
                                                      '*.jpg'),
                                                     ("all files",
                                                      "*.*")))
    return filename


def calculateSkeleton(op,working_mode='SNAP_FROM_LIVE'):
    global all_vertexes_dist_matrix_np, label_Result_display
    label_Result_display.configure(text="Wait for you to select image...", bg="light gray",fg="black")
    if working_mode=='SNAP_FROM_LIVE':
        last_snaped_image = newest_file_in_folder(op.FULL_IN_LOG_IMG_FOLDER)
        shutil.copy(last_snaped_image, op.SNAPSHOT_TMP_IMAGE_NAME)
        glb.logger.debug(f'Copy last snaped image to OpenPose: shutil.copy({last_snaped_image}, {OpenPose.SNAPSHOT_TMP_IMAGE_NAME})')
    elif working_mode=='DEMO_IMAGE':
        fullfilename = browseFiles()
        glb.logger.debug(f'The selected file from the Browser {op.FULL_PATH_DEMO_IMG}')
        if fullfilename != '':
            op.FULL_PATH_DEMO_IMG = fullfilename
            #label_Result_display.configure(text="Wait for results...", bg="gray", fg="black")
        else :
            label_Result_display.configure(text="", bg="light gray", fg="black")
            return
        shutil.copy(op.FULL_PATH_DEMO_IMG, op.SNAPSHOT_TMP_IMAGE_NAME)
        glb.logger.debug(f'Process buildin DEMO image : shutil.copy({op.FULL_PATH_DEMO_IMG}, {op.SNAPSHOT_TMP_IMAGE_NAME})')
    else:
        glb.logger.debug(f'RAMI ERROR: No such working_mode={working_mode} there fore set it to SNAP_FROM_LIVE')
        working_mode = 'DEMO_IMAGE'
        shutil.copy(op.FULL_PATH_DEMO_IMG, op.SNAPSHOT_TMP_IMAGE_NAME)
        glb.logger.debug(f'Process buildin DEMO image : shutil.copy({op.FULL_PATH_DEMO_IMG}, {op.SNAPSHOT_TMP_IMAGE_NAME})')

    label_Result_display.configure(text="Wait for results...", bg="light gray", fg="black")
    OpenPose.Run()
    body_vertexes_df = op.op_json_to_df(OpenPose.JSON_TMP_FILE)
    all_vertexes_dist_matrix_np = op.generate_ditance_np_matrix(body_vertexes_df)
    normal_difference_distance = 0
    tolerance = 0.1
    reult_text = ''
    what_to_measure = 'Genu Varum'
    if what_to_measure =='Genu Varum':
        waist_dist = all_vertexes_dist_matrix_np[9][12]
        if waist_dist == 0:
            waist_dist = 1 #no normalization
        #Calculate distances while normalizing them to waist_dist
        knee_dist = all_vertexes_dist_matrix_np[10][13]/waist_dist
        heels_dist = all_vertexes_dist_matrix_np[11][14]/waist_dist
        diff_dist = np.absolute(knee_dist-heels_dist)
        glb.logger.debug(f'Knee normolize distance = {knee_dist:2.2f} Heels normolize dist = {heels_dist:2.2f} the difference is {diff_dist:2.2f}')
        if knee_dist == 0 or diff_dist == 0:
            glb.logger.debug(f'RAMI ERROR: Vertices for Knees and Heels are empty (they are not in the image)')
            reult_text = 'Error: Vertices for Knees and Heels are empty (they are not in the image).'
            label_Result_display.configure(text=reult_text, bg="red", fg="yellow")
        elif diff_dist <= normal_difference_distance + tolerance:
            glb.logger.debug(f'Genu Normal')
            reult_text = 'Genu Normal'
            label_Result_display.configure(text=reult_text, bg="light gray", fg="green")
        elif knee_dist < heels_dist:
            glb.logger.debug(f'Genu Valgus')
            reult_text = 'Genu Valgus'
            label_Result_display.configure(text=reult_text, bg="light gray", fg="red")
        else :
            glb.logger.debug(f'Genu Varum')
            reult_text = 'Genu Varum'
            label_Result_display.configure(text=reult_text, bg="light gray", fg="red")


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

def open_form_window(op):
    form_win_ob = frm.PatientClass('C:\\24D\\LibertySnapshot\\LibertyConfig',op)




if __name__ == "__main__":
    create_logger()
    OpenPose=OpenPoseClass('C:/24D/LibertySnapshot')
    #OpenPose.PROGRAM_RUNNING_MODE='SNAP_FROM_LIVE'
    outputPath = OpenPose.FULL_IN_LOG_IMG_FOLDER

    # Create an instance of TKinter Window or frame
    win = Tk()
    # Set the size of the window
    win.geometry("700x595")
    win.iconbitmap(OpenPose.FULL_PATH_APP_ICON )
    # create a button, that when pressed, will take the current
    # frame and save it to file
    # btn = Button(win, text="Snapshot",command=takeSnapshot)
    patient_form_btn = Button(win, text="Insert Patient Data",
                 command = lambda myOp=OpenPose: open_form_window(myOp))

    patient_form_btn.grid(row=1, column=0, ipadx="100")

    # btn = Button(win, text="Snapshot",command=takeSnapshot)
    btn = Button(win, text="Snapshot!",
                 command=lambda myOp=OpenPose: takeSnapshot(myOp))
    btn.grid(row=2, column=0, ipadx="122")
    btn_prev = Button(win, text="Measure Demo Image",
                 command=lambda myOp=OpenPose, myMode='DEMO_IMAGE' : calculateSkeleton(myOp,myMode))
    btn_prev.grid(row=3, column=0, ipadx="90")

    label_Result_display = Label(win,
                                     text="",
                                     width=100, height=2,
                                     fg="blue")
    label_Result_display.grid(row=4, column=0)

    label = Label(win)

    # button_browser = Button(win,
    #                         text = "Browse Files",
    #                         command = browseFiles)
    # button_browser.grid(row=3, column=0)

    # Create a Label to capture the Video frames
    label = Label(win)
    label.grid(row=0, column=0)
    cap = cv2.VideoCapture(0)

    show_frames()
    win.mainloop()

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
import json
import cv2
import os
import GlobalVars as glb
#from IPython.display import Image
#from IPython.display import display

#import a function from another .ipynb nootbook file
#from ipynb.fs.full.RmiOpenPoseUtils import tstFunc
import logging
import time




class OpenPoseClass:

    def __init__(self, new_folder=None):
        self.PROGRAM_RUNNING_MODE = 'DEMO_IMAGE' #'SNAP_FROM_LIVE' 'DEMO_IMAGE'
        self.SNAPSHOT_TMP_NAME = "tmp1"
        self.ROOT_DIR = "C:/24D/openpose"
        self.OP_PROGRAM_NAME = self.ROOT_DIR + "/bin/OpenPoseDemo.exe"
        self.DATA_FOLDER = "C:/24D/RmifSample"
        self.INPUT_SNAP_LOG_FOLDER = "/Snapshot-Log"
        self.INPUT_SNAP_IMAGE_FOLDER = "/Snapshot-Image"
        self.OUTPUT_FOLDER_NAME = self.DATA_FOLDER + "/Results"
        self.FULL_PATH_CONFIG_FOLDER = self.DATA_FOLDER + "/LibertyConfig"
        self.FULL_PATH_DEMO_IMG = self.FULL_PATH_CONFIG_FOLDER + "/Men-Stand-Normal.jpg"
        self.CAMERA_ID = 0
        self.update_data_folders(new_folder)

    def update_data_folders(self, new_folder=None):
        if new_folder is not None:
            if not os.path.exists(new_folder):
                os.mkdir(new_folder)
                if os.path.exists(new_folder):
                    self.DATA_FOLDER = new_folder
                    glb.logger.debug(f'New Data folder was created: {new_folder}')
            else:
                self.DATA_FOLDER = new_folder
                glb.logger.debug(f'Update to existing Data folder: {new_folder}')

        self.OUTPUT_FOLDER_NAME = self.DATA_FOLDER + "/Results"

        # Snapshot LOG images
        self.FULL_IN_LOG_IMG_FOLDER = self.DATA_FOLDER + self.INPUT_SNAP_LOG_FOLDER
        glb.logger.debug(self.FULL_IN_LOG_IMG_FOLDER)
        if not os.path.exists(self.FULL_IN_LOG_IMG_FOLDER):
            os.mkdir(self.FULL_IN_LOG_IMG_FOLDER)
        # Input image to OP
        self.FULL_IN_TMP_IMG_FOLDER = self.DATA_FOLDER + self.INPUT_SNAP_IMAGE_FOLDER
        glb.logger.debug(self.FULL_IN_TMP_IMG_FOLDER)
        if not os.path.exists(self.FULL_IN_TMP_IMG_FOLDER):
            os.mkdir(self.FULL_IN_TMP_IMG_FOLDER)
        self.SNAPSHOT_TMP_IMAGE_NAME = self.FULL_IN_TMP_IMG_FOLDER + "/" + self.SNAPSHOT_TMP_NAME + ".jpg"
        # self.INPUT_IMAGES_FOLDER_NAME = "Src-Images"
        # OP results
        if not os.path.exists(self.OUTPUT_FOLDER_NAME):
            os.mkdir(self.OUTPUT_FOLDER_NAME)
        self.JSON_FOLDER_NAME = self.OUTPUT_FOLDER_NAME + "/" + "Jsons"
        self.SKELETON_IMAGE_FOLDER_NAME = self.OUTPUT_FOLDER_NAME + "/" + "Images"
        if not os.path.exists(self.JSON_FOLDER_NAME):
            os.mkdir(self.JSON_FOLDER_NAME)
        if not os.path.exists(self.SKELETON_IMAGE_FOLDER_NAME):
            os.mkdir(self.SKELETON_IMAGE_FOLDER_NAME)
        self.JSON_TMP_FILE = self.JSON_FOLDER_NAME + "/" + self.SNAPSHOT_TMP_NAME + "_keypoints.json"
        self.SEKELETON_TMP_IMG = self.SKELETON_IMAGE_FOLDER_NAME + "/" + self.SNAPSHOT_TMP_NAME + "_rendered.png"
        #Configuration
        self.FULL_PATH_CONFIG_FOLDER = self.DATA_FOLDER + "/LibertyConfig"
        if not os.path.exists(self.FULL_PATH_CONFIG_FOLDER):
            os.mkdir(self.SKELETON_IMAGE_FOLDER_NAME)
            glb.logger.debug(f'RAMI ERROR: The configuration folder dose not exist there fore I create it for you but and its content is missing: {self.SKELETON_IMAGE_FOLDER_NAME}')
        self.FULL_PATH_DEMO_IMG = self.FULL_PATH_CONFIG_FOLDER + "/Men-Stand-Normal.jpg"

        self.OpInput = " --image_dir " + self.FULL_IN_TMP_IMG_FOLDER
        self.OpJsonResult = " --write_json " + self.JSON_FOLDER_NAME
        self.OpSkelatonImageResult = " --write_images " + self.SKELETON_IMAGE_FOLDER_NAME

    def snap_frame_2_image(self):
        webcam = cv2.VideoCapture(OpenPoseClass.CAMERA_ID)
        check, frame = webcam.read()
        cv2.imwrite(filename=self.SNAPSHOT_TMP_IMAGE_NAME, img=frame)
        webcam.release()
        glb.logger.debug(
            f'A snapshot was taken from the WEB camera {self.CAMERA_ID} and saved as a jpg image to file {self.SNAPSHOT_TMP_IMAGE_NAME}')

    # Snap selected specific video frame to image file
    def Snap_video_frame_to_image_file(self, camid, imagefile):
        cap = cv2.VideoCapture(camid)
        # Check if the webcam is opened correctly
        if not cap.isOpened():
            raise IOError("Cannot open webcam")
        while True:
            ret, frame = cap.read()
            frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            cv2.imshow('Input', frame)
            c = cv2.waitKey(1)
            if c == 27:
                cv2.imwrite(filename=imagefile, img=frame)
                break
        cap.release()
        cv2.destroyAllWindows()

    def Run(self):
        os.system(
            "cd " + self.ROOT_DIR + " & " + self.OP_PROGRAM_NAME + self.OpInput + self.OpJsonResult + self.OpSkelatonImageResult)
        glb.logger.debug(
            "cd " + self.ROOT_DIR + " & " + self.OP_PROGRAM_NAME + self.OpInput + self.OpJsonResult + self.OpSkelatonImageResult)

    def print_all_defenitions(self):
        print(f'self.SNAPSHOT_TMP_NAME : {self.SNAPSHOT_TMP_NAME}')
        print(f'self.ROOT_DIR : {self.ROOT_DIR}')
        print(f'self.OP_PROGRAM_NAME : {self.OP_PROGRAM_NAME}')
        print(f'self.DATA_FOLDER : {self.DATA_FOLDER}')
        print(f'self.INPUT_SNAP_IMAGE_FOLDER : {self.INPUT_SNAP_IMAGE_FOLDER}')
        print(f'self.OUTPUT_FOLDER_NAME : {self.OUTPUT_FOLDER_NAME}')
        print(f'self.CAMERA_ID : {self.CAMERA_ID}')

        print(f'self.FULL_IN_LOG_IMG_FOLDER : {self.FULL_IN_LOG_IMG_FOLDER}')

        print(f'self.FULL_IN_TMP_IMG_FOLDER : {self.FULL_IN_TMP_IMG_FOLDER}')
        print(f'self.SNAPSHOT_TMP_IMAGE_NAME : {self.SNAPSHOT_TMP_IMAGE_NAME}')

        # OP results
        print(f'self.JSON_FOLDER_NAME : {self.JSON_FOLDER_NAME}')
        print(f'self.SKELETON_IMAGE_FOLDER_NAME : {self.SKELETON_IMAGE_FOLDER_NAME}')
        # print(f'self.FULL_JSON_TMP_PATH : {self.FULL_JSON_TMP_PATH}')
        # print(f'self.FULL_IMAGE_TMP_PATH : {self.FULL_IMAGE_TMP_PATH}')
        print(f'self.JSON_TMP_FILE : {self.JSON_TMP_FILE}')
        print(f'self.SEKELETON_TMP_IMG : {self.SEKELETON_TMP_IMG}')

        print(f'self.OpInput : {self.OpInput}')
        print(f'self.OpJsonResult : {self.OpJsonResult}')
        print(f'self.OpSkelatonImageResult : {self.OpSkelatonImageResult}')

    def op_json_to_df(self,json_file):
        selected_person = 0
        no_of_vertexes = 25
        vertex_dimension = 3
        body_part_name = 'pose_keypoints_2d'

        with open(json_file) as jsonFile:
            jsonObject = json.load(jsonFile)
            jsonFile.close()

        version = jsonObject['version']
        people = jsonObject['people']

        body_vertexes_np = np.array(people[selected_person].get(body_part_name)).reshape(no_of_vertexes, vertex_dimension)

        glb.logger.debug(version)
        glb.logger.debug(body_vertexes_np.shape)

        return pd.DataFrame(body_vertexes_np, columns=['X', 'Y', 'C'])

    # Calculates all limb distances between vertices
    def generate_ditance_np_matrix(self,body_df):
        distances = pdist(body_df[['X', 'Y']].values, metric='euclidean')
        return squareform(distances)

    # Calculates limb distances between two specics vertices
    def dist_between_2_vertexes(self,vertexes_df, v1, v2):
        return (
        self.all_vertexes_dist_matrix_np[v1][v2])  # Keep in mind vertexes id here are -1 compare to openpose vertexes ids



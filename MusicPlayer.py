import cv2
import numpy as np
from ffpyplayer.player import MediaPlayer
import requests

if __name__ == "__main__":

    headers = {'Authorization': ''}
    # play = requests.put('https://api.spotify.com/v1/me/player/play', headers=headers)
    # pause = requests.put('https://api.spotify.com/v1/me/player/pause', headers=headers)    

    # =====Below is the OpenCV's way of playing video.=====
    # cap = cv2.VideoCapture('videos/video1.mp4')
    # player = MediaPlayer('videos/video1.mp4')

    # if (cap.isOpened() == False):
    #     print("Error opening video file")
    
    # while(cap.isOpened()):
    #     ret, frame = cap.read()
    #     if (ret == True):
    #         cv2.imshow('Frame', frame)
    #         # waitKey is in milliseconds
    #         if cv2.waitKey(22) & 0xFF == ord('q'):
    #             break
    #     else:
    #         break
    
    # cap.release()

    # cv2.destroyAllWindows()
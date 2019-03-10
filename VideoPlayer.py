import cv2
import numpy as np
from ffpyplayer.player import MediaPlayer

if __name__ == "__main__":
    # =====Below is the ffpyplayer's way of showing video.=====
    # player = MediaPlayer('videos/video1.mp4')
    # val = ''
    # while val != 'eof':
    #     frame, val = player.get_frame()
    #     if val != 'eof' and frame is not None:
    #         img, t = frame

    # =====Below is the OpenCV's way of playing video.=====
    cap = cv2.VideoCapture('videos/video1.mp4')
    player = MediaPlayer('videos/video1.mp4')

    if (cap.isOpened() == False):
        print("Error opening video file")
    
    while(cap.isOpened()):
        ret, frame = cap.read()
        if (ret == True):
            cv2.imshow('Frame', frame)
            # waitKey is in milliseconds
            if cv2.waitKey(20) & 0xFF == ord('q'):
                break
        else:
            break
    
    cap.release()

    cv2.destroyAllWindows()
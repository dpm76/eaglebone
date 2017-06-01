'''
Created on 24/05/2015

@author: david
'''
import cv2


def main():
    
    cam = cv2.VideoCapture(0)
    
    done = False
    while not done:
        
        _, frame = cam.read()
        frame = cv2.flip(frame, 1)
        
        cv2.imshow('cam', frame)
        
        key = cv2.waitKey(1) & 0xff
        if key == ord('q'):
            done = True
        elif key == ord('c'):
            cv2.imwrite('/home/david/dummy.png', frame)
            print "captured"
        


if __name__ == '__main__':
    
    main()
    
    
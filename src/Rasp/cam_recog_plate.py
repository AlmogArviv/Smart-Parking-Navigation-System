import cv2

import imutils

import numpy as np

import pytesseract

from PIL import Image

def validate_text(text):
    return ''.join(filter(str.isdigit, text))

def run_cam(cam_num, queue):

    text_valid=""
    cap = cv2.VideoCapture(int(cam_num))
    print("cam_num - " + str(cam_num))

    if not cap.isOpened():
        print("Failed to open camera")
        exit()

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Cam " +str(cam_num) +" - Failed to capture frame")
            #so we don't send a response
            continue
            #break

        cv2.imwrite('frame'+str(cam_num)+'.jpg', frame)
        img = cv2.imread('frame.jpg',cv2.IMREAD_COLOR)
        img = cv2.resize(frame, (620,480) )


        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to grey scale

        gray = cv2.bilateralFilter(gray, 11, 17, 17) #Blur to reduce noise

        edged = cv2.Canny(gray, 30, 200) #Perform Edge detection


        # find contours in the edged image, keep only the largest

        # ones, and initialize our screen contour

        cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cnts = imutils.grab_contours(cnts)

        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:30]

        screenCnt = None


        # loop over our contours

        for c in cnts:
            #print(c)
        # approximate the contour

            peri = cv2.arcLength(c, True)

            approx = cv2.approxPolyDP(c, 0.018 * peri, True)

            #print("approx" +str(approx))

            # if our approximated contour has four points, then

            # we can assume that we have found our screen

            if len(approx) == 4:

                screenCnt = approx

                break





        if screenCnt is None:

            detected = 0

            print("No contour detected")


        else:

            detected = 1


        if detected == 1:
            print("cam_num: " +str(cam_num))
            #print(screenCnt)
            try:
                cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)

            except:
                continue


        # Masking the part other than the number plate

        mask = np.zeros(gray.shape,np.uint8)

        try:
            new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)

        except:
            continue


        new_image = cv2.bitwise_and(img,img,mask=mask)


        # Now crop

        (x, y) = np.where(mask == 255)

        (topx, topy) = (np.min(x), np.min(y))

        (bottomx, bottomy) = (np.max(x), np.max(y))

        Cropped = gray[topx:bottomx+1, topy:bottomy+1]





        #Read the number plate

        text = pytesseract.image_to_string(Cropped, config='--psm 11')
        #if entrance_camera:
        text_valid = validate_text(text)
        if len(text_valid)==8:
            print("Cam Num " +str(cam_num) +"Detected License Plate Number is: "+str(text_valid))
            break
        print("Detected Number is:",text)



        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    queue.put(text_valid)
    print("finish recog")
    return text_valid
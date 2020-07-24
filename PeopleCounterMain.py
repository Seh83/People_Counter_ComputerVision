import datetime
import os
import time

import cv2
import imutils

width = 800

textIn = 0
textOut = 0

'''
def getIntersection(line1, line2):
    s1 = numpy.array(line1[0])
    e1 = numpy.array(line1[1])

    s2 = numpy.array(line2[0])
    e2 = numpy.array(line2[1])

    a1 = (s1[1] - e1[1]) / (s1[0] - e1[0])
    b1 = s1[1] - (a1 * s1[0])

    a2 = (s2[1] - e2[1]) / (s2[0] - e2[0])
    b2 = s2[1] - (a2 * s2[0])

    if abs(a1 - a2) < sys.float_info.epsilon:
        return False

    x = (b2 - b1) / (a1 - a2)
    y = a1 * x + b1
    return

'''


def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y


def testIntersectionIn(x, y):
    res = -450 * x + 400 * y + 157500
    #print(res)
    # if((x>340 and x<390) and (y<30) and (w<190 and w > 170)):
    if (x > 340 and x < 370) and (y < 20):
        # if (res >= -550) and (res <= 550):
        # if (res >= -1700) and (res < 1700):
        print(str(res))
        return True
    return False


#         x -  y - w - h
# sol alt 0 - 300-   -
# kapı   300 - 40-   -
# IN x > 290 and x < 320 OUT x > 340 and x < 370 WHILE Y < 30


def testIntersectionOut(x, y):
    res = -450 * x + 400 * y + 180000
    #print(res)
    # if((x>270 and x<320) and (y<30) and (w<240 and w > 210)):
    if ((x > 290 and x < 320) and (y < 10)):
        # if (res >= -550) and (res <= 550):
        # if (res >= -1700) and (res <= 1700):
        print(str(res))
        return True

    return False


camera = cv2.VideoCapture('rtsp://admin:admin123@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0')

firstFrame = None

# loop over the frames of the video
while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    (grabbed, frame) = camera.read()
    text = "Unoccupied"

    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if not grabbed:
        break

    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=width)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        continue

    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # loop over the contours
    # cv2.line(img=frame, pt1=(0, 200), pt2=(width, 200), color=(0, 0, 255), thickness=5, lineType=8, shift=0)
    # cv2.line(img=frame, pt1=(0, 300), pt2=(width, 300), color=(255, 0, 0), thickness=5, lineType=8, shift=0)

    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < 12000:
            continue
        # print(cv2.arcLength(c, True))
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #print(w)
        cv2.line(frame, (width // 2, 0), (width, 550), (250, 0, 1), 2)  # blue line
        cv2.line(frame, (width // 2 - 50, 0), (width - 50, 550), (0, 0, 255), 2)  # red line
        # print(x, y, w, h)
        ######################################
        a = (width // 2, 0), (width, 550)

        b = (width // 2 - 50, 0), (width - 50, 550)
        print(line_intersection(a, b))
        ######################################
        # x: yatay y: yakınlık

        rectangleCenterPoint = ((x + x + w) // 2, (y + y + h) // 2)
        cv2.circle(frame, rectangleCenterPoint, 1, (0, 0, 255), 5)

        #Color for rectangleCenterPoint
        cv2.line(img=frame, pt1=((x + x + w) // 2, (y + y + h) // 2), pt2=((x + x + w) // 2, (y + y + h) // 2),
                 color=(255, 0, 0), thickness=5, lineType=8,
                 shift=0)

        #
        # if testIntersectionIn((x + x + w) // 2, (y + y + h) // 2):
        # if testIntersectionIn(w,h):
        # if rectangleCenterPoint ( x > 290 and x < 320  ):

        # if (  ):
        #
        #if (((x + x + w) // 2) >= (width // 2 - 50, 0) and ((x + x + w) // 2) <= (width // 2, 0)) and (((y + y + h) // 2) >= (width - 50, 550) and ((y + y + h) // 2)  <= (width, 550)):
        if testIntersectionIn(x, y):
            textIn += 1
            camera.release()
            camera = cv2.VideoCapture('rtsp://admin:admin123@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0')

        # print(x,y)
        # if testIntersectionOut((x + x + w) // 2, (y + y + h) // 2):
        # if testIntersectionOut(w,h):
        # if rectangleCenterPoint in (x > 340 and x < 370):
        # todo Correctly calculate the lines and place the intersections accordingly.
        #if (((x + x + w) // 2) >= (width // 2 - 50, 0) and ((x + x + w) // 2) <= (width // 2, 0)) and (((y + y + h) // 2) >= (width - 50, 550) and ((y + y + h) // 2)  <= (width, 550)):
        if testIntersectionOut(x, y):
            textOut += 1
            camera.release()
            camera = cv2.VideoCapture('rtsp://admin:admin123@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0')

        # draw the text and timestamp on the frame

        # show the frame and record if the user presses a key
        # cv2.imshow("Thresh", thresh)
        # cv2.imshow("Frame Delta", frameDelta)

    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break

    cv2.putText(frame, "In: {}".format(str(textIn)), (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.putText(frame, "Out: {}".format(str(textOut)), (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    cv2.imshow("Kisi Sayar", frame)

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()

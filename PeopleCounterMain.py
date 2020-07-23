import datetime
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


def testIntersectionIn(x, y):
    res = -750 * x + 700 * y + 157500
    print(res)
    if (res >= -850) and (res < 850):
        print(str(res))
        return True
    return False


def testIntersectionOut(x, y):
    res = -750 * x + 700 * y + 180000
    print(res)
    if (res >= -850) and (res <= 850):
        print(str(res))
        return True

    return False


camera = cv2.VideoCapture('rtsp://admin:admin123@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0')
# camera = cv2.VideoCapture(0)

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
        if cv2.contourArea(c) < 11000:
            continue
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.line(frame, (width // 2, 0), (width, 750), (250, 0, 1), 2)  # blue line
        cv2.line(frame, (width // 2 - 50, 0), (width - 50, 750), (0, 0, 255), 2)  # red line
        #print(x, y, w, h)

        # x: yatay y: yakınlık

        rectangleCenterPoint = ((x + x + w) // 2, (y + y + h) // 2)
        cv2.circle(frame, rectangleCenterPoint, 1, (0, 0, 255), 5)
        cv2.line(img=frame, pt1=((x + x + w) // 2, (y + y + h) // 2), pt2=((x + x + w) // 2, (y + y + h) // 2),
                 color=(255, 0, 0), thickness=5, lineType=8,
                 shift=0)

        #
        # if testIntersectionIn((x + x + w) // 2, (y + y + h) // 2):
        if testIntersectionIn((x + x + w) // 2, (y + y + h) // 2):
            textIn += 1

        # if testIntersectionOut((x + x + w) // 2, (y + y + h) // 2):
        if testIntersectionOut((x + x + w) // 2, (y + y + h) // 2):
            textOut += 1

        # draw the text and timestamp on the frame

        # show the frame and record if the user presses a key
        # cv2.imshow("Thresh", thresh)
        # cv2.imshow("Frame Delta", frameDelta)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cv2.putText(frame, "In: {}".format(str(textIn)), (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, "Out: {}".format(str(textOut)), (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    cv2.imshow("Security Feed", frame)

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()

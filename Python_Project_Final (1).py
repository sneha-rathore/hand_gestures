import cv2
import numpy as np
import math
import pyautogui as pyy

cap = cv2.VideoCapture(0)
while (cap.isOpened()):
    isTrue, img = cap.read()
    # read image

    # get hand data from the rectangle sub window on the screen
    cv2.rectangle(img, (80, 88), (300, 400), (0, 255, 0), 0)
    crop_img = img[100:300, 100:300]

    # convert to grayscale
    grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    # applying gaussian blur
    value = (35, 35)
    blurred = cv2.GaussianBlur(grey, value, 0)

    # thresholdin: Otsu's Binarization method
    _, thresh1 = cv2.threshold(blurred, 127, 255,
                               cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # show thresholded image
    cv2.imshow('Thresholded', thresh1)

    contours, hierarchy = cv2.findContours(thresh1.copy(), cv2.RETR_TREE, \
                                           cv2.CHAIN_APPROX_NONE)

    # find contour with max area
    cnt = max(contours, key=lambda x: cv2.contourArea(x))

    # finding convex hull
    hull = cv2.convexHull(cnt)

    # drawing contours
    drawing = np.zeros(crop_img.shape, np.uint8)
    cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 0)
    cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 0)

    # finding convex hull
    hull = cv2.convexHull(cnt, returnPoints=False)  

    # finding convexity defects
    defects = cv2.convexityDefects(cnt, hull)
    count_defects = 0
    cv2.drawContours(thresh1, contours, -1, (0, 255, 0), 3)

    # applying Cosine Rule to find angle for all defects (between fingers)
    # with angle > 90 degrees and ignore defects
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]

        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])

        # find length of all sides of triangle
        a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
        c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)

        # apply cosine rule here
        angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

        # ignore angles > 90 and highlight rest with red dots
        if angle <= 90:
            count_defects += 1
            cv2.circle(crop_img, far, 1, [0, 0, 255], -1)
        # dist = cv2.pointPolygonTest(cnt,far,True)

        # draw a line from start to end i.e. the convex points (finger tips)
        cv2.line(crop_img, start, end, [0, 255, 0], 2)
        # cv2.circle(crop_img,far,5,[0,0,255],-1)

    # define actions required
    if count_defects == 1:
        cv2.putText(img, "2 Fingers", (50, 50), cv2.FONT_ITALIC, 2, 2)
        pyy.press('right')
    elif count_defects == 2:
        str = " 3 fingers"
        pyy.press('left')
        cv2.putText(img, str, (5, 50), cv2.FONT_ITALIC, 1, 2)
    elif count_defects == 3:
        pyy.press('f'or'F')
        cv2.putText(img, " 4 fingers", (50, 50), cv2.FONT_ITALIC, 2, 2)
    elif count_defects == 4:
        pyy.press('space')
        cv2.putText(img, " 5 fingers", (50, 50), cv2.FONT_ITALIC, 2, 2)
    else:
        cv2.putText(img, "This means an entire hand", (50, 50), \
                    cv2.FONT_ITALIC, 2, 2)

    # show appropriate images in windows
    cv2.imshow('Gesture', img)
    # all_img = np.hstack((drawing, crop_img))
    cv2.imshow('Contours', crop_img)

    if cv2.waitKey(20) & 0XFF == ord('d'):
        break

cap.release()
cv2.destroyAllWindows()

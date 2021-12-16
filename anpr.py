import cv2
import imutils  # for contouring, resizing, rotation etc
import numpy as np
import pytesseract  # this has the ocr functions

# this is the path where I have downloaded tesseract folder
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

image = cv2.imread('car1.jpg', cv2.IMREAD_COLOR)

# avoiding extra resolution and making sure licence plate remains in the frame
image = cv2.resize(image, (600, 400))

# gray-scaling is a common practice in image processing
# so that it eliminates the detailing of colours and only focus on processing
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# bilateral filter or blurring removes the useless info around the plate called
# noise.  destination_image = cv2.bilateralFilter(source_image, diameter of pixel,
# sigmaColor, sigmaSpace). You can increase the sigma color and sigma space from 15 to
# higher values to blur out more background information, but be careful that the useful part does not get
# blurred.
gray = cv2.bilateralFilter(gray, 13, 15, 15)

# edge detection using canny method from opencv where the detection gives the skeleton of the image(think of it as
# spider webs on a black bg) detecting only edges between threshold 30 and 200
edged = cv2.Canny(gray, 30, 200)

# Once the counters(they are curves joining continuous points with same color and intensity on only black bg,basically
# a numpy array)
# have been detected we sort them from big to small and consider only the first 10 results ignoring
# the others. In our image the counter could be anything that has a closed surface but of all the obtained results the
# license plate number will also be there since it is also a closed surface.
contours = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = imutils.grab_contours(contours)
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
screenCnt = None

# To filter the license plate image among the obtained results, we will loop though all the results and check which has
# a rectangle shape contour with four sides and closed figure. Since a license plate would definitely be a rectangle
# four sided figure.
for c in contours:

    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.018 * peri, True)
    # contour has 4 simple points(corners of rectangle of licence plate) detected then it is the license plate
    if len(approx) == 4:
        screenCnt = approx
        break

if screenCnt is None:
    detected = 0
    print("No contour detected")
else:
    detected = 1

# once contour is found we save it in screenCnt variable and draw a rectangle box around it
if detected == 1:
    cv2.drawContours(image, [screenCnt], -1, (0, 0, 255), 3)

# masking is eliminating all that is outside the rectangle box
mask = np.zeros(gray.shape, np.uint8)
new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1, )
new_image = cv2.bitwise_and(image, image, mask=mask)

# now we crop the image and save it for further use
(x, y) = np.where(mask == 255)
(topx, topy) = (np.min(x), np.min(y))
(bottomx, bottomy) = (np.max(x), np.max(y))
Cropped = gray[topx:bottomx + 1, topy:bottomy + 1]

# read the plate by using pytesseract method image_to_string where psm means page segmentation modes which are
# numbered from 0-13. we need them because here we are working with group of characters and 11 means treat image
# as single character
txt = pytesseract.image_to_string(Cropped, config='--psm 11')
print("Detected license plate Number is:", txt)
img = cv2.resize(image, (500, 300))
Cropped = cv2.resize(Cropped, (400, 200))
cv2.imshow('car', img)
cv2.imshow('Cropped', Cropped)

cv2.waitKey(0)
cv2.destroyAllWindows()

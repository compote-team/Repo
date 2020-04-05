import cv2
import numpy as np
import math
from robodk import*
from robolink import*
RDK = Robolink()
robot = RDK.Item("KUKA KR 3 R540")
RDK.setRunMode(6)

wind2 = "s"

cv2.namedWindow(wind2)

if __name__ == '__main__':
	def nothing(*arg):
		pass

def quita(self):
    self.root.destroy()

cap = cv2.VideoCapture(1)

cv2.createTrackbar('xc', wind2, 0, 640, nothing)

cv2.createTrackbar('yc', wind2, 0, 480, nothing)

def kuka(camy=0, camz=0):
	kuku = RDK.AddTarget('kuku')
	kuku.setJoints([0, 0, 0, 0, 0, 0])
	a = kuku.Pose()
	a=str(a).split("):")
	a=str(a).split(", ")
	x, y, z, rotx, roty, rotz = float(a[0]),float(a[1]),float(a[2]),float(a[3]), float(a[4]), float(str(a[5])[:-1])
	rotx *= -1
	rotz *= -1
	target = RDK.AddTarget("T1")
	target.setAsCartesianTarget()
	target.setJoints([0, 0, 0, 0, 0, 0])
	target.setPose(KUKA_2_Pose([x, y+camy, z+camz, rotx, roty, rotz]))
	robot.MoveJ(target)
	target.Delete()
	kuku.Delete()


while True:
	frame, img = cap.read()
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

	h1 = 0
	s1 = 95
	v1 = 200
	h2 = 255
	s2 = 255
	v2 = 255

	noise = 250

	min_height = 0
	min_width = 0

	max_height = 480
	max_width = 640

	xc = cv2.getTrackbarPos('xc', wind2)
	yc = cv2.getTrackbarPos('yc', wind2)

	cv2.circle(img, (xc, yc), 3, (255, 0, 255), -1)


	if cv2.waitKey(5) & 0xFF == ord('q'):
		quit()

	thresh = cv2.inRange(hsv, (h1, s1, v1), (h2, s2, v2))

	h_min = np.array((h1, s1, v1), np.uint8)
	h_max = np.array((h2, s2, v2), np.uint8)

	contours, hierarchy = cv2.findContours(
		thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 

	for cnt in contours:
		x1, y1, w1, h1 = cv2.boundingRect(cnt)
		Areab = cv2.contourArea(cnt)

		X2 = x1 + w1
		Y2 = y1 + h1

		if min_width <= w1 <= max_width and min_height <= h1 <= max_height and Areab > noise: 
			cX, cY = int((x1+X2)/2), int((y1+Y2)/2)

			cXY = np.array([cX, cY])
			camC = np.array([320, 240])
			onobj = camC - cXY
			xny = 0

			if onobj[0] > 1:
				print("x++++1")
				kuka(camy=2)
			elif onobj[0] < -1:
				print("x----1")
				kuka(camy=-2)
			else:
				print("X - gotcha")
			
			if onobj[1] > 1:
				print("y----1")
				kuka(camz=-2)
			elif onobj[1] < -1:
				print("y++++1")
				kuka(camz=2)
			else:
				print("Y - gotcha")

			if -1 <= onobj[0] <= 1 and -1 <= onobj[1] <= 1:
				print("def toobj")

			cv2.circle(img, (cX, cY), 3, (255, 0, 255), -1)
			cv2.rectangle(img, (x1, y1), (X2, Y2), (0, 255, 0), 2)


	cv2.imshow('result', img)
	cv2.imshow('BozhePomogiMne', thresh)


cap.release()
cv2.destroyAllWindows()

#Тут *ОЧЕНЬ* много костылей, не пытайтесь это понять
import cv2

import os
from os import chdir

import numpy as np
import math

from tkinter import *
from tkinter import filedialog as fd

import requests

from robodk import*
from robolink import*

def shift():
	RDK.RunCode('shift')


def spread():
	RDK.RunCode('spread')


h_p = [0.000, 230.846, 348.378, -92.980, 0.000, 180.000]


def vacuum(v):
	requests.get("http://192.168.20.120:5002/user/"+v)

def DaS(nx, ny, nz, rx, ry, rz):
	# TODO Вставить код передвижения к "зоне" и передвижение в начальную точку

	target = RDK.AddTarget("T1")
	target.setAsCartesianTarget()
	target.setJoints([0, 0, 0, 0, 0, 0])
	target.setPose(KUKA_2_Pose([x, y, vz, -180.000, 0.000, 180.000]))
	robot.MoveJ(target)

	target.setJoints([0, 0, 0, 0, 0, 0])
	target.setPose(KUKA_2_Pose([nx, ny, vz, -180.000, 0.000, 180.000]))
	robot.MoveJ(target)

	target.setJoints([0, 0, 0, 0, 0, 0])
	target.setPose(KUKA_2_Pose([nx, ny, nz, -180.000, 0.000, 180.000]))
	robot.MoveJ(target)

	vacuum(0)
	spread()

	target.setJoints([0, 0, 0, 0, 0, 0])
	target.setPose(KUKA_2_Pose(h_p))  # !возможно не работает
	robot.MoveJ(target)

chdir("C:\\Save")  # перемещение в папку с надстройками
a = open("home.py").read()
exec(a)

RDK = Robolink()
robot = RDK.Item("KUKA KR 3 R540")
RDK.setRunMode(6)




if __name__ == '__main__':
	def nothing(*arg):
		pass

cap = cv2.VideoCapture(1)

sm = 0.1952380952380952  # qr/pix

crange = [0, 0, 0, 0, 0, 0]

vz=300
pogZ = -90

while True:
	os.chdir("C:\\Save")  # перемещение в папку с надстройками
	nl=True
	while nl:
		pause(0.25)
		try:
			file_name = requests.get("http://192.168.20.120:5000").text

			print(file_name)
			
			f = open(file_name+".py", 'r')
			f = f.read()

			exec(f)

			print("=====SETTINGS=====")
			print(f)
			print("==================")

			nl=False
		except:
			print("ERROR, again...")


	frame, img = cap.read()
	
	# преобразуем RGB картинку в HSV модель
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		
	# применяем цветовой фильтр
	thresh = cv2.inRange(hsv, (h1, s1, v1), (h2, s2, v2))

	h_min = np.array((h1, s1, v1), np.uint8)
	h_max = np.array((h2, s2, v2), np.uint8)

	contours, hierarchy = cv2.findContours(
		thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # Нахождение контуров

	for cnt in contours:
		x1, y1, w1, h1 = cv2.boundingRect(cnt)  # получение первых точек
		Areab = cv2.contourArea(cnt)

		X2 = x1 + w1  # Получение 2-ой х
		Y2 = y1 + h1  # Получение 2-ой у

		if Areab > noise:  # Отсеевание шумов
		
			if min_width <= w1 <= max_width and min_height <= h1 <= max_height:  # сравнивание размеров
				# нахождение центра объекта
				cX, cY = int((x1+X2)/2), int((y1+Y2)/2)

				rect = cv2.minAreaRect(cnt)  # пытаемся вписать прямоугольник
				# поиск четырех вершин прямоугольника
				box = cv2.boxPoints(rect)
				box = np.int0(box)  # округление координат
				areac = int(rect[1][0] * rect[1][1])

				# вычисление координат двух векторов, являющихся сторонам прямоугольника
				edge1 = np.int0((box[1][0] - box[0][0], box[1][1] - box[0][1]))
				edge2 = np.int0((box[2][0] - box[1][0], box[2][1] - box[1][1]))

				# выясняем какой вектор больше
				usedEdge = edge1
				if cv2.norm(edge2) > cv2.norm(edge1):
					usedEdge = edge2
				reference = (1, 0)  # горизонтальный вектор, задающий горизонт
				
				if cX < 320:    # Если объект правее центра, то...
					rX = (320-(640-cX))*sm*10
				elif cX >= 320:
					rX = (cX-320)*sm*10
				y = rX  #перевод из пикселей в сантиметры
				x = cY*sm*10
				
				# вычисляем угол между самой длинной стороной прямоугольника и горизонтом
				angle =90 - (180.0 / math.pi * \
					math.acos((reference[0] * usedEdge[0] + reference[1] *
							   usedEdge[1]) / (cv2.norm(reference) * cv2.norm(usedEdge))))
				

				if x > 500 or y > 500:
					break
				else:			

					# !---НАЧАЛО УПРАВЛЕНИЯ КУКОЙ---!
					# *Передвижение к точке над объектом

					target = RDK.AddTarget("T1")
					target.setAsCartesianTarget()
					target.setJoints([0, 0, 0, 0, 0, 0])
					target.setPose(KUKA_2_Pose([x, y, vz, -180.000, 0.000, 180.000]))
					robot.MoveJ(target)

					# *Вращение фланса
					joints = robot.Joints().list()
					print("angle=", angle)
					r1 = joints[0]
					r6 = joints[5]
					r6 = r6-r1  # Выравнивание фланса на 90. относительно Y
					r6 = r6-angle  # Поворот фланса по объекту
					joints[5] = r6  # обозначение поворота для фланса
					robot.MoveJ(joints)  # вращение фланса

					notLoaded=True
					while notLoaded:  # Пытаемся получить информацию с Android-приложения
					
						try:
							z = requests.get("http://192.168.20.120:5001").text
							z = int(z)
							z = z+pogZ
							print('ha')
							notLoaded = False
					
						except:
							print("[!] Z not found! Get request again...")


					print('[·]', 'y=', y, 'x=', x, 'z=', z)

					# *Код передвижения к объекту
					
					kuku = RDK.AddTarget('kuku')
					kuku.setJoints([0, 0, 0, 0, 0, 0])
					a = kuku.Pose()
					a=str(a).split("):")
					a=str(a).split(", ")
					rotx, roty, rotz = float(a[3]), float(a[4]), float(str(a[5])[:-1])
					rotx *= -1
					rotz *= -1
					mz = float(a[2])
					print('mz=', mz)
					rz = mz - z
					print('rz=', rz)
					pause(2)
					rz += 55.000
					print(rotx, roty, rotz)

					pause(5)
					kuku.Delete()

					target.setJoints([0, 0, 0, 0, 0, 0])
					target.setPose(KUKA_2_Pose([x, y, rz, rotz, roty, rotx]))
					robot.MoveJ(target)  # вращение фланса

					RDK.RunCode('shift')
					pause(3)

					if zone == 0:

						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([x, y, vz, rotz, roty, rotx]))
						robot.MoveJ(target)  # вращение фланса

						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([4.953211, 388.645043, vz, rotz, roty, rotx]))
						robot.MoveJ(target)  # вращение фланса

						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([4.953211, 388.645043, 195.366170, -159.390574, 1.440576, 175.399279]))
						robot.MoveJ(target)
					elif zone == 1:

						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([x, y, vz, rotz, roty, rotx]))
						robot.MoveJ(target)  # вращение фланса
						
						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([112.236140, -278.347448, vz, rotz, roty, rotx]))
						robot.MoveJ(target)  # вращение фланса

						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([112.236140, -278.347448, 325.973670, 66.957624, 2.624899, 177.377594 ]))
						robot.MoveJ(target)
					else:

						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([x, y, vz, rotz, roty, rotx]))
						robot.MoveJ(target)  # вращение фланса
						
						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([159.897334, 378.957109, 320, rotz, roty, rotx]))
						robot.MoveJ(target)  # вращение фланса

						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([159.897334, 378.957109, 106.069731, 178.471565, -1.518154, -177.135065]))
						robot.MoveJ(target)
					target.setJoints([0, 0, 0, 0, 0, 0])
					target.setPose(KUKA_2_Pose(h_p))  # !возможно не работает
					robot.MoveJ(target)
					
					# *Отчистка сцены от мусорных точек
					target.Delete()

cap.release()
cv2.destroyAllWindows()

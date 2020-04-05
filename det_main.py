from imageai.Detection.Custom import CustomObjectDetection
import cv2
import numpy as np
from robodk import*
from robolink import*
import requests
import os
import pymorphy2 as pm2
import pymorphy2_dicts_ru

import speech_recognition as sr

RDK = Robolink()
robot = RDK.Item("KUKA KR 3 R540")

RDK.setRunMode(1)

target = RDK.AddTarget("T1")
target.setAsCartesianTarget()
target.setJoints([0, 0, 0, 0, 0, 0])
target.setPose(KUKA_2_Pose([218.969, 19.596, 375.746, 177.900, 38.797, 174.764]))
robot.MoveJ(target)
target.Delete()

input("Запустить на роботе?")

#!-----------------------------------------------------!#
#!                                                     !#
RDK.setRunMode(6)

target = RDK.AddTarget("T1")
target.setAsCartesianTarget()
target.setJoints([0, 0, 0, 0, 0, 0])
target.setPose(KUKA_2_Pose([218.969, 19.596, 375.746, 177.900, 38.797, 174.764]))
robot.MoveJ(target)
target.Delete()
#!													   !#
#!-----------------------------------------------------!#
cap = cv2.VideoCapture(1)

detector = CustomObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath("C:/Users/dagae/OneDrive/Рабочий стол/jar/models/detection_model-ex-146--loss-0015.267.h5")
detector.setJsonPath("C:/Users/dagae/OneDrive/Рабочий стол/jar/json/detection_config.json")
detector.loadModel()

def kuka(camy=0, camz=0):
	joints = robot.Joints().list()
	# print("angle=", angle)
	# r1 = joints[0]
	# r6 = joints[5]
	# r6 = r6-r1  # Выравнивание фланса на 90. относительно Y
	# r6 = r6-angle  # Поворот фланса по объекту
	# joints[5] = r6  # обозначение поворота для фланса
	print(joints)
	
	k = joints[4]
	k += camz
	
	joints[4] = k
	i = 0
	robot.MoveJ(joints)
	i+=1
	print(i)
	
	kaka = RDK.AddTarget('kaka')
	kaka.setJoints([0, 0, 0, 0, 0, 0])
	
	a = kaka.Pose()
	a=str(a).split("):")
	a=str(a).split(", ")
	
	x, y, z, rotx, roty, rotz = float(str(a[0])[7:]),float(a[1]),float(a[2]),float(a[3]), float(a[4]), float(str(a[5])[:-1])
	rotx *= -1
	
	target = RDK.AddTarget("T1")
	target.setAsCartesianTarget()
	target.setJoints([0, 0, 0, 0, 0, 0])
	target.setPose(KUKA_2_Pose([x, y+camy, z, rotz, roty, rotx]))
	robot.MoveJ(target)
	target.Delete()
	kaka.Delete()

def atobj(onobj):
	if not -15 <= onobj[0] <= 15:
		if onobj[0] > 1:
			print("x++++1")
			print(onobj)
			kuka(camy=1)
		else:
			print("x----1")
			print(onobj)
			kuka(camy=-1)

	if not -15 <= onobj[1] <= 15:
		if onobj[1] > 1:
			print("Y++++")
			print(onobj)
			kuka(camz=-1)
		else:
			print("Y----")
			print(onobj)
			kuka(camz=1)

voiceresult = "bank"

cmin, cmax = (0, 0, 0), (255, 255, 255)

query = ""

nums = {
    "один": 1,
    "два": 2,
    "три": 3,
    "четыре": 4,
    "пять": 5,
    "шесть": 6,
    "семь": 7,
    "восемь": 8,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "всё": 8
}

colors = {
    "красный": ((0, 90, 0), (10, 255, 255)),
    "синий": ((95, 90, 135), (155, 255, 255)),
    "зелёный": ((40, 55, 77), (110, 200, 255)),
    "фиолетовый": ((0, 60, 255), (150, 255, 255)),
    "белый": ((35, 0, 250), (175, 5, 255)),
    "чёрный": ((75, 15, 5), (140, 255, 155)),
    "жёлтый": ((20, 125, 255), (25, 255, 255)),
    "оранжевый": ((10, 120, 180), (25, 255, 255)),
    "коричневый": ((0, 155, 120), (12, 255, 255)),
    "всё": ((0, 0, 0), (255, 255, 255))
}

# TODO: добавить остальные предметы
objects = {
    "банан": "banan",
    "бандероль": "banderol",
    "банка": "bank",
    "бутылка": "bottle",
    "игрушка": "ptoy",
    "пакет": "package",
    "рубль": "money"
}

materials = {
    "стеклянный": "g",
    "пластмасса": "p",
    "пластик": "p"
}


def voice():
    with sr.Microphone(device_index=1) as source:
        print('\rСкажите что нибудь...', end='')
        audio = r.listen(source)

    try:
        query = r.recognize_google(audio, language="ru-RU")
        print('\rРаспознано: \"%s\"      ' % query, end='')

    except sr.UnknownValueError:
        print("\rGoogle Speech Recognition could not understand audio\n")
        query = "ERROR"

    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service\n")
        query = "ERROR"

    return query


morph = pm2.MorphAnalyzer()
r = sr.Recognizer()


def text_analyze(x):
    class analyze:
        def __init__(self, color, count, subject, material):
            self.color = color
            self.count = count
            self.subject = subject
            self.material = material

    analyze.color, analyze.count, analyze.material, analyze.subject = (
        (0, 0, 0), (255, 255, 255)), 1, "", ""  # Значения по дефолту
    x = x.split(" ")

    for a in x:  # Разбив предложения на слова
        parsed = morph.parse(a)  # Парсим слово

        for parsedword in parsed:
            NormalForm = (parsedword.normal_form)  # Перевод в начальную форму

            print(NormalForm)

            for key, value in nums.items():  # Добавление количество предметов в класс
                if key in NormalForm:
                    analyze.count = value

            for key, value in colors.items():  # Добавление цвета предмета в класс
                if key in NormalForm:
                    analyze.color = value

            for key, value in materials.items():  # Добавление матерьяла предмета в класс
                if key in NormalForm:
                    analyze.material = value

            for key, value in objects.items():  # Добавление предмета в класс
                if key in NormalForm:
                    analyze.subject = analyze.material+value

    return analyze

while 1: 	
    # query = voice()
	query = "красная банка"

    if query != "ERROR":
        analyzed = text_analyze(query)
        print(
            f"\nCOLOR : {analyzed.color}\nCOUNT : {analyzed.count}\nMATERIAL : {analyzed.material}\nSUBJECT : {analyzed.subject}\n")
	else:
		continue
	for count in range(analyzed.count):   
		_, img = cap.read()

		hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

		if cv2.waitKey(5) & 0xFF == ord('q'):						#выход
			quit()
					
		print("\n[!] STARTING DETECTION\n")

		img,detections = detector.detectObjectsFromImage(output_type="array", input_type="array", input_image=img, minimum_percentage_probability=90)
		for detection in detections:
			print(detection)
			print("detection",detection["name"], " : ", detection["percentage_probability"], " : ", detection["box_points"])

			name = detection["name"]

			if name != voiceresult: #пропуск, если объект не тот, что указан в "голосе"
				continue

			p1, p2 = (detection["box_points"][0], detection["box_points"][1]), (detection["box_points"][2], detection["box_points"][3])

			d1, d2 =  np.array(p1), np.array(p2)
			dot = (d1+d2)/2
			d3 = (int(dot[0]), int(dot[1]))
			
			cXY = dot
			camC = np.array([320, 240])
			onobj = camC - cXY
			xny = 0

			if (not -15 <= onobj[0] <= 15) and (not -15 <= onobj[1] <= 15):
				atobj(onobj)
			else:
				RDK.setRunMode(1)
				kaka = RDK.AddTarget("kaka")
				a = kaka.Pose()
				a = str(a).split("):")
				a = str(a).split(", ")

				x, y, z, rotx, roty, rotz = float(str(a[0])[7:]), float(a[1]), float(
					a[2]), float(a[3]), float(a[4]), float(str(a[5])[:-1])
				
				rotx *= -1
				pif = ((617-120)**2 - z**2)**0.5
				target = RDK.AddTarget("T1")
				target.setAsCartesianTarget()
				target.setJoints([0, 0, 0, 0, 0, 0])
				target.setPose(KUKA_2_Pose([x+pif-120.0, y, z-100.0, -180.0, 0.0, 180.0]))
				robot.MoveJ(target)
				target.Delete()
				kaka.Delete()
				#!-----------------------------------------------------!#
				#!                                                     !#
				input("Запустить на роботе?")
				RDK.setRunMode(6)
				kaka = RDK.AddTarget("kaka")
				a = kaka.Pose()
				a = str(a).split("):")
				a = str(a).split(", ")

				x, y, z, rotx, roty, rotz = float(str(a[0])[7:]), float(a[1]), float(
					a[2]), float(a[3]), float(a[4]), float(str(a[5])[:-1])
				
				rotx *= -1
				pif = ((617-120)**2 - z**2)**0.5
				target = RDK.AddTarget("T1")
				target.setAsCartesianTarget()
				target.setJoints([0, 0, 0, 0, 0, 0])
				target.setPose(KUKA_2_Pose([x+pif-120.0, y, z-100.0, -180.0, 0.0, 180.0]))
				robot.MoveJ(target)
				target.Delete()
				kaka.Delete()
				#!												       !#
				#!-----------------------------------------------------!#
				pixel = hsv[d3[0], d3[1]]

				print(pixel)

				upper = np.array([pixel[0] + 20, pixel[1] + 20, pixel[2] + 60])
				lower = np.array([pixel[0] - 20, pixel[1] - 20, pixel[2] - 60])

				thresh = cv2.inRange(hsv, lower, upper)

				contours, hierarchy = cv2.findContours(
					thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # Нахождение контуров

				for cnt in contours:
					Areab = cv2.contourArea(cnt)

					if Areab > 100:  # Отсеевание шумов

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

						# вычисляем угол между самой длинной стороной прямоугольника и горизонтом\
						angle = 90 - (180.0 / math.pi * \
							math.acos((reference[0] * usedEdge[0] + reference[1] *
										usedEdge[1]) / (cv2.norm(reference) * cv2.norm(usedEdge))))
										
						print(angle)				
						#Графика
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!-----------------------------------

						joints = robot.Joints().list()
						print("angle=", angle)
						r1 = joints[0]
						r6 = joints[5]
						r6 = r6-r1  # Выравнивание фланса на 90. относительно Y
						r6 = r6-angle  # Поворот фланса по объекту
						joints[5] = r6  # обозначение поворота для фланса
						robot.MoveJ(joints)
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!-----------------------------------

						cv2.putText(img, "%d" % int(angle), (d3[0], d3[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
						cv2.circle(img, (d3[0], d3[1]), 5, (255, 255, 255))
						RDK.setRunMode(1)
						kaka = RDK.AddTarget("kaka")
						a = kaka.Pose()
						a = str(a).split("):")
						a = str(a).split(", ")
						x, y, z, rotx, roty, rotz = float(str(a[0])[7:]), float(a[1]), float(a[2]), float(a[3]), float(a[4]), float(str(a[5])[:-1])

						rotx *= -1
						target = RDK.AddTarget("T1")
						target.setAsCartesianTarget()
						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([x, y, z-380.0+210.0, -180.0, 0.0, 180.0]))
						robot.MoveJ(target)
						target.Delete()
						kaka.Delete()

						#!-----------------------------------------------------!#
						#!                                                     !#
						input("Запустить на роботе?")
						RDK.setRunMode(6)
						kaka = RDK.AddTarget("kaka")
						a = kaka.Pose()
						a = str(a).split("):")
						a = str(a).split(", ")
						x, y, z, rotx, roty, rotz = float(str(a[0])[7:]), float(a[1]), float(a[2]), float(a[3]), float(a[4]), float(str(a[5])[:-1])

						rotx *= -1
						target = RDK.AddTarget("T1")
						target.setAsCartesianTarget()
						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([x, y, z-380.0+210.0, -180.0, 0.0, 180.0]))
						input("Запустить на роботе?")
						robot.MoveJ(target)
						target.Delete()
						kaka.Delete()
						#!												       !#
						#!-----------------------------------------------------!#
						input("Запустить на роботе?")

						RDK.setRunMode(1)

						RDK.RunProgram('shiftik')

						input("Запустить на роботе?")


						RDK.setRunMode(1)

						kaka = RDK.AddTarget("kaka")
						a = kaka.Pose()
						a = str(a).split("):")
						a = str(a).split(", ")

						x, y, z, rotx, roty, rotz = float(str(a[0])[7:]), float(a[1]), float(
							a[2]), float(a[3]), float(a[4]), float(str(a[5])[:-1])
						
						rotx *= -1
						target = RDK.AddTarget("T1")
						target.setAsCartesianTarget()
						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([x, y, z+380.0-210.0, -180.0, 0.0, 180.0]))
						robot.MoveJ(target)
						target.Delete()
						kaka.Delete()
						#!-----------------------------------------------------!#
						#!                                                     !#

						input("Запустить на роботе?")
						RDK.setRunMode(6)

						kaka = RDK.AddTarget("kaka")
						a = kaka.Pose()
						a = str(a).split("):")
						a = str(a).split(", ")

						x, y, z, rotx, roty, rotz = float(str(a[0])[7:]), float(a[1]), float(
							a[2]), float(a[3]), float(a[4]), float(str(a[5])[:-1])
						
						rotx *= -1
						target = RDK.AddTarget("T1")
						target.setAsCartesianTarget()
						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([x, y, z+380.0-210.0, -180.0, 0.0, 180.0]))
						robot.MoveJ(target)
						target.Delete()
						kaka.Delete()
						#!												       !#
						#!-----------------------------------------------------!#
						RDK.setRunMode(1)
						kaka = RDK.AddTarget("kaka")
						a = kaka.Pose()
						a = str(a).split("):")
						a = str(a).split(", ")

						x, y, z, rotx, roty, rotz = float(str(a[0])[7:]), float(a[1]), float(
							a[2]), float(a[3]), float(a[4]), float(str(a[5])[:-1])
						
						rotx *= -1
						target = RDK.AddTarget("T1")
						target.setAsCartesianTarget()
						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([x-50.0, y+100.0, z, -180.0, 0.0, 180.0]))
						input("Запустить на роботе?")
						robot.MoveJ(target)

						target.Delete()
						kaka.Delete()
						#!-----------------------------------------------------!#
						#!                                                     !#
						RDK.setRunMode(6)
						kaka = RDK.AddTarget("kaka")
						a = kaka.Pose()
						a = str(a).split("):")
						a = str(a).split(", ")

						x, y, z, rotx, roty, rotz = float(str(a[0])[7:]), float(a[1]), float(
							a[2]), float(a[3]), float(a[4]), float(str(a[5])[:-1])
						
						rotx *= -1
						target = RDK.AddTarget("T1")
						target.setAsCartesianTarget()
						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([x-50.0, y+100.0, z, -180.0, 0.0, 180.0]))
						input("Запустить на роботе?")
						robot.MoveJ(target)

						target.Delete()
						kaka.Delete()
						#!												       !#
						#!-----------------------------------------------------!#

						input("Запустить на роботе?")

						RDK.setRunMode(1)

						RDK.RunProgram('spread')

						target = RDK.AddTarget("T1")
						target.setAsCartesianTarget()
						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([218.969, 19.596, 375.746, 177.900, 38.797, 174.764]))
						robot.MoveJ(target)
						target.Delete()

						input("Запустить на роботе?")

						#!-----------------------------------------------------!#
						#!                                                     !#
						RDK.setRunMode(6)

						target = RDK.AddTarget("T1")
						target.setAsCartesianTarget()
						target.setJoints([0, 0, 0, 0, 0, 0])
						target.setPose(KUKA_2_Pose([218.969, 19.596, 375.746, 177.900, 38.797, 174.764]))
						robot.MoveJ(target)
						target.Delete()
						#!													   !#
						#!-----------------------------------------------------!#

						break

					cv2.circle(img, tuple(d3), 3, (255, 0, 255), -1)
					cv2.rectangle(img, p1, p2, (255, 255, 0), 2)


		cv2.imshow('result', img)
cap.release()
cv2.destroyAllWindows()
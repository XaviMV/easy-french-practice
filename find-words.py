import os
import cv2
import random
import time as t

import streamlit as st

def funcio_ordenar_subtitols(a):

    num = ""
    for c in a:
        if c != "-":
            num += c
        else:
            break

    try:
        return int(num)
    except:
        return 0

def funcio_ordenar_paraules(x):
	return len(x.aparicions)


class Paraula:
	def __init__(self, paraula):
		self.paraula = paraula
		self.aparicions = []

	def afegir_aparicio(self, carpeta, frames):
		posicio = Posicio_paraula(carpeta, frames)
		self.aparicions.append(posicio)

class Posicio_paraula:
	def __init__(self, carpeta, frames):
		self.carpeta = carpeta
		self.frames = frames


def buscar_paraules(path, carpeta, diccionari): # path apunta al directori amb les carpetes, carpeta es el numero de carpeta, diccionari es el que es vol ampliar

	path = os.path.join(path, carpeta)
	arxius = os.listdir(path)
	for i in arxius:
		if ".txt" in i: # si es un fitxer tipus .txt
			path = os.path.join(path, i)

	fitxer = open(path)

	while True: # cada iteracio es una linia del document .txt

		linia = fitxer.readline()

		if linia == "":
			break

		buff = "" # guarda les paraules temporalment
		frames = ""
		llegir = False # boolean que marca quan s'ha de començar a llegir la frase
		for c in linia:
			if c == "#":
				llegir = True
			if not llegir and c != '.' and c != ' ':
				frames += c

			if llegir:
				c = c.lower()
				if (ord(c) < 97 or (ord(c) > 122 and ord(c) < 192)) and len(buff) != 0: # Si el caracter no es una lletra
					if diccionari.get(buff) == None:
						p = Paraula(buff)
						p.afegir_aparicio(carpeta, frames)
						diccionari[buff] = p
					else:
						diccionari[buff].afegir_aparicio(carpeta, frames)
					buff = ""
				
				elif ord(c) > 96 and (ord(c) < 123 or ord(c) > 191):
					buff += c

	return diccionari


def trobar_exemple(path_ini, p, num_aparicio):

	carpeta, frames = p.aparicions[num_aparicio].carpeta, p.aparicions[num_aparicio].frames

	path = os.path.join(path_ini, carpeta, frames+".png")

	img = cv2.imread(path)

	#cv2.imshow("sub", img)
	#cv2.waitKey()

	# despres mostrar la imatge total

	path = os.path.join(path_ini, carpeta)

	for a in os.listdir(path):
		if ".mp4" in a:
			path = os.path.join(path_ini, carpeta, a)

	frame_ini, frame_fi = frames.split('-')

	frame_number = int((int(frame_ini)+int(frame_fi))/2)

	cap = cv2.VideoCapture(path)
	cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number-1)
	res, frame = cap.read()

	cap.release()

	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	st.image(frame)

	# cv2.imshow("img", frame)
	# cv2.waitKey()


def play_video(path, frame_ini, frame_fi):

	# create video object
	return 0

def get_segons(frames, path_video):

	video = cv2.VideoCapture(path_video);

	framerate = video.get(cv2.CAP_PROP_FPS)

	# trobar frames ini
	frames_ini = int(frames.split("-")[0])
	frames_fi = int(frames.split("-")[1])

	segons_ini = frames_ini/framerate
	minuts_ini = 0
	while (segons_ini > 59):
		minuts_ini += 1
		segons_ini -= 60

	segons_fi = frames_fi/framerate
	minuts_fi = 0
	while (segons_fi > 59):
		minuts_fi += 1
		segons_fi -= 60

	return minuts_ini, segons_ini, minuts_fi, segons_fi



@st.cache_data
def funcio_fer_un_sol_cop():
	dict_paraules = dict()

	PATH = os.path.join(os.getcwd(), "videos")

	carpetes = os.listdir(PATH)
	carpetes.sort(key=funcio_ordenar_subtitols) # ordenar carpetes de num mes baix a num mes alt
	for i in carpetes:
	    if not ("." in i): # si es una carpeta
		    dict_paraules = buscar_paraules(PATH, i, dict_paraules)


	llista_paraules = []
	for p in dict_paraules:
		llista_paraules.append(dict_paraules[p])


	llista_paraules.sort(key=funcio_ordenar_paraules)

	random.seed(t.time())

	return llista_paraules

llista_paraules = funcio_fer_un_sol_cop()




# imprimir totes les paraules i els cops que apareixen, tambe mostrar subtitols d'exemple on apareix una en concret si el while es posa a True

# paraules_totals = 0
# for e in llista_paraules:
# 	print(e.paraula, len(e.aparicions))
# 	paraules_totals += len(e.aparicions)
# 	if e.paraula == "soleil":
# 		while True:
# 			num = random.randint(0, len(e.aparicions)-1)
# 			trobar_exemple(os.path.join(os.getcwd(), "videos"), e, num)




count = 0
llista_string_paraules = []
for p in llista_paraules[::-1]:

	if len(p.aparicions) < 10: # agafa totes les paraules amb 10 o mes aparicions
		break

	llista_string_paraules.append(p.paraula)
	count += 1
	

paraula_escollida = st.selectbox('Search or select a word (only the ones with more than 10 instances are available)', llista_string_paraules)

paraula = None

for p in llista_paraules:
	if p.paraula == paraula_escollida:
		paraula = p
		break


if paraula != None:
	st.write("There are " + str(len(paraula.aparicions)) + " instances of the word: " + paraula_escollida)

def trobar_nom_video(carpeta):
	arxius = os.listdir(os.path.join(os.getcwd(), "videos", carpeta))
	for a in arxius:
		if ".mp4" in a:
			return a

if st.button("Show random example"):
	num = random.randint(0, len(paraula.aparicions)-1)
	trobar_exemple(os.path.join(os.getcwd(), "videos"), paraula, num)
	nom_video = trobar_nom_video(paraula.aparicions[num].carpeta)
	st.write("Video name: " + nom_video)


	minuts_ini, segons_ini, minuts_fi, segons_fi = get_segons(paraula.aparicions[num].frames, os.path.join(os.getcwd(), "videos", paraula.aparicions[num].carpeta, nom_video))

	st.write(str(minuts_ini)+"m "+ str(int(segons_ini))+"s")



# veure quantes paraules es necessiten saber per entendre el 80% de totes les paraules que es diuen
# aux2 = 0
# llista_paraules.reverse()
# for i in range(len(llista_paraules)):
# 	aux2 += len(llista_paraules[i].aparicions)
# 	if aux2 > float(paraules_totals)*0.8:
# 		print("numero de paraules a saber per entendre el 80%:", i)
# 		print(len(llista_paraules[i].aparicions))
# 		break


# fer prova de la funcio play_video (de moment no esta feta)
# for f in os.listdir(os.path.join(PATH, "10")):
# 	if ".mp4" in f:
# 		play_video(os.path.join(PATH, "10", f), 100, 1)
# 		print("playing video")





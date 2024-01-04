import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
import time as t
import copy
from multiprocessing import Process
from paddleocr import PaddleOCR, draw_ocr

# aquest programa guarda una imatge per cada subtitol detectat en un video. Tambe es pot fer que llegeixi els subtitols ja generats i els guardi com a text en un fitxer .txt en el mateix directori


def subtitols_han_canviat(img1, img2): # retorna un numero que representa el canvi de img1 a img2. Canvis de subtitol normalment donen entre 1.1 i 1.6 i si no hi ha canvi dona menys de 0.005
    img_diferencia = get_diferencia(img1, img2)

    if type(img_diferencia) == bool:
        return False

    pixels_blanc_img1 = float(get_num_pixels_blancs(img1))
    

    if pixels_blanc_img1 != 0:
        return float(get_num_pixels_blancs(img_diferencia))/pixels_blanc_img1

    return 0

def get_diferencia(img1, img2): # retorna una imatge amb pixels blancs on hi ha hagut un canvi entre la imatge 1 i la imatge 2
    if img1.shape != img2.shape:
        return False

    img = np.zeros((img1.shape[0], img1.shape[1]))
    
    for y in range(len(img1)):
        for x in range(len(img1[y])):
            if img1[y][x] != img2[y][x]:
                img[y][x] = 255

    return img

def get_num_pixels_blancs(img): # retorna el num de pixels blancs en una imatge blanc i negre
    if len(img.shape) != 2:
        return False

    r = 0
    for y in range(len(img)):
        for x in range(len(img[y])):
            if img[y][x] == 255:
                r += 1

    return r


def processar_vid(path): # el path es la carpeta on esta el video, True ha sigut successful, False si hem parat el video
    fitxers = os.listdir(path)

    nom_arxiu_video = ""
    for i in fitxers: # per cada fitxer
        if i[len(i)-4:len(i)] == ".mp4":
            nom_arxiu_video = i
        else: # si no es .mp4
            os.remove(os.path.join(path, i))


    # read video
    
    video = cv2.VideoCapture(os.path.join(path, nom_arxiu_video))

    for i in range(0): # per avançar el video
        ret, img = video.read()

    ultims_subs_blanc_i_negre = 0
    ultims_subs = 0
    frame = 1
    frame_ultim_canvi = 0
    temps_ini = t.time()
    while True:
        ret, img = video.read()

        if ret == False: # Si es el ultim frame
            cv2.imwrite(os.path.join(path, str(frame_ultim_canvi)+"-"+str(frame)+".png"), ultims_subs)
            frame_ultim_canvi = frame
            print(path+" fet!", t.time()-temps_ini)
            #cv2.destroyAllWindows()
            return True

        img =  cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # converteixo imatge a blanc i negre (aixi computa mes rapid)

        img = cv2.resize(img, (1920, 1080))


        #img = cv2.rectangle(img, (0, 840), (1919, 925), (0,0,255), 3) # rectangle que marca els subtitols

        subs = img[840:925, 0: 1919]

        temps1 = t.time()

        shrink_factor = 4
        subs_blanc_i_negre = cv2.resize(subs, (int(subs.shape[1]/shrink_factor), int(subs.shape[0]/shrink_factor)))

        ret,subs_blanc_i_negre = cv2.threshold(subs_blanc_i_negre,200,255,cv2.THRESH_BINARY) # si un pixel esta per sobre de 200 passa a ser 255, si esta per sota passa a ser 0

        temps2 = t.time()

        if False:
            img = cv2.resize(img, (1280, 720))

            cv2.imshow(path, img)
            cv2.imshow("subtitols", subs_blanc_i_negre)
            key = cv2.waitKeyEx(1)
        
        temps3 = t.time()


        if type(ultims_subs_blanc_i_negre) == int: # Si es la primera iteracio
            ultims_subs_blanc_i_negre = copy.deepcopy(subs_blanc_i_negre)

        temps4 = t.time()


        canvi_subtitols = subtitols_han_canviat(ultims_subs_blanc_i_negre, subs_blanc_i_negre)
        if canvi_subtitols > 0.1 and frame-frame_ultim_canvi > 20: # si subtitols han canviat i ha passat suficient temps desde l'ultim canvi; guardem el subtitol i li posem com a nom els frames on apareixen
            cv2.imwrite(os.path.join(path, str(frame_ultim_canvi)+"-"+str(frame)+".png"), ultims_subs)
            frame_ultim_canvi = frame
        elif canvi_subtitols > 0.1:
            frame_ultim_canvi = frame


        ultims_subs_blanc_i_negre = copy.deepcopy(subs_blanc_i_negre)
        ultims_subs = subs

        frame += 1

        temps5 = t.time()

        if False:
            print(temps2-temps1)
            print(temps3-temps2)
            print(temps4-temps3)
            print(temps5-temps4)
            print()

        #if key != -1: # si es clica qualsevol tecla
        #    return False

def get_text(path, arxiu):

    subs = cv2.imread(os.path.join(path, arxiu))

    ret, subs = cv2.threshold(subs,200,255,cv2.THRESH_BINARY) # si un pixel esta per sobre de 230 passa a ser 255, si esta per sota passa a ser 0

    subs = (255-subs) # invertir la imatge perque les lletres siguin negres (nose si ajuda amb el ocr)

    if ret == False:
        return "PROBLEMA AMB LA IMATGE"

    reader = easyocr.Reader(['fr'], gpu=False, verbose=False)
    text_ = reader.readtext(subs)

    text_subtitols = ""

    if len(text_)>1:
        return "?"

    for info in text_:

        bbox, text, score = info

        for y in range(len(bbox)): # Passar info de la bbox de float a int
            for x in range(len(bbox[y])):
                bbox[y][x] = int(bbox[y][x])

        if score > 0.3: # si supera el threshold
            text_subtitols += text

    return text_subtitols


def get_text_paddleocr(path, arxiu, ocr):

    subs = cv2.imread(os.path.join(path, arxiu))

    ret, subs = cv2.threshold(subs,200,255,cv2.THRESH_BINARY) # si un pixel esta per sobre de 230 passa a ser 255, si esta per sota passa a ser 0

    subs = (255-subs) # invertir la imatge perque les lletres siguin negres (nose si ajuda amb el ocr)

    if ret == False:
        return "PROBLEMA AMB LA IMATGE"

    text_ = ocr.ocr(subs, cls=False)

    text_subtitols = ""


    if type(text_[0]) != list:
        return ""

    if len(text_[0]) > 1:
        return "?"


    for info in text_[0]:

        bbox, altres = info

        text, score = altres

        for y in range(len(bbox)): # Passar info de la bbox de float a int
            for x in range(len(bbox[y])):
                bbox[y][x] = int(bbox[y][x])

        if score > 0.3: # si supera el threshold
            text_subtitols += text

    return text_subtitols

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


def llegir_subtitols(path): # el path es la direccio a la carpeta on estan tots els subtitols

    temps1 = t.time()

    arxius = os.listdir(path)

    fitxer_text = open(os.path.join(path, "text_subtitols.txt"), "w")

    arxius.sort(key=funcio_ordenar_subtitols)

    ocr = PaddleOCR(use_angle_cls=False, lang="fr", show_log = False)
    for i in arxius: # si es un arxiu png
        if i[len(i)-4:len(i)] == ".png":
            nom_arxiu_video = i
            text_subtitols = get_text_paddleocr(path, nom_arxiu_video, ocr)
            fitxer_text.write(i[0:len(i)-3] + " # ")
            fitxer_text.write(str(text_subtitols)+"\n")

    fitxer_text.close()

    print(path+" -> fet", t.time()-temps1)



if __name__ == "__main__":
    #subtitols mal posats: 77 79

    print("SI ESTAS SEGUR D'EXECUTAR EL PROGRAMA EDITA LA LINIA INFERIOR A AQUESTA")
    exit()

    PATH = os.path.join(os.getcwd(), "videos")

    carpetes = os.listdir(PATH)
    carpetes.sort(key=funcio_ordenar_subtitols) # ordenar carpetes de num mes baix a num mes alt
    processes = []
    for i in carpetes:
        if not ("." in i): # si es una carpeta
            p = Process(target=llegir_subtitols, args=(os.path.join(PATH, i),))
            processes.append(p)


    num_procs = 9
    if num_procs > 9:
        print("realment no fa falta fer servir mes de 9, molts processos simultanis pujen les probabilitats de que el PC peti")
        exit()

    for i in range(0, len(processes), num_procs):

        for x in range(num_procs):
            if (i+x) < len(processes):
                processes[i+x].start()

        for x in range(num_procs):
            if (i+x) < len(processes):
                processes[i+x].join()
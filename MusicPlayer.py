import random
import time
import tkinter as tk
from tkinter import ttk
from tkinter import *
import tkinter
import pygame
pygame.init()
from tkinter import filedialog as fd
import mutagen
from mutagen.id3 import ID3
import io
import PIL.Image as Image
from PIL import ImageTk,Image
from functools import partial
from pypresence import Presence 
import os


class Queue:
    def __init__(self,text1,text2,text3,text4,text5) -> None:
        self.queueList = [text1,text2,text3,text4,text5]
        self.fileLocation = r'C:\Users\jm355\Music'
        self.topIndex = 0
        self.cursor = 2
    
    def initialise(self):
        for i in range(len(self.queueList)):
            self.queueList[i].pack(side = TOP, anchor = W, padx = 10, fill = X)
            self.queueList[i]['text'] = os.listdir(self.fileLocation)[i]
    
    def moveDown(self, event):
        if not (self.topIndex + 6 > len(os.listdir(self.fileLocation))):
            self.topIndex += 1
            for i in range(len(self.queueList)):
                self.queueList[i]['text'] = os.listdir(self.fileLocation)[self.topIndex + i]
    
    def moveUp(self, event):
        if self.topIndex > 0:
            self.topIndex -= 1
            for i in range(len(self.queueList)):
                self.queueList[i]['text'] = os.listdir(self.fileLocation)[self.topIndex + i]
    
    def moveLeft(self, event):
        self.fileLocation = self.fileLocation[0:self.fileLocation.rfind("\\")]
        self.topIndex = 0
        for i in range(len(self.queueList)):
            self.queueList[i]['text'] = os.listdir(self.fileLocation)[self.topIndex + i]
    
    def moveRight(self, event):
        if ("." not in self.queueList[self.cursor]['text']):
            self.fileLocation += f"\{self.queueList[self.cursor]['text']}"
            self.topIndex = 0
            for i in range(len(self.queueList)):
                self.queueList[i]['text'] = os.listdir(self.fileLocation)[self.topIndex + i]
        
        #elif [".mp3",".ogg",".wav"] in self.queueList[self.cursor]['text']:
        elif any(x in self.queueList[self.cursor]['text'] for x in [".mp3",".ogg",".wav"]):
           globalLoad(self.fileLocation + f"\{self.queueList[self.cursor]['text']}")

def globalLoad(filepath):
    #loading and playing the song
    pygame.mixer.music.load(filepath)
    pygame.mixer.music.play()

    #letting mutagen read the file
    file=mutagen.File(filepath)

    #looking to see if there is an APIC tag (album art)
    for localkeys in file.keys():
        if localkeys.startswith("APIC"):
            albumcover = file.tags[localkeys].data
            break
    
    albumArt = Image.open(io.BytesIO(albumcover))
    albumrArtResized= albumArt.resize((320,320),Image.ANTIALIAS)
    finalAlbumArt= ImageTk.PhotoImage(albumrArtResized)
    albumArtLabel.photo=finalAlbumArt
    albumArtLabel.config(image=finalAlbumArt)

def pause(event):
    print(pygame.mixer.music.get_busy())
    if pygame.mixer.music.get_busy() == 1:
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()

client_id = "1026996358785290290"
RPC = Presence(client_id)
RPC.connect()
RPC.update(state="Listening to WalkWoman",small_image="flippedmusicplayericon")

window = tk.Tk()
window.geometry("600x600")
window.title("Music Player")
window.resizable(False, False)
window["background"] = "#17221C"

icon = PhotoImage(file = "MusicPlayerIcon.png")
window.iconphoto(False, icon)

filetypes = (("mp3 files","*.mp3"),("wav files","*.wav"),("ogg files","*.ogg"))

albumArtFrame = Frame(window, bg = "#17221C", height = 345, width= 600)
fileLoader = Frame(window, bg = "#17221C", height = 150, width= 600)
songDetails = Frame(window, bg = "yellow", height = 60, width= 600)
bottomPadding = Frame(window, bg = "blue", height = 45, width= 600)

bottomPadding.pack(side = BOTTOM)
songDetails.pack(side = BOTTOM)
fileLoader.pack(side = BOTTOM)
albumArtFrame.pack(side = TOP)
##17221C
albumArtLabel = Label(albumArtFrame,anchor="w",bg = "#17221C")
albumArtLabel.place(x = 20, y = 30)

#width = 65
text1 = Label(fileLoader, bg = "#17221C",fg = "#7BA94F", padx= 5, anchor = "w", bd = 5, font=("Helvetica bold",13)) 
text2 = Label(fileLoader, bg = "#17221C",fg = "#7BA94F", padx= 5, anchor = "w", bd = 5, font=("Helvetica bold",13)) 
text3 = Label(fileLoader, bg = "#F7FFA4",fg = "#99A067", padx= 5, anchor = "w", bd = 5, font=("Helvetica bold",13)) 
text4 = Label(fileLoader, bg = "#17221C",fg = "#7BA94F", padx= 5, anchor = "w", bd = 5, font=("Helvetica bold",13))  
text5 = Label(fileLoader, bg = "#17221C",fg = "#7BA94F", padx= 5, anchor = "w", bd = 5, font=("Helvetica bold",13))  
queue = Queue(text1,text2,text3,text4,text5)
queue.initialise()

songData = Label(songDetails, width = 55, height = 1, bg = "#F7FFA4",fg = "#99A067", padx= 5, anchor = "w", bd = 5, font=("Helvetica bold",13)) 
songData.pack(side = BOTTOM) 

window.bind('<Down>', queue.moveDown)
window.bind('<Up>', queue.moveUp)
window.bind('<Left>', queue.moveLeft)
window.bind('<Right>', queue.moveRight)
window.bind('<space>', pause)




window.mainloop()
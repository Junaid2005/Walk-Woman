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
            #self.queueList[i].pack(side = LEFT, anchor = W, padx = 10, expand = TRUE, fill = X)
            self.queueList[i].grid(row = i, column = 0, sticky = W)
            self.queueList[i]['text'] = os.listdir(self.fileLocation)[i]
    
    def moveDown(self, event):
        if self.cursor < 2:
            self.queueList[self.cursor]['bg'], self.queueList[self.cursor]['fg']  = "#17221C", "#7BA94F"
            self.cursor += 1
            self.queueList[self.cursor]['bg'], self.queueList[self.cursor]['fg'] = "#F7FFA4", "#99A067"
        elif not (self.topIndex + 6 > len(os.listdir(self.fileLocation))):
            self.topIndex += 1
            for i in range(len(self.queueList)):
                self.queueList[i]['text'] = os.listdir(self.fileLocation)[self.topIndex + i]
        elif self.cursor <= 3:
            self.queueList[self.cursor]['bg'], self.queueList[self.cursor]['fg']  = "#17221C", "#7BA94F"
            self.cursor += 1
            self.queueList[self.cursor]['bg'], self.queueList[self.cursor]['fg'] = "#F7FFA4", "#99A067"
    
    def moveUp(self, event):
        if self.cursor > 2:
            self.queueList[self.cursor]['bg'], self.queueList[self.cursor]['fg']  = "#17221C", "#7BA94F"
            self.cursor -= 1
            self.queueList[self.cursor]['bg'], self.queueList[self.cursor]['fg'] = "#F7FFA4", "#99A067"
        elif self.topIndex > 0:
            self.topIndex -= 1
            for i in range(len(self.queueList)):
                self.queueList[i]['text'] = os.listdir(self.fileLocation)[self.topIndex + i]
        elif self.cursor >= 1:
            self.queueList[self.cursor]['bg'], self.queueList[self.cursor]['fg']  = "#17221C", "#7BA94F"
            self.cursor -= 1
            self.queueList[self.cursor]['bg'], self.queueList[self.cursor]['fg'] = "#F7FFA4", "#99A067"
    
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
    albumrArtResized= albumArt.resize((300,300),Image.ANTIALIAS)
    finalAlbumArt= ImageTk.PhotoImage(albumrArtResized)
    albumArtLabel.photo=finalAlbumArt
    albumArtLabel.config(image=finalAlbumArt)

    #gathering song data
    file=mutagen.File(filepath,easy = True)
    title = file['title'][0]
    artist = file['artist'][0]
    album = file['album'][0]
    albumpos =  file['tracknumber'][0]
    songlen = f"0:00"

    #updating song data label
    baseText = "INFO {\n"
    endBracket = "}"
    songMetaDataList = [baseText,f"       title: {title},\n",f"       artist: {artist},\n",f"       album: {album},\n",f"       #: {albumpos},\n",f"       length: {songlen} {endBracket}"]

    songMetaData.delete("1.0",END)
    for i in range(6):
        songMetaData.insert(END,songMetaDataList[i])
    songMetaData.config(spacing1=7)

def pause(event):
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

albumArtFrame = Frame(window, bg = "#17221C", height = 335, width= 600)
fileLoader = Frame(window, bg = "#17221C", height = 160, width= 580, highlightbackground="#F7FFA4", highlightthickness=2, relief= "groove")
songLengthDetails = Frame(window, bg = "#17221C", height = 60, width= 580,  highlightbackground="#F7FFA4", highlightthickness=2)
bottomPadding = Frame(window, bg = "#17221C", height = 30, width= 600)

bottomPadding.pack(side = BOTTOM)
songLengthDetails.pack(side = BOTTOM)
fileLoader.pack(side = BOTTOM)
fileLoader.grid_propagate(False)
albumArtFrame.pack(side = TOP)

albumArtLabel = Label(albumArtFrame,anchor="w",bg = "#17221C")
albumArtLabel.place(x = 25, y = 25)
#songMetaData = Label(albumArtFrame,anchor="w",bg = "#17221C",text = "INFO", fg = "#7BA94F", font=("Helvetica bold",13))
songMetaData = Text(albumArtFrame,bg = "#17221C", fg = "#7BA94F", font=("Helvetica bold",13))
songMetaData.place(x = 350, y = 25)     


#width = 65
text1 = Label(fileLoader, bg = "#17221C",fg = "#7BA94F", padx= 5, anchor = "w", bd = 5, font=("Helvetica bold",13), justify= "left") 
text2 = Label(fileLoader, bg = "#17221C",fg = "#7BA94F", padx= 5, anchor = "w", bd = 5, font=("Helvetica bold",13), justify= "left") 
text3 = Label(fileLoader, bg = "#F7FFA4",fg = "#99A067", padx= 5, anchor = "w", bd = 5, font=("Helvetica bold",13), justify= "left") 
text4 = Label(fileLoader, bg = "#17221C",fg = "#7BA94F", padx= 5, anchor = "w", bd = 5, font=("Helvetica bold",13), justify= "left")  
text5 = Label(fileLoader, bg = "#17221C",fg = "#7BA94F", padx= 5, anchor = "w", bd = 5, font=("Helvetica bold",13), justify= "left")  
queue = Queue(text1,text2,text3,text4,text5)
queue.initialise()

window.bind('<Down>', queue.moveDown)
window.bind('<Up>', queue.moveUp)
window.bind('<Left>', queue.moveLeft)
window.bind('<Right>', queue.moveRight)
window.bind('<space>', pause)




window.mainloop()
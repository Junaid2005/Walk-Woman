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

client_id = "1026996358785290290"
RPC = Presence(client_id)
RPC.connect()
RPC.update(state="Listening to WalkWoman",small_image="flippedmusicplayericon")

window = tk.Tk()
window.geometry("600x600")
window.title("Music Player")
window.resizable(False, False)
icon = PhotoImage(file = "MusicPlayerIcon.png")
window.iconphoto(False, icon)
filetypes = (("mp3 files","*.mp3"),("wav files","*.wav"),("ogg files","*.ogg"))
failnew = True
playlistnewimage = ""

def updatetextfile(playlistdict):
    with open("Playlists.txt","w") as file:
        file.write(str(playlistdict))

def secondsfunc(seconds):
    if len(str(seconds)) == 1:
        seconds= f"0{seconds}"
    return seconds

def globalload(filepath):
    pygame.mixer.music.load(filepath)
    pygame.mixer.music.play()
    global file
    global filelen
    global lyricsfound
    file = mutagen.File(filepath,easy=True)
    filelen = file.info.length
    currentsliderfunc()
    slider()
    Pausebutton.configure(image=Pauseimage)
    global rpcsecs
    rpcsecs = file.info.length
    seconds = secondsfunc(int(file.info.length%60))
    songlen = f"{int(file.info.length//60)}:{seconds}"
    Songlenlabel["text"] = songlen
    try:
        global listeningtext
        listeningtext = f"{file['title'][0]} · {file['artist'][0]}"
    except KeyError:
        listeningtext = filepath[filepath.rfind("/")+1:]
    ListeningLabel['text'] = listeningtext
    TimeSlider["state"]=NORMAL
    songname = file['title'][0]
    SongTitle['text'] = songname
    global albumname
    albumname = file['album'][0]

    try:
        RPC.update(state=albumname,details = listeningtext,start = int(time.time()),end = int(time.time())+rpcsecs,large_image="flippedmusicplayericon")
    except BrokenPipeError:
        pass
    #Lyrics['text'] = file["USLT::XXX"]
    #print(file["USLT::XXX"])

    file=mutagen.File(filepath)
    lyricsfound = False
    Lyrics.delete(0,Lyrics.size())
    for localkeys in file.keys():
        if localkeys.startswith("USLT") == True:
            splitstring = str(file[localkeys]).split("\n")
            for line in splitstring:
                Lyrics.insert(END,"  "+line)
            lyricsfound = True
            Lyrics.insert(0,"\n")
            Lyrics.insert(Lyrics.size(),"\n")
            break
    if lyricsfound == False:
        Lyrics.insert(0,"\n")
        Lyrics.insert(END,"  No lyrics available :(")
        
    #print("KEYCHECK FIRST: ", file.keys())
    #print("FILE: ",file)
    #print("\n,\n,\n")
    #print("KEYCHECK SECOND ", file.keys())
    #Lyrics['text'] = file["USLT::XXX"]

    imagefound = False
    for localkeys in file.keys():
        if localkeys.startswith("APIC") == True:
            imagefound = True
            albumcover = file.tags[localkeys].data
            break
    
    if imagefound == True:
        albumimg = Image.open(io.BytesIO(albumcover))
        albumresized_image= albumimg.resize((400,400),Image.ANTIALIAS)
        finalalbum= ImageTk.PhotoImage(albumresized_image)
        Albumlabel.photo=finalalbum
        Albumlabel.config(image=finalalbum)
        lyricimage = albumimg.resize((80,80),Image.ANTIALIAS)
        finallyric= ImageTk.PhotoImage(lyricimage)
        LyricsCover.photo=finallyric
        LyricsCover.config(image=finallyric)
    else:
        Albumlabel.config(image=finalblank)
        LyricsCover.config(image=finallyricblank)
    #try:
    #    albumcover=file.tags["APIC:"].data
    #except (KeyError,TypeError):
    #    albumcover = None
    #if albumcover != None:
    #    albumimg = Image.open(io.BytesIO(albumcover))
    #    albumresized_image= albumimg.resize((400,400),Image.ANTIALIAS)
    #    finalalbum= ImageTk.PhotoImage(albumresized_image)
    #    Albumlabel.photo=finalalbum
    #    Albumlabel.config(image=finalalbum)
    #else:
    #    Albumlabel.config(image=finalblank)
    ListeningLabel.config(font=("Consolas",12))


def load():
    filetypes = (("mp3 files","*.mp3"),("wav files","*.wav"),("ogg files","*.ogg"))
    filepath = fd.askopenfilename(filetypes=filetypes)
    if filepath != "":
        globalload(filepath)
        
def currentsliderfunc():
    currenttime = pygame.mixer.music.get_pos()
    seconds = secondsfunc(int(currenttime/1000%60))
    currenttimetext=f"{int(currenttime/1000//60)}:{seconds}"
    if currenttimetext == "-1:59":
        Songposlabel['text'] = Songlenlabel["text"]
    else:
        Songposlabel['text'] = currenttimetext
    Songposlabel.after(950,currentsliderfunc)

def slider():
    sliderpos = ((pygame.mixer.music.get_pos()/1000)/filelen)*100
    TimeSlider.set(sliderpos)
    TimeSlider.after(2000,slider)

def move():
    currentsliderpos = TimeSlider.get()
    newpos = (currentsliderpos/100)*filelen
    pygame.mixer.music.set_pos(int(newpos))
    TimeSlider.after(10,move)

def pauseplaybutton():
    if Pausebutton['image'] == "pyimage5":
        print("here")
        Pausebutton.configure(image=Pauseimage)
        TimeSlider["state"]=NORMAL
        pygame.mixer.music.unpause()
        currentsliderfunc()
        endnum = rpcsecs-(pygame.mixer.music.get_pos()/1000)
        RPC.update(state=albumname,details = listeningtext,start = int(time.time()),end = int(time.time())+endnum,large_image="flippedmusicplayericon")
        try:
            slider()
        except NameError:
            pass
    else:
        Pausebutton.configure(image=Resumeimage)
        pygame.mixer.music.pause()
        RPC.update(state=albumname,details = listeningtext,large_image="flippedmusicplayericon")

def back():
    try:
        pygame.mixer.music.play()
        if Pausebutton['image'] == "pyimage5":
            pygame.mixer.music.pause()
    except pygame.error:
        pass

def skip():
    if len(queue) != 0:
        globalload(queue[0])
        print("New song called: ",queue[0])
        queue.pop(0)

def shuffle():
    if Shufflebutton["relief"] == "flat":
        random.shuffle(queue)
        Shufflebutton["relief"] = "sunken"
        Shufflebutton["bd"] = 1
    else:
        Shufflebutton["bd"] = 0
        Shufflebutton["relief"] = "flat"

    #if shufflecheck == False:
    #    random.shuffle(queue)
    #    shufflecheck = True
    #else:
    #   shufflecheck = False
   # 
   # return shufflecheck

def playlistplace():
    global currentmenu
    currentmenu = "playlistplace"
    PlaylistmenuFrame.place(x=0,y=25)
    ListeningFrame.place_forget()
    InsidePlaylistWhole.place_forget()
    LyricMenu.place_forget()
    TagMenu.place_forget()
    
def main():
    global currentmenu
    currentmenu = "home"
    ListeningFrame.place(x=0,y=0)
    LyricMenu.place_forget()
    PlaylistmenuFrame.place_forget()
    InsidePlaylistWhole.place_forget()
    TagMenu.place_forget()

def lyricsmenu():
    global currentmenu
    currentmenu = "lyrics"
    LyricMenu.place(x=0,y=25)
    ListeningFrame.place_forget()
    PlaylistmenuFrame.place_forget()
    InsidePlaylistWhole.place_forget()
    TagMenu.place_forget()
    #print(file.keys())
    #print(file["USLT::XXX"])
    #print(file["USLT::XXX"])

def SearchMenuPlace():
    SearchingMenu.place(x=0,y=125)
    CreatingMenu.place_forget()

def TagMenuPlace():
    CreatingMenu.place(x=0,y=125)
    SearchingMenu.place_forget()

def tagmenu():
    TagMenu.place(x=0,y=25 )
    ListeningFrame.place_forget()
    LyricMenu.place_forget()
    PlaylistmenuFrame.place_forget()
    InsidePlaylistWhole.place_forget()

def newtagcheck():
    newtagname = CreateEntryBox.get()
    passtest = True
    if (len(newtagname) == 0) or (newtagname.count(" ") == len(newtagname)):
        tkinter.messagebox.showerror(title="Music Player", message="This tag name is not allowed :/ Please try another")
        passtest = False
    for tagnames in tags.keys():
        if newtagname == tagnames:
            tkinter.messagebox.showerror(title="Music Player", message="This tag already exists")
            passtest = False
    
    if passtest == True:
        filepaths = fd.askopenfilenames()
        compatiblefilepaths = []
        notcompatible = False
        for file in filepaths:
            if (file[file.rfind("."):]) not in [".mp3",".wav",".ogg"]:
                notcompatible = True
            else:
                compatiblefilepaths.append(file)

        if len(compatiblefilepaths) == 0:
            tkinter.messagebox.showerror(title="Music Player", message="None of the files were compatible")
        elif notcompatible == True:
            tkinter.messagebox.showerror(title="Music Player", message="At least one of the file types selected was not supported")
        
        if len(compatiblefilepaths) != 0:
            tags[newtagname] = compatiblefilepaths
            with open("Tags.txt","w") as file:
                file.write(str(tags))
            tkinter.messagebox.showinfo(title="Music Player", message="Tag successfully created")

def searchtag():
    query = SearchEntryBox.get()
    result = []
    sourcetag = []
    for tagnames in tags.keys():
        if query in str(tagnames):
            for i in range(len(tags[tagnames])):
                sourcetag.append(str(tagnames))
                result.append(tags[tagnames][i])

    print(sourcetag,result)
    
    for widget in songsearchmenu.winfo_children():
        widget.destroy()
    
    for i in range(len(result)):
        weaksong = mutagen.File(result[i],easy=True)
        try:
            songname = " " + weaksong['title'][0]
            if len(songname) > 32 :
                songname = songname[0:28] + "..."
            secondstext = secondsfunc(int(weaksong.info.length%60))
            songlentext = f"{int(weaksong.info.length//60)}:{secondstext}"
            songartist = weaksong['artist'][0]
            if len(songartist) > 24:
                songartist = songartist[0:18] + "..."
            songbuttontext = songname + " "*(32-len(songname)) +  songartist + " "*(24-len(songartist))  + songlentext + "  " + sourcetag[i]
            
        except KeyError:    
            print("here")
            songbuttontext = result[i]
        SongInPlaylist = Button(songsearchmenu,anchor="w",bg="white",relief = "ridge",command=partial(playinginplaylist,result[i],result,i))
        SongInPlaylist.grid(row=i,column=1,padx=5,pady=3)

        findingalbum=mutagen.File(result[i])

        imagefound = False
        for localkeys in findingalbum.keys():
            if localkeys.startswith("APIC") == True:
                imagefound = True
                playlistalbumcover = findingalbum.tags[localkeys].data
                break
        
        if imagefound == True:
            buttonalbum = Image.open(io.BytesIO(playlistalbumcover))
            fixedbuttonalbum= buttonalbum.resize((40,40),Image.ANTIALIAS)
            finalbuttonalbum= ImageTk.PhotoImage(fixedbuttonalbum)
            SongInPlaylist.photo=finalbuttonalbum
            SongInPlaylist.config(image=finalbuttonalbum,width=550,height=40,text=songbuttontext,compound=LEFT,font=("Consolas",10))
        else:
            SongInPlaylist.photo=finalsmallblank
            SongInPlaylist.config(image=finalsmallblank,width=550,height=40,text=songbuttontext,compound=LEFT,font=("Consolas",10))
    

def viewplaylist(playlistname):
    for widget in Bottom.winfo_children():
        widget.destroy()
    global songs
    global playlistnameforfunc
    playlistnameforfunc = playlistname
    songs = playlistdict[playlistname]["songs"]
    image = playlistdict[playlistname]["image"]

    newname = playlistnameforfunc
    PlaylistTitle.place_forget()
    if len(newname) > 22:
        splitname = newname[:22]
        lastspace = splitname.rfind(" ")
        newname = newname[:lastspace] + "\n" + newname[lastspace+1:]
        PlaylistTitle.place(x=100,y=1.9)
    else:
        PlaylistTitle.place(x=100,y=23.5)
    PlaylistTitle.configure(text = newname)

    if image != "":
        playlistlogo = Image.open(image)
        resizedimage= playlistlogo.resize((85,85),Image.ANTIALIAS)
        finalimage= ImageTk.PhotoImage(resizedimage)
        InsidePlaylistCover.photo=finalimage
        InsidePlaylistCover.config(image=finalimage)
    else:
        InsidePlaylistCover.config(image=finalnocover)

    for i in range(len(songs)):
        weaksong = mutagen.File(songs[i],easy=True)
        try:
            songname = " " + weaksong['title'][0]
            if len(songname) > 35 :
                songname = songname[0:31] + "..."
            secondstext = secondsfunc(int(weaksong.info.length%60))
            songlentext = f"{int(weaksong.info.length//60)}:{secondstext}"
            songartist = weaksong['artist'][0]
            if len(songartist) > 27:
                songartist = songartist[0:21] + "..."
            songbuttontext = songname + " "*(35-len(songname)) +  songartist + " "*(27-len(songartist))  + songlentext
            
        except KeyError:    
            print("here")
            songbuttontext = songs[i]
        Numberlabel=Label(Bottom,text=i+1,bg="white",font=("Consolas",10))
        Numberlabel.grid(row=i,column=0)
        SongInPlaylist = Button(Bottom,anchor="w",bg="white",relief = "ridge",command=partial(playinginplaylist,songs[i],songs,i))
        SongInPlaylist.grid(row=i,column=1,padx=5,pady=3)

        findingalbum=mutagen.File(songs[i])

        imagefound = False
        for localkeys in findingalbum.keys():
            if localkeys.startswith("APIC") == True:
                imagefound = True
                playlistalbumcover = findingalbum.tags[localkeys].data
                break
        
        if imagefound == True:
            buttonalbum = Image.open(io.BytesIO(playlistalbumcover))
            fixedbuttonalbum= buttonalbum.resize((40,40),Image.ANTIALIAS)
            finalbuttonalbum= ImageTk.PhotoImage(fixedbuttonalbum)
            SongInPlaylist.photo=finalbuttonalbum
            SongInPlaylist.config(image=finalbuttonalbum,width=550,height=40,text=songbuttontext,compound=LEFT,font=("Consolas",10))
        else:
            SongInPlaylist.photo=finalsmallblank
            SongInPlaylist.config(image=finalsmallblank,width=550,height=40,text=songbuttontext,compound=LEFT,font=("Consolas",10))

    InsidePlaylistWhole.place(x=0,y=25)
    PlaylistmenuFrame.place_forget()

def playinginplaylist(fileinplaylist,songlist,startpos):
    global queue
    queue = []
    for song in range(startpos+1,len(songlist)):
        queue.append(songlist[song])
        
    if Shufflebutton["relief"] == "sunken" and startpos == 0:
        random.shuffle(queue)
        globalload(queue[0])
    else:
        globalload(fileinplaylist)

def placingplaylist(playlistname,playlistimage):
    global count
    Playlist = Button(PlaylistFrame,text=playlistname,width=40,height=5,anchor="w",command=partial(viewplaylist,playlistname))
    
    if playlistimage == "":
        Playlist.photo=nocover
        Playlist.config(image=nocover,width=281,height=77,text=" "+playlistname,compound=LEFT)
    else:
        opencover = Image.open(playlistimage)
        resizedcover= opencover.resize((75,75),Image.ANTIALIAS)
        finalcover= ImageTk.PhotoImage(resizedcover)
        Playlist.photo=finalcover
        Playlist.config(image=finalcover,width=281,height=77,text=" "+playlistname,compound=LEFT)
        
    if count % 2 == 1:
        Playlist.grid(row=int(count/2),column=1,padx=5,pady=5)
    else:
        Playlist.grid(padx=5,pady=5)
    count += 1

def getimage():
    global playlistnewimage
    playlistnewimage = fd.askopenfilename(filetypes=[("png files","*.png")])
    playlistwindow.lift()

def getchecknewname(inputwidget,edit):
    global failnew
    global inputtedname
    global count
    failnew = False
    inputtedname = inputwidget.get()
    if inputtedname.count(" ") ==  len(inputtedname):
        tkinter.messagebox.showerror(title="Music Player", message="Playlist name can't be blank")
        failnew = True
    elif len(inputtedname) > 30:
        tkinter.messagebox.showerror(title="Music Player", message="Please choose a shorter name")
        failnew = True
    elif failnew == False:
        for playlistnames in playlistdict.keys():
            if playlistnames == inputtedname:
                tkinter.messagebox.showerror(title="Music Player", message="This playlist name has already been taken")
                failnew = True
                break
    
    if failnew == False and edit:
        playlistdict[inputtedname] = playlistdict[playlistnameforfunc]
        playlistdict[inputtedname]["image"] = playlistnewimage
        playlistdict.pop(playlistnameforfunc)
        updatetextfile(playlistdict)
        tkinter.messagebox.showinfo(title="Music Player", message="Playlist details updated successfully")
        playlistwindow.destroy()
        count = 0
        for widget in PlaylistFrame.winfo_children():
            widget.destroy()
        for value in playlistdict.items():
            placingplaylist(value[0],value[1]["image"])


    elif failnew == False and edit == False:
        #print("image url = " + playlistnewimage + " playlist name: " + inputtedname)
        filepaths = fd.askopenfilenames()
        compatiblefilepaths = []
        notcompatible = False
        for file in filepaths:
            if (file[file.rfind("."):]) not in [".mp3",".wav",".ogg"]:
                notcompatible = True
            else:
                compatiblefilepaths.append(file)

        if notcompatible == True:
            tkinter.messagebox.showerror(title="Music Player", message="At least one of the file types selected was not supported")

        playlistdict[inputtedname] = {}
        playlistdict[inputtedname]["songs"] = compatiblefilepaths
        playlistdict[inputtedname]["image"] = playlistnewimage
        with open("Playlists.txt","w") as file:
            file.write(str(playlistdict))

        placingplaylist(inputtedname,playlistnewimage)
        playlistwindow.destroy()

def playlistmenu(edit,source):
    global playlistwindow
    global playlistphoto
    global playlistnewimage
    try:
        playlistwindow.destroy()
    except (NameError,tkinter.TclError):
        pass
    if edit:
        playlistnewimage = source
    else:   
        playlistnewimage = ""
    playlistwindow = tk.Tk()
    playlistwindow.geometry("350x150")
    playlistwindow.title("Music Player")
    playlistwindow.resizable(False, False)

    playlistphoto = tk.Button(playlistwindow,text="📁",width=17,height=8,command = getimage)
    playlistphoto.place(x=10,y=10)
    askplaylistname = tk.Label(playlistwindow,text="Enter playlist name :")
    askplaylistname.place(x=142,y=15)
    
def addbutton():
    playlistmenu(False,"")
    enterplaylistname = tk.Entry(playlistwindow,width = 32,text="")
    enterplaylistname.place(x=144.5, y=40)
    getplaylistname = tk.Button(playlistwindow,width = 10,text = "Submit",command = partial(getchecknewname,enterplaylistname,False))
    getplaylistname.place(x=205,y=115)

def addsongs():
    addfilepaths,Fail,playlistposcounter = fd.askopenfilenames(),False,0
    for filepath in addfilepaths:
        if (filepath[filepath.rfind("."):]) in [".mp3",".ogg",".wav"]:
            playlistposcounter += 1
            playlistsongs = playlistdict[playlistnameforfunc]["songs"]
            playlistsongs.append(filepath)

            weakmetadatasong = mutagen.File(filepath,easy=True)
            #weaksong = mutagen.File(songs[i],easy=True)
            try:
                songname = " " + weakmetadatasong['title'][0]
                if len(songname) > 35 :
                    songname = songname[0:31] + "..."
                secondstext = secondsfunc(int(weakmetadatasong.info.length%60))
                songlentext = f"{int(weakmetadatasong.info.length//60)}:{secondstext}"
                songartist = weakmetadatasong['artist'][0]
                if len(songartist) > 27:
                    songartist = songartist[0:21] + "..."
                songbuttontext = songname + " "*(35-len(songname)) +  songartist + " "*(27-len(songartist))  + songlentext

            except KeyError:    
                songbuttontext = filepath
            #songtextadded=f" {weakmetadatasong['title'][0]} · {weakmetadatasong['artist'][0]}"

            SongInPlaylist = Button(Bottom,anchor="w",bg="white",relief = "ridge",command=partial(playinginplaylist,filepath,songs,playlistposcounter))
            SongInPlaylist.grid(column=1,padx=5,pady=3)

            findingalbum=mutagen.File(filepath)
            try:
                playlistalbumcover=findingalbum.tags["APIC:"].data
            except (KeyError,TypeError):
                playlistalbumcover = None
            
            if playlistalbumcover != None:
                buttonalbum = Image.open(io.BytesIO(playlistalbumcover))
                fixedbuttonalbum= buttonalbum.resize((40,40),Image.ANTIALIAS)
                finalbuttonalbum= ImageTk.PhotoImage(fixedbuttonalbum)
                SongInPlaylist.photo=finalbuttonalbum
                SongInPlaylist.config(image=finalbuttonalbum,width=550,height=40,text=songbuttontext,compound=LEFT,font=("Consolas",10))
            else:
                SongInPlaylist.photo=finalsmallblank
                SongInPlaylist.config(image=finalsmallblank,width=550,height=40,text=songbuttontext,compound=LEFT,font=("Consolas",10))
        else:
            Fail = True
    playlistdict[playlistnameforfunc]["songs"] = playlistsongs
    with open("Playlists.txt","w") as file:
            file.write(str(playlistdict))
    if Fail == True:
        tkinter.messagebox.showerror(title="Music Player", message="At least one of the file types selected was not supported")

def deleteplaylist():
    choice = tkinter.messagebox.askyesno(title="Music Player", message="Are you sure you want to delete this playlist?")
    if choice:
        global count
        playlistdict.pop(playlistnameforfunc)
        playlistwindow.destroy()
        updatetextfile(playlistdict)
        count = 0
        for widget in PlaylistFrame.winfo_children():
            widget.destroy()
        for value in playlistdict.items():
            placingplaylist(value[0],value[1]["image"])
        playlistplace()

def editplaylist():
    playlistmenu(True,playlistdict[playlistnameforfunc]["image"])
    newplaylistname = tk.Entry(playlistwindow,width = 32,text="wip")
    newplaylistname.place(x=144.5, y=40)
    getplaylistname = tk.Button(playlistwindow,width = 10,text = "Submit",command = partial(getchecknewname,newplaylistname,True))
    getplaylistname.place(x=157.9,y=115)
    deletebutton = tk.Button(playlistwindow,width = 10,text = "Delete",command = partial(deleteplaylist,))
    deletebutton.place(x=256.57,y=115)

def playplaylist():
    playinginplaylist(songs[0],songs,0)
    #if Shufflebutton["relief"] == "raised":
    #    random.shuffle(queue)

queue = []
shufflecheck = False

def check_event():
    for event in pygame.event.get():
        if event.type == MUSIC_END:
            try:
                globalload(queue[0])
                print("New song called: ",queue[0])
                queue.pop(0)
            except IndexError:
                pass
    window.after(100,check_event) 

MUSIC_END = pygame.USEREVENT+1
pygame.mixer.music.set_endevent(MUSIC_END)

check_event()

playlistdict = {}
with open("Playlists.txt","r") as file:
    for line in file:
        playlistdict = eval(line)

tags = {}
with open("Tags.txt","r") as tagfile:
    for tagline in tagfile:
        tags = eval(tagline)

#for values in playlistdict.items():
    #print(values)
    ##print(values[0])
    ##print(values[1]["image"])

blankimage = Image.open("MusicPlayerIcon.png")
resizedblank= blankimage.resize((400,400),Image.ANTIALIAS)
finalblank= ImageTk.PhotoImage(resizedblank)
smallblankresized= blankimage.resize((40,40),Image.ANTIALIAS)
finalsmallblank = ImageTk.PhotoImage(smallblankresized)
lyricblank = blankimage.resize((80,80),Image.ANTIALIAS)
finallyricblank = ImageTk.PhotoImage(lyricblank)
Resumeimage = PhotoImage(file='play.png')
Pauseimage = PhotoImage(file='pause.png')
Previousimage = PhotoImage(file="rear.png")
Nextimage = PhotoImage(file="forward.png")
AddImage = PhotoImage(file="add.png")
EditImage = PhotoImage(file="editing.png")
ShuffleImage = PhotoImage(file="shuffle.png")
QueueImage = PhotoImage(file="queue.png")
finalnocover = blankimage.resize((75,75),Image.ANTIALIAS)
nocover = ImageTk.PhotoImage(finalnocover)
resizednocover= blankimage.resize((85,85),Image.ANTIALIAS)
finalnocover= ImageTk.PhotoImage(resizednocover)

ListeningFrame = Frame(window,height = 600,width = 600,highlightbackground="white")
ListeningFrame.place(x=0,y=0)

AlbumFrame = Frame(ListeningFrame,height=450,width=600,bg="white",highlightbackground="white")
AlbumFrame.place(x=0,y=0)
Albumlabel = Label(AlbumFrame,bg="white",highlightbackground="white")
Albumlabel.config(image=finalblank)
Albumlabel.place(x=100,y=35)

ButtonFrame = Frame(ListeningFrame,height=150,width=600,bg="white",highlightbackground="white")
ButtonFrame.place(x=0,y=450)

Pausebutton = Button(ButtonFrame,height=37,width=37,image=Resumeimage,borderwidth = 0,bg="white",activebackground="white",command=pauseplaybutton)
Pausebutton.place(x=280.8,y=55.4)

Previousbutton = Button(ButtonFrame,height=37,width=37,image=Previousimage,borderwidth = 0,bg="white",activebackground="white",command=back)
Previousbutton.place(x=240,y=55.4)
Nextbutton = Button(ButtonFrame,height=37,width=37,image=Nextimage,borderwidth = 0,bg="white",activebackground="white",command = skip)
Nextbutton.place(x=321.6,y=55.4)

Shufflebutton = Button(ButtonFrame,height=37,width=37,image=ShuffleImage,borderwidth = 0,bg="white",activebackground="white",relief="flat",command = shuffle)
Shufflebutton.place(x=199.2,y=55.4)
Queuebutton = Button(ButtonFrame,height=37,width=37,image=QueueImage,borderwidth = 0,bg="white",activebackground="white",command = skip)
Queuebutton.place(x=362.4,y=55.4)

ListeningLabel = Label(ButtonFrame,text="Junaid's Music Player",bg="white",font=("Fredoka One",14))
ListeningLabel.place(x=300,y=22,anchor=CENTER)
#ListeningLabel.place(x=300,y=7,anchor=CENTER)

TimeSlider = ttk.Scale(ButtonFrame,orient=HORIZONTAL,from_=0,to=101,length=400,state=DISABLED)
sliderstyle = ttk.Style(TimeSlider)
sliderstyle.configure("TScale",troughcolor="white",background="white")
TimeSlider.place(x=300,y=110,anchor=CENTER) 
Songlenlabel=Label(ButtonFrame,text="0:00",bg="white")
Songlenlabel.place(x=507,y=110,anchor=W)
Songposlabel=Label(ButtonFrame,text="0:00",bg="white")
Songposlabel.place(x=93,y=110,anchor=E)

#FileSelector = Button(ButtonFrame,height=2,width=10,text="Choose a file",command=load)
#FileSelector.place(x=20,y=0)

MenuFrame = Frame(window,height=25,width=600,bd="2")
MenuFrame.place(x=0,y=0)
PlaylistPortal = Button(MenuFrame,height=1,width=15,text="Playlists",command=playlistplace,anchor="w")
PlaylistPortal.place(x=113,y=-2)
retrievebutton = Button(MenuFrame,height=1,width=15,text="Home",command=main,anchor="w")
retrievebutton.place(x=-2,y=-2)
LyricsPortal = Button(MenuFrame,height=1,width=15,text="Lyrics",command=lyricsmenu,anchor="w")
LyricsPortal.place(x=228,y=-2)
TagPortal = Button(MenuFrame,height=1,width=15,text="Tagging",command=tagmenu,anchor="w")
TagPortal.place(x=343,y=-2)

LyricMenu = Frame(window,height = 575,width = 600,highlightbackground="white",bg="white")
SongTitle =  Label(LyricMenu,text="No song selected",bg="white",font=("Fredoka One",24))
SongTitle.place(x=100,y=50,anchor = W)
Lyrics = Listbox(LyricMenu,height=28,width=75,font=("Fredoka One",10),cursor="plus")
Lyrics.place(x=-1,y=100)
LyricsCover = Label(LyricMenu,bg="white",highlightbackground="white")
LyricsCover.config(image=finallyricblank)
LyricsCover.place(x=7.5,y=7.5)
#LyricsScrollbar = Scrollbar(LyricMenu,orient='vertical',bg="blue",command=Lyrics.yview)
#LyricsScrollbar.place(x=580,y=100)
#Lyrics.config(yscrollcommand = LyricsScrollbar.set)
#LyricsScrollbar.config(command = Lyrics.yview)
#Lyrics['yscrollcommand'] = LyricsScrollbar.set

PlaylistmenuFrame = Frame(window,height = 575,width = 600,highlightbackground="white",bg="white")

PlaylistMenuTitle = Label(PlaylistmenuFrame,text="Playlists",bg="white",font=("Fredoka One",30),anchor="w")
PlaylistMenuTitle.place(x=0,y=30.6)

PlaylistFrame = Frame(PlaylistmenuFrame, width=600, height=400,bg="white")
PlaylistFrame.place(x=0,y=175)
Scroller = Scrollbar(PlaylistmenuFrame,orient="vertical")
count = 0 
for value in playlistdict.items():
    placingplaylist(value[0],value[1]["image"])


AddPlaylist = Button(PlaylistmenuFrame,text="Add Playlist",height=2,width=10,command=addbutton)
AddPlaylist.place(x=5,y=130)

InsidePlaylistWhole = Frame(window,height = 575,width = 600,highlightbackground="white",bg="white")
TopHalf = Frame(InsidePlaylistWhole,height=100,width=600,highlightbackground="white",bg="white")
TopHalf.place(x=0,y=0)
InsidePlaylistCover = Label(TopHalf,bg="white",highlightbackground="white")
InsidePlaylistCover.config(image=finalnocover)
InsidePlaylistCover.place(x=7.5,y=7.5)
PlaylistButtons = Frame(InsidePlaylistWhole,height=40,width=600,highlightbackground="white",bg="white")
PlaylistButtons.place(x=0,y=100)
Bottom=Frame(InsidePlaylistWhole,height=425,width=600,highlightbackground="white",bg="white")
Bottom.place(x=0,y=140)

PlayPlaylistButton = Button(PlaylistButtons,height=37,width=37,image=Resumeimage,borderwidth = 0,bg="white",activebackground="white",command=playplaylist)
PlayPlaylistButton.place(x=0,y=1)
AddSongs = Button(PlaylistButtons,height=37,width=37,image=AddImage,borderwidth = 0,bg="white",activebackground="white",command = addsongs)
AddSongs.place(x=40,y=1)
EditPlaylistButton = Button(PlaylistButtons,height=37,width=37,image=EditImage,borderwidth = 0,bg="white",activebackground="white",command = editplaylist)
EditPlaylistButton.place(x=80,y=1)

PlaylistTitle = Label(TopHalf,text="",anchor="w",bg="white",font=("Consolas",30),width=22,justify=LEFT)
PlaylistTitle.place(x=100,y=23.5)

TagMenu = Frame(window,height = 575,width = 600,highlightbackground="white",bg="white")

SearchTag = Button(TagMenu,text="Search by tag /",font=("Fredoka One",32,"underline"),bg="white",relief=FLAT,command = SearchMenuPlace)
SearchTag.place(x=-5,y=25)
CreateTag = Button(TagMenu,text="Create tag",font=("Fredoka One",32),bg="white",relief=FLAT,command = TagMenuPlace)
CreateTag.place(x=335,y=25)

SearchingMenu = Frame(TagMenu,height = 475,width = 600,highlightbackground="white",bg="white")
SearchingMenu.place(x=0,y=125)
SearchEntryBox = Entry(SearchingMenu,width=36,bd=4,font=("Fredoka One",16))
SearchEntryBox.place(x=10,y=5)
SearchTag = Button(SearchingMenu,text="Search",font=("Fredoka One",12), padx = 10,command = searchtag)
SearchTag.place(x=500,y=3)
songsearchmenu = Frame(SearchingMenu,width=600,height=400,bg="white")
songsearchmenu.place(x=0,y=50)

CreatingMenu = Frame(TagMenu,height = 475,width = 600,highlightbackground="white",bg="white")
CreateEntryBox = Entry(CreatingMenu,width = 36,bd=4,font=("Fredoka One",16))
CreateEntryBox.place(x=10,y=5)
SubmitTag = Button(CreatingMenu,text="Create",font=("Fredoka One",12), padx = 10,command = newtagcheck)
SubmitTag.place(x=500,y=3)
window.mainloop()
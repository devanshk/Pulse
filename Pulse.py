######################################################
#        Devansh Kukreja Term Project - Pulse        #
######################################################

import random
import math
from tkinter import *
import pyaudio
import wave
import time
import numpy as np
import os
import soundcloud
import subprocess
import wave
import urllib
import string
from beatDetection import SimpleBeatDetection
from grapher import Graph
from grapher import BeatGrapher
from HelperWidgets import Dot
from HelperWidgets import Button

CHUNK = 2048 # The size of the chunk to read from the mic stream
FORMAT = pyaudio.paInt16 # The format depends on the mic used
CHANNELS = 2 # The number of channels used to record the audio. Depends on the mic
RATE = 44100 # The sample rate for audio. Depends on the mic
THRESHOLD = 6000 # The threshold intensity that defines silence. 
                 # an int lower than THRESHOLD is considered silence 
RECORD_SECONDS=10


fourierInterval = 5
songTimeScale = 0.7
decay = 0.9945
game = True
audioLocation = "/Users/dkukreja/Desktop/TP_AudioFiles"


beatDetect = SimpleBeatDetection()
wf = None
data = None
handleDots = True

def proont(*args):
    debug = False
    if (debug):
        print(*args)

def init(data): #Initialize all of data's variables
    global dati
    dati = data

    data.checkRadius = 400
    data.targetRadii = []
    data.leftScore = 0
    data.rightScore = 0
    data.leftDistance = 99999
    data.rightDistance = 99999
    data.lastBeatTimer = 0
    data.beatTimer = 0
    data.circWidth = 3
    data.circColor = "black"

    data.songPath = ""
    data.dots = []
    data.buttons = []
    data.instant_energies = []
    data.energy_averages = []
    data.maxEnergy = 0
    data.beats = []
    data.fourier = []
    data.fourier_colors=["#FFC5C5", "#FFDFDF"]
    data.colorschemas = [
    ["#BE1B38", "#01A98F", "#C9CF7E", "#E86644"],
    ["#354458", "#EB7260", "#29ABA4","#E9E0D6", "#3A9AD9"],
    ["#FF0066", "#333366", "#3399CC", "#00CCCC", "#003399"],
    ["#a6dace", "#F7A04B", "#666699", "#EF8D24"],
    ["#05b3b2", "#2ca5dc", "#a5d3ea", "#f4cfbd", "#ff946c"]
    ]
    data.colors = data.colorschemas[0]
    data.targets = []
    data.time = 0
    data.last = 0
    data.radius = 10
    data.posx = data.width//3
    data.posy = data.height//2
    pickNewTarget(data)
    data.timescale = 1.0
    data.backgroundBase = "#FEFEFE"
    data.font = "Calibri"
    data.gamestate = 0
    data.gamemode = "song"
    data.offset = 0
    data.score = 0
    data.graphers = []
    data.lastBeat = int(round(time.time() * 1000))
    data.lastCallBack = time.time()
    data.backgroundColor = data.backgroundBase
    data.canvas = None
    data.playerPhased = False
    data.soundcloudActive = False
    data.beats = []

    data.velx = 10
    data.vely = 10
    data.p = None
    data.volSum = 1841616
    data.volCount = 1
    data.max = 343

    data.phaseJuice = 0
    data.maxPhaseJuice = 100
    data.boostJuice = 0
    data.maxBoostJuice = 100

    data.playerR = 370
    data.playerPos = 6.28
    data.playerVel = 0
    data.playerAcel = 0.001

    data.graphers += [BeatGrapher((1390, 10), 250, "#979797")]
    data.graphers += [Graph((1390, 10), 250, "red")]
    data.graphers += [Graph((1390, 10), 250, "green", 1)]
    data.graphers += [Graph((1390, 10), 250, "blue", 2)]
    data.graphers += [Graph((1412, 260), 300, data.fourier_colors[0], 1.5, 0.684 * fourierInterval, False)]
    # Usual Fourier height = 625

    makeBtns(data)

    #getSoundCloudSong(data)

def isFile(path):
    return os.path.isdir(path) == False

def getWavFiles(path, filename = ""): #Returns a list of all wav files in the audioLocation directory
    if (isFile(path)):
        # base case:  not a folder, but a file
        if (path.endswith(".wav")):
            name = filename[:-4]
            return [(name.replace("_"," "), path)]
        return []
    else:
        bestPath = ""
        bestSize = 0
        # recursive case: it's a folder
        allWaves = []
        for filename in os.listdir(path): #Iterate through every item in there
            curPath = path + os.sep + filename
            result = getWavFiles(curPath, filename)
            allWaves += result
    return allWaves

def setSong(name): #Sets the current song and starts the game
    global dati
    dati.songPath = name
    dati.posx = 710
    dati.posy = 410
    dati.targets = [(710,410)]
    dati.dots = []
    dati.gamestate = 5

def makeBtns(data): #Makes all the buttons for the menu screen
    def sandfunc(data): #Unique function for sandbox mode
        data.posx = 710
        data.posy = 410
        data.targets = [(710,410)]
        data.gamemode = "sandbox"
        data.dots = []
        data.gamestate = 5

    def helpfunc(data): #Unique function for the tutorial button
        setSong("Tutorial.wav")

    helpBtn = Button((710-310, 100), (710-250,160), "?", "#6D6D6D", "#63EC39", helpfunc, data)
    sandbox = Button((710-225, 100), (710,160), "Sandbox", "#6D6D6D", "#0091FF", sandfunc, data)
    soundcloud = Button((710+25, 100), (710+250,160), "SoundCloud", "#6D6D6D", "#fe4700", getSoundCloudSong, data)
    data.buttons.append(helpBtn)
    data.buttons.append(sandbox)
    data.buttons.append(soundcloud)

    global audioLocation
    data.songs = songs = getWavFiles(audioLocation)

    lastEnd = 0
    lastRowEndIndex = 0
    r = 0 #row
    for i in range(len(songs)):
        song = songs[i]
        name = song[0]
        path = song[1]
        c = i - lastRowEndIndex #column
        btnWidth = 15*len(name) + 30
        btnHeight = 60
        (gapx, startx, gapy, starty) = (0, lastEnd + 20, 80, 220)
        startTest = gapx * c + startx + btnWidth
        if (startTest > 1420-70):
            r += 1
            lastRowEndIndex = i
            c = 0
            startx = 20
        btn = Button((gapx * c + startx + 70, gapy * r +starty), (gapx * c + startx + btnWidth + 70, gapy * r +starty + btnHeight),
            name, "#6D6D6D", "#0091FF", generateLambda(path), data)
        data.buttons.append(btn)
        lastEnd = gapx * c + startx + btnWidth

def generateLambda(name): #Generates a function for the current button to set the song to its respective path
    curName = name
    return lambda d: setSong(curName)

def explode(data, x,y, pCount = 20, vel = 3, velr = -1.5, offset = 0, r=None, curvy=True, safe = True): #Creates dots for an explosion with the given parameters
    directions = []
    if (not game): safe = False
    for i in range(pCount):
        directions.append(i * 2*math.pi/pCount + offset)

    for d in directions:
        velx = math.cos(d) * vel
        vely = math.sin(d) * vel
        if (safe and len(dati.dots) < 325):
            data.dots.append(Dot(x, y, data, velx, vely, velr, r, curvy))
        elif (not safe):
            data.dots.append(Dot(x, y, data, velx, vely, velr, r, curvy))

def mousePressed(event, data):
    (data.mouseX, data.mouseY) = (event.x, event.y)
    if (data.gamestate == 0): #Handle all the button clicks on the menu screen
        for btn in data.buttons:
            btn.handleClick(event)
    else:
        if (data.gamestate == 4 and data.timescale < 1): #If the game's in a certain situation, add a new target for the emitter to go to
            data.targets.append((event.x,event.y))
        else: #Create an explosion at the click point. Used for testing.
            x = data.targets[0][0]
            y = data.targets[0][1]
            explode(data, event.x, event.y, 50, 10, -0.7)

def redrawAll(canvas, data):
    if (data.gamestate == 0): #Draw the menu screen
        canvas.create_rectangle(-5,-5, 1425, 825, fill="#333333") #Draw the background
        canvas.create_line(110, 200, 1310, 200, fill="#555555", width=2) #Draw a divider
        canvas.create_text(710, 50, fill="white", text="Pulse", #Draw the game title
            font = "Helvetica 60 bold")
        for btn in data.buttons: #And all its buttons
            btn.draw(canvas, data)
    else:
        canvas.create_rectangle(-10, -10,data.width+10,data.height+10, fill = data.backgroundColor, width=0) #Apply the background color

        data.graphers[4].draw(data.fourier, canvas) #Draw the equalizer fourier transform behind everything else
        drawTargetLinks(canvas, data) #Draw lines that connect all the targets

        if not data.gamemode == "sandbox":
            #Draw the target ring
            canvas.create_oval(710-data.checkRadius, 410-data.checkRadius,710+data.checkRadius,410+data.checkRadius, fill="", outline=data.circColor, width=str(data.circWidth))
            for rad in data.targetRadii: #Draw all the beat rings
                canvas.create_oval(710-rad, 410-rad,710+rad,410+rad, fill="", outline="purple", width="2.5")

        for tup in data.targets: #Draw all the targets
            drawTarget(canvas, data, tup[0], tup[1])
        for dot in reversed(data.dots): #Draw all the dots, most recent ones first
            dot.draw(canvas)

        #Draw all lines of the graph in the top-right
        data.graphers[0].draw(data.beats, canvas)
        data.graphers[2].draw(data.energy_averages, canvas)
        data.graphers[3].draw(data.instant_energies, canvas)

        if not data.gamemode == "sandbox":
            #Draw the player scores
            canvas.create_text(10, 410, text= str(data.leftScore), anchor=W, fill = "Blue", font = "Avenir 30 bold")
            canvas.create_text(1410, 410, text= str(data.rightScore), anchor=E, fill = "Red", font = "Avenir 30 bold")

        if (data.gamestate == 5):
            #Also draw the graph labels
            canvas.create_text(1200, 145, text="instant energy", fill="blue")
            canvas.create_text(1300, 145, text="local average", fill="green")
            canvas.create_text(1370, 145, text="beat", fill="black")

def drawTarget(canvas, data, x, y):
    #Draw a target at the given location as a cluster of four orbs
    tr = 5
    offset = 3
    if (len(data.colors) == 1): tarColors = [data.colors]*4
    else: tarColors = data.colors
    canvas.create_oval(x - offset - tr, y - offset - tr, x - offset + tr, y - offset + tr,
        fill = tarColors[0], width=0)
    canvas.create_oval(x + offset - tr, y - offset - tr, x + offset + tr, y - offset + tr,
        fill = tarColors[1], width=0)
    canvas.create_oval(x - offset - tr, y + offset - tr, x - offset + tr, y + offset + tr,
        fill = tarColors[2], width=0)
    canvas.create_oval(x + offset - tr, y + offset - tr, x + offset + tr, y + offset + tr,
        fill = tarColors[3], width=0)

def drawTargetLinks(canvas, data):
    #Draw lines that connect all of the targets
    if (data.timescale < 1):
        fill = "red"
    else:
        fill = "#E4E4E4"
    canvas.create_line(data.posx, data.posy, data.targets[0][0], data.targets[0][1], fill=fill, width=2)
    for i in range(0, len(data.targets)-1):
        cur = data.targets[i]
        to = data.targets[i+1]
        canvas.create_line(cur[0], cur[1], to[0], to[1], fill=fill, width=2)

def remakeStream(percentage):
    #Remake the audio stream with a given timescale. Slow down or speed up the song at will.
    global dati
    data = dati
    data.p = pyaudio.PyAudio()
    if (data.stream != None):
        data.stream.stop_stream()
    data.stream = None
    data.stream = data.p.open(format=data.p.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=int(wf.getframerate()*percentage),
        output=True,
        stream_callback = callback)
    data.stream.start_stream()

def keyPressed(event, data):
    if (event.keysym == "space"): #Slow down time (or speed it back up)
        if (data.timescale == 1):
            data.backup = data.colors
            data.timescale = 0.2
            for dot in data.dots:
                dot.fill = "#FF0051"
            data.colors = ["#FF0051"]
            data.backgroundColor = "#FFB9B9"
            data.graphers[4] = Graph((1412, 260), 300, data.fourier_colors[1], 1.5, 0.684 * fourierInterval, False) #Change the fourier graph's colors
            if (data.gamemode == "song"):
                remakeStream(songTimeScale)
        else:
            proont("-----")
            data.timescale = 1.0
            data.backgroundColor = data.backgroundBase
            data.colors = data.backup
            for dot in data.dots:
                dot.fill = random.choice(data.colors)
            data.graphers[4] = Graph((1412, 260), 300, data.fourier_colors[0], 1.5, 0.684 * fourierInterval, False) #Change the fourier graph's colors
            if (data.gamemode == "song"):
                remakeStream(1)

    elif (event.keysym == "r"): #Move the emitter back to the center
        data.posx = data.width//2
        data.posy = data.height//2
        data.startx = data.posx
        data.starty = data.posy

    #Change some game modes
    elif (event.keysym == "1"):
        data.gamestate = 1
        data.timer = 0
    elif (event.keysym == "2"):
        data.gamestate = 2
        data.startx = data.posx
        data.starty = data.posy
    elif (event.keysym == "3"):
        data.gamestate = 3
        data.startx = data.posx
        data.starty = data.posy
    elif (event.keysym == "4"):
        data.gamestate = 4
    elif (event.keysym == "5"):
        data.gamestate = 5

    elif (event.keysym == "Escape"): #Go back to the menu screen and clean up
        data.gamestate = 0
        if (data.stream != None):
            data.stream.stop_stream()
        data.p = None
        data.stream = None
        data.maxEnergy = 0
        data.timescale = 1
        data.gamemode = "song"
        data.fourier = []
        data.instant_energies = []
        data.energy_averages = []
        data.beats = []
        data.graphers[4].maxVal = 0
        data.playerR = 370
        data.playerPos = 6.28
        data.playerVel = 0
        data.leftScore = 0
        data.rightScore = 0
        data.targetRadii = []

    elif (event.keysym == "0"): #Change the emitter's colors
        changeColors(data)

    if (not data.gamemode == "sandbox"): #If we're playing a game, handle the players' key presses
        if (event.keysym == "a"):
            bestDist = 9999999
            for test in data.targetRadii:
                distance = abs(data.checkRadius - test)
                if distance < bestDist:
                    bestDist = distance
            data.leftDistance = bestDist
            if (bestDist > 50): #If there's no beat even somewhat close, they lose points
                data.leftScore -= 1
            else:
                data.beatTimer = 2 #Wait a bit for the other player to make their move before we decide who gets the beat

        elif (event.keysym == "l"):
            bestDist = 9999999
            for test in data.targetRadii:
                distance = abs(data.checkRadius - test)
                if distance < bestDist:
                    bestDist = distance
            data.rightDistance = bestDist
            if (bestDist > 50): #If there's no beat even somewhat close, they lose points
                data.rightScore -= 1
            else:
                data.beatTimer = 2 #Wait a bit for the other player to make their move before we decide who gets it

    pass

def changeColors(data): #Pick a new random color scheme, and create an explosion of dots to commemorate it
    newColorSchema(data)
    
    data.targetRadii += [0]
    explode(data, data.posx, data.posy, 50, 30, -0.5, 0, None, False, False)
    #explode(data, x,y, pCount = 20, vel = 3, velr = -1.5, offset = 0, r=None, curvy=True):

def pickNewTarget(data): #Pick a new target location for the emitter to head to
    if (hasattr(data, 'startx')):
        x = data.targets[0][0]
        y = data.targets[0][1]
        explode(data, data.posx, data.posy, 50, ((data.startx-x)**2 + (data.starty-y)**2)**0.7/500, -0.5)
        data.targets.pop(0)
    if (len(data.targets) == 0):
        x = random.randint(0, data.width)
        y = random.randint(0, data.height)
        data.targets.append((x,y))
    data.startx = data.posx
    data.starty = data.posy

def moveCircle(data): #Move the emitter in a circle
    data.posx = data.posx + data.radius * math.sin(data.time/20 * data.timescale) * data.timescale
    data.posy = data.posy + data.radius * math.cos(data.time/20 * data.timescale) * data.timescale

def moveFollow(data): #Move the emitter towards the mouse. Have it move faster if the mouse is farther away
    x = data.root.winfo_pointerx()
    y = data.root.winfo_pointery()
    data.targets = None
    data.targets = [(x-5,y-45)]
    data.startx = data.posx
    data.starty = data.posy

    dif = data.targets[0][0] - data.startx
    data.posx += dif/15 * data.timescale

    dif = data.targets[0][1] - data.starty
    data.posy += dif/15 * data.timescale

def timerFired(data):
    if (data.circWidth > 3): #Bring the target circle's width back down to normal if it was just inflated by a point grab
        data.circWidth -= 3 * data.timescale
    if (data.leftScore < 0): data.leftScore = 0 #Stop player scores from going negative
    if (data.rightScore < 0): data.rightScore = 0

    for i in range(len(data.targetRadii)): #Increment all the beat rings' radii
            try:
                curpos = len(data.targetRadii) - i - 1 #Go backwards because we may have to remove some rings
                data.targetRadii[curpos] += 30 * data.timescale
                if (data.targetRadii[curpos] > 1420):
                    data.targetRadii.pop(curpos)
            except:
                pass

    

    if (data.beatTimer == 0 and data.lastBeatTimer > 0): #If it's been long enough since a player claimed a beat, decide who wins it
        data.circWidth = 10 #Have the circle get thicker for a bit
        if data.leftDistance < data.rightDistance:
            data.leftScore += 1
            data.circColor = "blue" #Show who won that beat
        else:
            data.rightScore += 1
            data.circColor = "red" #Show who won that beat
        data.leftDistance = data.rightDistance = 9999999

    data.lastBeatTimer = data.beatTimer

    if (data.beatTimer > 0):
        data.beatTimer -= 1

    if (not handleDots): data.dots = [] #Debug method to run the program without any dots
    data.time += 1 * data.timescale

    #Decay the max value so the song has a chance to trigger another explosion
    global decay
    decrement = (data.maxEnergy - data.maxEnergy*decay) * data.timescale
    data.maxEnergy -= decrement

    if (data.gamestate == 0): #Get the mouse position and update all the buttons in case the mouse is hovering over them
        data.mouseX = data.root.winfo_pointerx()-5
        data.mouseY = data.root.winfo_pointery()-50
        for btn in data.buttons:
            btn.update(data)

    elif (data.gamestate == 1): #If we're in the right game mode, have the emitter move in a circle
        moveCircle(data)

    elif (data.gamestate == 2 or data.gamestate == 4): #If we're in the other ones, have it pick a target and head to it, then pick another
        if (almostEqual(data.posx, data.targets[0][0]) and almostEqual(data.posy, data.targets[0][1])):
            pickNewTarget(data)
        if (not almostEqual(data.posx, data.targets[0][0])):
            dif = data.targets[0][0] - data.startx
            data.posx += dif/20 * data.timescale
        if (not almostEqual(data.posy, data.targets[0][1])):
            dif = data.targets[0][1] - data.starty
            data.posy += dif/20 * data.timescale

    elif (data.gamestate == 3): #Or if we're in another one, have it chase the mouse
        moveFollow(data)

    elif (data.gamestate == 5): #Otherwise we're in audio mode. Make sure the stream is running.
        if (data.p == None):
            data.p = pyaudio.PyAudio()
            p = data.p
            if (data.gamemode == "sandbox"):
                data.stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK,
                    stream_callback = callback)
            else:
                global wf
                wf = wave.open(data.songPath, 'rb')
                data.stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    stream_callback = callback)

    for dot in (data.dots):
        x = math.sin(data.playerPos) * data.playerR + data.posx
        y = math.cos(data.playerPos) * data.playerR + data.posy
        if not data.playerPhased and (((dot.x-x)**2 + (dot.y-y)**2) ** 0.5 < dot.r): #When the player is touching a dot, push them back
            force = dot.r * 0.07
            data.playerVel -= force * data.timescale
        dot.update(data)

    if (data.time - data.last >= 1): #If we're at the right time, make more dots at the emitter spot to identify it
        data.last = data.time
        for i in range(2):
            data.dots.append(Dot(data.posx, data.posy, data, None, None, -1))

    if data.phaseJuice > data.maxPhaseJuice: data.phaseJuice = data.maxPhaseJuice
    if data.boostJuice > data.maxBoostJuice: data.boostJuice = data.maxBoostJuice
    if data.phaseJuice < 0: data.phaseJuice = 0
    if data.boostJuice < 0: data.boostJuice = 0
    pass

def callback(in_data, frame_count, time_info, status): #Handle the audio processing on another thread to keep things fluid
    global dati
    data = dati

    if (dati.gamemode == "sandbox"): #Get audio either from the microphone or from the current song
        datum = in_data
    else:
        datum = wf.readframes(frame_count)

    data.lastCallBack = time.time() #

    p = data.p
    stream = data.stream

    try:
        data.signal = np.fromstring(datum, dtype=np.int16) #Convert the byte code to an understandable signal

        result = beatDetect.detect_beat(np.frombuffer(datum, np.int16), data) #Find out if this chunk had a beat or not
        if (result != None):
            if (data.gamemode == "sandbox"): #If it's a beat and we're in sandbox mode
                count = math.ceil(result[0].item())
                curTime = int(round(time.time() * 1000))
                if curTime - data.lastBeat > 3000: #If it's been a long time since the last beat, count this one as extra important
                    changeColors(data)
                data.lastBeat = curTime
                data.offset += 0.11
                if (result[0] > data.maxEnergy):
                        data.maxEnergy = result[0]
                        changeColors(data)
                explode(data, data.posx, data.posy, count, 20, -0.1, data.offset, 5 + random.randrange(4), False, False)

            else: #Otherwise if it's a beat and we're in the middle of a game
                curTime = int(round(time.time() * 1000))
                timeSinceLastBeat = curTime - data.lastBeat

                intervalNeeded = 20
                if (data.timescale < 1):
                    intervalNeeded /= (songTimeScale / 4.5)
                if (timeSinceLastBeat > intervalNeeded):
                    InstantEnergy = result[0].item()
                    count = (math.ceil(InstantEnergy))//15
                    if (count == 0):
                        count = 1
                        baseSize = 2
                    else:
                        baseSize = 5

                    if curTime - data.lastBeat > 3000:
                        changeColors(data)
                    if (InstantEnergy > data.maxEnergy):
                        data.maxEnergy = InstantEnergy
                        changeColors(data)

                    data.lastBeat = curTime
                    data.offset += 0.11
                    explode(data, data.posx, data.posy, count, 20, -0.1, data.offset, baseSize + random.randrange(4) ,False)
                    #explode(data, x,y, pCount = 20, vel = 3, velr = -1.5, offset = 0, radius = None, curvy=True)
    except Exception as e:
        print ("Unexpected error:", str(e))
        proont("overflow issue. resetting.")
        #data.p = pyaudio.PyAudio()
        data.stream = data.p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK,
                stream_callback = callback)

    return (datum, pyaudio.paContinue)

def almostEqual(f1, f2): #Self explanatory
    threshold = 10
    return abs(f1-f2) < threshold

def newColorSchema(data): #Gets a new colorschema that is different from the last
    if (data.timescale == 1):
        bad = data.colors
        while (data.colors == bad):
            data.colors = random.choice(data.colorschemas)
    else:
        bad = data.backup
        while (data.backup == bad):
            data.backup = random.choice(data.colorschemas)


def getSoundCloudSong(data):
    data.canvas.create_text(710, 790, text="Finding Random SoundCloud Song...", fill="white", font="Helvetica 20")

    # create a client object with your app credentials. Unused now due to authorization issues in reading tracks
    client = soundcloud.Client(client_id='97cb40ade708093de0c9276826222021',
                                client_secret='f63f9a9d2594537edc2f6e5acd0d5995',
                                username='devanshkukreja1@gmail.com',
                                password='TermProject')

    #tracks = client.get('/tracks', genres='edm', license='cc-by-sa') #Gets the top 10 tracks from this search. Commented due to authorization issues

    #A bit of brute force to find a working track id for soundcloud, because of authorization issues
    client = soundcloud.Client(client_id='97cb40ade708093de0c9276826222021')
    i = random.randrange(9986) + 30709986
    track = None

    while (track == None):
        try:
            track = client.get('/tracks/'+str(i))
            stream_url = client.get(track.stream_url, allow_redirects=False)
        except Exception as e:
            print ("<1> Error: ", str(e))
            track = None
            i = random.randrange(9986) + 30709986

    # print the tracks stream URL
    print (stream_url.location)

    #We sound a song, now let's download it
    tarSong = stream_url.location
    fileName = randomString(10)
    urllib.request.urlretrieve (tarSong, "input.mp3")

    #And now let's convert it
    subprocess.call(['ffmpeg', '-i', 'input.mp3',
                        fileName + '.wav'])

    #And finally, let's push it into the game and begin
    setSong(fileName + '.wav')

def randomString(length): #Get a random file name to save the soundcloud mp3 as
    res = ''
    letters = len(string.ascii_letters)
    for i in range(length):
        res += string.ascii_letters[random.randrange(letters)]
    return res

def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        #redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 15 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    data.root = root
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    data.canvas = canvas
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<KeyPress>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1420, 820)
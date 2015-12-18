######################################################
#        Devansh Kukreja Term Project - Pulse        #
#----------------------------------------------------#
#     The Dot/Particle class and the Button class    #
######################################################

import random
import math

class Dot(object): #Lots of variables/arguments so they're more particles than just boring old dots
    def __init__(self, x, y, data, velx = None, vely = None, velr = None, r = None, curvy=True):
        self.x = x
        self.y = y
        self.r = r
        self.fill = random.choice(data.colors)
        self.clickCount = 0
        self.timer = 0
        self.velx = velx
        self.vely = vely
        self.velr = velr
        self.curvy = curvy

        if (self.velx == None):
            negnum = random.random()-0.5
            self.velx = random.random()*2 * abs(negnum)/negnum
        if (self.vely == None):
            negnum = random.random()-0.5
            self.vely = random.random()*2 * abs(negnum)/negnum
        if (self.velr == None):
            self.velr = -0.5
        if (self.r == None):
            self.r = random.randint(10,20)

    def containsPoint(self, x, y): #Check if the given point is within the dot's circle
        d = ((self.x - x)**2 + (self.y - y)**2)**0.5
        return (d <= self.r)

    def draw(self, canvas): #Draw the dot
        canvas.create_oval(self.x-self.r, self.y-self.r,
                           self.x+self.r, self.y+self.r,
                           fill=self.fill, width=0)

    def update(self, data): #Update the dot based on all its variables and the time speed
        self.timer += 1 * data.timescale
        if (self.curvy):
            self.x += self.velx * math.sin(self.timer/10) * data.timescale
            self.y += self.vely * math.sin(self.timer/10) * data.timescale
        else:
            self.x += self.velx * data.timescale
            self.y += self.vely * data.timescale
        self.r += self.velr * data.timescale

        if (self.r < 0): #If the dot disappeared, remove it
            data.dots.remove(self)

        elif ((self.x < self.r or self.x > data.width+self.r) and (self.y < self.r or self.y > data.height+self.r)): #If the dot went off-screen, remove it
            data.dots.remove(self)
            data.score += 1

class Button(object): #Near-universal button class
    def __init__(self, topleft, bottomright, text, color, outline, function, data, size=" 30"):
        self.text = text
        self.bg = color
        self.outline = outline
        self.callback = function
        self.topleft = topleft
        self.bottomright = bottomright
        self.state = "idle"
        self.data = data
        self.didClick = False
        self.size = size

    def handleClick(self, event): #If we clicked on the button, run the given function with data as an argument
        if (self.inBounds((event.x,event.y))):
            self.callback(self.data)

    def update(self, data): #If we're hovering over the button, change its color to show that
        self.state = "idle"
        if (self.inBounds((data.mouseX, data.mouseY))):
            self.state = "hover"

    def inBounds(self, pos): #Check if a given point is within the rectangle of the button
        if (pos[0] < self.topleft[0] or
            pos[0] > self.bottomright[0] or
            pos[1] < self.topleft[1] or
            pos[1] > self.bottomright[1]):
            return False
        return True

    def draw(self, canvas, data):
        if (self.state == "hover"): #If the mouse is hovering of this button, draw the bg with the same fill as outline
            canvas.create_rectangle(self.topleft, self.bottomright,
                fill=self.outline, outline=self.outline, width = 2)
        else: #Otherwise draw the bg normally
            canvas.create_rectangle(self.topleft, self.bottomright,
            fill=self.bg, outline=self.outline, width = 2)

        #All good buttons have names
        canvas.create_text((self.topleft[0]+self.bottomright[0])//2,
                            (self.topleft[1] + self.bottomright[1])//2,
                            text = self.text, fill="#ffffff",
                            font = data.font+self.size)


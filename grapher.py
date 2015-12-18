######################################################
#        Devansh Kukreja Term Project - Pulse        #
#----------------------------------------------------#
#         Grapher class that graphs everything       #
######################################################

maxVal = 0

class Graph(object): #The normal graphs in the top-right for instant and average energies
    def __init__(self, topRight, height, color, r=1, spread = 2, unified = True):
        (self.right, self.top) = topRight
        self.height = height
        self.color = color
        self.r = r
        self.unified = unified
        self.maxVal = 0

        self.spread = spread

    def draw(self, points, canvas):
        global maxVal

        if (self.unified): #The group of graphs in the top-right share the same maxValues since they're on the same scale
            for i in range(len(points)-1):
                val = points[i]
                if (abs(val) > maxVal): maxVal = abs(val) 
                curX = self.right - (len(points) - 1 - i) * self.spread
                curY = self.top + self.height/2 - val/maxVal * self.height/2

                val = points[i+1]
                if (abs(val) > self.maxVal): self.maxVal = abs(val)
                nextX = self.right - (len(points) - 2 - i) * self.spread
                nextY = self.top + self.height/2 - val/maxVal * self.height/2

                canvas.create_line(curX,curY,nextX,nextY, fill = self.color, width=self.r)

                if (self.color == "green"): #If we're graphing the average energy graph, shade the area beneath it
                    canvas.create_line(curX,curY,curX,self.top + self.height/2, fill = self.color, width=self.r)

        else: #The fourier graph in the center is on its own scale, so it has its own maxValue.
            for i in range(len(points)-1): #Draw lines from each point to the next point
                val = points[i]
                if (abs(val) > 900000):
                    val = 900000 * abs(val)/val
                if (abs(val) < 5000 and val!=0):
                    val = 5000 * abs(val)/val
                if (abs(val) > self.maxVal): self.maxVal = abs(val)
                curX = self.right - (len(points) - 1 - i) * self.spread
                curY = self.top + self.height/2 - val/self.maxVal * self.height/2

                val = points[i+1]
                if (abs(val) > 900000):
                    val = 900000 * abs(val)/val
                if (abs(val) < 5000 and val!=0):
                    val = 5000 * abs(val)/val
                if (abs(val) > self.maxVal): self.maxVal = abs(val)
                nextX = self.right - (len(points) - 2 - i) * self.spread
                nextY = self.top + self.height/2 - val/self.maxVal * self.height/2

                canvas.create_line(curX,curY,nextX,nextY, fill = self.color, width=self.r)

class BeatGrapher (Graph): #Draw beats as fully vertical lines, but let's extend the graph class to save code
    def __init__(self, topRight, height, color):
        super().__init__(topRight, height, color)

    def draw(self, points, canvas):
        for i in range(len(points)):
            val = points[i]
            if val:
                x = self.right - (len(points) - 1 - i) * self.spread
                canvas.create_line(x-self.r, self.top,
                    x+self.r,self.top + self.height/2, fill = self.color)
                

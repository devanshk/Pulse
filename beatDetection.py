######################################################
#        Devansh Kukreja Term Project - Pulse        #
#----------------------------------------------------#
#                  Beat Detection                    #
######################################################

import numpy
import pyaudio
import time
import grapher

doGraphs = True
fourierInterval = 5

class SimpleBeatDetection:
    # Beat detection algorithm from: 
    # http://archive.gamedev.net/archive/reference/programming/features/beatdetection/index.html

    def __init__(self, history = 15):
        self.local_energy = numpy.zeros(history) # A ring buffer for values from the last few chunks we want to get the average energy from. Ring buffer to make it easy to replace data every update.
        self.local_energy_index = 0 # The index of the oldest energy value. Needed since we're using a ring buffer.

    def detect_beat(self, signal, data = None):

        samples = signal.astype(numpy.int) # Creates a copy of the array, casted to integers

        # Do samples**2 very efficiently, and get its sum
        instant_energy = numpy.dot(samples, samples) / float(0xffffffff) # normalize

        local_energy_average = self.local_energy.mean() #Get the average energy from the history
        local_energy_variance = self.local_energy.var() #As well as the variance

        beat_sensibility = (-0.0025714 * local_energy_variance) + 1.15142857 #If there's too much noise, it's less likely this was a beat. Using some magic numbers found online as coefficents here.

        if (data.gamemode == "sandbox"): #If we're in sandbox mode, just count it as a beat
            beat = abs(instant_energy) > abs(beat_sensibility * local_energy_average)
        else:
            beat = (abs(instant_energy) > abs(beat_sensibility * local_energy_average) and instant_energy > 1) #Otherwise make sure it's atleast somewhat loud

        self.local_energy[self.local_energy_index] = instant_energy #Push the current chunk's value into the ring buffer
        self.local_energy_index -= 1 #And queue up the next position

        if self.local_energy_index < 0: #If we've gone all the way around the buffer, reset the index
            self.local_energy_index = len(self.local_energy) - 1

        if len(data.signal) == 0: #Detect when it's the end of the song and go back to the menu after cleaning up things
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

        fourier = numpy.fft.fft(data.signal) #Do the fourier transform
        data.fourier = fourier.real[::fourierInterval] #And save a version we can use to data for graphing

        if (doGraphs): #Add all the values we got to lists to be graphed
            data.instant_energies += [instant_energy]
            data.energy_averages += [local_energy_average]
            data.beats += [beat]

            if len(data.instant_energies) > 200: #If we have too many data points, remove the oldest one
                removedTop = False

                #And if we got rid of the previous max, compute a new maximum value for the graph
                if (data.instant_energies.pop(0) >= grapher.maxVal): removedTop = True
                if (data.energy_averages.pop(0) >= grapher.maxVal): removedTop = True
                if (data.beats.pop(0) >= grapher.maxVal): removedTop = True

                if (removedTop):
                    self.max = 0
                    for i in range(200):
                        if (data.instant_energies[i] > self.max):
                            self.max = data.instant_energies[i]
                        if (data.energy_averages[i] > self.max):
                            self.max = data.energy_averages[i]

                    grapher.maxVal = self.max
        if (beat):
            return (instant_energy, local_energy_average)
        return None
    
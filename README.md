# Pulse
##An AudioVisualizer Game: 15-112 Term Project

Pulse is an audio visualizer and multiplayer game.
It can analyze audio from the microphone, or parse a song and dynamically calculate beats/beat strength to create its visualization and game. All the processing is done on a different thread to keep the main ui thread more fluid. From a tech standpoint, this is done by using a callback function with PyAudio.

#Running Pulse
To run this, there's a series of modules you'll need to install.

First is HomeBrew: http://brew.sh

Then you can install PyAudio with "brew install portaudio" and "pip install pyaudio" (more detail at https://people.csail.mit.edu/hubert/pyaudio/)

Then install the SoundCloud module with "pip install soundcloud" (more detail at https://github.com/soundcloud/soundcloud-python)

After that, download FFmpeg from https://www.ffmpeg.org and follow its instructions to install it. You may need to download additional files to decode mp3s.

In order to play your own songs, you should also change the 'audioLocation' variable at the top of the pulse.py file to the location of the folder where you're storing your .wav music files.

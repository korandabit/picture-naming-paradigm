import os
import time
import glob
import pyaudio
import wave
from psychopy import visual, event, core, gui, sound

# Generalizable functions for all kinds of experiments

# I added two interruptions to the continuous playback
#	1. keypress 'space'
#   2. duration
# both are passed as function parameters.
# - Mark Koranda/06.15.2018

# and some toggles on the display text fn

class AudioRecorder(object):
	def __init__(self, fname,
				 RECORD = True,
				 CHANNELS = 1,
				 RATE = 44100,
				 BUFFER = 2048):
		AUDIO = pyaudio.PyAudio()
		self.fname = fname
		self.wav = wave.open(fname, "wb")
		self.wav.setnchannels(CHANNELS)
		self.wav.setsampwidth(AUDIO.get_sample_size(pyaudio.paInt16))
		self.wav.setframerate(RATE)
		def cb(in_data, count, time_info, status):
			self.wav.writeframes(in_data)
			return in_data, pyaudio.paContinue
		self.stream = AUDIO.open(format = pyaudio.paInt16,
								 channels = 2*CHANNELS,
								 rate = RATE/2,
								 input = True,
								 frames_per_buffer = BUFFER,
								 stream_callback = cb)

	def start(self):
		self.stream.start_stream()
		
	def stop(self):
		self.stream.stop_stream()
		self.stream.close()
		self.wav.close()

def playAudio(waveFile,duration,keypress='space'):
	chunk = 1024
	wf = wave.open(waveFile, 'rb')
	# create an audio object
	p = pyaudio.PyAudio()
	# open stream based on the wave object which has been input.
	stream = p.open(format =
	                p.get_format_from_width(wf.getsampwidth()),
	                channels = wf.getnchannels(),
	                rate = wf.getframerate(),
	                output = True)
	# read data (based on the chunk size)
	data = wf.readframes(chunk)
	# play stream (looping from beginning of file to the end)
	timer = core.Clock()
	responses =[]
	while data != '':
	    # writing to the stream is what *actually* plays the sound.
		stream.write(data)
		data = wf.readframes(chunk)
		response = event.getKeys()
		if response:
			# print(response)  # check what the key was
			responses.append(response[0])
			if keypress in response:
				print(timer.getTime())
				duration = timer.getTime()
				break
		if timer.getTime() > duration:
			print(timer.getTime())
			duration = timer.getTime()
			break

	# cleanup stuff.
	stream.close()    
	p.terminate()
	return(responses,duration)


	
# Takes information about experiment name and repository
# Gets information from experimenter about participant ID number
def makePath(expName,cbal, ID,
		  header = "", 
		  dataRepository = "/Data"):
	cwd = os.getcwd()
	cbal_strip = cbal[:-4] #remove csv
	newpath = cwd + dataRepository + "/" + expName + "_" + cbal_strip + "_" + str(ID).zfill(2)
	while os.path.exists(newpath):
		if str(ID) == "TEST":
			return (ID, newpath)
		popupError('File Exists')
		userInfo = {"Participant ID": "00"}
		dlg = gui.DlgFromDict(dictionary = userInfo, title = title_text)
		ID = dlg.data[0].encode('ascii','ignore').strip()
		newpath = cwd + dataRepository + "/" + expName + str(ID).zfill(2)
	os.makedirs(newpath)
	return (newpath)

# Take the instruction files from the instructionsDir. Searches specifically for filetype files
# and matches the files for the condition of the participant. The instruction files should be in
# the format of "Instructions_%EXP_PORTION%_%CONDITION%.txt"
### Default format for comprehension/production experiments
def getInstructions(instructionsDir,
					filetype = ".txt", 
					separator = "_",
					instrTaskIndex = 1):
	instructions = {}
	for instructionFile in glob.glob(os.getcwd() + instructionsDir + "/*" + filetype):
		# Get the condition name
		getInfo = instructionFile.split('/')[-1]
		# Get the task name
		task_key = getInfo.split(separator)[instrTaskIndex]
		task_key = task_key.split('.')[0]
		if task_key not in instructions:
			instructions[task_key] = {}
		with open(instructionFile, 'r') as f:
			instruction = f.read()
			instructions[task_key] = instruction
	return instructions

# Presents a string of text to participants
def presentText(win, text, 
				respKey = 'space',
				wait = True,
				timeDelay = 1,
				text_ht = 50):
	win.winHandle.set_fullscreen(True)
	win.flip()
	textVis = visual.TextStim(win, text = text, height = text_ht, wrapWidth = 1100, color = 'black', pos = [0, 0])
	textVis.draw()
	win.flip()
	if wait == True:
		event.waitKeys(keyList = [respKey])
	else:
		core.wait(timeDelay)
	win.flip()

def recordResponse(fileName, record, 
				   ender = "\n", 
				   header = None):
	if os.path.exists(fileName):
		writeCode = 'a'
		with open(fileName, writeCode) as f:
			header = header + ender
			f.write(header)
			record = record + ender
			f.write(record)
	else:
		writeCode = 'w'
		with open(fileName, writeCode) as f:
			record = record + ender
			f.write(record)
			
			
def write_row(row,f,delim,rowend):
	for col in row:
		f.write(str(col)+delim)
	f.write(rowend)
			
def write_2(filename,row,header,rowend='\n',delim=','):
	#wrapper to allow easy appending.
	method = 'a' if os.path.exists(filename) else 'w'
	f = open(filename, method)

	if method == 'w':
		write_row(header,f,delim,rowend)
		
	write_row(row,f,delim,rowend)

	f.close()
		

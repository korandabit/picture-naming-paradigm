# 2018.07.21
# word choice 3.2
# pilot v4 (in development)
# picture (and word) naming experiment with a deadline buzzer. this is a pre-functional build for the third pilot version (in python). it entails xx s ISI, and xx s deadline. (2.7s buzzer duration)

"""
# to do:
- test helper functions, which i migrated to here. delete helperFunctions.py
- add col for wc3.1 manipulation
- need to map new header to (some new) variables.
- add timer tests.
- upload code from 279 computer that writes data to participant .txt

- Pause/Quit fns.
Still haven't solved this. waitKeys does not advance [pauses all activity] until a certain time, then reports what happened during that time.
getKeys will work idiosyncratically.
the return function of get_keys from the hf.function seems to work. duplicate this.
"""

import pyaudio
import csv, datetime, glob, os, socket, shutil, time, wave
from psychopy import visual, event, core, gui, sound


# hf --------------------------

# copied straight from 'helperFunctions.py'
# Generalizable functions for all kinds of experiments

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
# generates file structure for each participant
def getID(expName, 
		  header = "", 
		  dataRepository = "/Data"):
	cwd = os.getcwd()
	userInfo = {"Participant ID": "TEST"}
	title_text = "Configure Participant"   
	dlg = gui.DlgFromDict(dictionary = userInfo, title = title_text)
	ID = dlg.data[0].encode('ascii','ignore').strip()
	newpath = cwd + dataRepository + "/" + expName + "_P" + str(ID).zfill(2)
	while os.path.exists(newpath):
		if str(ID) == "TEST":
			return (ID, newpath)
		popupError('File Exists')
		userInfo = {"Participant ID": "00"}
		dlg = gui.DlgFromDict(dictionary = userInfo, title = title_text)
		ID = dlg.data[0].encode('ascii','ignore').strip()
		newpath = cwd + dataRepository + "/" + expName + str(ID).zfill(2)

		os.makedirs(newpath)
	return (ID, newpath)

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


#------------------------------
# runtime functions

def build_subdir(data_dir):
	os.makedirs(data_dir + "/trgt_audio")
	os.makedirs(data_dir + "/othr_audio")

	# os.makedirs(data_dir + "/trgt_falign")
	# os.makedirs(data_dir + "/othr_falign")

	
# this is the main loop which presents a list of stimuli according to args params.
def presentStimuli(win,stimuli_list, exp, ID, dataPath,
				   outputFolder = "/Data",
				   presTime = .1,
				   catchBuffer = 0.5):
				   
	sceneVis = visual.ImageStim(win, image = None)
	# makedir()
	# for itemNum, cur_row in enumerate(stim_list[0:2]):
	for itemNum, cur_row in enumerate(stimuli_list):
		key_check = []
		
		# define variables.
		participant = str(ID).zfill(2)
		trial = str(cur_row[2]).zfill(3)
		trial_type = cur_row[0]
		condition = presTime
		img = cur_row[1]
		if trial_type == 'prac':
			trial = 'p'+ trial[1:]
			
		#paths for audio files
		audio_file = exp + '_' + participant + "_" + trial + ".wav"
		audio_path = dataPath + '/othr_audio/' + audio_file 
		
		if trial_type=="trgt":
			audio_path = dataPath + '/trgt_audio/' + audio_file
			# write to file falign format.
		
		#--------------
		# find, add path for data.txt
		#--------------
		# path for 
		stim_path = os.getcwd() + stimuliDir + img

		fixation_duration = float(cur_row[3])/1000 + 1

		recorder = AudioRecorder(audio_path)
		
		# some will be subbed out...
		word, error, word_onset, word_duration = '','','',''
		cur_key = event.getKeys(keyList=['p','u','q','space'])
		if cur_key:
			key_check.append(cur_key[0])
		
		# load current image.
		sceneVis.setImage(stim_path)
		sceneVis.draw()
		recorder.start()
		
		win.flip() # show stim

		core.wait(presTime) # for this duration,
		print("1 ",key_check)
		win.flip() # then hide screen
		
		if buzzerGo: # play the deadline buzzer
			response,duration = playAudio("bell.wav",catchBuffer)
			
		recorder.stop()
		print("2 ",key_check,response)
		
					
		# write row
		try:
			trial_duration = duration + presTime
		except:
			trial_duration = presTime
			
		header = ["computer","datetime", "experimenter", "cbal_script", "isi_dur", "deadline", "participant", "trial", "trial_type","condition", "target", "image_file", "timg_on", "timg_off", "tfix_dur", "tpause","tpause_dur", "keypress", "audio_file"]


		lrow = [computer, cur_date, exp, cbal, participant, trial, condition, trial_type, img, trial_duration, audio_path, audio_file, word, error, word_onset, word_duration]
		
		# lrow = [cur_date,exp,participant,trial,trial_type,img,dur,audio_path,audio_file]
		
		#-----------------
		# find, add data.txt write block
		#-----------------
		
		# write long format.
		try:
			write_2('data.csv',lrow,header)
			# print(lrow)
		except:
			print("error opening datafile")
			write_2('{0}.csv'.format(file_date),lrow,header)

		# write wide format.
		if trial_type=="trgt":
			intf = stimuli_list[itemNum - 1][0]
			lrow[6] = intf
			try:
				write_2('wdata.csv',lrow,header)
				# print(lrow)
			except:
				print("error opening datafile")
				write_2('w{0}.csv'.format(file_date),lrow,header)
		# key_check = event.getKeys(keyList=['a'])

		# experimenter control functions
		
		if pause_key in key_check or pause_key in response:
			key_check = ''
			presentText(win, "*paused*", wait = True,
					timeDelay = 2, text_ht = 80)

		if quit_key in key_check or quit_key in response:
			break
			
		if fixGo: # show the fix cross
			fix_timer = core.Clock()
			presentText(win, "+", wait = False,
					timeDelay = fixation_duration, text_ht = 80)
					
		event.getKeys(keyList=['p','u','q','space'])
		
instr1 = """Welcome and thank you for your participation.
  
For this experiment a series of images and words will briefly appear 
on the screen one at a time. Please say say the word or name the picture quickly and accurately. After a brief period of time, the word or picture will disappear and a bell will sound. Do your best to beat the bell, but it is okay if you do not start before the bell sounds. Either way, say the first name you think of, at which point the experimenter will advance the trial and stop the bell.

Let the experimenter know when you're ready to practice. The experimenter will advance the trial as soon as you say STAIRS"""

instr2 = """The plus sign ( + ) signals the beginning of the next picture or word. If you have not yet named the previous picture or word when the plus sign appears that is okay. However, do not try to do so at that time.

Please let the experimenter know if you have any questions, or are ready to begin."""
	
def runExp(stimuliDir, exp):
	ID, dataPath = getID(exp)

	build_subdir(dataPath)
	
	print(dataPath)
	win = visual.Window(size = [1400, 900], color = "white", units = 'pix')

	if not development_mode:
		# instructions and practice trial
		presentText(win, instr1, text_ht = 30)
		presentStimuli(win,demo_item, exp, ID , dataPath, presTime = presTime, catchBuffer = 2.3) # practice trial
	
		# instructions pt 2		
		presentText(win, instr2, text_ht = 30)
		
	# main trail block
	presentStimuli(win,stim_list, exp, ID, dataPath, presTime = presTime, catchBuffer = 2.3)

if __name__ == '__main__':
	instructionsDir = "/Instructions"
	stimuliDir = "/stimuli/"
	expName = "wc32v4" # don't have . in names.

	# import stimuli
	demo_item = [['prac','prac01.gif','1',1330]]

	with open('cbal_0.csv', 'rb') as f:
		reader2=csv.reader(f)
		stim_list = list(reader2)


	computer = socket.gethostname().upper()
	cur_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
	file_date = datetime.datetime.now().strftime("%Y%m%d_%H%M")
	cbal = 'A1a'

	## RUNTIME PARAMS
	presTime  = .5 # how long before deadline buzzer sounds.
	
	# dev parameters
	development_mode = True # if True, overwrites TEST data everytime.
	if development_mode:
		stim_list = stim_list[5:6]
		
	try:
		shutil.rmtree(dataPath+expName+"_PTEST/") # re-wrote from hard coding..
		error = "deleted old dir(TEST)"
	except:
		print("TEST dir didn't exist.")
		error = "failed: delete dir"
	
	buzzerGo = True # play buzzer slide
	fixGo = True # play fixation slide
	quit_key = 'q'
	pause_key = 'p'
	
	# runtime
	runExp(stimuliDir = stimuliDir, exp = expName)
	
	
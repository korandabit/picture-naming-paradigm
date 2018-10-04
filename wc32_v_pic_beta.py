# Version .33
#   (immediately preceded by v.30, v.30L; fix those names.)
# 2018.08.06 (modified in rm 279)

# picture (and word) naming experiment with a deadline buzzer.
# this version waits 1+ seconds before the buzzer sounds.
# AND ISI = .5

import pyaudio
import wave, glob, os, csv, datetime, socket, shutil
import helperFunctions as hf
from psychopy import visual, event, core, gui, sound

# see helperFunctions for mods 
# A. to audio playback
# I added two interruptions to the continuous playback
#	1. keypress 'space'
#   2. duration
# both are passed as function parameters.
# B. to text display.
# added a parameter for text size.
	
# conversion from steve's scripts
# minimum build.
# he's got stims mapped to a filepath, not just filename
# reads from a list of filepaths.
# I've got a list of filenames, so filepath needs to be appended, and column of filenames called (i.e. index the col position.)	

# gifs work with his script despite things...
# got the fixation to work
# 	converted ms to s
# .1s speed-run successful (with audio recording)
# minimum .csv data file added.
# added zfill p name.
# added demo instr, timedatestamp to data file
# wide data format
# tested that space doesn't override future trials, too, and/or bugs for a full run.


# TO DO: 

# fix quit/pause fns
""" Still haven't solved this. waitKeys does not advance [pauses all activity] until a certain time, then reports what happened during that time.
getKeys will work idiosyncratically.
the return function of get_keys from the hf.function seems to work. duplicate this.
"""

# test fixation timer accuracy; general latencies.
# expand data file: look at other exp for things.
# for whatever reason, itms 2-4 practice, don't register under 'if prac then'..

instr1 = """Welcome and thank you for your participation.
  
For this experiment a series of images and words will briefly appear 
on the screen one at a time. Please say say the word or name the picture quickly and accurately. After a brief period of time, the word or picture will disappear and a bell will sound. Do your best to beat the bell, but it is okay if you do not start before the bell sounds. Either way, say the first name you think of, at which point the experimenter will advance the trial and stop the bell.

Let the experimenter know when you're ready to practice. The experimenter will advance the trial as soon as you say STAIRS"""

instr2 = """The plus sign ( + ) signals the beginning of the next picture or word. If you have not yet named the previous picture or word when the plus sign appears that is okay. However, do not try to do so at that time.

Please let the experimenter know if you have any questions, or are ready to begin."""
# def foo():
	# friends = wint
	# print(wint)
# wint = 'tree'
def presentStimuli(main_window,
					dataPath,
				    ID,
				   stimuli_list,
				   presTime = .1,
				   catchBuffer = 0.5,
				   outputFolder = "/Data"):
	win = main_window
	sceneVis = visual.ImageStim(win, image = None)
	# foo()
	
	for itemNum, cur_row in enumerate(stimuli_list):

		participant = str(ID).zfill(2)
		trial = str(cur_row[2]).zfill(3)
		trial_type = cur_row[0]
		img = cur_row[1]
		if trial_type == 'prac':
			trial = 'p'+ trial[1:]
		audio_file = exp + '_' + participant + "_" + trial + ".wav"
		data_file  = exp + '_' + participant + "_" + ".txt"
		audio_path = dataPath + '/' + audio_file
		pdata_path = dataPath + '/' + data_file
		
		stim_path = os.getcwd() + stimuliDir + img

		fixation_duration = .5 # float(cur_row[3])/1000 + 1

		recorder = hf.AudioRecorder(audio_path)
		
		# vars to be recorded. some will be subbed out...
		word, error, word_onset, word_duration = '','','',''

		# set up key press watcher
		key_check = []
		cur_key = event.getKeys(keyList=['p','u','q','space'])
		if cur_key:
			key_check.append(cur_key[0])
		
		
		# load current image.
		sceneVis.setImage(stim_path)
		sceneVis.draw()
		recorder.start()
		
		main_window.flip() # show stim

		core.wait(presTime) # for this duration,
		# print("1 ",key_check)
		main_window.flip() # then hide screen
		
		trial_duration = presTime
		response=[]
		if buzzerGo: # play the deadline buzzer
			response,duration = hf.playAudio("bell.wav",catchBuffer)
			trial_duration += duration
			
		recorder.stop()
		# print("2 ",key_check,response)
		
			
		header = ["computer","datetime", "exp", "cbal", "participant", "trial", "trial_type", "img", "trial_duration", "audio_path", "audio_file", "word", "error", "word_onset", "word_duration"]
		# this should be moved to outside the loop

		# cur_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
		lrow = [computer, cur_date, exp, cbal, participant, trial, trial_type, img, trial_duration, audio_path, audio_file, word, error, word_onset, word_duration]
		
		# write long format.
		try:
			hf.write_2('data.csv',lrow,header)
			# print(lrow)
		except:
			print("error opening datafile")
			hf.write_2('{0}.csv'.format(file_date),lrow,header)
			
		# data.txt for participant in the part folder
		try:
			hf.write_2(pdata_path,lrow,header)
			# print(lrow)
		except:
			print("error opening pdatafile")
			hf.write_2('{0}.csv'.format(file_date),lrow,header)
			
			
		# write wide format.
		if trial_type=="trgt":
			# lrow[6] = stimuli_list[itemNum - 1][0] # pull the label from previous trial to determine 'trial_type'
			try:
				hf.write_2('wdata.csv',lrow,header)
				print("wdata")
				print(lrow)
			except:
				print("error opening datafile")
				hf.write_2('w{0}.csv'.format(file_date),lrow,header)
		# key_check = event.getKeys(keyList=['a'])

		# experimenter control functions
		
		if pause_key in key_check or pause_key in response:
			key_check = ''
			hf.presentText(main_window, "*paused*", wait = True,
					timeDelay = 2, text_ht = 80)

		if quit_key in key_check or quit_key in response:
			break
			
		if fixGo: # show the fix cross
			fix_timer = core.Clock()
			hf.presentText(main_window, "+", wait = False,
					timeDelay = fixation_duration, text_ht = 80)
					
		event.getKeys(keyList=['p','u','q','space'])
		
def runExp():
	# instructions = hf.getInstructions(instructionsDir)
	main_window = visual.Window(size = [1400, 900], color = "white", units = 'pix')
	ID, dataPath = hf.getID(exp)

	# instructions and practice trial
	hf.presentText(main_window, instr1, text_ht = 30)
	presentStimuli(main_window, dataPath, ID, demo_item, presTime, catchBuffer = 2.3) # practice trial

	# instructions + rest of trials.
	hf.presentText(main_window, instr2, text_ht = 30)
	presentStimuli(main_window, dataPath, ID, stimuli_list, presTime, catchBuffer = 2.3)

if __name__ == '__main__':
	"""ALL HARDCODED DEPENDS:
	lns: 199 (stimuliDir),204 (demo_item)
	improve depends:
	wdata should look at if 'target', but requires if 'trgt'
	
	"""

	## RUNTIME PARAMS
	
	#environment
	computer = socket.gethostname().upper()
	cur_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
	file_date = datetime.datetime.now().strftime("%Y%m%d_%H%M")

	# experiment
	exp = "wc32v.33"
		
	# import stimuli
	stimuliDir = "/stimuli/"
	demo_item = [['prac','obj001accordion.jpg','1',1330]]

	#import cbal
	cbal = 'objects1.csv'
	with open(cbal, 'rb') as f:
		reader2=csv.reader(f)
		stimuli_list = list(reader2)

	#variables
	buzzerGo = True # play buzzer slide
	fixGo = True # play fixation slide

	presTime  = 1.2 # how long before deadline buzzer sounds.

	# control functions
	quit_key = 'q'
	pause_key = 'p'

	# runtime
	try:
		shutil.rmtree("Data/wc32v.33_PTEST")
	except:
		print("TEST dir didn't exist.")

	runExp()
	
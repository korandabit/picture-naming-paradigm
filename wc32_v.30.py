# this version implemented first in the piloting.
# it entails 1s ISI, and .7s deadline. (3s buzzer duration)

# picture (and word) naming experiment with a deadline buzzer.


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


def presentStimuli(win,stimuli_list, exp, ID, dataPath,
				   outputFolder = "/Data",
				   presTime = .1,
				   catchBuffer = 0.5):
				   
	sceneVis = visual.ImageStim(win, image = None)

	# for itemNum, cur_row in enumerate(stim_list[0:2]):
	for itemNum, cur_row in enumerate(stimuli_list):
		key_check = []
		
		participant = str(ID).zfill(2)
		trial = str(cur_row[2]).zfill(3)
		trial_type = cur_row[0]
		img = cur_row[1]
		if trial_type == 'prac':
			trial = 'p'+ trial[1:]
		audio_file = exp + '_' + participant + "_" + trial + ".wav"
		audio_path = dataPath + '/' + audio_file
		
		stim_path = os.getcwd() + stimuliDir + img

		fixation_duration = float(cur_row[3])/1000 + 1

		recorder = hf.AudioRecorder(audio_path)
		
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
			response,duration = hf.playAudio("bell.wav",catchBuffer)
			
		recorder.stop()
		print("2 ",key_check,response)
		
					
		# write row
		try:
			trial_duration = duration + presTime
		except:
			trial_duration = presTime
			
		header = ["computer","datetime", "exp", "cbal", "participant", "trial", "trial_type", "img", "trial_duration", "audio_path", "audio_file", "word", "error", "word_onset", "word_duration"]

		lrow = [computer, cur_date, exp, cbal, participant, trial, trial_type, img, trial_duration, audio_path, audio_file, word, error, word_onset, word_duration]
		
		# lrow = [cur_date,exp,participant,trial,trial_type,img,dur,audio_path,audio_file]
		
		# write long format.
		try:
			hf.write_2('data.csv',lrow,header)
			# print(lrow)
		except:
			print("error opening datafile")
			hf.write_2('{0}.csv'.format(file_date),lrow,header)

		# write wide format.
		if trial_type=="trgt":
			intf = stimuli_list[itemNum - 1][0]
			lrow[6] = intf
			try:
				hf.write_2('wdata.csv',lrow,header)
				# print(lrow)
			except:
				print("error opening datafile")
				hf.write_2('w{0}.csv'.format(file_date),lrow,header)
		# key_check = event.getKeys(keyList=['a'])

		# experimenter control functions
		
		if pause_key in key_check or pause_key in response:
			key_check = ''
			hf.presentText(win, "*paused*", wait = True,
					timeDelay = 2, text_ht = 80)

		if quit_key in key_check or quit_key in response:
			break
			
		if fixGo: # show the fix cross
			fix_timer = core.Clock()
			hf.presentText(win, "+", wait = False,
					timeDelay = fixation_duration, text_ht = 80)
					
		event.getKeys(keyList=['p','u','q','space'])
		
instr1 = """Welcome and thank you for your participation.
  
For this experiment a series of images and words will briefly appear 
on the screen one at a time. Please say say the word or name the picture quickly and accurately. After a brief period of time, the word or picture will disappear and a bell will sound. Do your best to beat the bell, but it is okay if you do not start before the bell sounds. Either way, say the first name you think of, at which point the experimenter will advance the trial and stop the bell.

Let the experimenter know when you're ready to practice. The experimenter will advance the trial as soon as you say STAIRS"""

instr2 = """The plus sign ( + ) signals the beginning of the next picture or word. If you have not yet named the previous picture or word when the plus sign appears that is okay. However, do not try to do so at that time.

Please let the experimenter know if you have any questions, or are ready to begin."""
	
def runExp(stimuliDir, exp):
	# instructions = hf.getInstructions(instructionsDir)
	ID, dataPath = hf.getID(exp)
	print(dataPath)
	win = visual.Window(size = [1400, 900], color = "white", units = 'pix')

	# instructions and practice trial
	hf.presentText(win, instr1, text_ht = 30)
	presentStimuli(win,demo_item, exp, ID , dataPath, presTime = presTime, catchBuffer = 2.3) # practice trial
	
	# instructions + rest of trials.
	hf.presentText(win, instr2, text_ht = 30)
	presentStimuli(win,stim_list, exp, ID, dataPath, presTime = presTime, catchBuffer = 2.3)

if __name__ == '__main__':
	instructionsDir = "/Instructions"
	stimuliDir = "/stimuli/"


	# import stimuli
	demo_item = [['prac','prac01.gif','1',1330]]

	with open('cbal_0.csv', 'rb') as f:
		reader2=csv.reader(f)
		stim_list = list(reader2)
	stim_list = stim_list

	computer = socket.gethostname().upper()
	cur_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
	file_date = datetime.datetime.now().strftime("%Y%m%d_%H%M")
	cbal = 'A1a'

	## RUNTIME PARAMS
	presTime  = .7 # how long before deadline buzzer sounds.
	
	# dev parameters
	development_mode = True # if True, overwrites TEST data everytime.
	if development_mode:
		try:
			shutil.rmtree("Data/wc32v.3_PTEST")
			error = "deleted old dir(TEST)"
		except:
			print("TEST dir didn't exist.")
			error = "failed: delete dir"
	
	buzzerGo = True # play buzzer slide
	fixGo = True # play fixation slide
	quit_key = 'q'
	pause_key = 'p'
	
	# runtime
	runExp(stimuliDir = stimuliDir, exp = "wc32v.3")
	
	
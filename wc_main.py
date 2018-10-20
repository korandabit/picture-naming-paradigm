# Version .33
#   (immediately preceded by v.30, v.30L; fix those names.)
# 2018.08.06 (modified in rm 279)

# picture (and word) naming experiment with a deadline buzzer.
# this version waits 1+ seconds before the buzzer sounds.
# AND ISI = .5

import pyaudio
import wave, glob, os, csv, datetime, socket, shutil, sys
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
def userGUI(exp="wc",cbal = "cbal.csv"):
	# this is a branch off from the makePath (formerly getID) function.
	# a = os.listdir("Data/")[-1]
	# print(a)
	try:
		name_base = sorted(os.listdir("Data/"))[-1][-2:]
		print(name_base)
		suggest =  int(name_base)+1
		suggest_id = str(suggest).zfill(2)
		print(suggest)
		# suggest_id = sorted(os.listdir("Data/"))[-2][-3:]

	except: 
		suggest_id = "name"
		# print(sorted(os.listdir("Data/"))[-2][-3:])
	userInfo = {"Participant ID": suggest_id,
				"cbal":cbal,
				"exp_name": exp}
	title_text = "Configure Participant"   
	dlg = gui.DlgFromDict(dictionary = userInfo, title = title_text)
	# print dlg.data[1]
	ID = dlg.data[0].encode('ascii','ignore').strip()
	cbal = dlg.data[1].encode('ascii','ignore').strip()
	expName = dlg.data[2].encode('ascii','ignore').strip()
	
	return (ID,cbal,expName)
	
# test fixation timer accuracy; general latencies.
# expand data file: look at other exp for things.
# for whatever reason, itms 2-4 practice, don't register under 'if prac then'..

def build_subdir(data_path):
	try:
		os.makedirs(data_path + "/trgt_audio")
		os.makedirs(data_path + "/othr_audio")
	except:
		print("subdir target already made.")


def presentStimuli(win,stimuli_list, runtime_info ,
				   outputFolder = "/Data",
				   presTime = .1,
				   catchBuffer = 0.5):
				   
	sceneVis = visual.ImageStim(win, image = None)

	# for itemNum, cur_row in enumerate(stim_list[0:2]):
	for itemNum, cur_row in enumerate(stimuli_list):
		key_check = []
		
		participant = str(runtime_info["ID"]).zfill(2)
		trial = str(cur_row[2]).zfill(3)
		trial_type = cur_row[0]
		img = cur_row[1]
		isi = cur_row[3]
		if trial_type == 'prac':
			trial = 'p'+ trial[1:]
		audio_file = runtime_info["exp"] + '_' + participant + "_" + trial + ".wav"
		data_file  = runtime_info["exp"] + '_' + participant + "_" + ".txt"
		audio_path = runtime_info["datapath"] + '/' + audio_file
		pdata_path = runtime_info["datapath"] + '/' + data_file
		trgt_path = runtime_info["datapath"] + "/trgt_audio" + '/' + audio_file
		
		stim_path = os.getcwd() + stimuliDir + img

		fixation_duration = .5 # float(cur_row[3])/1000 + 1

		recorder = hf.AudioRecorder(audio_path)
		
		# some will be subbed out...
		said, error = '',''
		cur_key = event.getKeys(keyList=['p','u','q','space'])

		
		
		# load current image.
		sceneVis.setImage(stim_path)
		sceneVis.draw()
		recorder.start()
		
		win.flip() # show stim
		
		trial_duration = 0
		
		if advance_on_space:
			timer = core.Clock()
			cur_key = event.waitKeys(keyList=['p','u','q','space'])
			trial_duration += timer.getTime()
			
		else:
			core.wait(presTime) # for this duration
			trial_duration += presTime
			
		if cur_key:
			key_check.append(cur_key[0])

		print("1 ",key_check)
		win.flip() # then hide screen


		response = []
		if deadline: # play the deadline buzzer
			response,duration = hf.playAudio("bell.wav",catchBuffer)
			trial_duration += duration
			
		recorder.stop()
		print("2 ",key_check,response)
		
					
		# write row
		# try:
			# trial_duration = duration + presTime
		# except:
			# trial_duration = presTime
		trial_duration_ms = trial_duration*1000
		header = ["computer","datetime", "exp", "cbal", "participant", "trial", "trial_type", "img", "trial_duration", "isi", "audio_path", "audio_file", "said", "error"]
		# this should be moved to outside the loop

		cur_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
		lrow = [computer, cur_date, runtime_info["exp"], runtime_info["cbal"], participant, trial, trial_type, img, trial_duration_ms, isi, audio_path, audio_file, said, error]
		
		if deadline:
			header.append("deadline")
			lrow.append(deadline)
		# lrow = [cur_date,exp,participant,trial,trial_type,img,dur,audio_path,audio_file]
		
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
		wide_type_trials = ["target","repetition"]
		
		if trial_type in wide_type_trials:
			intf = stimuli_list[itemNum - 1][0]
			lrow[6] = intf
			try:
				hf.write_2('wdata.csv',lrow,header)
				os.rename(audio_path, trgt_path)
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
		
instr1 = """Welcome and thank you for your participation.  For this experiment you will see a series of images and words that will appear on the screen one at a time. Please say what you see on the screen quickly and accurately. Once you have finished speaking the experimenter will press SPACE to advance to the next trial.

Please let the research assistant know if you have questions or are ready to move on, at this time."""

instr2 = """This concludes the experiment, thank you for your time. Please let the research assistant know that you have finished the experiment and wait for your next instructions."""
	
	
def runExp(stimuliDir):
	# instructions = hf.getInstructions(instructionsDir)
	ID, cbal, expName = userGUI(exp = "wcRepPilot",cbal = "wc1a_rep.csv")
	dataPath = hf.makePath(expName=expName,cbal= cbal,ID= ID)
	# print(dataPath)
	build_subdir(dataPath)
	win = visual.Window(size = [1400, 900], color = "white", units = 'pix')

	# instructions and practice trial
	hf.presentText(win, instr1, text_ht = 30)
	
	# presentStimuli(win,demo_item, exp, ID , dataPath, presTime = presTime, catchBuffer = 2.3) # practice trial
	
	# instructions + rest of trials.
	with open(cbal, 'rb') as f:
		reader2=csv.reader(f)
		stim_list = list(reader2)
	
	runtime_info = {"exp":expName,"cbal":cbal,"ID":ID,"datapath":dataPath}
	presentStimuli(win,stim_list, runtime_info, presTime = presTime, catchBuffer = 2.3)
	
	# conclusion
	hf.presentText(win, instr2, text_ht = 30)

if __name__ == '__main__':

	stimuliDir = "/stimuli/"

	# import stimuli
	demo_item = [['prac','prac01.gif','1',1330]]

	computer = socket.gethostname().upper()
	cur_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
	file_date = datetime.datetime.now().strftime("%Y%m%d_%H%M")


	## RUNTIME PARAMS
	presTime  = 1.2 # how long before deadline buzzer sounds.
	
	# dev parameters
	development_mode = False # if True, overwrites TEST data everytime.
	if development_mode:
		try:
			shutil.rmtree("Data/wc32v.33_PTEST")
			error = "deleted old dir(TEST)"
		except:
			print("TEST dir didn't exist.")
			error = "failed: delete dir"
			
	advance_on_space = True
	deadline = False # play buzzer slide
	fixGo = True # play fixation slide
	
	quit_key = 'q'
	pause_key = 'p'
	
	# runtime
	runExp(stimuliDir = stimuliDir)
	
	
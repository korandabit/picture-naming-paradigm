# Picture Naming
Classic paradigm for picture and word naming, that allows a number of adjustable parameters.

Main functionality includes
- takes a list of filenames as stimuli to-be-presented.
- presents pictures one at a time, in order listed.
- trials advanced by space-bar.
- fixation cross between each stimuli.
- audio recording recorded and saved during each stimuli presentation.
- detailed .txt log saved with realtime data including 
  - by-trial duration of presentation (ms).
  - runtime environment.

python picture naming experiment with option for:  

 - variable durations.
 - deadline buzzer.

## Needs file
cbal_xx.csv list of experiment trial (jpg) filenames and runtime variables  

## Needs directories  
/stimuli - containing relevant images, indexed by cbal_xx.csv  
/Data

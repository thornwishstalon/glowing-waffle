# README

## markov chains:
* all tasks regarding markov chain can be found in the noteboook: Intro_To_Markov_Chains.ipynb

## bonus
* Source Code for an android app can be found in the bonus folder
* the app is based on examples from tensorflow: https://github.com/tensorflow/examples/tree/master/lite/examples/sound_classification/android_compose
* stop word recognition does not work because:
	* I failed to find a usable mfcc feature extraction implementation that yields similar results as the one from python_speech_features
		* tried a librosa port as well as an implementation packed in tarsos dsp 
	* retraining the model under these circumstances seemed tedious
	* probably should have trained a network instead using autoencoders instead, this would have avoided my mfcc issue
 

	



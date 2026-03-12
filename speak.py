# text_to_speech.py
# This is a simple interactive text-to-speech program using pyttsx3

import pyttsx3
import time
# Initialize the speech engine
engine = pyttsx3.init()

# Optional tuning: adjust speech rate and volume
engine.setProperty('rate', 130)   # Speed of speech
engine.setProperty('volume', 1.0) # Volume level (0.0 to 1.0)


def speak(sentence_num = 4):

    text1 = "Hello Hunter, please give us a good grade. I'm mostly functional."
    text2 = "Oww my arm."
    text3 = "Hi, are you my mommy? This was done in a British accent."
    text4 = "What is my purpose? Dang it."
    if sentence_num == 1:
        engine.say(text1)
        engine.runAndWait()
	time.sleep(2)
    elif sentence_num == 2:
        engine.say(text2)
        engine.runAndWait()
    elif sentence_num == 3:
        engine.say(text3)
        engine.runAndWait()
    elif sentence_num == 4:
        engine.say(text4)
        engine.runAndWait()
    else:
        print("Invalid number")


speak(1)

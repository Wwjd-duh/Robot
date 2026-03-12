import pyttsx3
import time

# Initialize the speech engine
engine = pyttsx3.init()

# Optional tuning: adjust speech rate and volume
engine.setProperty('rate', 130)   # Speed of speech
engine.setProperty('volume', 1.0) # Volume level (0.0 to 1.0)


def speak(sentence_num=4):

    text1 = "Hello Hunter, please give us a good grade. I'm mostly functional."
    text2 = "Oww my arm."
    text3 = "Josh is my daddy."
    text4 = "What is my purpose? Dang it."

    if sentence_num == 1:
        engine.say(text1)
        engine.runAndWait()
        time.sleep(1)

    elif sentence_num == 2:
        engine.say(text2)
        engine.runAndWait()
        time.sleep(1)

    elif sentence_num == 3:
        engine.say(text3)
        engine.runAndWait()
        time.sleep(1)

    elif sentence_num == 4:
        engine.say(text4)
        engine.runAndWait()
        time.sleep(1)

    else:
        print("Invalid number")


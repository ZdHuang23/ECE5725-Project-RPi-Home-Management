# Import the modules
import os
from gtts import gTTS
import time
fifo_path = 'speechfifo'

# read command from fifo and play it
while True:
    with open(fifo_path, 'r') as fifo_file:
    # read from fifo
        data = fifo_file.read()
        print("Spoke: "+data)
        if(data == 'exit'):
            exit()
        tts = gTTS(text=data, lang='en')
        tts.save("speech.mp3")
        os.system("nohup mpg123 speech.mp3 > playerlog.txt 2>&1 &")
        time.sleep(1)
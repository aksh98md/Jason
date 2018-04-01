import RPi.GPIO as GPIO
import time
import os
import serial

from speechAPI import Microsoft_ASR, callLUIS
from imgAPI.img_recog import *
from otherRes import *
from tts import TTS
from fft import FFT
from PythonUp import read_sheet

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

allIntents = ["只是打招呼", "打電話", "文字辨識", "景象辨識", "發簡訊", "罵人", "認人", "拍照", "查詢餘額", "掰掰", "None"]


# run ls /dev/tty* before and after plugging in arduino to find out
ser = serial.Serial('/dev/ttyACM0', 9600)

# initilialize an Microsoft_ASR object

tts = TTS()
fft = FFT(time_gap=0.5)
ms_asr = Microsoft_ASR()

temperature_flag = False

while True:
    #st = time.time()
    print("\rPress to activate your voice assistant...",end='  ')
    input_state = GPIO.input(18)
    ret = None
    if input_state == True:
        # Button Pressed
        print()
        intent, entities = callLUIS(ms_asr.listen_for_speech())
        
        print('intent:', intent)
        
        if intent == "只是打招呼":
            ret = sayHello()
        elif intent == "打電話":
            ret = call(entities)
        elif intent == "文字辨識":
            ret = ocr()
        elif intent == "景象辨識":
            ret = img_caption()
        elif intent == "發簡訊":
            ret = sendText(entities)
        elif intent == "罵人":
            ret = insult()
        elif intent == "認人":
            ret = face_recog()
        elif intent == "拍照":
            ret = get_img(save=True)
        elif intent == "查詢餘額":
            ret = read_sheet()
        elif intent == "掰掰":
            ret = "親愛的再見"
        elif intent == "None":
            ret = none_reply()
    
    else:
        output = ser.readline().decode('utf-8').strip('\r\n')
        
        while output[0:4] == 'FALL':
            ret = "跌倒了啊啊啊啊啊啊!!!"
            output = output[4:]
        temperature, heartCondition = output.split(",")
        print("溫度："+temperature, end = "℃  ")
        
        temperature = float(temperature)
        if temperature_flag==False and temperature > 40:
            ret = "氣溫過高，請注意保持身體水分"
            temperature_flag = True
        elif temperature_flag==False and temperature < 15:
            ret = "氣溫過低，請注意保暖"
            temperature_flag = True
        elif temperature_flag and temperature > 15 and temperature < 40:
            temperature_flag = False
        
        tmp = fft.fft(float(heartCondition))
        if tmp != None:
            print(tmp, end='')
        
        
    #print('\n',time.time()-st)
            
    if ret != None:
        print('bot:', ret, '\n')
        tts.tts(ret)
        
    if ret == "親愛的再見":
        exit()
"""    
    
        #if "1" in fallCondtion:
        #	ret = fallAlert()
"""


    


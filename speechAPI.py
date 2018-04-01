import pyaudio
import wave
import audioop
from collections import deque
import os, sys
import time
import math

import requests
import http.client
import uuid
import json


 
LANG_CODE = 'zh-TW'    # Language to use

# Microphone stream config.
CHUNK = 1024  # CHUNKS of bytes to read each time from mic
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
THRESHOLD = 2650  # The threshold intensity that defines silence
                  # and noise signal (an int. lower than THRESHOLD is silence).

SILENCE_LIMIT = 1.5  # Silence limit in seconds. The max ammount of seconds where
                     # only silence is recorded. When this time passes the
                     # recording finishes and the file is delivered.

PREV_AUDIO = 0.5  # Previous audio (in seconds) to prepend. When noise
                  # is detected, how much of previously recorded audio is
                  # prepended. This helps to prevent chopping the beggining
                  # of the phrase.

class Microsoft_ASR():
    def __init__(self):
        self.sub_key = 'd70e49b5f2b94cea82a1293aea43e384'
        self.token = None
        self.get_speech_token()
        pass

    def get_speech_token(self):
        FetchTokenURI = "/sts/v1.0/issueToken"
        header = {'Ocp-Apim-Subscription-Key': self.sub_key}
        conn = http.client.HTTPSConnection('api.cognitive.microsoft.com')
        body = ""
        conn.request("POST", FetchTokenURI, body, header)
        response = conn.getresponse()
        str_data = response.read()
        conn.close()
        self.token = str_data.decode('utf-8')
        #print ("Got Token: ", self.token)
        return True

    def transcribe(self,speech_file):

        # Grab the token if we need it
        #if self.token is None:
        #    print ("No Token... Getting one")
        #    self.get_speech_token()

        endpoint = 'https://speech.platform.bing.com/recognize'
        request_id = uuid.uuid4()
        # Params form Microsoft Example 
        params = {'scenarios': 'ulm',
                  'appid': 'D4D52672-91D7-4C74-8AD8-42B1D98141A5',
                  'locale': 'zh-TW',
                  'version': '3.0',
                  'format': 'json',
                  'instanceid': '565D69FF-E928-4B7E-87DA-9A750B96D9E3',
                  'requestid': uuid.uuid4(),
                  'device.os': 'linux'}
        content_type = "audio/wav; codec=""audio/pcm""; samplerate=16000"

        def stream_audio_file(self,speech_file, chunk_size=1024):
            with open(speech_file, 'rb') as f:
                while 1:
                    data = f.read(1024)
                    if not data:
                        break
                    yield data
        data = open(speech_file, 'rb').read()
        headers = {'Authorization': 'Bearer ' + self.token, 
                   'Content-Type': content_type}
        resp = requests.post(endpoint, 
                            params=params, 
                            data=data, #stream_audio_file(speech_file), 
                            headers=headers)
        #val = json.loads(resp.text)
        val = resp.json()
        try:
            return val["results"][0]["name"], val["results"][0]["confidence"]
        except:
            return '', ''

    def audio_int(self,num_samples=50):
        """ Gets average audio intensity of your mic sound. You can use it to get
            average intensities while you're talking and/or silent. The average
            is the avg of the 20% largest intensities recorded.
        """

        print ("Getting intensity values from mic.")
        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        values = [math.sqrt(abs(audioop.avg(stream.read(CHUNK), 4))) 
                  for x in range(num_samples)] 
        values = sorted(values, reverse=True)
        r = sum(values[:int(num_samples * 0.2)]) / int(num_samples * 0.2)
        print (" Finished ")
        print (" Average audio intensity is ", r)
        stream.close()
        p.terminate()
        return r


    def listen_for_speech(self,threshold=THRESHOLD, num_phrases=-1):
        """
        Listens to Microphone, extracts phrases from it and sends it to 
        Google's TTS service and returns response. a "phrase" is sound 
        surrounded by silence (according to threshold). num_phrases controls
        how many phrases to process before finishing the listening process 
        (-1 for infinite). 
        """

        #Open stream
        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print ("* Listening mic. ",flush=True)
        audio2send = []
        cur_data = ''  # current chunk  of audio data
        rel = int(RATE/CHUNK)
        slid_win = deque(maxlen=int(SILENCE_LIMIT * rel))
        #Prepend audio from 0.5 seconds before noise was detected
        prev_audio = deque(maxlen=int(PREV_AUDIO * rel)) 
        started = False
        n = num_phrases
        response = []

        while (num_phrases == -1 or n > 0):
            cur_data = stream.read(CHUNK)
            slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
            #print slid_win[-1]
            if(sum([x > THRESHOLD for x in slid_win]) > 0):
                if(not started):
                    print ("** Listening...", end='  ',flush=True)
                    started = True
                audio2send.append(cur_data)
            elif (started is True):
                print ("Finished",flush=True)
                num_phrases += 1
                # The limit was reached, finish capture and deliver.
                filename = self.save_speech(list(prev_audio) + audio2send, p)
                text, confidence = self.transcribe(filename)
                
                if text=='' and confidence=='':
                    print("語音辨識失敗")
                else:
                    print ("** Text:", text, end='  ')
                    print ("Confidence:", confidence)
                    
                os.remove(filename)
            else:
                prev_audio.append(cur_data)

        print ("* Done recording")
        stream.close()
        p.terminate()

        return text

    def save_speech(self,data, p):
        """ Saves mic data to temporary WAV file. Returns filename of saved 
            file """

        filename = 'output_'+str(int(time.time()))
        # writes data to WAV file
        #print('type',type(data))
        data = b''.join(data)
        wf = wave.open(filename + '.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)  # TODO make this value a function parameter?
        wf.writeframes(data)
        wf.close()
        return filename + '.wav'

def callLUIS(value):
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': '52fea206b3654194a2a9f03808fd0178',
    }

    params = {
        # Query parameter
        'q': 'turn on the left light',
        # Optional request parameters, set to default values
        'timezoneOffset': '0',
        'verbose': 'false',
        'spellCheck': 'false',
        'staging': 'false',
    }
    query = value
    try:
        r = requests.get('https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/ac22bab6-7555-486c-b879-76c6328b2ae7?subscription-key=52fea206b3654194a2a9f03808fd0178&verbose=true&timezoneOffset=0&q=' + query)
        response = r.json()
        intent = response["topScoringIntent"]["intent"]
        entities = response["entities"]
        for entity in entities:
            print(entity["entity"])
        return intent, entities

    except Exception as e:
        # print("[Errno {0}] {1}".format(e.errno, e.strerror))
        return 'None', 'None'


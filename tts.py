import http.client
from xml.etree import ElementTree
import soundfile as sf
import sounddevice as sd
import pyaudio
import time
import wave
import os


class TTS():
    def __init__(self):
        self.p = pyaudio.PyAudio()
        # Note: The way to get api key:
        # Free: https://www.microsoft.com/cognitive-services/en-us/subscriptions?productId=/products/Bing.Speech.Preview
        # Paid: https://portal.azure.com/#create/Microsoft.CognitiveServices/apitype/Bing.Speech/pricingtier/S0
        apiKey = "42d6d94924384bfcb9b35df61025a8db"

        params = ""
        headers = {"Ocp-Apim-Subscription-Key": apiKey}

        #AccessTokenUri = "https://api.cognitive.microsoft.com/sts/v1.0/issueToken";
        AccessTokenHost = "api.cognitive.microsoft.com"
        path = "/sts/v1.0/issueToken"

        # Connect to server to get the Access Token
        # print ("Connect to server to get the Access Token")
        conn = http.client.HTTPSConnection(AccessTokenHost)
        conn.request("POST", path, params, headers)
        response = conn.getresponse()
        # print(response.status, response.reason)

        data = response.read()
        conn.close()
        self.token = data.decode("UTF-8")
        

    def tts(self, textToRead):
        body = ElementTree.Element('speak', version='1.0')
        body.set('{http://www.w3.org/XML/1998/namespace}lang', 'zh-TW')
        voice = ElementTree.SubElement(body, 'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'zh-TW')
        voice.set('{http://www.w3.org/XML/1998/namespace}gender', 'Female')
        voice.set('name', "Microsoft Server Speech Text to Speech Voice (zh-CN, HuihuiRUS)")
        voice.text = textToRead

        headers = {"Content-type": "application/ssml+xml",
                   "X-Microsoft-OutputFormat": "riff-16khz-16bit-mono-pcm",
                   "Authorization": "Bearer " + self.token,
                   "X-Search-AppId": "07D3234E49CE426DAA29772419F436CA",
                   "X-Search-ClientID": "1ECFAE91408841A480F00935DC390960",
                   "User-Agent": "TTSForPython"}

        # Connect to server to synthesize the wave
        conn = http.client.HTTPSConnection("speech.platform.bing.com")
        conn.request("POST", "/synthesize", ElementTree.tostring(body), headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        self.speak(data)
        
    def speak(self, data):
        """ Saves mic data to temporary WAV file. Returns filename of saved 
            file """

        filename = 'output_' + str(int(time.time()))
        # writes data to WAV file
        #data = ''.join(data)
        wf = wave.open(filename + '.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)  # TODO make this value a function parameter?
        wf.writeframes(data)
        wf.close()

        samples, samplerate = sf.read(filename + '.wav')
        sd.play(samples, samplerate)
        sd.wait()
        os.remove(filename + '.wav')

    

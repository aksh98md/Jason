import http.client, urllib.request, urllib.parse, urllib.error, base64
import json
from googletrans import Translator

def face_recog_key():
    return '530455df28d14e78952ac15537dcde99'
    
def web_request(act, path, body, headers):
    try:
        conn = http.client.HTTPSConnection('eastasia.api.cognitive.microsoft.com')
        conn.request(act, path, body, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        data = json.loads(data.decode('utf-8'))
        return data
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
        return None
        
def cv_key():
    return '0e7cc1a2eeb44d508849b8ab232ff00b'
    

def en2ch(x,n=0):
    t = Translator()
    if x == '' or n > 3:
        return "無法識別"
    elif n < 5:
        try:
            y = t.translate(src='en',dest='zh-tw',text=x)
            return y.text
        except:
            return en2ch(x,n+1)

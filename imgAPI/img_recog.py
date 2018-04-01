from imgAPI.utils import *
import cv2
import json
import requests
import time, datetime

def get_img(cam_id=0, save=False):
    cam = cv2.VideoCapture(cam_id)
    ret, frame = cam.read()
    cam.release()
    
    if save:
        st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H:%M:%S')
        cv2.imwrite('photo/'+st+'.jpg', frame)
        return "已將照片存為 photo/{}.jpg".format(st)
    
    _, frame = cv2.imencode('.jpg',frame)
    return frame.tostring()


def face_recog(img=None):
    key = face_recog_key()
    if img == None:
        img = get_img()
    
    #################
    ## detect face ##
    #################
    headers = {
        # Request headers
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': key,
    }

    params = urllib.parse.urlencode({
        # Request parameters
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': '',
    })
    
    data = web_request("POST", "/face/v1.0/detect?%s" % params, img, headers)
    
    if data == None:
        # error occured at web requests
        return '網路出現錯誤'
    elif len(data) == 0:
        # no face detected
        return '沒有偵測到人臉'
    
    ##############
    ## identify ##
    ##############
    faceId = data[0]['faceId']
    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': key,
    }

    params = urllib.parse.urlencode({
    })

    body = {
        "PersonGroupId": '0331',
        "faceIds": [ faceId ],
        "maxNumOfCandidatesReturned": 1,
        "confidenceThreshold": 0.5
    }
    
    data = web_request("POST", "/face/v1.0/identify?%s" % params, json.dumps(body), headers)
    
    if data == None:
        # error occured at web requests
        return '網路出現錯誤'
    elif len(data[0]['candidates']) == 0:
        # no face detected
        return '資料庫中沒有對應的人臉'
    
    # load personal info. data
    pid = data[0]['candidates'][0]['personId']
    p_info = json.load(open('imgAPI/p_info.json'))
    return p_info[pid]
    
def ocr(img=None):
    key = cv_key()
    if img == None:
        img = get_img()
    url = 'https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/ocr'
    headers = {'Ocp-Apim-Subscription-Key': key, 'Content-Type': 'application/octet-stream'}
    params = {'language': 'unk', 'detectOrientation': 'true'}
    
    #url = 'https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/RecognizeText'
    #headers  = {'Ocp-Apim-Subscription-Key': key, 'Content-Type': 'application/octet-stream'}
    #params   = {'handwriting' : False}
    
    r = requests.post(url, headers=headers, params=params, data=img)
    r = r.json()
    line_infos = [region["lines"] for region in r["regions"]]
    words = ''
    for line in line_infos:
        for word_metadata in line:
            for word_info in word_metadata["words"]:
                words += (word_info['text']) + ' '
    return words
    

def img_caption(img=None):
    key = cv_key()
    if img == None:
        img = get_img()
    url = "https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/analyze"
    headers  = {'Ocp-Apim-Subscription-Key': key, 'Content-Type': 'application/octet-stream'}
    params   = {'visualFeatures': 'Description'}
    response = requests.post(url, headers=headers, params=params, data=img)
    a = response.json()
    return en2ch(a['description']['captions'][0]['text'])




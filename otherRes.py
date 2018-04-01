import random

def sayHello():
    greeting_words = ["嗨你好啊", "很高興見到你", "也跟你問聲好", "嗨", "nice to meet you", "歡迎跟我聊聊天", "今天過得如何呢"]
    reply = random.choice(greeting_words)
    return reply


def call(entities):
    if len(entities) != 0:
        for i in entities:
            if i['type'] == "對象":
                return "撥號給"+i['entity']+"中..."
    return "撥號中..."

def sendText(entities):
    context = ''
    target = ''
    if len(entities) != 0:
        for i in entities:
            if i['type'] == "對象":
                target = "給"+i['entity']
            elif i['type'] == "簡訊內容":
                context = "『"+i['entity']+"』"
    return "傳送簡訊"+context+target+"中..."

def insult():
    insulting_words = ["幹你娘", "你在工三小", "你才吃屎", "北七", "f**k you", "唉我不想跟白癡說話", "別太侮辱人喔", "我也是人欸!"]
    reply = random.choice(insulting_words)
    return reply
    
def none_reply():
    return "請您在說一遍..."
    
def fallAlert():
	return "跌倒了阿阿阿阿阿！！！！！"

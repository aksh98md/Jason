import gspread
from oauth2client.service_account import ServiceAccountCredentials

def auth_gss_client(path, scopes):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scopes)
    return gspread.authorize(credentials)


def read_sheet():
    key = '17lMxjJVXHqdCkqE2mkuCQhE_vHZ5GuGgSO4s5rXcuCw'
    auth_json_path = 'PythonUpload.json'
    gss_scopes = ['https://spreadsheets.google.com/feeds']
    gss_client = auth_gss_client(auth_json_path, gss_scopes)
    
    wks = gss_client.open_by_key(key)
    sheet = wks.sheet1
    val = sheet.acell('D2').value
    return "金融卡餘額還有"+str(val)+"元"

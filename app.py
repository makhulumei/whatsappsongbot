import requests
import os
import uuid
import yt_dlp
import tempfile
from ytmusicapi import YTMusic
from flask import Flask, request

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
PHONE_NUMBER_ID = os.environ.get('PHONE_NUMBER_ID')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
YTDL_COOKIE_PATH = os.environ.get('YTDL_COOKIE_PATH')
processed_message_ids = set()

numbers = set()

welcome = "Hello! I'm a WhatsApp Music Bot Developed by Ali Hussnain. Just send me the name of any song, and I’ll fetch it for you instantly. 🎵"

def rename():
    return f"song_{uuid.uuid4().hex[:8]}"

def send_message(sender,message):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization":f"Bearer {ACCESS_TOKEN}",
        "Content-Type":"application/json"
    }
    payload = {
        "messaging_product":"whatsapp",
        "to": sender,
        "type":"text",
        'text': {
            "body":message
        }
    }
    response = requests.post(url=url,headers=headers,json=payload)
    print(f"Welcome message sent to {sender}: {response.status_code} - {response.text}")
@app.route('/', methods=['GET'])
def home():
    return "WhatsApp Webhook is running!", 200

@app.route('/whatsapp-webhook', methods=['GET'])
def      verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print("✅ Webhook verified successfully!")
        return str(challenge), 200
    else:
        print("❌ Webhook verification failed. Invalid token.")
        return "Verification token mismatch", 403

def audio(url,name):
    temp_name = rename()
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir,temp_name)
    ydl_opt = {
        'format':'bestaudio/best',
        'outtmpl': file_path,
        'postprocessors':[{
            'key':'FFmpegExtractAudio',
            'preferredcodec':'mp3',
            'preferredquality':'128',
        }],
        'prefer_ffmpeg':True,
        'quiet': True,
        "cookiefile": YTDL_COOKIE_PATH,
    }
    with yt_dlp.YoutubeDL(ydl_opt) as ydl:
        ydl.download([url])
        filename = f"{file_path}.mp3"
        return filename

def send_song(phone_number, audio_path,song_name,message_id=None):
    upload_url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/media"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    with open(audio_path, 'rb') as f:
        files = {
            'file': (os.path.basename(audio_path), f, 'audio/mpeg'),
            'type': (None, 'audio/mpeg'),
            'messaging_product': (None, 'whatsapp')
        }
        upload_response = requests.post(upload_url, headers=headers, files=files)
        print("🎵 Upload response:", upload_response.status_code, upload_response.text)

        media_id = upload_response.json().get("id")
        if not media_id:
            print("❌ Failed to get media ID")
            return
    send_message(phone_number,song_name)
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "audio",
        "audio": {
            "id": media_id
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print("Audio sent:", response.status_code, response.text)
    os.remove(audio_path)
    # ✅ Clear from memory if sent successfully
    if response.status_code == 200 and message_id in processed_message_ids:
        processed_message_ids.remove(message_id)
        return 'OK',200

@app.route('/whatsapp-webhook', methods=['POST'])
def receive_message():
    if request.is_json:
        data = request.get_json()
        for entry in data.get('entry',[]):
            for change in entry.get('changes',[]):
                value = change.get('value',[])
                if 'messages' in value:
                    for message in value['messages']:
                        message_id = message.get('id')
                        if message_id in processed_message_ids:
                            print(f"⚠️ Skipping duplicate message: {message_id}")
                            continue
                        processed_message_ids.add(message_id)
                        sender = message.get('from')
                        if sender not in numbers:
                            numbers.add(sender)
                            send_message(sender,welcome)
                            return 'ok',200
                        text = message.get('text',{}).get('body')
                        mem_path,song_name = get_song(text)
                        send_message(sender,'Downloading Please wait...')
                        send_song(sender,mem_path,song_name)
    return 'Message received',200

def get_song(text):
    ytmusic = YTMusic()
    search = ytmusic.search(text, filter='songs')

    first_result = search[0]
    print(f"Title name: {first_result['title']}")
    print(f"Video ID: {first_result['videoId']}")
    print(f"URL: https://music.youtube.com/watch?v={first_result['videoId']}")

    url = f"https://music.youtube.com/watch?v={first_result['videoId']}"
    name = first_result['title']
    song_path = audio(url,name)
    return song_path,name


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)

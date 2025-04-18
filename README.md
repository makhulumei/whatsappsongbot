🎵 WhatsApp SongBot
SongBot is a smart WhatsApp bot that lets users request and receive songs in MP3 format directly through chat. It uses the WhatsApp Business Cloud API to interact with users and fetches audio from YouTube Music based on the song title provided by the user.

When a user sends a message with a song name, the bot searches for the track on YouTube Music, downloads the audio, converts it to MP3 using ffmpeg, and sends the file back—all automatically. There’s no need for manual input or file storage, making the process fast, lightweight, and efficient.

This bot is ideal for quick song access without switching apps. Whether you’re sharing music with friends or building a personal on-demand library, SongBot delivers audio seamlessly within WhatsApp.

The project is developed in Python and deployed on Render to run continuously without interruption. It’s designed for personal use, testing, and extending into more advanced media services.

🔧 Features
Accepts song requests via WhatsApp messages

Downloads songs from YouTube Music

Converts audio to MP3

Sends audio files directly in WhatsApp

Runs 24/7 with no local file storage

🛠️ Tech Stack
Python

WhatsApp Business Cloud API

YouTube Music Downloader

ffmpeg

Render (cloud deployment)

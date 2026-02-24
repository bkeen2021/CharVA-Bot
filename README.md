🎭 CharVA Bot

A Discord voice AI bot that lets you talk to customizable AI characters using real-time speech recognition and text-to-speech.

CharVA listens to your voice in a Discord VC, transcribes what you say, generates a character-based AI response, and speaks the reply back in the voice channel.

✨ Features

Real-time voice recording from Discord voice channels

Local speech-to-text transcription (Whisper)

Character-based AI chat responses (OpenAI)

Character-specific text-to-speech voices (ElevenLabs)

Multiple selectable personas

Full voice conversation loop with /talk command

Text echo of transcript + AI response


How It Works

The /talk command runs the full pipeline:

Bot joins your voice channel

Records your speech until 2 seconds of silence

Transcribes audio using Whisper

Sends transcript to OpenAI with selected character persona

Generates AI response

Converts AI response to speech using ElevenLabs

Plays audio reply in the voice channel

Posts transcript + response in the text channel

📦 Requirements

Python 3.10+

FFmpeg installed and added to PATH

Discord Bot Token

OpenAI API Key

ElevenLabs API Key

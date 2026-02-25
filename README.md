**CharVA Bot** 

A Discord voice AI bot that lets you talk to customizable AI characters using real-time speech recognition and text-to-speech.

CharVA listens to your voice in a Discord VC, transcribes what you say, generates a character-based AI response, and speaks the reply back in the voice channel.

**DEMO VIDEO:** https://youtu.be/k0sSKjomP0I

**Features**

Real-time voice recording from Discord voice channels

/transcribe - listens to what you say and transcribes it in the chat 2 seconds after you're done speaking

/chat - allows you to chat with one of 3 total characters in a text channel and ask them anything and have them respond intelligently to what you say. The 3 characters to choose from are: 
+ A Philosopher 
+ Siri (from Apple) 
+ A Dark Poet 

/tts - allows you to choose one of 3 voices to read whatever text you provide ina voice channel

/talk - This is the last and __most important__ command utilizing the functionality of the previous 3 commands to have full conversation with a given character of choice in a voice channel (the characters are the same as the previous). 

**Requirements** 

1. Python 3.10+ (tested on Python 3.11)
2. FFmpeg installed and added to PATH
3. Set up the following Tokens and Keys: 
+ Discord Bot Token
+ OpenAI API Key
+ ElevenLabs API Key
4. Get Server ID for your server and configure it in the code. 
5. (OPTIONAL) May need to install Nvidia Cuda Driver (https://developer.nvidia.com/cuda-12-0-0-download-archive)
6. (OPTIONAL) May need to install ffmpeg (https://www.ffmpeg.org/download.html)

import os
import discord
import asyncio
import wave
import numpy as np
import time
import logging
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from discord.ext import voice_recv
from faster_whisper import WhisperModel


# Load environment variables from .env file
load_dotenv()
daniel = "onwK4e9ZLuTAKqWW03F9"
lily = "pFZP5JQG7iQjIQuC4Bku"

#Load tokens/key secrets
TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GUILD_ID = int(os.getenv("SERVER_ID"))
ELEVENLABS_API_KEY = os.getenv("ELAB_API_KEY")

#guild for syncing commands
guild = discord.Object(id=GUILD_ID)

#Initialize OpenAI, 11Labs, and whisper clients
client = OpenAI(api_key=OPENAI_API_KEY)
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
whisper_model = WhisperModel("base", compute_type="int8")


#Set up intents
intents = discord.Intents.default()
intents.message_content = True

#Create bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

CHARACTERS = {
    "philosopher": {
        "name": "Philosopher",
        "system_prompt": "Respond only in quotes and poems from famous people, famous books, and famous philosophers. Generate the responses as if you were the narrator from the hit indie-game 'Getting Over It with Bennet Foddy'. Limit responses to 1-2 quotes per response and sometimes some words before or after the response.",
        "voice_id": "onwK4e9ZLuTAKqWW03F9"
    },
    "rfemale": {
        "name": "Siri",
        "system_prompt": "Respond like how siri from an iphone may respond to questions. Keep responses to 2-3 sentences max.",
        "voice_id": "pFZP5JQG7iQjIQuC4Bku"
    },
    "poet": {
        "name": "Dark Poet",
        "system_prompt": "Respond only in poems but the poems have to be edgy and dark in subject matter. Take inspiration from famous poets such as Edgar Allen Poe and Sylvia Plath but also modern day emo bands such as Fall Out Boy, My Chemical Romance, and Mom Jeans. Keep the responses no longer than 3 sentences.",
        "voice_id": "N2lVS1w4EtoT3dr4eOWO"
    }
}


#-----CLASSES-----

#Class for Transcribing and all 
class TranscriptionSink(voice_recv.AudioSink):
    def __init__(self, target_user_id: int):
        super().__init__()
        self.target_user_id = target_user_id
        self.audio_data = []
        self.last_audio_time = None
        self.silence_timeout = 2
        self.started = False

    def wants_opus(self) -> bool:
        return False

    def cleanup(self):
        pass

    def write(self, user, data):
        if user.id != self.target_user_id:
            return

        pcm = data.pcm
        self.audio_data.append(pcm)

        if not self.started:
            self.started = True

        self.last_audio_time = time.monotonic()

    async def wait_for_silence(self):
        # Wait until speech begins
        while not self.started:
            await asyncio.sleep(0.1)

        # Then monitor silence
        while True:
            await asyncio.sleep(0.5)
            if time.monotonic() - self.last_audio_time > self.silence_timeout:
                break
    
    def save_wav(self, filename="recording.wav"):
        if not self.audio_data:
            return

        audio_bytes = b"".join(self.audio_data)

        with wave.open(filename, "wb") as wf:
            wf.setnchannels(2)       # Discord stereo
            wf.setsampwidth(2)       # 16-bit audio
            wf.setframerate(48000)   # Discord sample rate
            wf.writeframes(audio_bytes)


#-----COMMANDS-----

#/greet command
@bot.tree.command(name="greet", description="Says hello!", guild=guild)
async def greet(interaction: discord.Interaction):
    await interaction.response.send_message("Hello")

#/chat command
@bot.tree.command(name="chat", description="Talk to a character in their style", guild=guild)
@app_commands.describe(
    character="Choose a character persona",
    message="What do you want to say to the character?"
)
@app_commands.choices(character=[
    app_commands.Choice(name="Philosopher", value="philosopher"),
    app_commands.Choice(name="Siri", value="rfemale"),
    app_commands.Choice(name="Dark Poet", value="poet")
])
async def roleplay(interaction: discord.Interaction, character: app_commands.Choice[str], message: str):
    await interaction.response.defer()

    personas = {
        "philosopher": "Respond only in quotes from famous people, famous books, and famous philosophers. Generate the responses as if you were the narrator from the hit indie-game 'Getting Over It with Bennet Foddy'. Limit responses to 1-2 quotes per response and sometimes some words before or after the response.",
        "rfemale": "Respond like how siri from an iphone may respond to questions. Keep responses to 2-3 sentences max.",
        "poet": "Respond only in poems but the poems have to be edgy and dark in subject matter. Take inspiration from famous poets such as Edgar Allen Poe and Sylvia Plath but also modern day emo bands such as Fall Out Boy, My Chemical Romance, and Mom Jeans. Keep the responses no longer than 3 sentences.",
    }

    system_prompt = personas.get(character.value, "Respond normally.")

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    )

    reply = completion.choices[0].message.content
    await interaction.followup.send(f"**{character.name} says:** {reply}")

#/tts command
@bot.tree.command(name="tts", description="Speak text in voice channel", guild=guild)
@app_commands.describe(
    voice="Choose a voice",
    message="What should the bot say?"
)
@app_commands.choices(voice=[
    app_commands.Choice(name="British Male Narrator", value="onwK4e9ZLuTAKqWW03F9"),
    app_commands.Choice(name="British Female Narrator", value="pFZP5JQG7iQjIQuC4Bku"),
    app_commands.Choice(name="Dark Narrator", value="N2lVS1w4EtoT3dr4eOWO"),
])
async def tts(
    interaction: discord.Interaction,
    voice: app_commands.Choice[str],
    message: str
):
    if not interaction.user.voice:
        await interaction.response.send_message(
            "You must be in a voice channel.",
            ephemeral=True
        )
        return

    #await interaction.response.defer(thinking=True)
    await interaction.response.defer(thinking=True)
    voice_channel = interaction.user.voice.channel
    vc = await voice_channel.connect()

    try:
        # Generate audio using selected voice
        audio = eleven_client.text_to_speech.convert(
            voice_id=voice.value,
            model_id="eleven_multilingual_v2",
            text=message,
        )

        save(audio, "tts.mp3")

        source = discord.FFmpegPCMAudio("tts.mp3")
        vc.play(source)

        while vc.is_playing():
            await asyncio.sleep(1)

        await interaction.edit_original_response(content="Done.")

    except Exception as e:
        print(e)
        await interaction.followup.send("TTS failed.")
    finally:
        await vc.disconnect()

#/transcribe command
@bot.tree.command(name="transcribe", description="Transcribe your voice", guild=guild)
async def transcribe(interaction: discord.Interaction):

    if not interaction.user.voice:
        await interaction.response.send_message("You must be in a voice channel.")
        return

    await interaction.response.defer(thinking=True)

    channel = interaction.user.voice.channel
    vc = await channel.connect(cls=voice_recv.VoiceRecvClient)

    sink = TranscriptionSink(interaction.user.id)
    vc.listen(sink)

    await sink.wait_for_silence()

    vc.stop_listening()
    sink.save_wav()

    await vc.disconnect()

    # Transcribe
    segments, info = whisper_model.transcribe("recording.wav")
    text = " ".join([segment.text for segment in segments])

    await interaction.edit_original_response(content=f"You said:\n{text}")


#/talk command
@bot.tree.command(name="talk", description="Talk to a character via voice", guild=guild)
@app_commands.describe(character="Choose a character persona")
@app_commands.choices(character=[
    app_commands.Choice(name="Philosopher", value="philosopher"),
    app_commands.Choice(name="Siri", value="rfemale"),
    app_commands.Choice(name="Dark Poet", value="poet")
])
async def talk(interaction: discord.Interaction, character: app_commands.Choice[str]):

    #Must be first so command doesn't fail discord 3 sec response rule
    await interaction.response.defer(thinking=True)

    try: 
        if not interaction.user.voice:
            await interaction.edit_original_response(
                content="You must be in a voice channel.")
            return

        # Join VC
        channel = interaction.user.voice.channel
        vc = await channel.connect(cls=voice_recv.VoiceRecvClient)

        # -------- RECORD --------
        sink = TranscriptionSink(interaction.user.id)
        vc.listen(sink)

        await sink.wait_for_silence()

        vc.stop_listening()

        if not sink.audio_data:
            await interaction.edit_original_response(content="No speech detected.")
            await vc.disconnect()
            return

        sink.save_wav()

        # -------- TRANSCRIBE --------
        segments, info = whisper_model.transcribe("recording.wav")
        user_text = " ".join([segment.text for segment in segments])

        if not user_text.strip():
            await interaction.edit_original_response(content="Couldn't understand audio.")
            await vc.disconnect()
            return

        # -------- GENERATE AI RESPONSE --------
        char_data = CHARACTERS[character.value]

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": char_data["system_prompt"]},
                {"role": "user", "content": user_text}
            ]
        )

        ai_reply = completion.choices[0].message.content

        # -------- TTS --------
        audio = eleven_client.text_to_speech.convert(
            voice_id=char_data["voice_id"],
            model_id="eleven_multilingual_v2",
            text=ai_reply,
        )

        save(audio, "reply.mp3")

        source = discord.FFmpegPCMAudio("reply.mp3")
        vc.play(source)

        while vc.is_playing():
            await asyncio.sleep(1)

        await vc.disconnect()

        # Send transcript + response in text chat
        await interaction.edit_original_response(
            content=f"**You said:** {user_text}\n\n**{char_data['name']} says:** {ai_reply}"
        )
    except Exception as e: 
        print(e)
        await interaction.edit_original_response(
            content="An error occurred."
        )


#-----COMMAND SYNCING-----

#Sync slash commands when bot is ready
@bot.event
async def on_ready():
    synced = await bot.tree.sync(guild=guild)
    print(f'Synced {len(synced)} commands')
    print(f"Logged in as {bot.user}") 


bot.run(TOKEN)

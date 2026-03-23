import os
from flask import Flask, request, Response
import twilio
from twilio.twiml.voice_response import VoiceResponse
import asyncio
import websockets
import requests

app = Flask(__name__)

# Twilio Call Handler
@app.route('/voice', methods=['POST'])
def voice():
    response = VoiceResponse()
    response.say('You are now connected to the audio processing service.')
    response.redirect('/tts')  # Redirect to TTS endpoint
    return str(response)

# Real-time Audio Streaming WebSocket
async def audio_stream(websocket, path):
    while True:
        audio_data = await websocket.recv()  # Receive audio data from Twilio
        response = requests.post('https://api.elevenlabs.io/synthesize', json={'model': 'eleven_turbo_v2_5', 'audio': audio_data})
        synthesized_audio = response.content  # Get the synthesized audio
        await websocket.send(synthesized_audio)  # Send back synthesized audio to Twilio

# TTS Endpoint
@app.route('/tts', methods=['POST'])
def tts():
    text = request.form['text']  # Get text input from Twilio
    response = requests.post('https://api.elevenlabs.io/synthesize', json={'model': 'eleven_turbo_v2_5', 'text': text})
    synthesized_audio = response.content
    return Response(synthesized_audio, mimetype='audio/wav')

# Start WebSocket server
async def start_server():
    async with websockets.serve(audio_stream, 'localhost', 6789):
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
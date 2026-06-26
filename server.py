import asyncio
import audioop
import base64
import json
import os
from datetime import datetime

import pyaudio
import uvicorn
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import Response
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions, SpeakOptions
from twilio.twiml.voice_response import VoiceResponse, Connect

import config
from llm import get_response
from scenarios import get_scenario

app = FastAPI()

LIVE_LISTEN = True

def create_audio_player():
    if not LIVE_LISTEN:
        return None
    try:
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=8000,
            output=True,
            frames_per_buffer=640,
        )
        return stream
    except Exception as e:
        print(f"Could not open audio output: {e}")
        return None

calls_dir = "calls"
os.makedirs(calls_dir, exist_ok=True)

active_calls: dict[str, dict] = {}


@app.get("/")
async def health():
    return {"status": "running"}


@app.post("/twiml/{scenario_name}")
async def twiml(scenario_name: str):
    response = VoiceResponse()
    connect = Connect()
    stream = connect.stream(url=f"wss://{config.NGROK_URL.replace('https://', '').replace('http://', '')}/media-stream")
    stream.parameter(name="scenario", value=scenario_name)
    response.append(connect)
    return Response(content=str(response), media_type="application/xml")


@app.post("/recording-status")
async def recording_status(request: Request):
    form = await request.form()
    recording_url = form.get("RecordingUrl")
    call_sid = form.get("CallSid")
    if recording_url and call_sid:
        print(f"Recording available for {call_sid}: {recording_url}")
        rec_path = os.path.join(calls_dir, f"{call_sid}_recording_url.txt")
        with open(rec_path, "w") as f:
            f.write(f"{recording_url}.mp3")
    return {"status": "ok"}


@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected")

    stream_sid = None
    scenario_name = None
    scenario = None
    conversation_history = []
    transcript_lines = []
    agent_buffer = ""
    last_agent_speech_time = None
    silence_threshold = 1.5
    is_bot_speaking = False
    call_start_time = datetime.now()
    audio_player = create_audio_player()

    deepgram_client = DeepgramClient(config.DEEPGRAM_API_KEY)
    dg_connection = deepgram_client.listen.asynclive.v("1")

    async def on_transcript(self, result, **kwargs):
        nonlocal agent_buffer, last_agent_speech_time
        transcript = result.channel.alternatives[0].transcript
        if not transcript.strip():
            return
        is_final = result.is_final
        if is_final:
            agent_buffer += " " + transcript
            last_agent_speech_time = asyncio.get_event_loop().time()
            print(f"  [Agent]: {transcript}")

    dg_connection.on(LiveTranscriptionEvents.Transcript, on_transcript)

    dg_options = LiveOptions(
        model="nova-2",
        language="en-US",
        encoding="mulaw",
        sample_rate=8000,
        channels=1,
        interim_results=True,
        utterance_end_ms=1000,
        vad_events=True,
    )

    await dg_connection.start(dg_options)

    async def process_agent_response():
        nonlocal agent_buffer, last_agent_speech_time, is_bot_speaking, conversation_history

        while True:
            await asyncio.sleep(0.3)

            if is_bot_speaking or not agent_buffer.strip():
                continue

            now = asyncio.get_event_loop().time()
            if last_agent_speech_time and (now - last_agent_speech_time) >= silence_threshold:
                agent_text = agent_buffer.strip()
                agent_buffer = ""
                last_agent_speech_time = None

                if not agent_text:
                    continue

                transcript_lines.append(f"Agent: {agent_text}")
                conversation_history.append({"role": "user", "content": agent_text})

                print(f"  [Generating response...]")
                is_bot_speaking = True
                try:
                    bot_reply = get_response(scenario["system_prompt"], conversation_history)
                    print(f"  [Bot]: {bot_reply}")
                    conversation_history.append({"role": "assistant", "content": bot_reply})
                    transcript_lines.append(f"Bot: {bot_reply}")

                    await send_tts_audio(bot_reply, websocket, stream_sid)
                except Exception as e:
                    print(f"Error generating response: {e}")
                finally:
                    is_bot_speaking = False

    async def send_tts_audio(text: str, ws: WebSocket, sid: str):
        try:
            dg_tts = DeepgramClient(config.DEEPGRAM_API_KEY)
            options = SpeakOptions(
                model="aura-asteria-en",
                encoding="mulaw",
                sample_rate=8000,
                container="none",
            )

            response = await asyncio.to_thread(
                dg_tts.speak.rest.v("1").stream_raw,
                {"text": text},
                options,
            )

            response.read()
            audio_data = response.content

            chunk_size = 640
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i : i + chunk_size]
                payload = base64.b64encode(chunk).decode("utf-8")
                media_message = {
                    "event": "media",
                    "streamSid": sid,
                    "media": {"payload": payload},
                }
                await ws.send_json(media_message)
                if audio_player:
                    pcm = audioop.ulaw2lin(chunk, 2)
                    audio_player.write(pcm)
                await asyncio.sleep(0.04)

            mark_message = {
                "event": "mark",
                "streamSid": sid,
                "mark": {"name": "tts_done"},
            }
            await ws.send_json(mark_message)

        except Exception as e:
            print(f"TTS error: {e}")

    response_task = asyncio.create_task(process_agent_response())

    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            event = data.get("event")

            if event == "start":
                start_data = data.get("start", {})
                stream_sid = start_data.get("streamSid")
                custom_params = start_data.get("customParameters", {})
                scenario_name = custom_params.get("scenario", "simple_appointment")
                scenario = get_scenario(scenario_name)
                print(f"Call started — scenario: {scenario_name}, streamSid: {stream_sid}")

            elif event == "media":
                media = data.get("media", {})
                payload = media.get("payload")
                if payload:
                    audio_bytes = base64.b64decode(payload)
                    await dg_connection.send(audio_bytes)
                    if audio_player:
                        pcm = audioop.ulaw2lin(audio_bytes, 2)
                        audio_player.write(pcm)

            elif event == "stop":
                print("Call ended")
                break

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        response_task.cancel()
        await dg_connection.finish()
        if audio_player:
            audio_player.stop_stream()
            audio_player.close()

        if transcript_lines:
            timestamp = call_start_time.strftime("%Y%m%d_%H%M%S")
            filename = f"{scenario_name}_{timestamp}"

            transcript_path = os.path.join(calls_dir, f"{filename}.txt")
            with open(transcript_path, "w") as f:
                f.write(f"Scenario: {scenario_name}\n")
                f.write(f"Date: {call_start_time.isoformat()}\n")
                f.write(f"{'=' * 50}\n\n")
                f.write("\n".join(transcript_lines))
            print(f"Transcript saved: {transcript_path}")


def start_server():
    uvicorn.run(app, host="0.0.0.0", port=config.SERVER_PORT)


if __name__ == "__main__":
    start_server()

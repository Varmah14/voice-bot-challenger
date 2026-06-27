"""Test each component of the pipeline locally without making a call."""

import audioop
import os
import sys
from dotenv import load_dotenv

load_dotenv()


def test_claude():
    print("=== Testing Claude LLM ===")
    from llm import get_response
    from scenarios import get_scenario

    scenario = get_scenario("simple_appointment")
    history = [{"role": "user", "content": "Thank you for calling Pivot Point Orthopedics. How can I help you?"}]
    reply = get_response(scenario["system_prompt"], history)
    print(f"  Agent said: 'Thank you for calling Pivot Point Orthopedics. How can I help you?'")
    print(f"  Bot reply: '{reply}'")
    print("  ✓ Claude working!\n")
    return True


def test_deepgram_tts():
    print("=== Testing Deepgram TTS ===")
    from deepgram import DeepgramClient, SpeakOptions

    dg = DeepgramClient()
    options = SpeakOptions(model="aura-asteria-en", encoding="mulaw", sample_rate=8000, container="none")
    resp = dg.speak.rest.v("1").stream_raw(
        {"text": "Hi, I'd like to schedule a routine checkup appointment for next week please."},
        options,
    )
    resp.read()
    audio_data = resp.content

    if len(audio_data) < 200:
        print(f"  ✗ TTS error: {audio_data}")
        return False

    print(f"  Audio size: {len(audio_data)} bytes")
    print("  ✓ Deepgram TTS working!\n")
    return audio_data


def test_deepgram_stt():
    print("=== Testing Deepgram STT ===")
    from deepgram import DeepgramClient, PrerecordedOptions

    dg = DeepgramClient()

    # Generate some TTS audio first, then transcribe it back
    from deepgram import SpeakOptions
    tts_options = SpeakOptions(model="aura-asteria-en", encoding="mulaw", sample_rate=8000, container="none")
    tts_resp = dg.speak.rest.v("1").stream_raw(
        {"text": "Hello, I would like to schedule an appointment."},
        tts_options,
    )
    tts_resp.read()
    audio_data = tts_resp.content

    if len(audio_data) < 200:
        print(f"  ✗ Could not generate test audio")
        return False

    # Transcribe the audio
    options = PrerecordedOptions(model="nova-2", language="en-US", encoding="mulaw", sample_rate=8000)
    source = {"buffer": audio_data, "mimetype": "audio/mulaw"}
    response = dg.listen.rest.v("1").transcribe_file(source, options)
    transcript = response.results.channels[0].alternatives[0].transcript
    print(f"  Transcribed: '{transcript}'")
    print("  ✓ Deepgram STT working!\n")
    return True


def test_audio_playback(audio_data=None):
    print("=== Testing Local Audio Playback ===")
    try:
        import pyaudio

        if audio_data is None:
            from deepgram import DeepgramClient, SpeakOptions
            dg = DeepgramClient()
            options = SpeakOptions(model="aura-asteria-en", encoding="mulaw", sample_rate=8000, container="none")
            resp = dg.speak.rest.v("1").stream_raw(
                {"text": "Hello! This is a test of the audio playback system. Can you hear me?"},
                options,
            )
            resp.read()
            audio_data = resp.content

        pcm_data = audioop.ulaw2lin(audio_data, 2)

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=8000, output=True)
        print("  Playing audio through speakers...")
        stream.write(pcm_data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("  ✓ Audio playback working!\n")
        return True
    except Exception as e:
        print(f"  ✗ Audio playback error: {e}\n")
        return False


def test_full_pipeline():
    print("=== Full Pipeline Test (no phone call) ===")
    from llm import get_response
    from scenarios import get_scenario
    from deepgram import DeepgramClient, SpeakOptions
    import pyaudio

    scenario = get_scenario("simple_appointment")
    dg = DeepgramClient()

    agent_lines = [
        "Thank you for calling Pivot Point Orthopedics. How can I help you today?",
        "Sure, I can help you schedule an appointment. What day works best for you?",
        "We have a 9 AM slot available on Tuesday. Would that work?",
    ]

    conversation_history = []
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=8000, output=True)

    for agent_line in agent_lines:
        print(f"\n  Agent: {agent_line}")
        conversation_history.append({"role": "user", "content": agent_line})

        # Play agent line
        options = SpeakOptions(model="aura-asteria-en", encoding="mulaw", sample_rate=8000, container="none")
        resp = dg.speak.rest.v("1").stream_raw({"text": agent_line}, options)
        resp.read()
        if len(resp.content) > 200:
            pcm = audioop.ulaw2lin(resp.content, 2)
            stream.write(pcm)

        # Get bot response
        bot_reply = get_response(scenario["system_prompt"], conversation_history)
        print(f"  Bot:   {bot_reply}")
        conversation_history.append({"role": "assistant", "content": bot_reply})

        # Play bot reply
        resp = dg.speak.rest.v("1").stream_raw({"text": bot_reply}, options)
        resp.read()
        if len(resp.content) > 200:
            pcm = audioop.ulaw2lin(resp.content, 2)
            stream.write(pcm)

    stream.stop_stream()
    stream.close()
    p.terminate()
    print("\n  ✓ Full pipeline working!\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "claude":
            test_claude()
        elif test_name == "tts":
            test_deepgram_tts()
        elif test_name == "stt":
            test_deepgram_stt()
        elif test_name == "audio":
            test_audio_playback()
        elif test_name == "full":
            test_full_pipeline()
        else:
            print(f"Unknown test: {test_name}")
            print("Options: claude, tts, stt, audio, full")
    else:
        print("Running all component tests...\n")
        test_claude()
        audio_data = test_deepgram_tts()
        test_deepgram_stt()
        if audio_data:
            test_audio_playback(audio_data)
        print("=" * 40)
        print("Run 'python test_local.py full' to test the full conversation pipeline with audio")

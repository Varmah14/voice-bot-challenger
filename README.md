# PGAI Voice Bot Challenger

An automated voice bot that calls the Pretty Good AI test line, simulates realistic patient scenarios, and identifies bugs in the AI agent's responses.

## Architecture

The system uses a real-time voice pipeline: Twilio initiates an outbound call and streams audio via WebSocket to a local FastAPI server (exposed via ngrok). Incoming agent audio is transcribed in real-time by Deepgram's Nova-2 STT model. The transcript is fed to Claude (Sonnet), which generates contextual patient responses based on predefined scenarios. Deepgram's Aura TTS converts the response back to audio, which streams through Twilio to the agent. After all calls complete, Claude analyzes the full transcripts to identify bugs, quality issues, and edge-case failures in the agent's behavior.

This architecture was chosen to keep latency manageable while maintaining high conversation quality. Deepgram handles both STT and TTS to minimize the number of services and reduce round-trip overhead. Claude was selected for the LLM layer because of its strong instruction-following for scenario roleplay and its analytical capability for post-call bug detection.

## Setup

### Prerequisites
- Python 3.10+
- ngrok (`brew install ngrok`)
- ffmpeg (`brew install ffmpeg`)
- Twilio account with a phone number
- Deepgram API key (free $200 credit at deepgram.com)
- Anthropic API key

### Install

```bash
git clone <repo-url>
cd voice-bot-challenger
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

## Running

### 1. Start ngrok
```bash
ngrok http 8000
```
Copy the https URL and set it as `NGROK_URL` in your `.env` file.

### 2. Start the server
```bash
python main.py server
```

### 3. Make calls

```bash
# List available scenarios
python main.py list

# Run a single scenario
python main.py call simple_appointment

# Run all scenarios (with 30s delay between calls)
python main.py call-all

# Run all with custom delay
python main.py call-all --delay 45
```

### 4. Download recordings
```bash
python download_recordings.py
```

### 5. Generate bug report
```bash
python main.py analyze
```

## Scenarios

| Scenario | Description |
|----------|-------------|
| simple_appointment | Schedule a routine checkup |
| reschedule_appointment | Reschedule an existing appointment |
| cancel_appointment | Cancel an appointment |
| medication_refill | Request a medication refill |
| office_hours_inquiry | Ask about hours and location |
| insurance_question | Check insurance acceptance |
| urgent_symptoms | Call about concerning symptoms |
| weekend_appointment | Try to book a weekend slot (edge case) |
| multiple_requests | Multiple needs in one call |
| confused_patient | Vague, unclear patient (edge case) |
| spanish_speaker | Starts in Spanish (edge case) |
| interruption_test | Impatient, interrupting patient |

## Output

- `calls/*.txt` — Transcripts for each call
- `calls/recordings/*.mp3` — Audio recordings
- `calls/bug_report.md` — Automated bug analysis

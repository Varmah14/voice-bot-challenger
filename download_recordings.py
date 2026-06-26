import os
import requests
from twilio.rest import Client
import config


def download_all_recordings():
    client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
    recordings = client.recordings.list(limit=20)

    os.makedirs("calls/recordings", exist_ok=True)

    for rec in recordings:
        call_sid = rec.call_sid
        mp3_url = f"https://api.twilio.com{rec.uri.replace('.json', '.mp3')}"

        filepath = os.path.join("calls", "recordings", f"{call_sid}.mp3")
        if os.path.exists(filepath):
            print(f"Already downloaded: {filepath}")
            continue

        print(f"Downloading {call_sid}...")
        resp = requests.get(
            mp3_url,
            auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN),
        )
        with open(filepath, "wb") as f:
            f.write(resp.content)
        print(f"  Saved: {filepath}")

    print("\nDone! Recordings saved to calls/recordings/")


if __name__ == "__main__":
    download_all_recordings()

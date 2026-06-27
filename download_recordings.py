import os
import requests
from twilio.rest import Client
import config


def download_all_recordings():
    client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
    recordings = client.recordings.list(limit=20)

    for rec in recordings:
        call_sid = rec.call_sid

        # Determine which phone number made the call
        try:
            call = client.calls(call_sid).fetch()
            from_number = call.from_formatted or call.from_
        except Exception:
            from_number = "unknown"

        # Map phone number to patient folder
        if from_number in (config.TWILIO_PHONE_NUMBER_1, getattr(config, 'TWILIO_PHONE_NUMBER_1', '')):
            patient = "sarah_johnson"
        elif from_number in (config.TWILIO_PHONE_NUMBER_2, getattr(config, 'TWILIO_PHONE_NUMBER_2', '')):
            patient = "mike_chen"
        else:
            patient = "unknown"

        rec_dir = os.path.join("calls", patient, "recordings")
        os.makedirs(rec_dir, exist_ok=True)

        mp3_url = f"https://api.twilio.com{rec.uri.replace('.json', '.mp3')}"
        filepath = os.path.join(rec_dir, f"{call_sid}.mp3")

        if os.path.exists(filepath):
            print(f"Already downloaded: {filepath}")
            continue

        print(f"Downloading {call_sid} -> {patient}...")
        resp = requests.get(
            mp3_url,
            auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN),
        )
        with open(filepath, "wb") as f:
            f.write(resp.content)
        print(f"  Saved: {filepath}")

    print("\nDone!")


if __name__ == "__main__":
    download_all_recordings()

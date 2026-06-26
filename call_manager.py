from twilio.rest import Client
import config


def make_call(scenario_name: str) -> str:
    client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
    ngrok_url = config.NGROK_URL.rstrip("/")

    call = client.calls.create(
        to=config.TARGET_PHONE_NUMBER,
        from_=config.TWILIO_PHONE_NUMBER,
        url=f"{ngrok_url}/twiml/{scenario_name}",
        record=True,
        recording_channels="dual",
        recording_status_callback=f"{ngrok_url}/recording-status",
    )
    print(f"Call initiated: {call.sid}")
    return call.sid

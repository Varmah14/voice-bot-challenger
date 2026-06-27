from twilio.rest import Client
import config
from scenarios import get_scenario, get_patient


def make_call(scenario_name: str) -> str:
    scenario = get_scenario(scenario_name)
    patient = get_patient(scenario["patient"])
    from_number = config.get_phone_number(patient["phone_env"])

    client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
    ngrok_url = config.NGROK_URL.rstrip("/")

    call = client.calls.create(
        to=config.TARGET_PHONE_NUMBER,
        from_=from_number,
        url=f"{ngrok_url}/twiml/{scenario_name}",
        record=True,
        recording_channels="dual",
        recording_status_callback=f"{ngrok_url}/recording-status",
    )
    print(f"Call initiated: {call.sid} (patient: {patient['name']}, from: {from_number})")
    return call.sid

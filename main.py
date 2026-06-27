import argparse
import time

from scenarios import list_scenarios, SCENARIOS, PATIENTS
from call_manager import make_call
from server import start_server
from analyzer import analyze_all, analyze_patient


def run_single_call(scenario_name: str):
    print(f"\nStarting call: {scenario_name}")
    call_sid = make_call(scenario_name)
    print(f"Call SID: {call_sid}")
    print("Waiting for call to complete...")


def run_patient_calls(patient: str, delay: int = 30):
    scenarios = list_scenarios(patient)
    if not scenarios:
        print(f"No scenarios found for patient: {patient}")
        return

    print(f"Running {len(scenarios)} scenarios for {patient} with {delay}s delay\n")

    for i, name in enumerate(scenarios, 1):
        print(f"\n{'='*50}")
        print(f"Call {i}/{len(scenarios)}: {name}")
        print(f"{'='*50}")
        run_single_call(name)
        if i < len(scenarios):
            print(f"Waiting {delay}s before next call...")
            time.sleep(delay)

    print(f"\n{'='*50}")
    print(f"All calls for {patient} complete!")


def run_all_calls(delay: int = 30):
    for patient in PATIENTS:
        run_patient_calls(patient, delay)


def main():
    parser = argparse.ArgumentParser(description="PGAI Voice Bot Challenger")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("server", help="Start the FastAPI server")

    call_parser = subparsers.add_parser("call", help="Make a single call")
    call_parser.add_argument("scenario", choices=list_scenarios(), help="Scenario to run")

    patient_parser = subparsers.add_parser("call-patient", help="Run all scenarios for a patient")
    patient_parser.add_argument("patient", choices=list(PATIENTS.keys()), help="Patient name")
    patient_parser.add_argument("--delay", type=int, default=30, help="Delay between calls")

    all_parser = subparsers.add_parser("call-all", help="Run all scenarios for all patients")
    all_parser.add_argument("--delay", type=int, default=30, help="Delay between calls")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze transcripts")
    analyze_parser.add_argument("patient", nargs="?", help="Patient to analyze (default: all)")

    list_parser = subparsers.add_parser("list", help="List available scenarios")
    list_parser.add_argument("patient", nargs="?", help="Filter by patient")

    args = parser.parse_args()

    if args.command == "server":
        start_server()
    elif args.command == "call":
        run_single_call(args.scenario)
    elif args.command == "call-patient":
        run_patient_calls(args.patient, args.delay)
    elif args.command == "call-all":
        run_all_calls(args.delay)
    elif args.command == "analyze":
        if args.patient:
            analyze_patient(args.patient)
        else:
            analyze_all()
    elif args.command == "list":
        if args.patient:
            print(f"\nScenarios for {args.patient}:\n")
            for s in SCENARIOS:
                if s["patient"] == args.patient:
                    print(f"  {s['name']:30s} — {s['description']}")
        else:
            for patient_key, patient in PATIENTS.items():
                print(f"\n{patient['name']} (Phone: {patient['phone_env']}):")
                for s in SCENARIOS:
                    if s["patient"] == patient_key:
                        print(f"  {s['name']:30s} — {s['description']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

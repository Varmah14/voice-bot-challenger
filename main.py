import argparse
import time
import threading

from scenarios import list_scenarios, SCENARIOS
from call_manager import make_call
from server import start_server
from analyzer import analyze_transcripts


def run_single_call(scenario_name: str):
    print(f"\nStarting call: {scenario_name}")
    call_sid = make_call(scenario_name)
    print(f"Call SID: {call_sid}")
    print("Waiting for call to complete...")


def run_all_calls(delay: int = 30):
    scenarios = list_scenarios()
    print(f"Running {len(scenarios)} scenarios with {delay}s delay between calls\n")

    for i, name in enumerate(scenarios, 1):
        print(f"\n{'='*50}")
        print(f"Call {i}/{len(scenarios)}: {name}")
        print(f"{'='*50}")
        run_single_call(name)
        if i < len(scenarios):
            print(f"Waiting {delay}s before next call...")
            time.sleep(delay)

    print(f"\n{'='*50}")
    print("All calls complete!")
    print("Run 'python main.py analyze' to generate bug report.")


def main():
    parser = argparse.ArgumentParser(description="PGAI Voice Bot Challenger")
    subparsers = parser.add_subparsers(dest="command")

    server_parser = subparsers.add_parser("server", help="Start the FastAPI server")

    call_parser = subparsers.add_parser("call", help="Make a single call")
    call_parser.add_argument("scenario", choices=list_scenarios(), help="Scenario to run")

    all_parser = subparsers.add_parser("call-all", help="Run all scenarios")
    all_parser.add_argument("--delay", type=int, default=30, help="Delay between calls in seconds")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze transcripts and generate bug report")

    list_parser = subparsers.add_parser("list", help="List available scenarios")

    args = parser.parse_args()

    if args.command == "server":
        start_server()
    elif args.command == "call":
        run_single_call(args.scenario)
    elif args.command == "call-all":
        run_all_calls(args.delay)
    elif args.command == "analyze":
        analyze_transcripts()
    elif args.command == "list":
        print("Available scenarios:\n")
        for s in SCENARIOS:
            print(f"  {s['name']:25s} — {s['description']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

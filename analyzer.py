import os
import glob
import anthropic
import config


client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

ANALYSIS_PROMPT = """You are a QA analyst reviewing transcripts of phone calls between an AI patient (Bot) and an AI medical office agent (Agent).

Analyze each transcript for bugs and quality issues. Look for:
1. Incorrect information (wrong hours, accepting impossible appointments, etc.)
2. Failure to verify patient identity properly
3. Inappropriate responses to medical concerns
4. Broken conversation flow (non-sequiturs, ignoring questions)
5. Missing follow-up questions that a real receptionist would ask
6. Handling of edge cases (weekends, after hours, unclear requests)
7. Any responses that could be harmful or misleading to a real patient

For each issue found, provide:
- Bug description
- Severity (High/Medium/Low)
- Which transcript and approximate location
- What happened vs what should have happened

Format as a markdown bug report."""


def analyze_transcripts():
    transcript_files = sorted(glob.glob(os.path.join("calls", "*.txt")))
    transcript_files = [f for f in transcript_files if not f.endswith("_recording_url.txt")]

    if not transcript_files:
        print("No transcripts found in calls/ directory.")
        return

    all_transcripts = ""
    for i, filepath in enumerate(transcript_files, 1):
        with open(filepath) as f:
            content = f.read()
        filename = os.path.basename(filepath)
        all_transcripts += f"\n\n--- Transcript {i}: {filename} ---\n{content}"

    print(f"Analyzing {len(transcript_files)} transcripts...")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=ANALYSIS_PROMPT,
        messages=[{"role": "user", "content": all_transcripts}],
    )

    report = response.content[0].text

    report_path = os.path.join("calls", "bug_report.md")
    with open(report_path, "w") as f:
        f.write("# Bug Report — PGAI Voice Agent\n\n")
        f.write(report)

    print(f"\nBug report saved: {report_path}")
    print("\n" + report)


if __name__ == "__main__":
    analyze_transcripts()

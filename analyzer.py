import os
import glob
import anthropic
import config
from scenarios import PATIENTS


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


def analyze_patient(patient_key: str):
    transcript_dir = os.path.join("calls", patient_key, "transcripts")
    transcript_files = sorted(glob.glob(os.path.join(transcript_dir, "*.txt")))

    if not transcript_files:
        print(f"No transcripts found for {patient_key} in {transcript_dir}")
        return

    all_transcripts = ""
    for i, filepath in enumerate(transcript_files, 1):
        with open(filepath) as f:
            content = f.read()
        filename = os.path.basename(filepath)
        all_transcripts += f"\n\n--- Transcript {i}: {filename} ---\n{content}"

    print(f"Analyzing {len(transcript_files)} transcripts for {patient_key}...")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=ANALYSIS_PROMPT,
        messages=[{"role": "user", "content": all_transcripts}],
    )

    report = response.content[0].text

    analysis_dir = os.path.join("calls", patient_key, "analysis")
    os.makedirs(analysis_dir, exist_ok=True)

    report_path = os.path.join(analysis_dir, "bug_report.md")
    with open(report_path, "w") as f:
        f.write(f"# Bug Report — {patient_key}\n\n")
        f.write(report)

    print(f"Bug report saved: {report_path}")
    print("\n" + report)


def analyze_all():
    for patient_key in PATIENTS:
        analyze_patient(patient_key)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyze_patient(sys.argv[1])
    else:
        analyze_all()

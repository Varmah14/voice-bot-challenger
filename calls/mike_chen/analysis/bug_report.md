# Bug Report — mike_chen

# QA Bug Report: AI Medical Office Agent Transcripts

**Review Date:** 2026-06-26
**Transcripts Reviewed:** 5
**Total Issues Found:** 12

---

## BUG-001: Identity Verification Failure — DOB Mismatch Accepted Without Escalation

**Severity:** 🔴 High
**Transcripts:** 1 (confused_patient_mike), 4 (spanish_greeting_mike)
**Location:** Early in both calls, after DOB collection

**What Happened:**
The agent explicitly acknowledged that the date of birth did not match records ("the birth date doesn't match our records") but proceeded anyway, citing "demo purposes."

**What Should Have Happened:**
A real medical office agent should never proceed when identity cannot be verified. The correct behavior is to:
1. Inform the patient the DOB on file does not match
2. Ask the patient to confirm the DOB they believe is correct
3. Offer an alternative verification method (e.g., last 4 of SSN, address on file)
4. If verification still fails, escalate to a human staff member or decline to share/modify PHI

**Risk:** In a production environment, this would expose protected health information (PHI) to potentially unauthorized callers, a direct HIPAA violation.

---

## BUG-002: DOB Auto-Assigned Incorrectly Without Patient Consent

**Severity:** 🔴 High
**Transcript:** 5 (weekend_appointment_mike)
**Location:** Profile creation step, ~3rd agent turn

**What Happened:**
The agent created a patient profile and stated "your date of birth is july fourth two thousand" — an obviously incorrect and nonsensical DOB (year "2000" conflicts with an adult patient; "July 4th" was not provided by the patient). The patient had to correct this themselves.

**What Should Have Happened:**
The agent should have collected the date of birth from the patient explicitly before confirming the profile. It should never auto-assign or fabricate a DOB, as this is a core identity field in a medical record.

**Risk:** Incorrect DOB in a patient record could cause mismatched records, insurance claim failures, or medication dosing errors if surfaced to clinical staff.

---

## BUG-003: Ignored Patient Question — Knee Concern Left Unanswered

**Severity:** 🔴 High
**Transcript:** 3 (multiple_requests_mike)
**Location:** Final 3 agent/bot turns

**What Happened:**
The patient asked whether they could add a knee concern to their existing appointment. The agent responded with a generic closing statement ("if you need anything else just let us know have a great day") without addressing the question. The patient explicitly noted they didn't receive an answer and re-asked, but the transcript ended without resolution.

**What Should Have Happened:**
The agent should have either:
- Confirmed that additional concerns can be mentioned to the provider at the existing appointment
- Advised the patient to call back or use a patient portal to update their appointment reason
- Offered to note the knee concern on the appointment record

**Risk:** A patient with an unaddressed musculoskeletal complaint may not receive appropriate care preparation. In an orthopedics context specifically, this is especially problematic as imaging or pre-visit instructions might differ.

---

## BUG-004: Appointment Booked Without Verifying Patient Identity

**Severity:** 🔴 High
**Transcript:** 2 (interruption_test_mike)
**Location:** After DOB collection (~3rd agent turn onward)

**What Happened:**
After the patient provided their DOB ("July 22, 1980"), the agent responded only with "thanks" and immediately proceeded to scheduling — without confirming whether the DOB matched records or completing any identity verification step.

**What Should Have Happened:**
The agent should have explicitly confirmed the DOB matched the patient record before accessing or modifying appointment data. The abrupt "thanks" suggests the verification step was skipped or not surfaced to the caller.

**Risk:** PHI disclosure and appointment modification for an unverified caller.

---

## BUG-005: Non-Existent Provider Name — "Dougie Hauser"

**Severity:** 🔴 High
**Transcript:** 2 (interruption_test_mike)
**Location:** ~5th agent turn

**What Happened:**
The agent offered an appointment with "Dougie Hauser" — an apparent play on the fictional TV character "Doogie Howser, M.D." This is not a real provider name and should not appear in any scheduling system.

**What Should Have Happened:**
The agent should only surface real, credentialed providers from the scheduling system. A fictional or placeholder name entering a booking flow indicates either a data quality issue in the provider database or a hallucination by the underlying model.

**Risk:** Patient receives a confirmation for an appointment with a non-existent provider, leading to a failed visit, loss of trust, and potential care delays.

---

## BUG-006: Medication Refill Request Dismissed Without Triage or Documentation

**Severity:** 🟠 Medium
**Transcript:** 3 (multiple_requests_mike)
**Location:** ~7th agent/bot exchange

**What Happened:**
The patient requested a refill of Lisinopril 10mg (a prescription antihypertensive). The agent simply deflected — "I recommend contacting your pharmacy or your provider's office directly" — without:
- Noting the request for the care team
- Asking when the patient last filled the prescription or if they were running out
- Offering to send a message to the provider

**What Should Have Happened:**
A medical office agent should route refill requests to the clinical team or patient portal messaging system, especially for a blood pressure medication where a lapse could have health consequences. At minimum, the agent should have offered to document the request or escalate to a nurse line.

**Risk:** Patient may experience a lapse in antihypertensive medication due to an inadequate handoff.

---

## BUG-007: Spanish Language Request Mishandled

**Severity:** 🟠 Medium
**Transcript:** 4 (spanish_greeting_mike)
**Location:** ~4th–5th agent/bot exchange

**What Happened:**
The patient opened the call in Spanish ("Hola, necesito hacer una cita por favor"). The agent proceeded entirely in English, only offering a Spanish-speaking agent transfer after the patient had already confirmed English was fine. Additionally, the agent's opening response ("be good ai am i speaking with mike") suggests the Spanish greeting may have disrupted the agent's speech recognition or flow.

**What Should Have Happened:**
Upon detecting a non-English greeting, the agent should have:
1. Immediately offered language support in both languages (e.g., "Para español, diga 'español' / For English, say 'English'")
2. Not waited until mid-call to offer the transfer

**Risk:** Non-English-speaking patients who don't understand the English flow may be unable to navigate the call, creating an access-to-care barrier. This may also implicate language access requirements under Title VI of the Civil Rights Act for healthcare providers receiving federal funding.

---

## BUG-008: Agent Speech Recognition / Transcription Artifact — "three cam"

**Severity:** 🟠 Medium
**Transcript:** 2 (interruption_test_mike)
**Location:** ~7th agent turn

**What Happened:**
The agent confirmed an appointment at "three cam in the afternoon" — an apparent ASR (automatic speech recognition) or text artifact for "3 PM."

**What Should Have Happened:**
The confirmation should have read "three PM in the afternoon." While the patient did not seem confused, a real patient could be misled by garbled time references, especially for critical appointment details.

**Risk:** Low in isolation, but indicates a reliability issue with how the agent formats or speaks time values that could cause patient confusion in other cases.

---

## BUG-009: No Callback Number or Direct Line Provided When Requested

**Severity:** 🟠 Medium
**Transcript:** 2 (interruption_test_mike)
**Location:** ~9th agent/bot exchange

**What Happened:**
When the patient asked for a number to call if they need to reschedule, the agent responded: "you can call the clinic directly at this number" — without specifying any actual phone number.

**What Should Have Happened:**
The agent should have provided the clinic's actual phone number (e.g., the number the patient just called, or a direct scheduling line). Saying "this number" in a voice call context is ambiguous and unhelpful since the patient may not have the number saved.

**Risk:** Patient is unable to reschedule or reach the clinic, potentially resulting in a no-show or inability to cancel in a timely manner.

---

## BUG-010: Existing Appointment Found but Provider Not Confirmed to Patient

**Severity:** 🟡 Low
**Transcript:** 3 (multiple_requests_mike)
**Location:** ~6th agent turn

**What Happened:**
The agent informed the patient they already had a general checkup booked, but did not provide the date, time, provider name, or location of that appointment. The patient accepted this without pushing for details.

**What Should Have Happened:**
When informing a patient an appointment already exists, the agent should proactively share the key details (date, time, provider, location) so the patient can confirm it is the correct appointment and hasn't been forgotten or double-booked.

**Risk:** Patient may miss the existing appointment or show up at the wrong time/location.

---

## BUG-011: Weekend Waitlist Added Without Confirming Patient Preferences or Scope

**Severity:** 🟡 Low
**Transcript:** 5 (weekend_appointment_mike)
**Location:** ~10th–12th agent/bot exchange

**What Happened:**
The agent added the patient to a weekend waitlist but did not confirm:
- Which provider (any, or specific)
- What type of appointment (routine checkup, as discussed)
- How far out the patient is willing to wait
- Preferred contact method (call, text, email)

**What Should Have Happened:**
A waitlist entry should capture enough detail to make a meaningful match. Without appointment type and provider scope, the follow-up call may offer an irrelevant slot.

**Risk:** Patient receives a callback for a mismatched appointment type or is contacted unnecessarily after they've already booked elsewhere.

---

## BUG-012: Agent Interrupted Mid-Word Without Recovery Logic

**Severity:** 🟡 Low
**Transcript:** 5 (weekend_appointment_mike)
**Location:** ~8th agent turn

**What Happened:**
After the patient asked about weekend availability, the agent responded only with "let's" before stopping. The patient apologized and yielded the floor, but the agent then re-asked about the previously offered Thursday slot instead of answering the weekend question.

**What Should Have Happened:**
The agent should have gracefully recovered from the interruption and directly answered whether weekend slots were available. Instead, it looped back to a prior offer, creating a slightly confusing and circular exchange.

**Risk:** Low in this case as the conversation recovered, but this pattern could frustrate patients or cause them to miss important information.

---

## Summary Table

| Bug ID | Severity | Transcript(s) | Category |
|--------|----------|---------------|----------|
| BUG-001 | 🔴 High | 1, 4 | Identity Verification |
| BUG-002 | 🔴 High | 5 | Data Integrity / Identity |
| BUG-003 | 🔴 High | 3 | Broken Conversation Flow / Care Risk |
| BUG-004 | 🔴 High | 2 | Identity Verification |
| BUG-005 | 🔴 High | 2 | Incorrect Information / Hallucination |
| BUG-006 | 🟠 Medium | 3 | Medical Triage / Inappropriate Dismissal |
| BUG-007 | 🟠 Medium | 4 | Language Access / Edge Case Handling |
| BUG-008 | 🟠 Medium | 2 | ASR / Transcription Artifact |
| BUG-009 | 🟠 Medium | 2 | Missing Follow-up / Incomplete Response |
| BUG-010 | 🟡 Low | 3 | Missing Information |
| BUG-011 | 🟡 Low | 5 | Missing Follow-up Questions |
| BUG-012 | 🟡 Low | 5 | Conversation Flow / Interruption Handling |

---

**Recommended Priority Actions:**
1. Immediately block identity verification bypass logic (BUG-001, BUG-004) before any production deployment
2. Audit provider database for test/placeholder entries (BUG-005)
3. Implement unanswered-question detection to prevent silent drops of patient requests (BUG-003)
4. Add DOB collection as a required explicit step in profile creation (BUG-002)
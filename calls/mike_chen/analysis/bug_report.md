# Bug Report — mike_chen

# QA Bug Report: AI Medical Office Agent Transcripts

**Review Date:** 2026-06-26
**Transcripts Analyzed:** 5
**Total Issues Found:** 12

---

## BUG-001: Identity Verification Failure — Date of Birth Mismatch Accepted

**Severity:** 🔴 High
**Transcripts:** 1 (confused_patient_mike), 4 (spanish_greeting_mike)
**Location:** Early in both calls, after DOB is provided

**What Happened:**
The agent explicitly acknowledged that the provided date of birth did not match records ("the birth date doesn't match our records") but proceeded to fully serve the patient anyway, citing "demo purposes."

**What Should Happen:**
A real medical office agent must not bypass identity verification failures, even in testing contexts, without a defined fallback process (e.g., secondary verification via address, last 4 of SSN, or transferring to a human agent). Accepting a mismatched DOB and proceeding exposes PHI and appointment details to an unverified caller. The "demo purposes" rationale should never appear in a patient-facing response.

---

## BUG-002: Incorrect/Fictional Patient Profile Creation with Wrong DOB

**Severity:** 🔴 High
**Transcript:** 5 (weekend_appointment_mike)
**Location:** After patient provides name

**What Happened:**
The agent created a patient profile and assigned an arbitrary date of birth ("July 4th, 2000") without asking the patient for it. The patient had to correct the agent.

**What Should Happen:**
The agent must collect the date of birth from the patient before creating or confirming a profile. Assigning a fabricated DOB to a medical record — even in demo mode — is a data integrity issue and could cause serious downstream harm if this behavior carried over to production.

---

## BUG-003: Patient's Direct Question Ignored (Sore Knee)

**Severity:** 🔴 High
**Transcript:** 3 (multiple_requests_mike)
**Location:** Final third of call

**What Happened:**
The patient asked whether they could add a sore knee concern to their existing appointment. The agent responded with a generic sign-off ("if you need anything else just let us know, have a great day") without answering the question. The patient explicitly noted they didn't receive an answer, but the transcript ends there.

**What Should Happen:**
The agent must answer the patient's question before closing the call. The correct response would be to either confirm the concern can be noted for the provider, suggest scheduling a separate appointment if needed, or advise the patient to mention it when they arrive. Hanging up on an unanswered medical question is a significant service failure.

---

## BUG-004: Failure to Check Patient Records for Existing Provider

**Severity:** 🟡 Medium
**Transcript:** 3 (multiple_requests_mike)
**Location:** Mid-call, after patient asks who they've been seeing

**What Happened:**
The patient asked the agent to check their file to find out which doctor they've been seeing. The agent responded by asking about scheduling preferences, never confirming or checking for an existing provider relationship.

**What Should Happen:**
The agent should attempt to look up the patient's visit history and identify their usual provider, or clearly state it cannot access that information and suggest an alternative (e.g., "I don't have access to that detail, but I can transfer you to someone who can check").

---

## BUG-005: Provider Name "Dougie Hauser" Raises Validity Concern

**Severity:** 🟡 Medium
**Transcript:** 2 (interruption_test_mike)
**Location:** Mid-call, when appointment is offered

**What Happened:**
The agent offered an appointment with a provider named "Dougie Hauser," which appears to be a reference to the fictional TV character "Doogie Howser, M.D." This is likely a test data artifact, but it was presented to the patient as a real provider without any flag.

**What Should Happen:**
Test/demo provider names should not resemble pop-culture references in a way that could undermine patient trust. More importantly, the system should not offer appointments with providers who do not exist in a real or properly validated provider directory. This needs to be flagged for data hygiene review.

---

## BUG-006: Agent Did Not Verify Identity Before Scheduling New Appointment

**Severity:** 🟡 Medium
**Transcript:** 2 (interruption_test_mike)
**Location:** After DOB is provided

**What Happened:**
The agent accepted the DOB ("thanks") and immediately moved into scheduling without any explicit confirmation that the identity was verified or matched. Unlike Transcripts 1 and 4 where the mismatch was at least surfaced, here the verification outcome is entirely opaque.

**What Should Happen:**
The agent should confirm successful identity verification explicitly before accessing records or scheduling (e.g., "I've verified your identity, Mike — how can I help you?"). Silent acceptance leaves ambiguity about whether verification actually occurred.

---

## BUG-007: Spanish Language Handling — Incorrect Escalation Offer

**Severity:** 🟡 Medium
**Transcript:** 4 (spanish_greeting_mike)
**Location:** After patient speaks in Spanish, then clarifies in English

**What Happened:**
The agent offered to connect to a Spanish-speaking agent *after* the patient had already switched to English and explained the Spanish was accidental. The offer was made out of sequence and was contextually unnecessary.

**What Should Happen:**
If the patient has already clarified they prefer English and there is no further ambiguity, the agent should proceed in English without offering the language redirect. A better flow would be to detect language at the start of the call and offer language options proactively, rather than reactively after confusion has already been resolved.

---

## BUG-008: Medication Refill Request Deflected Without Proper Guidance

**Severity:** 🟡 Medium
**Transcript:** 3 (multiple_requests_mike)
**Location:** After patient requests Lisinopril refill

**What Happened:**
The agent told the patient to "contact your pharmacy or your provider's office directly" for a medication refill — but the patient was already speaking with the provider's office. This is a circular and unhelpful response.

**What Should Happen:**
Since the patient is calling the provider's office, the agent should offer to route the refill request appropriately (e.g., note it for the provider, transfer to a nurse line, or take a message). Telling someone already at the right destination to go there is a failure of basic call routing logic.

---

## BUG-009: Transcript Cut Off Mid-Sentence During Weekend Availability Discussion

**Severity:** 🟡 Medium
**Transcript:** 5 (weekend_appointment_mike)
**Location:** Mid-call, after patient first requests weekend slot

**What Happened:**
The agent's response was cut off mid-word: "let's" — followed by the patient apologizing and letting the agent continue. The agent then ignored the interrupted content entirely and re-offered the same Thursday slot.

**What Should Happen:**
While conversational interruptions can happen, the agent should not lose the thread of the response it was delivering. The incomplete utterance ("let's") suggests a system-level truncation or speech generation failure. This should be investigated as a potential TTS or response generation bug.

---

## BUG-010: No Confirmation of What "Usual Location" Means

**Severity:** 🟢 Low
**Transcript:** 1 (confused_patient_mike)
**Location:** After patient asks about "the usual location"

**What Happened:**
The patient asked if the appointment was at "the usual location" — implying they may have multiple known locations or uncertainty. The agent provided the address without clarifying whether this was indeed the patient's preferred or previously visited location.

**What Should Happen:**
The agent should acknowledge the patient's framing (e.g., "Yes, this is the same location you've visited before at 220 Athens Way") or ask a brief clarifying question if location history is relevant. This is low severity but could cause a patient to show up at the wrong site.

---

## BUG-011: No Callback Number or Direct Line Provided When Asked

**Severity:** 🟢 Low
**Transcript:** 2 (interruption_test_mike)
**Location:** Near end of call

**What Happened:**
The patient asked for a number to call if they need to reschedule. The agent responded with "you can call the clinic directly at this number" — without actually stating a phone number.

**What Should Happen:**
The agent must provide the actual phone number when asked. A response referencing "this number" is meaningless in a voice interaction and leaves the patient without the information they requested.

---

## BUG-012: Waiting List Added Without Confirming Patient Consent to Be Contacted

**Severity:** 🟢 Low
**Transcript:** 5 (weekend_appointment_mike)
**Location:** Late in call, when waitlist is discussed

**What Happened:**
The agent added the patient to a weekend appointment waiting list and collected their phone number for follow-up. However, the agent did not confirm the patient's preferred contact method, best time to call, or whether leaving a voicemail was acceptable.

**What Should Happen:**
Before recording a callback number for outreach, a real receptionist would confirm preferred contact time/method (e.g., "Is there a best time to reach you?") and obtain any necessary consent for outbound contact, especially in a healthcare context where call content may involve PHI.

---

## Summary Table

| Bug ID | Severity | Transcript(s) | Category |
|--------|----------|---------------|----------|
| BUG-001 | 🔴 High | 1, 4 | Identity Verification |
| BUG-002 | 🔴 High | 5 | Data Integrity |
| BUG-003 | 🔴 High | 3 | Conversation Flow / Patient Safety |
| BUG-004 | 🟡 Medium | 3 | Missing Follow-Through |
| BUG-005 | 🟡 Medium | 2 | Data Quality / Provider Directory |
| BUG-006 | 🟡 Medium | 2 | Identity Verification |
| BUG-007 | 🟡 Medium | 4 | Language Handling Logic |
| BUG-008 | 🟡 Medium | 3 | Incorrect Routing / Unhelpful Response |
| BUG-009 | 🟡 Medium | 5 | System/Speech Generation |
| BUG-010 | 🟢 Low | 1 | Clarification Gap |
| BUG-011 | 🟢 Low | 2 | Missing Information |
| BUG-012 | 🟢 Low | 5 | Consent / Contact Preference |

---

*Report generated by QA review. Recommend immediate remediation of BUG-001 through BUG-003 before any production deployment.*
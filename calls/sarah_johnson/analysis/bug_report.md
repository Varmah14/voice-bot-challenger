# Bug Report — sarah_johnson

# QA Bug Report: AI Medical Office Agent Transcripts

**Review Date:** 2026-06-26
**Transcripts Reviewed:** 8
**Patient:** sarah_johnson (across all scenarios)

---

## Bug #1 — Identity Verification Failure: DOB Mismatch Accepted Without Escalation

**Severity:** 🔴 High

**Affected Transcripts:** 1, 2, 3, 4, 5, 6 (implicitly passing), 8

**What Happened:**
The agent consistently acknowledges that the date of birth provided by the caller does not match records ("the birthday doesn't match our records") but proceeds to assist the patient anyway, justified only with "but for demo purposes I'll accept it."

**What Should Happen:**
A failed identity verification should result in one of the following:
- Asking for an alternative identifier (e.g., address, phone number, last four of SSN)
- Declining to discuss or modify PHI until identity is confirmed
- Escalating to a human representative

**Risk:**
This is a HIPAA-relevant failure. In a production environment, proceeding after a failed identity check could expose protected health information to an unauthorized caller. The "demo purposes" language is especially dangerous if this phrasing ever leaks into a production system.

---

## Bug #2 — Scheduling Appointment at Wrong Facility Type

**Severity:** 🔴 High

**Affected Transcript:** 7 (`schedule_appointment_sarah_20260626_224322.txt`)

**Location:** Near end of scheduling confirmation

**What Happened:**
The agent confirmed a routine checkup appointment with Kelly Noble MD but cited the location as **"Pivot Point Orthopedics"** — an orthopedic specialty practice — for what was requested as a general routine checkup.

**What Should Happen:**
A routine/general checkup should be booked at a primary care or general practice location. If the provider is at a specialty practice, the agent should clarify whether the patient needs a referral or is aware it is a specialty visit. Booking a general checkup at an orthopedic clinic without clarification is clinically misleading.

**Risk:**
Patient may arrive at wrong facility type; insurer may deny coverage for a preventive visit at a specialty clinic.

---

## Bug #3 — Appointment Scheduling Ignores Stated Availability Constraint

**Severity:** 🔴 High

**Affected Transcript:** 5 (`office_hours_sarah_20260626_231923.txt`)

**Location:** Mid-transcript, appointment scheduling segment

**What Happened:**
The patient explicitly stated she works 9–5 and needs a **Wednesday evening** slot. The agent offered the next available slot — Wednesday July 2nd at **11:30 AM** — which directly conflicts with the patient's stated unavailability. The agent acknowledged the error only after the patient pointed it out.

**What Should Happen:**
The agent should filter available appointments against the patient's stated availability constraints *before* offering a slot. Offering a 11:30 AM slot to someone who just said they work 9–5 suggests the scheduling logic ignores availability preferences.

**Risk:**
Patient books an appointment they cannot attend; wastes clinical slot; erodes trust in the system.

---

## Bug #4 — Failed Cancellation with Poor Escalation Handling

**Severity:** 🔴 High

**Affected Transcript:** 2 (`cancel_appointment_sarah_20260626_230042.txt`)

**Location:** Middle of transcript

**What Happened:**
The agent stated it was unable to complete the cancellation and attempted to transfer the patient to "patient support." The transfer resulted in a message that said **"you've reached the pretty good ai test line goodbye"** and the call ended without completing the cancellation or providing any actionable next steps.

**What Should Happen:**
- If the agent cannot complete a cancellation, it should explain why and offer clear alternatives (call back number, alternative method, estimated wait time).
- A test/dummy endpoint should never be reachable in a scenario being evaluated for production quality.
- The patient's appointment was **not** canceled, but they received no confirmation of this and may incorrectly assume it was handled.

**Risk:**
Patient misses appointment thinking it was canceled; potential no-show fee charged; patient left without resolution.

---

## Bug #5 — Urgent Symptoms: No Triage Escalation or Safety-Netting for Potentially Serious Symptoms

**Severity:** 🔴 High

**Affected Transcript:** 8 (`urgent_symptoms_sarah_20260626_232338.txt`)

**Location:** Throughout

**What Happened:**
Patient reported **three days of severe headache with fever**. The agent documented the symptoms for clinic review and mentioned urgent care/911 only as a secondary afterthought if symptoms "get worse."

**What Should Happen:**
A persistent severe headache combined with fever can be a symptom of meningitis or other serious conditions. A medically responsible agent should:
1. Immediately and prominently advise the patient to seek **in-person evaluation today** (urgent care or ER) given the combination and duration of symptoms — not as a vague "if it gets worse" caveat.
2. Not simply log symptoms for async follow-up as the primary pathway.
3. Reference the 3-day duration as a reason for urgency, not routine documentation.

The agent's response prioritized process (documentation, callback) over patient safety. The 911/urgent care advisory was buried at the end after reassuring the patient the team would "reach out."

**Risk:**
Delayed care for a potentially serious condition. This is the highest-risk transcript in the set.

---

## Bug #6 — Broken/Incomplete Sentence During Identity Verification

**Severity:** 🟡 Medium

**Affected Transcript:** 3 (`insurance_question_sarah_20260626_232614.txt`)

**Location:** Early in call, immediately after DOB entry

**What Happened:**
The agent's response was cut off mid-sentence: *"the birthday doesn't match our records but for demo purposes i'll"* — the sentence never completed, and the conversation continued as if nothing happened. The patient was confused ("that's weird, but okay").

**What Should Happen:**
Response generation should not produce incomplete sentences. This suggests a TTS truncation, token cutoff, or prompt formatting issue. There should be a graceful fallback.

**Risk:**
Confuses patients; unprofessional; could cause patient to mishear partial instructions as complete ones.

---

## Bug #7 — Medication Refill: No Verification That Medication Is on Patient's Record

**Severity:** 🟡 Medium

**Affected Transcript:** 4 (`medication_refill_sarah_20260626_231432.txt`)

**Location:** Early-to-mid transcript

**What Happened:**
The patient requested a refill for Zyrtec (cetirizine) 10mg. The agent processed the refill request without confirming:
- Whether cetirizine is on the patient's active medication list
- Whether the prescribing provider is still associated with this patient
- Whether the patient has an active, non-expired prescription

**What Should Happen:**
Before initiating a refill request, the agent should verify the medication appears in the patient's chart and confirm it is an active prescription. Refilling medications not on record could result in clinical errors or be misused.

**Risk:**
Refill request submitted for medication not tied to a current valid prescription; potential for misuse.

---

## Bug #8 — Refill Flow: Unexplained Retry ("Let me try submitting that pharmacy information again")

**Severity:** 🟡 Medium

**Affected Transcript:** 4 (`medication_refill_sarah_20260626_231432.txt`)

**Location:** Pharmacy information segment

**What Happened:**
After the patient provided pharmacy details, the agent said *"let me try submitting that pharmacy information again for you"* — implying a prior failed submission that was never mentioned to the patient. There is no prior indication of a failure in the transcript.

**What Should Happen:**
If a backend submission fails, the agent should explicitly communicate the failure to the patient before retrying. The word "again" suggests a silent failure occurred. Silent failures in medical workflows are a quality and safety issue.

**Risk:**
Confusing phrasing; potential for the patient to miss that a step failed; could result in no refill being sent.

---

## Bug #9 — Insurance Flow: Extended Unresolved Loop with No Clear Outcome

**Severity:** 🟡 Medium

**Affected Transcript:** 3 (`insurance_question_sarah_20260626_232614.txt`)

**Location:** Middle-to-end of transcript (photo upload loop)

**What Happened:**
The agent sent a secure link for the patient to upload insurance card photos. After the patient claimed to submit, the agent repeatedly stated it could not see the submission (4+ exchanges), eventually pivoting to ask for the insurance info verbally. The loop consumed significant call time with no resolution, and the patient's original questions (copay amount, referral requirement) were **never answered**.

**What Should Happen:**
- The agent should set a clear timeout on the upload flow and pivot earlier.
- If the upload fails, the agent should have a clear fallback path (verbal capture, callback, etc.) triggered after 1–2 failed attempts, not 4+.
- Critically, the **patient's original questions were never answered**. At minimum, the agent should acknowledge this and provide a path to get the answers (e.g., "once we have your insurance on file, we can answer those coverage questions").

**Risk:**
Patient hung up without getting the information they called for; poor experience; potential for patient to make incorrect assumptions about coverage.

---

## Bug #10 — Agent Greeting Contains Garbled/OCR-Like Text

**Severity:** 🟡 Medium

**Affected Transcripts:** 1, 2, 3, 4, 5, 6, 7, 8 (all transcripts)

**Location:** Opening line of every call

**What Happened:**
Every transcript contains a garbled greeting such as:
- *"of pretty good ai am i speaking with sarah"*
- *"art of pretty good ai am i speaking with sarah"*
- *"caught a pretty good ai am i speaking with sarah"*
- *"part of pretty good ai am i speaking with sarah"*

The greeting appears to be a mangled version of a phrase like *"You've reached [Part of] Pretty Good AI, am I speaking with Sarah?"* — with the first word(s) being inconsistently transcribed or generated.

**What Should Happen:**
The greeting should be consistent and coherent. This likely indicates a STT transcription error on the opening phrase, or a prompt/TTS rendering issue. Even if this is a transcription artifact, it should be flagged because it appears in every call and could mask identity/branding errors.

**Risk:**
Low direct harm but reflects systemic STT/rendering issue; if the greeting is actually garbled on the call (not just in transcript), patients may be confused about who they've reached.

---

## Bug #11 — Reschedule Confirmation Does Not Flag Existing Appointment for Same Slot Held by Another Scenario

**Severity:** 🟢 Low

**Affected Transcripts:** 6 (`reschedule_appointment_sarah`) and 1 (`cancel_appointment_sarah`)

**Location:** Cross-transcript consistency check

**What Happened:**
In Transcript 6, Sarah reschedules to **Wednesday July 8th at 11:30 AM with Kelly Noble**. In Transcript 1, that same appointment (July 8th, Kelly Noble) is then canceled. This is internally consistent *within* the test scenario design. However, it is worth noting that in Transcript 7 (`schedule_appointment_sarah`), Sarah books **Thursday July 2nd at 11:30 AM**, and in Transcript 6 (rescheduled from), the original appointment was also **Thursday July 2nd at 11:30 AM**. This means two independent scenario runs booked the same slot without conflict detection.

**What Should Happen:**
Slot conflict detection should prevent double-booking across sessions if the underlying calendar state is shared. If sessions are isolated (stateless), this should be documented clearly.

**Risk:**
Low in test context; High in production if calendar state is shared across concurrent calls.

---

## Bug #12 — No Offer to Reschedule During Cancellation

**Severity:** 🟢 Low

**Affected Transcript:** 1 (`cancel_appointment_sarah_20260626_225727.txt`)

**Location:** Post-cancellation confirmation

**What Happened:**
After confirming the cancellation, the agent asked "is there anything else I can help you with?" but did not proactively offer to reschedule the appointment.

**What Should Happen:**
A real medical receptionist would routinely ask "Would you like to reschedule?" before closing out a cancellation call. This is a standard retention/care continuity practice, especially relevant when the patient has an ongoing care relationship.

**Risk:**
Patient may delay or forgo rescheduling; minor gap in care continuity.

---

## Summary Table

| # | Issue | Severity | Transcript(s) |
|---|-------|----------|---------------|
| 1 | DOB mismatch accepted without alternative verification | 🔴 High | 1, 2, 3, 4, 5, 8 |
| 2 | Routine checkup booked at orthopedic specialty clinic | 🔴 High | 7 |
| 3 | Appointment offered that ignores stated availability | 🔴 High | 5 |
| 4 | Failed cancellation with broken escalation path | 🔴 High | 2 |
| 5 | Serious symptoms triaged to async documentation only | 🔴 High | 8 |
| 6 | Truncated/incomplete agent sentence mid-call | 🟡 Medium | 3 |
| 7 | Refill processed without verifying active prescription | 🟡 Medium | 4 |
| 8 | Silent backend failure with unexplained retry | 🟡 Medium | 4 |
| 9 | Extended upload loop; original questions never answered | 🟡 Medium | 3 |
| 10 | Garbled greeting across all transcripts | 🟡 Medium | All |
| 11 | Potential slot double-booking across sessions | 🟢 Low | 6, 7 |
| 12 | No proactive reschedule offer after cancellation | 🟢 Low | 1 |

**Total Issues:** 12 (5 High, 5 Medium, 2 Low)
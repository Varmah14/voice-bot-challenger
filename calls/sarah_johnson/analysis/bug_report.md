# Bug Report — sarah_johnson

# Bug Report: AI Medical Office Agent QA Analysis

---

## Bug 1: Date of Birth Mismatch — Accepted Without Proper Handling

**Severity:** High
**Transcripts:** 1, 2, 4, 5, 6, 7, 10, 11 (nearly all transcripts)
**Location:** Identity verification step, early in each call

**What Happened:** The agent explicitly states the date of birth doesn't match records, then proceeds anyway with `"but for demo purposes I'll accept it"`. This phrase is surfacing verbatim in production-style transcripts.

**What Should Happen:** In a real deployment, a DOB mismatch should trigger a secondary verification method (e.g., address, last 4 of SSN, phone number on file) or the call should be escalated. The agent should never verbalize "for demo purposes" to a caller — this exposes internal testing logic and would be inappropriate and confusing to a real patient. This fallback acceptance logic should be removed or gated behind an internal flag invisible to the caller.

---

## Bug 2: Identity Not Verified Before Appointment Details Were Disclosed

**Severity:** High
**Transcript:** 8 (reschedule_appointment_sarah)
**Location:** After DOB is provided, before identity is confirmed

**What Happened:** The agent skipped the DOB match confirmation step entirely and immediately disclosed the patient's appointment details (date, time, provider, location) without noting any mismatch or requesting alternative verification.

**What Should Happen:** If the DOB doesn't match, the agent should not disclose PHI (appointment details, provider names, location) until identity is confirmed through another means. This transcript silently skipped the mismatch warning that appeared in all other transcripts, which may indicate an inconsistent identity verification code path.

---

## Bug 3: Failed Cancellation Leads to Dead-End Escalation

**Severity:** High
**Transcript:** 2 (cancel_appointment_sarah — 23:00:42)
**Location:** After patient states reason for cancellation

**What Happened:** The agent said it was unable to complete the cancellation and transferred the patient to a "support team," which then played a generic test-line message ("you've reached the pretty good ai test line goodbye") and disconnected the patient. The patient was left with no resolution and no guidance other than to call back.

**What Should Happen:** The agent should either complete the cancellation successfully or, if escalation is required, connect to a live agent or provide a clear alternative (callback number, office hours, email). Dumping the patient into a test/placeholder line is a broken user experience. The fallback escalation path needs a real resolution endpoint, and the trigger for cancellation failure should be investigated — the same scenario succeeded in Transcript 1.

---

## Bug 4: Incorrect/Inconsistent Office Hours Claim (Wednesday Hours)

**Severity:** High
**Transcript:** 6 (office_hours_sarah)
**Location:** When agent describes office hours, and when scheduling

**What Happened:** The agent stated Wednesday hours are 12 PM–7 PM, implying evening availability. However, when the patient asked to book a Wednesday evening slot (after 5 PM), the agent said no evening slots were available. Additionally, in Transcript 8, a Wednesday July 8th appointment was booked at 11:30 AM — which falls outside the stated Wednesday hours of 12 PM–7 PM.

**What Should Happen:** Office hours and appointment slot availability must be consistent. If Wednesday hours start at 12 PM, an 11:30 AM slot on Wednesday should not be bookable. Either the hours data is wrong, the scheduling system isn't respecting hours, or both. This needs reconciliation between the hours knowledge base and the slot availability logic.

---

## Bug 5: Appointment Booked at 11:30 AM on Wednesday Despite Hours Starting at 12 PM

**Severity:** High
**Transcript:** 8 (reschedule_appointment_sarah), also referenced in Transcript 6
**Location:** Appointment confirmation step

**What Happened:** The agent offered and confirmed an 11:30 AM appointment on Wednesday, July 8th. Per the office hours stated in Transcript 6, Wednesday hours begin at 12 PM.

**What Should Happen:** The scheduling system should not offer or confirm appointment slots outside of stated office hours. This indicates a disconnect between the hours configuration and the available slots data.

---

## Bug 6: Doctor Name Gender Inconsistency (Hauser)

**Severity:** Medium
**Transcript:** 11 (wrong_doctor_sarah)
**Location:** When agent describes Dr. Hauser

**What Happened:** The agent refers to Dr. Hauser as "he" (`"he's great for new patients"`). However, in Transcript 3, the same provider is referred to as "doctor judy houser" — a name strongly suggesting the provider is female.

**What Should Happen:** Provider profiles should include correct pronoun/gender data, and the agent should use consistent and accurate references. This is both a data integrity issue and potentially offensive to the provider and confusing to patients.

---

## Bug 7: "Kronos" Mentioned Unexpectedly Mid-Conversation

**Severity:** Medium
**Transcript:** 4 (insurance_question_sarah)
**Location:** Near the end of the upload loop

**What Happened:** The agent said: `"could you double check that you hit submit after uploading your kronos"`. The word "kronos" appears to be a garbled or hallucinated term — likely a transcription artifact or a template variable that was never filled in (e.g., `{form_name}`).

**What Should Happen:** The agent should say something clear like "photos" or "insurance card images." Nonsense words like "kronos" should never surface in patient-facing dialogue. This suggests a template rendering failure or a speech recognition error that is being fed back into the conversation without sanity checking.

---

## Bug 8: Redundant/Looping DOB Prompt in Transcript 3

**Severity:** Medium
**Transcript:** 3 (cancel_one_of_many_sarah)
**Location:** Identity verification step

**What Happened:** The agent asked for the date of birth twice in succession. After the patient provided it the first time, the agent responded with `"go ahead and tell me your date of birth"` as if the answer hadn't been received.

**What Should Happen:** The agent should recognize a valid DOB response and move on. This suggests a failure in the speech recognition pipeline or the dialogue state manager — the first response was not registered, causing a repeated prompt. In Transcript 3, notably, there is also no "birthday doesn't match" message, suggesting the second attempt produced a different (possibly matched?) result — or the mismatch logic was bypassed. Either way, the double-prompt is a broken flow.

---

## Bug 9: Urgent Symptoms — No Recommendation to Seek Immediate Care for Potentially Serious Symptoms

**Severity:** High
**Transcript:** 10 (urgent_symptoms_sarah)
**Location:** When patient describes three-day headache with fever

**What Happened:** The patient described a persistent severe headache for three days with fever. The agent documented the concern and mentioned calling 911 if symptoms worsen, but only as a secondary note. The primary response was to wait for the clinic team to follow up "as soon as possible."

**What Should Happen:** A three-day severe headache combined with fever can be a sign of meningitis or other serious neurological conditions. The agent should more prominently and immediately advise the patient to go to an emergency room or urgent care *now*, rather than framing ER/911 as a fallback. The clinic team callback should be secondary, not the primary path. The current response could cause a patient to wait when they need immediate evaluation — this is a patient safety issue.

---

## Bug 10: Agent Attempts Medication Refill Submission Twice Without Explanation

**Severity:** Medium
**Transcript:** 5 (medication_refill_sarah)
**Location:** After pharmacy information is provided

**What Happened:** After the patient provided the pharmacy address, the agent said `"let me try submitting that pharmacy information again for you one moment"` — using the word "again" despite this being the first attempt in the conversation. This implies a silent failure occurred that the agent tried to hide from the patient.

**What Should Happen:** If a submission fails, the agent should clearly inform the patient rather than retrying silently with misleading language. The patient deserves to know if there was a technical issue and whether the refill was actually submitted successfully.

---

## Bug 11: Agent Offers Appointment That Conflicts With Existing Booking

**Severity:** High
**Transcript:** 7 (past_date_appointment_sarah) cross-referenced with Transcript 3
**Location:** When confirming Monday July 6th 10:30 AM with Kelly Noble

**What Happened:** In Transcript 7, the agent books Sarah for Monday July 6th at 10:30 AM with Dr. Kelly Noble. However, in Transcript 3 (dated the following day, June 27th), Sarah already has an appointment on July 6th at 10:30 AM with Kelly Noble MD that she then cancels. This means the slot was apparently double-bookable or the records weren't being checked for conflicts.

**What Should Happen:** Before confirming a new appointment, the system should check if the patient already has an appointment in that slot, and should check for duplicate bookings. While these are different call sessions, this indicates the scheduling system may not be properly validating against existing patient bookings.

---

## Bug 12: Identity Verification Skipped Entirely for Scheduling in Transcript 9

**Severity:** Medium
**Transcript:** 9 (schedule_appointment_sarah)
**Location:** After DOB is provided

**What Happened:** The agent accepted the DOB with no mismatch warning (unlike nearly every other transcript) and immediately confirmed the scheduling request. There is no "birthday doesn't match" flag here, yet the same DOB (March 15, 1991) triggers mismatch errors in all other sessions.

**What Should Happen:** Verification behavior should be consistent across sessions for the same patient record. The absence of the mismatch error here suggests either the record was temporarily correct, a bug caused the check to be skipped, or the verification logic is non-deterministic. This needs investigation.

---

## Bug 13: No Offer to Reschedule After Cancellation

**Severity:** Low
**Transcripts:** 1, 3 (cancel scenarios)
**Location:** After cancellation is confirmed

**What Happened:** After confirming cancellation, the agent simply asked "is there anything else I can help you with?" without proactively offering to reschedule the canceled appointment.

**What Should Happen:** A real medical receptionist would typically ask if the patient wants to reschedule. Failing to do so may result in care gaps for patients who canceled due to conflicts but still need to be seen.

---

## Summary Table

| # | Bug | Severity | Transcripts Affected |
|---|-----|----------|----------------------|
| 1 | "Demo purposes" language exposed to caller | High | 1,2,4,5,6,7,10,11 |
| 2 | PHI disclosed without successful identity verification | High | 8 |
| 3 | Failed cancellation → broken escalation path | High | 2 |
| 4 | Inconsistent Wednesday office hours vs. available slots | High | 6, 8 |
| 5 | Appointment booked outside stated office hours | High | 8 |
| 6 | Dr. Hauser gender inconsistency across transcripts | Medium | 3, 11 |
| 7 | "Kronos" garbled/unfilled template variable | Medium | 4 |
| 8 | Duplicate DOB prompt / broken dialogue state | Medium | 3 |
| 9 | Urgent symptoms: insufficient safety escalation | High | 10 |
| 10 | Silent submission failure hidden from patient | Medium | 5 |
| 11 | Conflicting appointment slot offered without conflict check | High | 7, 3 |
| 12 | Inconsistent DOB verification behavior | Medium | 9 |
| 13 | No proactive rescheduling offer after cancellation | Low | 1, 3 |
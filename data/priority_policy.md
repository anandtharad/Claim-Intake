
# Priority Policy — Vehicle Insurance Claim Intake

## Overview

The claim intake system uses a priority-driven retrieval strategy to determine the next most useful question to ask.

Each question is assigned a priority level from **1 (highest importance)** to  **5 (lowest importance)** . Priority is the primary business signal used during ranking, alongside relevance and gap-filling considerations.

The objective is to collect the most critical claim information as early as possible while avoiding redundant or irrelevant questions.

---

## Priority 1 — Mandatory Claim Registration Information

These fields are required to establish the claim and should be collected as early as possible.

### Incident Identification

* Incident type (collision, theft, fire, flood, vandalism, etc.)
* Date and time of loss
* Location of loss

### Safety & Legal Information

* Injury status
* Emergency service involvement
* Police report status
* FIR number (when applicable)

### Vehicle Identification

* Insured vehicle registration number

### Theft-Specific Critical Fields

* Vehicle recovery status
* Key availability
* Evidence of forced entry

Failure to collect these fields may prevent claim registration or legal processing.

---

## Priority 2 — Liability and Third-Party Information

These fields are required to determine liability and support claim investigation.

### Third-Party Involvement

* Whether another vehicle or party was involved
* Third-party vehicle registration number
* Third-party vehicle type
* Third-party driver details
* Third-party insurer information

### Incident Responsibility

* Admission of fault
* Exchange of contact information
* Witness availability

These questions become especially important once third-party involvement has been established.

---

## Priority 3 — Damage and Loss Assessment

These fields help estimate claim severity and repair requirements.

### Vehicle Damage

* Damaged vehicle parts
* Damage severity
* Impact direction
* Airbag deployment

### Operational Status

* Whether the vehicle is drivable
* Vehicle moving or parked
* Approximate speed at impact

### Incident Conditions

* Weather conditions
* Road conditions
* Fire or flood severity indicators

---

## Priority 4 — Supporting Documentation and Evidence

These fields improve claim validation and settlement efficiency.

### Evidence Collection

* Photographs
* Videos
* Dashcam footage
* Witness statements

### Supporting Documentation

* Driver licence details
* Repair estimates
* Towing information
* Owner-driver relationship

These fields are useful but generally do not block claim registration.

---

## Priority 5 — Administrative and Preference Information

These fields affect claim processing convenience rather than claim validity.

### Settlement Preferences

* Cashless vs reimbursement preference
* Preferred workshop
* Inspection scheduling preferences

### Additional Context

* Road rage indicators
* Relationship between involved parties
* Same-insurer information
* Other non-essential investigative details

These questions are generally deferred until core claim information has been collected.

---

## Retrieval Rules

### Field Suppression

The system must not ask for information that has already been collected.

Questions targeting previously extracted fields are removed from consideration.

### Trigger-Based Filtering

Questions are filtered based on incident context.

Examples:

* Theft questions are shown only for theft claims.
* Fire questions are shown only for fire claims.
* Third-party questions are shown only when third-party involvement exists.

### Relevance Ranking

After filtering, candidate questions are ranked using:

* Business priority
* Relevance to the current claim state
* Ability to fill missing information

This ensures that the system asks the most useful next question rather than simply the most semantically similar one.

---

## Termination Policy

Claim intake may terminate when:

* All required fields for the active claim type have been collected.
* No high-priority unanswered questions remain.
* The user explicitly indicates completion.
* The maximum turn limit is reached.

Default configuration:

```text
max_turns = 20
```

A termination reason must be recorded for auditing and debugging purposes.

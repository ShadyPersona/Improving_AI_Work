# Recommended Security Actions

These recommendations consolidate the material findings into a practical action plan. Priorities indicate the proposed review sequence, not measured incident severity. Identification quarters reflect the supplied assessment history or the Q3 assessment. Status dates reflect this report's review, not assumed implementation dates.

**Security Awareness**

ASM's current evidence makes identity recovery and responsible AI usage appropriate awareness topics. Employees should use approved AI services and avoid submitting business-sensitive information unless permitted by the organization's data-use policy. Discovery confirms access to multiple AI services, but does not establish what information employees supplied. Explain the distinction between an approved service and an approved use case, and provide a clear escalation route for uncertain requests.

Use practical verification and reporting scenarios in ongoing awareness discussions, particularly alongside the impersonation-control review. If training is delivered, retain participation and follow-up records. NIST CSF 2.0 PR.AT-01 is the related awareness outcome. No training completion or effectiveness evidence was supplied.

## Active Recommendations

| Priority | Identified | Recommendation | Status |
| --- | --- | --- | --- |
| 1 | 2026 Q1 | Validate third-party coverage. Document Datto and Proofpoint scope, mapped controls, exclusions, policy evidence and operating tests. Update Secure Score treatment only where equivalent protection is supported. | This recommendation remains open because Datto and Proofpoint coverage is not sufficiently documented. |
| 2 | 2026 Q3 | Require SharePoint modern authentication. Test application dependencies and enforce CIS 7.2.1. | This recommendation remains open at 0/1 pending a review of SharePoint application dependencies. |
| 3 | 2026 Q3 | Verify mailbox auditing. Check organizational enablement, required actions and bypass exceptions. Test representative events separately from unified audit availability. | This recommendation remains open at 0/3 pending review of mailbox auditing and representative events. |
| 4 | 2026 Q3 | Validate all forwarding paths. Cover transport, outbound policy, inbox, OOF, OWA, administrator and automation paths. Block unauthorized forwarding and document exceptions. | This recommendation remains open at 0/5 because broader forwarding paths are not fully addressed. Automatic forwarding is complete. |
| 5 | 2026 Q3 | Close phishing and impersonation coverage gaps. Compare native requirements with Proofpoint, then configure required protections or document tested equivalence and residual gaps. | This recommendation remains open because phishing protections are incomplete and Proofpoint coverage is not sufficiently documented. |
| 6 | 2026 Q3 | Review remaining collaboration and data controls. Assess MailTips, add-ins, spam notifications, Office Safe Links, quarantine, bulk and sending limits, Lockbox and labeling scope. | This recommendation remains open pending review of the remaining collaboration and data controls. |

## CIS Microsoft 365 Foundation Benchmark

The following actions relate to the supplied CIS Microsoft 365 Foundations Benchmark v7.0.0 Level 1 guidance. They are targeted recommendations, not a full Level 1 compliance assessment. Level 2 recommendations, including custom anti-phishing policy, external calendar sharing and user-consent restriction, are identified separately in the signal review or history rather than represented as Level 1 requirements.

| CIS Ref. | Recommendation | Description | Status |
| --- | --- | --- | --- |
| 7.2.1 | Require modern authentication for SharePoint | Review compatibility and enforce the requirement. Microsoft reports the action open at 0/1. | This Level 1 recommendation remains open at 0/1. |
| 6.1.1; 6.1.2 | Validate organizational and mailbox auditing | Confirm that AuditDisabled is false, that auditing and required actions are enabled, and that representative events are available. | This Level 1 recommendation remains open pending an auditing review. |
| 6.1.3 | Validate audit bypass associations | Ensure bypass is not enabled without a documented written exception. Current bypass settings were not supplied. | This Level 1 recommendation remains open pending a review of audit bypass settings. |
| 6.2.1 | Block or disable all forwarding paths | Validate transport and outbound policies, user, administrator and automation paths, and documented exceptions. | This Level 1 recommendation remains open because broader forwarding paths are not fully addressed. |

## Deferred Recommendations

No current client-approved deferral was supplied. The earlier email-hygiene deferral was recorded as completed in Q2 through Proofpoint and is retained as history, not carried forward as an active deferral. The two open labeling actions without an applicable license require a scope and licensing decision. This assessment does not presume an approved deferral or recommend purchasing licenses solely to increase score.

## Recommendation History

Historical completions are retained for continuity. Current score credit corroborates the calendar-sharing and Q2 consent restrictions. Datto and Proofpoint describe completions recorded in Q2, not independently verified current service effectiveness. Q3 unified audit log progress is addressed in the signal review.

### CIS Recommendations

| Quarter | Recommendation | Action | Details |
| --- | --- | --- | --- |
| 2025 Q4 | Disable external calendar sharing | The recommendation is complete. | It was completed December 9, 2025 during the monthly touchpoint, as recorded in Q1 and Q2. Current Secure Score confirms the restriction at 5/5. CIS 1.3.3 is Level 2, and this is not a broader external-sharing audit. |
| 2026 Q2 | Restrict user consent to applications | The recommendation is complete. | It was implemented in Q2 and contributed to the Identity increase from 90.91% in Q1 to 96.97% in Q2. Current credit remains 4/4. CIS 5.1.5.1 is Level 2. The restriction does not automatically revoke earlier consent grants. |

### Advisory Recommendations

| Quarter | Recommendation | Action | Details |
| --- | --- | --- | --- |
| 2026 Q1 | Adopt endpoint detection and response | Completion is reported. | It originated in 2025 Q4 and was open in Q1. It was recorded as complete in Q2 through Datto RMM and Datto EDR. Present coverage and effectiveness are unvalidated. |

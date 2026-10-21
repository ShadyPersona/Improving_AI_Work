<!-- Run 2026-Q3-PunchOutATest-Bypass. Assembled from toned-part1-posture.md, toned-part2-signals.md and toned-part3-actions.md. PO-1 option 2: Executive Summary omitted as an accepted template deviation (Danny George, 2026-10-18T04:44Z). -->

Hialeah Housing Authority

Cloud Security Assessment – 2026: Q3

Prepared For

Luis Arellano

Prepared By

Danny George

October, 2026

# Current Microsoft Cloud Security Posture

HHA's Microsoft-reported identity controls are substantially complete. Apps remains the area with the largest concentration of open recommendations, and Data recommendations show no score movement since Q2. This assessment is limited to the available Microsoft 365 signals. It does not provide a comprehensive assurance opinion on all cloud and endpoint services.

## Posture Summary

HHA currently holds 163 earned points: Identity 65/66, Apps 91/189, and Data 7/9. Administrator and user MFA, legacy authentication blocking, user-consent restriction, and external calendar-sharing restriction are complete. Despite the high identity score, the open SharePoint modern-authentication action requires attention.

## Key Risk Themes

The key risk themes identify the primary security topics that should have focused discussions as part of this assessment. They do not intend to restate every Microsoft Secure Score recommendation or technical finding, but instead they summarize the broader patterns of risk that have emerged from the operational signals this past quarter. These themes are included to help distinguish between individual configuration opportunities and the larger areas where validation, prioritization, or security practice discussions may be needed.

* **Native phishing and impersonation controls remain incomplete.** Proofpoint's protected population, routing, policies, and exceptions must be compared with the relevant Microsoft requirements before HHA accepts equivalent coverage or enables overlapping controls. Until that comparison is complete, HHA cannot confirm that its third-party email protection matches the scope of the native Microsoft controls.

* **Logging and forwarding coverage is incomplete.** Unified audit log search is complete, but mailbox auditing is separately open. System-controlled automatic forwarding is also complete, while broader forwarding restriction remains open. Foundational logging is therefore in place, but coverage is not yet complete. HHA should review mailbox audit actions and all forwarding paths, document approved exceptions, and test representative events before treating these controls as operationally effective.

* **SharePoint modern authentication became relevant during Q3 and is open at 0/1.** This does not indicate that an existing control failed. Microsoft now considers the requirement applicable to the environment, and legacy authentication could allow older applications or connection methods to bypass stronger sign-in protections. HHA should identify any dependent applications or workflows, confirm their compatibility with modern authentication, and then enforce the requirement through a controlled implementation plan.

## Domain Posture

The domain posture summarizes only what the supplied evidence can support. Microsoft-reported completions are distinguished from operational assurance, and domains lacking current evidence are explicitly unassessed. No prior indicator is carried forward as a current conclusion without validation.

| Domain | Posture Indicator | Interpretation |
| --- | --- | --- |
| Identity & Access | Identity is strong, with one targeted gap. | HHA's identity score of 98.48% is strong. The remaining gap is the open SharePoint modern-authentication requirement. |
| Endpoint Security | Endpoint security is not assessed. | Q2 records Datto adoption, but no endpoint security data is available in Defender. |
| Vulnerability Management | Vulnerability management is not assessed. | No current device exposure, CVE, or remediation records are available. |
| Data Protection | Data protection scope is unverified. | HHA has completed the DLP recommendation. Improving does not have access to the Purview Portal, so DLP policy scope cannot be verified. |
| Email & Collaboration | A coverage review is needed. | Apps is 91/189. Native phishing, auditing, and forwarding gaps require a coverage review. |
| Detection & Operational Readiness | Only partial evidence is available. | The unified audit log is complete, mailbox auditing is open, and operational readiness is unverified. |
| Cloud Workload & Attack Paths | Cloud workload and attack-path exposure is not assessed. | No Azure workload or attack-path evidence is available. |
| AI Agents & Generative AI | AI agent and generative AI usage is not assessed. | No usage, permissions, or governance evidence is available. |

## Control Movement and Baseline Changes

Since Q2, HHA's overall Secure Score increased by 1.74 percentage points. This reflects steady improvement rather than a material change in risk. Earned points rose from 159 to 163, and available points declined from 265 to 264. The newly relevant SharePoint requirement is the only notable scoring pressure. Q3 history records unified audit log search completing on August 18 (+3) and SharePoint inactive-user sign-out becoming relevant with full credit on August 19 (+1). SharePoint modern authentication became relevant on August 19 at 0/1. These are scoring events, not established implementation dates. The identity trend's small August step down reflects newly relevant scoring requirements rather than a demonstrated loss of earned credit. Identity is 1.51 percentage points above Q2, Apps is 1.83 points higher, and Data's score is flat. HHA should address the SharePoint requirement through a planned compatibility review and continue to focus on the open controls that provide the greatest practical security benefit.

The Microsoft Secure Score overview and supplied trend are shown below. Peer comparisons provide context, not an overall maturity rating.

[Figure: Overall Secure Score comparison: HHA 61.74 percent; similarly sized organizations 52.21 percent.]

# Security Signal Review

The Security Signal Review supports the domain posture using the available Microsoft 365 recommendations and score history. Framework references use CIS Microsoft 365 Foundations Benchmark v7.0.0 and NIST Cybersecurity Framework 2.0. They identify related configuration guidance or outcomes. They are not certification, a full benchmark audit, or proof that controls operate effectively.

Microsoft-reported completions and open recommendations are read alongside the assessment history. Where third-party services, exceptions, licensing, or actual operating scope cannot be verified, this assessment keeps that limitation in view. It does not conclude either full mitigation or confirmed exploitation.

## Identity and Access

Identity is strong. Identity Secure Score is 98.48% (65/66), with 13 completed recommendations and one open recommendation. MFA for administrators (10/10) and for all users (9/9), legacy authentication blocking (8/8), and user-consent restriction (4/4) are complete. The consent restriction completed by Q2 remains complete, and the identity score rose from 90.91% in Q1 to 96.97% in Q2.

SharePoint modern authentication is the only open identity action, at 0/1. Both risk-policy recommendations are credited at 7/7, but they show no applicable license. That credit does not establish deployed Entra ID P2 sign-in or user-risk policies. The Q2 consent restriction remains in force, but it does not revoke consent grants that were already issued. The main follow-up is to review application compatibility before requiring modern authentication, and to check existing consent grants periodically against current business need.

Microsoft Identity Secure Score trend and contextual peer comparison.

[Figure: Supplied Q3 identity trend, showing high earned score credit and a small August step down as scoring requirements became relevant.]

[Figure: Identity Secure Score comparison: HHA 98.48 percent; similarly sized organizations 62.34 percent.]

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| Administrator and all-user MFA are complete: 10/10 and 9/9. | 5.2.2.1; 5.2.2.2 (Level 1) | PR.AA-03 | Score credit is complete. It reflects MFA policies implemented for users and administrators. |
| Legacy authentication blocking is complete: 8/8. | The benchmark mapping is not independently assessed. | PR.AA-03 | Score credit is complete for blocking legacy authentication. |
| User consent restriction is complete: 4/4. | 5.1.5.1 (Level 2) | PR.AA-05 | Score credit is complete for restricting user consent to applications. |
| SharePoint modern authentication is open: 0/1. | 7.2.1 (Level 1) | PR.AA-03 | This is not a regression. It became newly relevant during Q3 and should be reviewed and enforced. |
| Risk policies are credited at 7/7 each, but no applicable license is shown. | No benchmark mapping is supplied. | No NIST mapping is supplied. | The risk-policy credit reflects Entra Security Defaults. It does not show deployed Entra ID P2 policies. |

Prioritize SharePoint modern authentication, and verify the relevant application dependencies before enforcing it. Continue to validate privileged access and existing application grants through administrative evidence. Current score credit alone does not establish the detailed policy configuration or the effectiveness of these controls.

## Endpoint and Vulnerabilities

Endpoint coverage and vulnerability exposure cannot be assessed from the supplied Microsoft 365 score material. No device inventory, endpoint exposure distribution, CVE details, or affected-device records were provided. The exposure table below therefore records unavailable evidence. It does not report zero affected devices.

EDR adoption originated in 2025 Q4 and remained open in Q1. Q2 recorded completion through Datto RMM and Datto EDR. That advisory remains historically completed. Current deployment completeness, sensor health, monitoring, and vulnerability remediation cannot be accessed in Microsoft Defender, so this section cannot be completed.

| Exposure Level | 2026 Q1 | 2026 Q2 | 2026 Q3 |
| --- | --- | --- | --- |
| High | Data is not available. | Data is not available. | Data is not available. |
| Medium | Data is not available. | Data is not available. | Data is not available. |
| Low | Data is not available. | Data is not available. | Data is not available. |

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| The endpoint inventory was not provided. | No benchmark mapping is assessed. | No NIST mapping is assessed. | The device population and protection completeness cannot be validated. |
| Datto RMM and EDR completion is recorded for Q2. | No benchmark mapping is assessed. | DE.CM-09 (related outcome) | This is historical adoption only. Current sensor and monitoring coverage is unverified. |
| No CVE records were provided. | No benchmark mapping is assessed. | No NIST mapping is assessed. | No vulnerability count, exploitability, or severity conclusion can be drawn. |
| No exposure data was provided. | No benchmark mapping is assessed. | No NIST mapping is assessed. | Unavailable values are not treated as zero exposure. |
| No remediation data was provided. | No benchmark mapping is assessed. | No NIST mapping is assessed. | No supported remediation trend or closure conclusion can be drawn. |

## Data Protection and Collaboration

Data Secure Score is 77.78% (7/9), and Apps is 48.15% (91/189). DLP and Defender protection for SharePoint, OneDrive, and Teams are complete. Safe Links for email and Safe Attachments are also complete. These signals do not settle the remaining phishing, impersonation, or forwarding settings.

Material native gaps concern phishing thresholds, user and domain impersonation, associated intelligence-based actions, safety tips, and the custom anti-phishing policy. Mailbox intelligence is complete at 8/8, but its separate impersonation actions are not. Safe Links for email is 9/9, while Safe Links for Office applications is 0/3. Other open actions cover MailTips, Outlook add-ins, spam notifications, the 30-day quarantine, the bulk complaint threshold, and blocking users at the message limit. Broader forwarding restriction is 0/5, although system-controlled forwarding is 1/1. Customer Lockbox remains open even though the required license is available. Data-map labels and auto-labeling are not currently supported by the available licensing.

Taken together with the completed DLP recommendation, these results show that HHA has established part of its data protection foundation. They do not yet show that protection and labeling coverage extends across the intended business scope. HHA should prioritize enabling Customer Lockbox. It should also review where sensitive information is stored and shared, and decide whether broader labeling is needed based on business and regulatory requirements rather than Secure Score alone.

Data and Apps scores appear in the Secure Score overview above.

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| Unified audit is 3/3, and mailbox audit is 0/3. | 3.1.1; 6.1.1–6.1.3 (Level 1) | PR.PS-04 | Unified audit log availability is separate from mailbox action coverage and bypass validation. |
| Broad forwarding is 0/5, and automatic forwarding is 1/1. | 6.2.1 (Level 1) | PR.DS-02 | Validate the transport, outbound policy, inbox, and administrative forwarding paths and their exceptions. |
| Anti-phishing is 0/3, and impersonation is open. | 2.1.7 (E5 Level 2) | PR.PS-01 | Validate the native gaps against documented Proofpoint coverage. No equivalence is assumed. |
| DLP is 5/5, but labeling scope is unverified. | 3.2.1 (Level 1; DLP) | PR.DS-01; PR.DS-02; PR.DS-10 | Score credit does not demonstrate effective policy or labeling scope. |
| Calendar sharing restriction is 5/5. | 1.3.3 (Level 2) | PR.AA-05 | The current score corroborates the historical restriction. It is not a full collaboration-sharing audit. |

Coordinate the higher-impact email actions with Proofpoint, and document tested equivalent coverage where it applies. Address the remaining collaboration and data-governance controls according to business scope and licensing.

## Cloud Workload and Attack Path Exposure

Cloud workload and attack-path exposure could not be assessed. No Azure workload inventory, Defender for Cloud findings, exposure graph, or attack-path analysis was accessible. Microsoft 365 score credit cannot establish the state of Azure resources, public exposure, privileged workload access, or exploitable paths. No workload count, severity, remediation status, or change from prior assessments is asserted.

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| No workload inventory is available. | No benchmark mapping is assessed. | No NIST mapping is assessed. | The applicable resource population cannot be established. |
| No public exposure data is available. | No benchmark mapping is assessed. | No NIST mapping is assessed. | No public exposure finding or absence claim is made. |
| No attack-path data is available. | No benchmark mapping is assessed. | No NIST mapping is assessed. | No exploitable path or closure conclusion is drawn. |
| No workload configuration data is available. | No benchmark mapping is assessed. | No NIST mapping is assessed. | No workload control-effectiveness rating is given. |
| No workload remediation data is available. | No benchmark mapping is assessed. | No NIST mapping is assessed. | No supported trend comparison with prior assessments is possible. |

## AI Agents and Generative AI Usage

AI agent and generative AI usage could not be assessed. No usage inventory, approved-tool register, agent permissions, data-access configuration, or governance records were available. This gap does not demonstrate unmanaged AI use, and it does not demonstrate the absence of AI use. Microsoft 365 data-protection score credit also does not establish how information is shared with agents or external generative AI services.

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| No AI inventory is available. | No benchmark mapping is assessed. | No NIST mapping is assessed. | Usage and applicable scope cannot be established. |
| No agent permission data is available. | No benchmark mapping is assessed. | No NIST mapping is assessed. | No overprivileged-agent finding is asserted. |
| No AI sharing evidence is available. | No benchmark mapping is assessed. | No NIST mapping is assessed. | No client-specific data-leakage conclusion is drawn. |
| No AI governance records are available. | No benchmark mapping is assessed. | No NIST mapping is assessed. | No claim of approved or unmanaged use is made. |
| No AI monitoring data is available. | No benchmark mapping is assessed. | No NIST mapping is assessed. | No operational effectiveness or trend rating is given. |

## Detection and Operational Readiness

Unified audit log search is complete at 3/3, a positive score movement since Q2. Mailbox auditing remains separately open at 0/3. These are distinct controls. Availability of the unified audit capability does not demonstrate complete mailbox action coverage.

No incident records, response exercises, monitoring procedures, retention validation, or investigation samples were available. Q2's Datto and Proofpoint completion history is not evidence of current alert handling or response readiness.

The audit improvement supports a stronger Microsoft-reported baseline. Operating effectiveness remains unverified because the Datto and Proofpoint solutions were not accessible during this assessment. Review representative audit events and the accountable monitoring processes before treating these settings as proven detection capability.

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

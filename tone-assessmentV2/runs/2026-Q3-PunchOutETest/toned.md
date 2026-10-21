<!-- Step 05 tone-consistency output for run 2026-Q3-PunchOutETest. Executive Summary omitted per human decision (PO-1, option 2). Source draft sha256 bdf09afa53dfc797db082cb91082464306dedf177295839734a13bcebf6d5854 (converted.md). Substance freeze applied. -->

Hialeah Housing Authority

Cloud Security Assessment – 2026: Q3

Prepared For

Luis Arellano

Prepared By

Danny George

October, 2026


<!-- Page 2 -->
# Current Microsoft Cloud Security Posture

HHA's Microsoft-reported identity controls are substantially complete, while Apps continues to hold the largest concentration of open recommendations. Data recommendations show no score movement since Q2. The assessment is limited to the available Microsoft 365 signals and does not provide a comprehensive assurance opinion on all cloud and endpoint services.

## Posture Summary

HHA's current Microsoft 365 score is 163 earned points, composed of Identity 65/66, Apps 91/189, and Data 7/9. Administrator and user MFA, legacy authentication blocking, user-consent restriction, and external calendar-sharing restriction are marked complete, which places identity protections among the strongest areas of the posture. The open SharePoint modern-authentication action warrants attention despite the high identity score, because legacy connection methods could bypass stronger sign-in protections, as described under Key Risk Themes.

## Key Risk Themes

The themes below connect the material Microsoft 365 recommendations to practical validation and remediation discussions. They distinguish a reported configuration opportunity from a confirmed exploitable condition and avoid treating third-party product adoption as proof of effective coverage.

* **Native phishing and impersonation controls remain incomplete.** Proofpoint coverage should be compared against the relevant Microsoft requirements, including its protected population, routing, policies, and exceptions, before equivalent coverage is accepted or overlapping controls are enabled.

Foundational logging is in place, but coverage is not yet complete. Unified audit log search is complete, while mailbox auditing is separately open. System-controlled automatic forwarding is complete, while broader forwarding restriction remains open. HHA should review mailbox audit actions and all forwarding paths, document approved exceptions, and test representative events before treating these controls as operationally effective.

* **SharePoint modern authentication became relevant during Q3 and is open at 0/1.** This result does not indicate that an existing control failed. Microsoft has treated the requirement as applicable to the environment since August 19. Legacy authentication could allow older applications or connection methods to bypass stronger sign-in protections. HHA should identify dependent applications and workflows, confirm their compatibility with modern authentication, and then enforce the requirement through a controlled implementation plan.

## Domain Posture

The domain posture below summarizes only what the supplied evidence can support. Microsoft-reported completions are distinguished from operational assurance, and domains lacking current evidence are explicitly unassessed. No prior indicator is carried forward as a current conclusion without validation.

|  |  |  |
| --- | --- | --- |

| Domain | Posture Indicator | Interpretation |

<!-- Page 3 -->
| Identity & Access | Strong score; targeted gap | HHA achieved a strong score of 98.48%, and the remaining gap is that SharePoint modern authentication remains open. |
| Endpoint Security | Not assessed | Q2 records Datto adoption, but no endpoint security data from Defender was available. |
| Vulnerability Management | Not assessed | No current device exposure, CVE, or remediation records were available. |
| Data Protection | Scope unverified | HHA has completed the DLP recommendation, but Improving does not have access to the Purview Portal to verify DLP policies. |
| Email & Collaboration | Coverage review needed | Apps is 91/189. Native phishing, auditing, and forwarding gaps require coverage review. |
| Detection & Operational Readiness | Partial evidence | Unified audit log search is complete. Mailbox auditing is open. Operational readiness is unverified. |
| Cloud Workload & Attack Paths | Not assessed | There is no Azure workload or attack-path evidence. |
| AI Agents & Generative AI | Not assessed | There is no usage, permissions, or governance evidence. |

## Control Movement and Baseline Changes

HHA's overall Secure Score increased by 1.74 percentage points since Q2. Earned points rose from 159 to 163, while available points declined from 265 to 264. Identity is 1.51 percentage points above Q2, Apps is 1.83 points higher, and Data is flat. The quarter-over-quarter movement reflects steady improvement rather than a material change in risk, and the newly relevant SharePoint requirement accounts for the only notable scoring pressure. Q3 history records unified audit log search completing on August 18 (+3) and SharePoint inactive-user sign-out becoming relevant with full credit on August 19 (+1). SharePoint modern authentication became relevant on August 19 at 0/1. These are scoring events, not established implementation dates. The identity trend's small August step down reflects newly relevant scoring requirements, not a demonstrated loss of earned credit. HHA should address the SharePoint requirement through a planned compatibility review and continue focusing on the open controls that provide the greatest practical security benefit.

Microsoft Secure Score overview and supplied trend. Peer comparisons provide context, not an overall maturity rating.

![Overall Secure Score comparison: HHA 61.74 percent; similarly sized organizations 52.21 percent.](media/image3.png)

# Security Signal Review

The Security Signal Review supports the domain posture using the available Microsoft 365 recommendations and score history. Framework references use CIS Microsoft 365 Foundations Benchmark v7.0.0 and NIST Cybersecurity Framework 2.0. They identify related configuration guidance or outcomes, not certification, a full benchmark audit, or proof that controls operate effectively.

Microsoft-reported completions and open recommendations are interpreted alongside the client's assessment history. Where third-party services, exceptions, licensing, or actual operating scope cannot be verified, the assessment retains that limitation rather than declaring either full mitigation or confirmed exploitation.

## Identity and Access

Identity Secure Score is 98.48% (65/66), the highest domain score in the current posture, with 13 completed recommendations and one open recommendation. MFA for administrators (10/10) and all users (9/9), legacy authentication blocking (8/8), and user-consent restriction (4/4) are marked complete. The consent restriction, completed in Q2, contributed to the identity score increase from 90.91% in Q1 to 96.97% in Q2 and remains complete.


<!-- Page 5 -->
SharePoint modern authentication is the sole open identity action, at 0/1. Both risk-policy recommendations are credited at 7/7, but they show no applicable license. This credit does not establish deployed Entra ID P2 sign-in or user-risk policies. The Q2 consent restriction remains complete, but it does not revoke permissions granted before the restriction was implemented. The high identity score indicates that HHA has addressed most core identity protections. The remaining SharePoint requirement and the licensing limitation on risk policies leave specific areas that need attention. HHA should review application compatibility before requiring modern authentication, and it should periodically examine existing consent grants to confirm they remain appropriate for current business needs.

Microsoft Identity Secure Score trend and contextual peer comparison.

![Supplied Q3 identity trend, showing high earned score credit and a small August step down as scoring requirements became relevant.](media/image4.png)

![Identity Secure Score comparison: HHA 98.48 percent; similarly sized organizations 62.34 percent.](media/image5.png)

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| Administrator and all-user MFA complete: 10/10 and 9/9 | 5.2.2.1; 5.2.2.2 (Level 1) | PR.AA-03 | Score completion with implemented MFA policies for users and administrators. |
| Legacy authentication block complete: 8/8 | Not independently assessed | PR.AA-03 | Score completion blocking legacy authentication. |
| User consent restriction complete: 4/4 | 5.1.5.1 (Level 2) | PR.AA-05 | Score completion restricting user consent for applications. |
| SharePoint modern authentication open: 0/1 | 7.2.1 (Level 1) | PR.AA-03 | This is not a regression. The requirement became relevant during Q3. Review dependencies and enforce it. |
| Risk policies: 7/7 each; no applicable license | Not assessed | Not assessed | Risk policies recommendation is complete due to Entra Security Defaults. |


<!-- Page 6 -->
Prioritize SharePoint modern authentication and verify the relevant application dependencies before enforcement. Continue validating privileged access and existing application grants through administrative evidence; current score credit alone does not establish the detailed policy configuration or effectiveness of these controls.

## Endpoint and Vulnerabilities

Current endpoint coverage and vulnerability exposure cannot be assessed from the supplied Microsoft 365 score material. No device inventory, endpoint exposure distribution, CVE details, or affected-device records were provided. The exposure table therefore records unavailable evidence rather than zero affected devices.

EDR adoption originated in 2025 Q4 and remained open in Q1. Q2 recorded completion through Datto RMM and Datto EDR, and the advisory therefore remains historically completed. Current deployment completeness, sensor health, monitoring, and vulnerability remediation are not accessible in Microsoft Defender, so this section cannot be completed. Historical adoption does not establish current coverage.

|  |  |  |  |
| --- | --- | --- | --- |
| Exposure Level | 2026 Q1 | 2026 Q2 | 2026 Q3 |
| High | Not Available | Not Available | Not Available |
| Medium | Not Available | Not Available | Not Available |
| Low | Not Available | Not Available | Not Available |

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| Endpoint inventory not provided | Not assessed | Not assessed | Device population and protection completeness cannot be validated. |
| Datto RMM / EDR: Q2 completion | Not assessed | DE.CM-09 (related outcome) | Historical adoption only; current sensor and monitoring coverage unverified. |
| CVE records not provided | Not assessed | Not assessed | No vulnerability count, exploitability, or severity conclusion is supported. |
| Exposure data not provided | Not assessed | Not assessed | Unavailable values do not indicate zero exposure. |
| Remediation data not provided | Not assessed | Not assessed | No remediation trend or closure conclusion is supported. |

## Data Protection and Collaboration

Data Secure Score remains 77.78% (7/9), while Apps is 48.15% (91/189). DLP and Defender protection for SharePoint, OneDrive, and Teams are marked complete, as are Safe Links for email and Safe Attachments. These completions do not resolve the remaining phishing, impersonation, or forwarding settings.


<!-- Page 7 -->
The material native gaps concern phishing thresholds, user and domain impersonation, associated intelligence-based actions, safety tips, and custom anti-phishing policy. Mailbox intelligence is complete at 8/8, but its separate impersonation actions are not. Safe Links for email is 9/9, while Office applications is 0/3. Other open actions cover MailTips, Outlook add-ins, spam notifications, 30-day quarantine, bulk complaint threshold, and blocking users at the message limit. Broader forwarding restriction is 0/5, despite system-controlled forwarding at 1/1. Customer Lockbox remains open although the required license is available. Data-map labels and auto-labeling are not supported under the available licensing. Taken together with the completed DLP recommendation, these results show that HHA has established part of its data protection foundation. They do not yet provide clear evidence that protection and labeling coverage extends across the intended business scope. HHA should prioritize enabling Customer Lockbox. It should also review where sensitive information is stored and shared, and determine whether broader labeling capabilities are needed based on business and regulatory requirements rather than Secure Score alone.

Data and Apps scores appear in the Secure Score overview above.

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| Unified audit 3/3; mailbox audit 0/3 | 3.1.1; 6.1.1–6.1.3 (Level 1) | PR.PS-04 | Separate log availability from mailbox actions and bypass validation. |
| Forwarding: broad 0/5; automatic 1/1 | 6.2.1 (Level 1) | PR.DS-02 | Validate transport, outbound policy, inbox and administrative forwarding paths and exceptions. |
| Anti-phishing 0/3; impersonation open | 2.1.7 (E5 Level 2) | PR.PS-01 | Validate native gaps against documented Proofpoint coverage; no equivalence assumed. |
| DLP 5/5; labeling scope unverified | 3.2.1 (Level 1; DLP) | PR.DS-01; PR.DS-02; PR.DS-10 | Score credit does not demonstrate effective policy or labeling scope. |
| Calendar sharing restricted: 5/5 | 1.3.3 (Level 2) | PR.AA-05 | Current score corroborates the historical restriction. It does not constitute a full collaboration-sharing audit. |

Coordinate the higher-impact email actions with Proofpoint and document tested equivalent coverage where appropriate. Address the remaining collaboration and data-governance controls according to business scope and licensing.

## Cloud Workload and Attack Path Exposure

Cloud workload and attack-path exposure could not be assessed. No Azure workload inventory, Defender for Cloud findings, exposure graph, or attack-path analysis were accessible.


<!-- Page 8 -->
Microsoft 365 score credit cannot establish the state of Azure resources, public exposure, privileged workload access, or exploitable paths. No workload count, severity, remediation status, or change from the prior assessments is asserted.

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| Workload inventory unavailable | Not assessed | Not assessed | Applicable resource population cannot be established. |
| Public exposure unavailable | Not assessed | Not assessed | No public exposure finding or absence claim is supported. |
| Attack-path data unavailable | Not assessed | Not assessed | No exploitable path or closure conclusion is supported. |
| Workload configuration unavailable | Not assessed | Not assessed | No workload control-effectiveness rating is supported. |
| Workload remediation unavailable | Not assessed | Not assessed | No trend comparison with prior assessments is supported. |

## AI Agents and Generative AI Usage

AI agent and generative AI usage could not be assessed. No usage inventory, approved-tool register, agent permissions, data-access configuration, or governance records were available.

This gap does not demonstrate unmanaged AI use or the absence of AI use. Microsoft 365 data-protection score credit also does not establish how information is shared with agents or external generative AI services.

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| AI inventory unavailable | Not assessed | Not assessed | Usage and applicable scope cannot be established. |
| Agent permissions unavailable | Not assessed | Not assessed | No overprivileged-agent finding is asserted. |
| AI sharing evidence unavailable | Not assessed | Not assessed | No client-specific data-leakage conclusion is supported. |
| AI governance unavailable | Not assessed | Not assessed | No claim of approved or unmanaged use is supported. |
| AI monitoring unavailable | Not assessed | Not assessed | No operational effectiveness or trend rating is supported. |

## Detection and Operational Readiness

Unified audit log search is marked complete at 3/3, representing positive score movement since Q2. Mailbox auditing remains separately open at 0/3. These are distinct controls, and availability of the unified audit capability does not demonstrate complete mailbox action coverage.


<!-- Page 9 -->
No incident records, response exercises, monitoring procedures, retention validation, or investigation samples were available. Q2's Datto and Proofpoint completion history is not evidence of current alert handling or response readiness.

The audit improvement supports a stronger Microsoft-reported baseline, but operating effectiveness remains unverified because Datto and Proofpoint solutions were not accessible during this assessment. Review representative audit events and accountable monitoring processes before treating these settings as proven detection capability.

# Recommended Security Actions

These recommendations consolidate the material findings into a practical action plan. Priorities indicate the proposed review sequence, not measured incident severity. Identification quarters reflect the supplied assessment history or the Q3 assessment; status dates reflect this report's review, not assumed implementation dates.

|  |
| --- |

<!-- Page 10 -->
| ***Security Awareness***  *ASM's current evidence makes identity recovery and responsible AI usage appropriate awareness topics. Employees should use approved AI services and avoid submitting business-sensitive information unless permitted by the organization's data-use policy. Discovery confirms access to multiple AI services, but does not establish what information employees supplied. Explain the distinction between an approved service and an approved use case, and provide a clear escalation route for uncertain requests.* |

Use practical verification and reporting scenarios in ongoing awareness discussions, particularly alongside the impersonation-control review. If training is delivered, retain participation and follow-up records. NIST CSF 2.0 PR.AT-01 is the related awareness outcome; no training completion or effectiveness evidence was supplied.

## Active Recommendations

| **Priority** | **Identified** | **Recommendation** | **Status** |
| --- | --- | --- | --- |
| 1 | 2026 Q1 | Validate third-party coverage. Document Datto and Proofpoint scope, mapped controls, exclusions, policy evidence and operating tests. Update Secure Score treatment only where equivalent protection is supported. | This recommendation remains open because Datto and Proofpoint coverage is not sufficiently documented. |
| 2 | 2026 Q3 | Require SharePoint modern authentication. Test application dependencies and enforce CIS 7.2.1. | This recommendation remains open at 0/1 pending a review of SharePoint application dependencies. |
| 3 | 2026 Q3 | Verify mailbox auditing. Check organizational enablement, required actions and bypass exceptions; test representative events separately from unified audit availability. | This recommendation remains open at 0/3 pending review of mailbox auditing and representative events. |
| 4 | 2026 Q3 | Validate all forwarding paths. Cover transport, outbound policy, inbox/OOF/OWA, administrator and automation paths. Block unauthorized forwarding and document exceptions. | This recommendation remains open at 0/5 because broader forwarding paths are not fully addressed, although automatic forwarding is complete. |

<!-- Page 11 -->
| 5 | 2026 Q3 | Close phishing and impersonation coverage gaps. Compare native requirements with Proofpoint, then configure required protections or document tested equivalence and residual gaps. | This recommendation remains open because phishing protections are incomplete and Proofpoint coverage is not sufficiently documented. |
| 6 | 2026 Q3 | Review remaining collaboration and data controls. Assess MailTips, add-ins, spam notifications, Office Safe Links, quarantine, bulk and sending limits, Lockbox and labeling scope. | This recommendation remains open pending review of the remaining collaboration and data controls. |

## CIS Microsoft 365 Foundation Benchmark

The following actions relate to the supplied CIS Microsoft 365 Foundations Benchmark v7.0.0 Level 1 guidance. They are targeted recommendations, not a full Level 1 compliance assessment. Level 2 recommendations, including custom anti-phishing policy, external calendar sharing and user-consent restriction, are identified separately in the signal review or history rather than represented as Level 1 requirements.

| **CIS Ref.** | **Recommendation** | **Description** | **Status** |
| --- | --- | --- | --- |
| 7.2.1 | Require modern authentication for SharePoint | Review compatibility and enforce the requirement. Microsoft reports the action open at 0/1. | This Level 1 recommendation remains open at 0/1. |
| 6.1.1; 6.1.2 | Validate organizational and mailbox auditing | Confirm AuditDisabled is false, auditing and required actions are enabled, and representative events are available. | This Level 1 recommendation remains open pending an auditing review. |

<!-- Page 12 -->
| 6.1.3 | Validate audit bypass associations | Ensure bypass is not enabled without a documented written exception. Current bypass settings were not supplied. | This Level 1 recommendation remains open pending a review of audit bypass settings. |
| 6.2.1 | Block or disable all forwarding paths | Validate transport and outbound policies, user/admin and automation paths, and documented exceptions. | This Level 1 recommendation remains open because broader forwarding paths are not fully addressed. |

## Deferred Recommendations

No current client-approved deferral was supplied. The earlier email-hygiene deferral was recorded as completed in Q2 through Proofpoint and is retained as history, not carried forward as an active deferral. The two open labeling actions without an applicable license require a scope and licensing decision; this assessment does not presume an approved deferral or recommend purchasing licenses solely to increase score.

## Recommendation History

Historical completions are retained for continuity. Current score credit corroborates the calendar-sharing and Q2 consent restrictions. Datto and Proofpoint describe completions recorded in Q2, not independently verified current service effectiveness. Q3 unified audit log progress is addressed in the signal review.

### CIS Recommendations

| **Quarter** | **Recommendation** | **Action** | **Details** |
| --- | --- | --- | --- |
| 2025 Q4 | Disable external calendar sharing | Complete | Completed December 9, 2025 during the monthly touchpoint, as recorded in Q1 and Q2. Current Secure Score confirms the restriction at 5/5. CIS 1.3.3 is Level 2; this is not a broader external-sharing audit. |

<!-- Page 13 -->
| 2026 Q2 | Restrict user consent to applications | Complete | Implemented in Q2, contributing to the Identity increase from 90.91% in Q1 to 96.97% in Q2. Current credit remains 4/4. CIS 5.1.5.1 is Level 2. The restriction does not automatically revoke earlier consent grants. |

### Advisory Recommendations

| **Quarter** | **Recommendation** | **Action** | **Details** |
| --- | --- | --- | --- |
| 2026 Q1 | Adopt endpoint detection and response | Reported complete | Originated in 2025 Q4; open in Q1 and recorded complete in Q2 through Datto RMM / Datto EDR. Present coverage and effectiveness were not validated. |
| 2026 Q1 | Strengthen email hygiene | Reported complete | Deferred in Q1; recorded complete in Q2 using Proofpoint. Current policy scope and native-control equivalence were not validated. Adoption is not reopened. |

Hialeah Housing Authority

Cloud Security Assessment – 2026: Q3

Prepared For

Luis Arellano

Prepared By

Danny George

October, 2026

# Executive Summary

This assessment evaluated Hialeah Housing Authority’s (HHA) Microsoft cloud security posture for July 1 through September 30, 2026. The Q2 assessment served as the previous-quarter baseline, and Q1 supplied longer-term context. The assessment combined the supplied Q3 score trends and control history with the Microsoft 365 evidence supplied for Q3.

Secure Score provides useful evidence of Microsoft-reported control status, but it does not measure overall risk or control effectiveness. The supplied evidence did not include endpoint inventory, vulnerability exposure, incident records, Azure workload or attack-path evidence, AI usage, or operational validation of third-party controls. HHA’s posture in those areas is therefore unassessed, and it is not presumed secure or unchanged.

The primary risk theme for Q3 is validating the coverage behind the remaining Microsoft-native email and collaboration gaps. Q2 recorded the endpoint and email-hygiene advisories as complete through Datto RMM, Datto EDR and Proofpoint. Those completions remain part of HHA’s history, but their present coverage and effectiveness still require validation. In Identity, SharePoint modern authentication became relevant during Q3 and is the only open recommendation.

Overall Secure Score rose from 60.00% (159 of 265) in Q2 to 61.74% (163 of 264 points) in Q3, and Q1 was 58.49% (155 of 265). Identity increased from 90.91% in Q1 to 96.97% in Q2 following the consent restriction, and reached 98.48% in Q3. Apps increased from 46.32% in both earlier reports to 48.15%, and Data remained at 77.78%. The catalog contains 38 completed and 26 open recommendations, and none of those recommendations regressed in Q3. This indicates that HHA maintained its Microsoft-reported posture through the quarter, although the movement reflects Secure Score and does not by itself demonstrate reduced exposure.

HHA should prioritize validation of mailbox auditing, all forwarding paths, native phishing settings and their relationship to Proofpoint, and the SharePoint authentication requirement. The objective is demonstrable protection and usable monitoring, not Secure Score points alone. HHA should retain evidence of control scope, tested exceptions, and accountable ownership before closing each recommendation, so that closure reflects verified protection.

# Current Microsoft Cloud Security Posture

In Q3, Microsoft-reported identity controls were substantially complete, and Apps held the largest concentration of open recommendations. Data recommendations showed no score movement since Q2. This is a focused assessment of the available Microsoft 365 signals and not a comprehensive assurance opinion on all cloud and endpoint services.

## Posture Summary

Q3 earned points totaled 163, comprising Identity 65/66, Apps 91/189, and Data 7/9. Administrator and user MFA, legacy authentication blocking, user-consent restriction, and external calendar-sharing restriction are marked complete, which gives HHA a solid identity foundation. The open SharePoint modern-authentication action still needs attention, because legacy authentication could allow older applications or connection methods to bypass the stronger sign-in protections already in place.

## Key Risk Themes

The themes below connect the material Microsoft 365 recommendations to practical validation and remediation discussions. They distinguish a reported configuration opportunity from a confirmed exploitable condition and avoid treating third-party product adoption as proof of effective coverage.

* **Native phishing and impersonation controls remained incomplete in Q3.** HHA should compare Proofpoint’s protected population, routing, policies, and exceptions with the relevant Microsoft requirements before accepting equivalent coverage or enabling overlapping controls, because third-party adoption alone does not establish effective protection.

Logging and forwarding controls show the same pattern of partial coverage. Unified audit log search is complete, but mailbox auditing is separately open. System-controlled automatic forwarding is also complete, while broader forwarding restriction remains open. This split indicates that foundational logging is in place, but coverage is not yet complete. HHA should review mailbox audit actions and all forwarding paths, document approved exceptions, and test representative events before treating these controls as operationally effective.

* **SharePoint modern authentication became relevant during Q3 and is open at 0/1.** This does not indicate that an existing control failed. Microsoft considered the requirement applicable to the environment once it became relevant in Q3, and legacy authentication could allow older applications or connection methods to bypass stronger sign-in protections. HHA should identify any dependent applications or workflows, confirm their compatibility with modern authentication, and then enforce the requirement through a controlled implementation plan.

## Domain Posture

The domain posture below summarizes only what the supplied evidence can support. Microsoft-reported completions are distinguished from operational assurance, and domains lacking Q3 evidence are explicitly unassessed. No prior indicator is carried forward as a Q3 conclusion without validation.

|  |  |  |
| --- | --- | --- |
| Domain | Posture Indicator | Interpretation |
| Identity & Access | Strong score; targeted gap | HHA achieved a strong Identity score of 98.48%. The remaining gap is the open SharePoint modern authentication requirement. |
| Endpoint Security | Not assessed | Q2 recorded Datto adoption, and no endpoint security data was available in Defender. |
| Vulnerability Management | Not assessed | No device exposure, CVE, or remediation records were provided for Q3. |
| Data Protection | Scope unverified | HHA completed the DLP recommendation, but Improving did not have access to the Purview Portal to verify DLP policies. |
| Email & Collaboration | Coverage review needed | The Apps score is 91/189, and the native phishing, auditing, and forwarding gaps require coverage review. |
| Detection & Operational Readiness | Partial evidence | The unified audit log is complete, mailbox auditing is open, and operational readiness was not verified. |
| Cloud Workload & Attack Paths | Not assessed | No Azure workload or attack-path evidence was provided. |
| AI Agents & Generative AI | Not assessed | No usage, permissions, or governance evidence was provided. |

## Control Movement and Baseline Changes

Overall Secure Score rose by 1.74 percentage points from Q2 to Q3, as earned points increased from 159 to 163 while available points declined from 265 to 264. Q3 history records unified audit log search completing on August 18 (+3), and SharePoint inactive-user sign-out becoming relevant with full credit on August 19 (+1). SharePoint modern authentication became relevant on August 19 at 0/1. These are scoring events and do not establish implementation dates. The small August step down in the identity trend reflects newly relevant scoring requirements and does not demonstrate a loss of earned credit. Identity is 1.51 percentage points above Q2, Apps is 1.83 points higher, and Data’s score is flat. The movement reflects steady improvement and not a material change in risk, and the newly relevant SharePoint requirement accounts for the only notable scoring pressure. HHA should address that requirement through a planned compatibility review and continue focusing on the open controls that provide the greatest practical security benefit.

Microsoft Secure Score overview and supplied trend. Peer comparisons provide context, not an overall maturity rating.

![Overall Secure Score comparison: HHA 61.74 percent; similarly sized organizations 52.21 percent.](media/image3.png)

# Security Signal Review

The Security Signal Review supports the domain posture using the available Microsoft 365 recommendations and score history. Framework references use CIS Microsoft 365 Foundations Benchmark v7.0.0 and NIST Cybersecurity Framework 2.0. They identify related configuration guidance or outcomes, not certification, a full benchmark audit, or proof that controls operate effectively.

Microsoft-reported completions and open recommendations are interpreted alongside HHA’s assessment history. Where third-party services, exceptions, licensing, or actual operating scope could not be verified in Q3, the assessment retains that limitation rather than declaring either full mitigation or confirmed exploitation.

## Identity and Access

Identity reached a Secure Score of 98.48% (65/66) in Q3, up from 96.97% in Q2 and 90.91% in Q1, with 13 completed recommendations and one open recommendation. MFA for administrators (10/10) and all users (9/9), legacy authentication blocking (8/8), and user-consent restriction (4/4) are marked complete. The consent restriction was completed by Q2 and remains complete, and it contributed to the identity increase from 90.91% in Q1 to 96.97% in Q2.

SharePoint modern authentication is the sole open identity action, at 0/1. Both risk-policy recommendations are credited at 7/7 but show no applicable license, so the credit does not establish deployed Entra ID P2 sign-in or user-risk policies. The Q2 consent restriction remains complete, but it does not revoke previously granted permissions. The Identity score shows that HHA has addressed most core identity protections, while the SharePoint requirement and the licensing limitation on risk policies are the specific areas that need attention. HHA should review application compatibility before requiring modern authentication, and it should periodically examine existing consent grants to confirm they remain appropriate for its business needs.

Microsoft Identity Secure Score trend and contextual peer comparison.

![Supplied Q3 identity trend, showing high earned score credit and a small August step down as scoring requirements became relevant.](media/image4.png)

![Identity Secure Score comparison: HHA 98.48 percent; similarly sized organizations 62.34 percent.](media/image5.png)

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| Administrator and all-user MFA complete: 10/10 and 9/9 | 5.2.2.1; 5.2.2.2 (Level 1) | PR.AA-03 | Microsoft reports this control complete, with MFA policies implemented for users and administrators. |
| Legacy authentication block complete: 8/8 | Not independently assessed | PR.AA-03 | Microsoft reports this control complete, and legacy authentication is blocked. |
| User consent restriction complete: 4/4 | 5.1.5.1 (Level 2) | PR.AA-05 | Microsoft reports this control complete, and user consent for applications is restricted. |
| SharePoint modern authentication open: 0/1 | 7.2.1 (Level 1) | PR.AA-03 | This is not a regression. The requirement became relevant during Q3, and HHA should review and enforce it. |
| Risk policies: 7/7 each; no applicable license | Not assessed | Not assessed | Risk policies recommendation is complete due to Entra Security Defaults. |

HHA should prioritize SharePoint modern authentication and verify the relevant application dependencies before enforcement. HHA should also continue validating privileged access and existing application grants through administrative evidence, because score credit alone does not establish the detailed policy configuration or effectiveness of these controls.

## Endpoint and Vulnerabilities

Endpoint coverage and vulnerability exposure could not be assessed for Q3 from the supplied Microsoft 365 score material, because no device inventory, endpoint exposure distribution, CVE details, or affected-device records were provided. The exposure table therefore records unavailable evidence and does not indicate zero affected devices. HHA should treat endpoint and vulnerability posture as unassessed for Q3.

The EDR adoption advisory originated in 2025 Q4 and remained open in Q1. Q2 recorded completion through Datto RMM and Datto EDR, and that advisory remains completed in the assessment history. Deployment completeness, sensor health, monitoring, and vulnerability remediation are not accessible in Microsoft Defender, so this section of the assessment could not be completed for Q3. HHA should validate Datto scope and coverage as described in the Active Recommendations.

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
| Datto RMM / EDR: Q2 completion | Not assessed | DE.CM-09 (related outcome) | This is historical adoption only, and sensor and monitoring coverage for Q3 was not verified. |
| CVE records not provided | Not assessed | Not assessed | No conclusion about vulnerability count, exploitability, or severity can be drawn. |
| Exposure data not provided | Not assessed | Not assessed | Unavailable values are not zero exposure. |
| Remediation data not provided | Not assessed | Not assessed | No remediation trend or closure conclusion is supported. |

## Data Protection and Collaboration

Data and collaboration protection is partly established in Q3, with Data holding at 77.78% (7/9) since Q2 and Apps at 48.15% (91/189), up from 46.32% in Q1 and Q2. DLP and Defender protection for SharePoint, OneDrive, and Teams are marked complete, as are Safe Links for email and Safe Attachments. These completions do not settle the remaining phishing, impersonation, or forwarding settings.

The material native gaps concern phishing thresholds, user and domain impersonation, associated intelligence-based actions, safety tips, and the custom anti-phishing policy. Mailbox intelligence is complete at 8/8, but its separate impersonation actions are not. Safe Links for email is 9/9, while Office applications is 0/3. Other open actions cover MailTips, Outlook add-ins, spam notifications, 30-day quarantine, the bulk complaint threshold, and blocking users at the message limit. Broader forwarding restriction is 0/5, although system-controlled forwarding is 1/1. Customer Lockbox remains open even though the required license is available, while data-map labels and auto-labeling are not supported by the licensing available in Q3. Together with the completed DLP recommendation, these results indicate that HHA has established part of its data protection foundation but lacks clear evidence that protection and labeling coverage extends across the intended business scope. HHA should prioritize enabling Customer Lockbox, review where sensitive information is stored and shared, and determine whether broader labeling capabilities are needed based on business and regulatory requirements rather than Secure Score alone.

Data and Apps scores appear in the Secure Score overview above.

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| Unified audit 3/3; mailbox audit 0/3 | 3.1.1; 6.1.1–6.1.3 (Level 1) | PR.PS-04 | Log availability should be assessed separately from mailbox action coverage and bypass validation. |
| Forwarding: broad 0/5; automatic 1/1 | 6.2.1 (Level 1) | PR.DS-02 | Transport, outbound policy, inbox, and administrative forwarding paths and their exceptions should be validated. |
| Anti-phishing 0/3; impersonation open | 2.1.7 (E5 Level 2) | PR.PS-01 | Native gaps should be validated against documented Proofpoint coverage. Equivalence is not assumed. |
| DLP 5/5; labeling scope unverified | 3.2.1 (Level 1; DLP) | PR.DS-01; PR.DS-02; PR.DS-10 | Score credit does not demonstrate effective policy or labeling scope. |
| Calendar sharing restricted: 5/5 | 1.3.3 (Level 2) | PR.AA-05 | The Q3 score corroborates the historical restriction. It does not constitute a full collaboration-sharing audit. |

HHA should coordinate the higher-impact email actions with Proofpoint and document tested equivalent coverage where appropriate. The remaining collaboration and data-governance controls should be addressed according to business scope and licensing.

## Cloud Workload and Attack Path Exposure

Cloud workload and attack-path exposure could not be assessed for Q3, because no Azure workload inventory, Defender for Cloud findings, exposure graph, or attack-path analysis was accessible. HHA’s Azure exposure is therefore unassessed, and it is not presumed secure.

Microsoft 365 score credit cannot establish the state of Azure resources, public exposure, privileged workload access, or exploitable paths. No workload count, severity, remediation status, or change from the prior assessments is asserted. The domain remains unassessed until Azure workload evidence is accessible.

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| Workload inventory unavailable | Not assessed | Not assessed | Applicable resource population cannot be established. |
| Public exposure unavailable | Not assessed | Not assessed | No public exposure finding is made, and no claim is made that exposure is absent. |
| Attack-path data unavailable | Not assessed | Not assessed | No exploitable path or closure conclusion can be drawn. |
| Workload configuration unavailable | Not assessed | Not assessed | No workload control-effectiveness rating can be given. |
| Workload remediation unavailable | Not assessed | Not assessed | No supported trend comparison with prior assessments can be made. |

## AI Agents and Generative AI Usage

AI agent and generative AI usage could not be assessed for Q3, because no usage inventory, approved-tool register, agent permissions, data-access configuration, or governance records were available.

This gap does not demonstrate unmanaged AI use or the absence of AI use. Microsoft 365 data-protection score credit also does not establish how information is shared with agents or external generative AI services.

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| AI inventory unavailable | Not assessed | Not assessed | Usage and applicable scope cannot be established. |
| Agent permissions unavailable | Not assessed | Not assessed | No overprivileged-agent finding is asserted. |
| AI sharing evidence unavailable | Not assessed | Not assessed | No client-specific data-leakage conclusion can be drawn. |
| AI governance unavailable | Not assessed | Not assessed | No claim of approved or unmanaged use is made. |
| AI monitoring unavailable | Not assessed | Not assessed | No operational effectiveness or trend rating can be given. |

## Detection and Operational Readiness

Detection readiness is partly evidenced, because unified audit log search is marked complete at 3/3, which represents positive score movement since Q2. Mailbox auditing remains separately open at 0/3. These are distinct controls, and the availability of unified audit capability does not demonstrate complete mailbox action coverage.

No incident records, response exercises, monitoring procedures, retention validation, or investigation samples were available. The Q2 Datto and Proofpoint completion history is not evidence of alert handling or response readiness in Q3.

The Q3 audit improvement supports a stronger Microsoft-reported baseline, but operating effectiveness remains unverified because the Datto and Proofpoint solutions were inaccessible during this assessment. HHA should review representative audit events and accountable monitoring processes before treating these settings as proven detection capability.

# Recommended Security Actions

These recommendations consolidate the material findings into a practical action plan. Priorities indicate the proposed review sequence, not measured incident severity. Identification quarters reflect the supplied assessment history or the Q3 assessment; status dates reflect this report’s review, not assumed implementation dates.

|  |
| --- |
| ***Security Awareness***  *ASM’s current evidence makes identity recovery and responsible AI usage appropriate awareness topics. Employees should use approved AI services and avoid submitting business-sensitive information unless permitted by the organization’s data-use policy. Discovery confirms access to multiple AI services, but does not establish what information employees supplied. Explain the distinction between an approved service and an approved use case, and provide a clear escalation route for uncertain requests.* |

Use practical verification and reporting scenarios in ongoing awareness discussions, particularly alongside the impersonation-control review. If training is delivered, retain participation and follow-up records. NIST CSF 2.0 PR.AT-01 is the related awareness outcome; no training completion or effectiveness evidence was supplied.

## Active Recommendations

| **Priority** | **Identified** | **Recommendation** | **Status** |
| --- | --- | --- | --- |
| 1 | 2026 Q1 | **Validate third-party coverage.** Document Datto and Proofpoint scope, mapped controls, exclusions, policy evidence and operating tests. Update Secure Score treatment only where equivalent protection is supported. | This recommendation remains open because Datto and Proofpoint coverage is not sufficiently documented. |
| 2 | 2026 Q3 | **Require SharePoint modern authentication.** Test application dependencies and enforce CIS 7.2.1. | This recommendation remains open at 0/1 pending a review of SharePoint application dependencies. |
| 3 | 2026 Q3 | **Verify mailbox auditing.** Check organizational enablement, required actions and bypass exceptions; test representative events separately from unified audit availability. | This recommendation remains open at 0/3 pending review of mailbox auditing and representative events. |
| 4 | 2026 Q3 | **Validate all forwarding paths.** Cover transport, outbound policy, inbox/OOF/OWA, administrator and automation paths. Block unauthorized forwarding and document exceptions. | This recommendation remains open at 0/5 because broader forwarding paths are not fully addressed, although automatic forwarding is complete. |
| 5 | 2026 Q3 | **Close phishing and impersonation coverage gaps.** Compare native requirements with Proofpoint, then configure required protections or document tested equivalence and residual gaps. | This recommendation remains open because phishing protections are incomplete and Proofpoint coverage is not sufficiently documented. |
| 6 | 2026 Q3 | **Review remaining collaboration and data controls.** Assess MailTips, add-ins, spam notifications, Office Safe Links, quarantine, bulk and sending limits, Lockbox and labeling scope. | This recommendation remains open pending review of the remaining collaboration and data controls. |

## CIS Microsoft 365 Foundation Benchmark

The following actions relate to the supplied CIS Microsoft 365 Foundations Benchmark v7.0.0 Level 1 guidance. They are targeted recommendations, not a full Level 1 compliance assessment. Level 2 recommendations, including custom anti-phishing policy, external calendar sharing and user-consent restriction, are identified separately in the signal review or history rather than represented as Level 1 requirements.

| **CIS Ref.** | **Recommendation** | **Description** | **Status** |
| --- | --- | --- | --- |
| 7.2.1 | Require modern authentication for SharePoint | Review compatibility and enforce the requirement. Microsoft reports the action open at 0/1. | This Level 1 recommendation remains open at 0/1. |
| 6.1.1; 6.1.2 | Validate organizational and mailbox auditing | Confirm AuditDisabled is false, auditing and required actions are enabled, and representative events are available. | This Level 1 recommendation remains open pending an auditing review. |
| 6.1.3 | Validate audit bypass associations | Ensure bypass is not enabled without a documented written exception. Bypass settings were not supplied. | This Level 1 recommendation remains open pending a review of audit bypass settings. |
| 6.2.1 | Block or disable all forwarding paths | Validate transport and outbound policies, user/admin and automation paths, and documented exceptions. | This Level 1 recommendation remains open because broader forwarding paths are not fully addressed. |

## Deferred Recommendations

No client-approved deferral was supplied for Q3. The earlier email-hygiene deferral was recorded as completed in Q2 through Proofpoint, so it is retained as history and not carried forward as an active deferral. The two open labeling actions without an applicable license require a scope and licensing decision. This assessment does not presume an approved deferral and does not recommend purchasing licenses solely to increase score.

## Recommendation History

Historical completions are retained for continuity. The Q3 score credit corroborates the calendar-sharing and Q2 consent restrictions. The Datto and Proofpoint entries describe completions recorded in Q2 and do not represent independently verified service effectiveness. Q3 unified audit log progress is addressed in the signal review.

### CIS Recommendations

| **Quarter** | **Recommendation** | **Action** | **Details** |
| --- | --- | --- | --- |
| 2025 Q4 | Disable external calendar sharing | Complete | Completed December 9, 2025 during the monthly touchpoint, as recorded in Q1 and Q2. The Q3 Secure Score confirms the restriction at 5/5. CIS 1.3.3 is Level 2, and this is not a broader external-sharing audit. |
| 2026 Q2 | Restrict user consent to applications | Complete | Implemented in Q2, contributing to the Identity increase from 90.91% in Q1 to 96.97% in Q2. The Q3 credit remains 4/4. CIS 5.1.5.1 is Level 2. The restriction does not automatically revoke earlier consent grants. |

### Advisory Recommendations

| **Quarter** | **Recommendation** | **Action** | **Details** |
| --- | --- | --- | --- |
| 2026 Q1 | Adopt endpoint detection and response | Reported complete | The advisory originated in 2025 Q4, was open in Q1, and was recorded complete in Q2 through Datto RMM / Datto EDR. Present coverage and effectiveness have not been validated. |
| 2026 Q1 | Strengthen email hygiene | Reported complete | The advisory was deferred in Q1 and recorded complete in Q2 using Proofpoint. Current policy scope and native-control equivalence have not been validated, and the adoption item is not reopened. |
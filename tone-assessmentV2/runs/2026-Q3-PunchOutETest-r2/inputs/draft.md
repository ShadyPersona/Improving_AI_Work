<!-- Page 1 -->
Bethany College

Cloud Security Assessment – 2026: Q3

Prepared For

Edward Stough

Prepared By

Danny George

October 2026


<!-- Page 2 -->
# Executive Summary

This is to verify C

Secure Score remains useful for identifying Microsoft security recommendations and tracking control movement. It does not, by itself, establish actual exposure, control effectiveness, or the adequacy of alternative safeguards. The available evidence supports an assessment of selected Microsoft 365 configurations; it does not establish endpoint exposure, vulnerability severity, cloud attack paths, AI usage, or incident-response performance.

The primary concern remains incomplete identity protection, particularly for administrative access. MFA receives only partial credit, while legacy-authentication blocking, application-consent restrictions, and SharePoint modern-authentication requirements remain uncredited. The continuing DLP and external-calendar-sharing recommendations also remain appropriate. Newly visible opportunities in sensitivity labeling and collaboration controls should be incorporated into those existing priorities rather than treated as unrelated projects.

The current overall Secure Score is 27.35% (76.02 of 278 points), compared with 27.97% (79.15 of 283 points) in Q2. The changed scoring baseline prevents this difference from being interpreted as a like-for-like deterioration in security. Q3 performance remained broadly around 27–28%, with repeated Outlook add-in scoring swings. User-MFA credit improved modestly during Q3; additional administrator-MFA progress appeared in October, but neither control is complete. No prior recommendation can be confirmed as resolved.

Bethany College should continue to use this report to guide risk-based remediation rather than pursue score improvement as an end goal. The most valuable next step is to complete administrative MFA protection, confirm the appropriate identity-policy approach and licensing entitlements, and validate DLP and external-sharing settings. This preserves the direction of the previous assessment while focusing effort on the controls that remain incomplete.

# Current Microsoft Cloud Security Posture

Bethany College’s Microsoft 365 cloud security posture reflects a combination of credited safeguards and continuing configuration gaps. Identity protection remains the leading priority. The broader domain view below distinguishes the areas supported by current Microsoft recommendations from those for which insufficient evidence was available. It should not be read as a comprehensive assessment of every service or asset.

## Posture Summary


<!-- Page 3 -->
Identity Secure Score is 49.32%, Apps is 20.71%, and Data is 0%. Current recommendations evaluate nine available points across DLP, sensitivity labels, data mapping, and automatic labeling, with none credited. Microsoft also credits several identity, email, and audit controls as complete. These credits describe current Microsoft assessment results, not verified Q3 implementation milestones or proof of comprehensive protection. Microsoft has confirmed that some security settings are in place, but important gaps remain, especially in data protection. A completed Secure Score recommendation does not always mean the organization is fully protected.

## Key Risk Themes

The following themes connect the continuing findings with the material opportunities identified in this assessment. They prioritize practical discussions about protection and policy enforcement rather than reproduce the full Microsoft recommendation catalog.

* **Complete identity protection**. Prioritize MFA for administrative accounts, broaden user protection, and validate the enforcement of modern authentication and restrictions on application consent.
* **Protect sensitive information**. Revisit the continuing DLP recommendation and establish the policy coverage and classification needed for Bethany College’s sensitive information.
* **Reduce avoidable collaboration exposure**. Address external calendar sharing and validate Outlook add-in approval, external storage, and meeting-access settings alongside the existing email safeguards.
* **Separate control credit from assurance**. Confirm configuration and licensing before treating score changes, completed recommendations, or potential advanced features as evidence of effective protection.

## Domain Posture

The domain posture provides qualitative descriptions of supported conditions, not numerical maturity ratings. The previous quarterly assessment did not assign domain indicators. The Security Signal Review explains the observations and their limitations. Not assessed means insufficient evidence, rather than a conclusion that the domain is secure or that no assets exist.

| Domain | Posture Indicator | Interpretation |
| --- | --- | --- |
| Identity & Access | Incomplete protection | MFA is partially credited as some users and most administrators have MFA enabled. Legacy-authentication, consent, and SharePoint authentication controls remain uncredited. |
| Endpoint Security | Not assessed | No device inventory or endpoint-control evidence was available. |
| Vulnerability Management | Not assessed | No vulnerability or remediation evidence was available. |

<!-- Page 4 -->
| Data Protection | Continuing policy gap | The Data category has zero credit across nine points indicating that Bethany is weak in Data protection and Data Loss Prevention. |
| Email & Collaboration | Mixed control credit | Some email safeguard controls are credited and coexist with calendar-sharing and collaboration gaps. |
| Detection & Operational Readiness | Limited configuration assurance | Audit search is credited but mailbox auditing is not. A separate policy would need created for mailbox auditing. |
| Cloud Workload & Attack Paths | Not assessed | Cloud workload inventory or attack-path evidence cannot be assessed |
| AI Agents & Generative AI | Not assessed | AI service usage, agent permissions, and AI-specific exposure cannot be assessed. |

## Control Movement and Baseline Changes

Overall Secure Score moved from 27.23% (77.07/283) in Q1 to 27.97% (79.15/283) in Q2. The current validation value of 27.35% (76.02/278) is 0.62 percentage points and 3.13 earned points below Q2, while possible points decreased from 283 to 278. The Q3 trend remained broadly around 27–28%, with brief spikes. Repeated three-point gains and losses on the Outlook add-in recommendation contribute to the movement, but do not establish deliberate configuration changes or a reporting fault.

Microsoft Secure Score: overall position and Q3 trend. The displayed peer comparison is 47%, a 19.65-percentage-point gap. This is scoring context, not a risk or maturity ranking.

![Original Microsoft Secure Score view showing 27.35 percent, 76.02 of 278 points, peer comparison of 47 percent, and July to September score history.](media/image2.png)

# Security Signal Review


<!-- Page 5 -->
The Security Signal Review provides the supporting analysis behind the domain posture. It considers Microsoft Secure Score recommendations and trends across identity, data protection, email, and collaboration. Directly applicable configuration recommendations are aligned to the supplied CIS Microsoft 365 Foundations Benchmark v7.0.0 and relevant outcomes in NIST CSF 2.0. These mappings identify the purpose of remediation; they do not constitute a CIS compliance audit or certification of NIST outcomes.

Microsoft recommendations are baseline evidence, not final maturity conclusions. They do not independently establish the effectiveness of third-party safeguards, managed services, business exceptions, or compensating processes. Recommendations with undefined results are not treated as evidence that a product is deployed or vulnerable.

## Identity and Access

Identity protection remains incomplete, and the Q3 trend shows only modest upward movement around 49% rather than a major change. Identity Secure Score is 49.32%, compared with the displayed peer value of 55.98%, a 6.66-percentage-point gap. The current administrator MFA recommendation receives 5.71/10 points and the user recommendation 5/9.

Q1 reported three of eight administrators without MFA protection; Q2 reported four of eight. Q3 reported three out of seven. User-MFA credit rose from 4.73/9 in July to 5.04/9 in September, supporting modest Q3 progress. The earlier student-MFA risk acceptance remains historical context, not a reconfirmed current decision, and should be revisited when the identity baseline is reviewed.

Microsoft Identity Secure Score: peer comparison and Q3 trend.

![Original Microsoft Identity Secure Score comparison, 49.32 percent versus peers 55.98 percent, and the July to September trend.](media/image3.png)

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |

<!-- Page 6 -->
| Administrator MFA 5.71/10; user MFA 5/9 | 5.2.2.1 and 5.2.2.2 (E3/E5 Level 1) | PR.AA-03 | MFA remains partial and needs addressed. |
| Legacy-authentication blocking through Conditional Access 0/8 | 5.2.2.3 (E3/E5 Level 1) | PR.AA-03 | Validate legacy sign-in dependencies and enforcement. Confirm entitlements and enabled policy coverage. |
| Restrict user consent to applications 0/4 | 5.1.5.1 (E3/E5 Level 2) | PR.AA-05 | Review administrator approval of application permissions. The CIS target is no user consent which ensures no malicious consent is granted. |
| Require modern authentication for SharePoint 0/1 | 7.2.1 (E3/E5 Level 1) | PR.AA-03 | Validate blocking access for applications that do not use modern authentication. |
| User-risk policy 0/7; sign-in-risk policy 0/7 | 5.2.2.6 and 5.2.2.7 (E5 Level 1) | PR.AA-03 | Risk-based controls need implemented but are contingent on verified entitlements and business need. |

Microsoft currently credits password hash synchronization, Exchange Online modern authentication, self-service password reset for all users, SharePoint inactive-session sign-out, least-privileged administrative roles, and the presence of more than one global administrator. Those results do not close the MFA gaps. Improving recommends retaining the Q2 identity-baseline recommendation, adding consent and SharePoint authentication checks, and confirming entitlements before selecting Security Defaults, Conditional Access, or risk-based capabilities.

## Endpoint and Vulnerabilities

Endpoint security and vulnerability management remain unassessed, so the current condition and quarter-over-quarter movement cannot be established.

Exposure counts are unavailable for Q1, Q2, and Q3. The comparison entries below represent insufficient evidence, not zero exposed devices.

| Exposure Level | 2026 Q1 | 2026 Q2 | 2026 Q3 |
| --- | --- | --- | --- |
| High | Unassessed | Unassessed | Unassessed |

<!-- Page 7 -->
| Medium | Unassessed | Unassessed | Unassessed |
| Low | Unassessed | Unassessed | Unassessed |

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| No device, vulnerability, or exposure evidence available | Not assessed | Not assessed | Endpoint protection and vulnerability status cannot be assessed. |

## Data Protection and Collaboration

Information protection remains a continuing policy gap because the evaluated Data category has 0% credit across nine points. Default DLP receives 0/5 points, sensitivity labels 0/2, Purview data mapping 0/1, and automatic labeling 0/1. These results do not prove that all information-protection measures are absent. Q1 described partial implementation dating to 2023 Q3, but that historical statement does not confirm current policy scope or enforcement.

Apps receives 20.71% credit. External calendar sharing remains uncredited at 0/5, supporting the existing recommendation. Outlook add-in restrictions, external storage restrictions, mailbox auditing, and MailTips also receive no credit. Teams recommendations identify opportunities in automatic admission of invited users, presenter permissions, and anonymous meeting access. These are configuration findings, not evidence of unauthorized disclosure, malicious add-ins, or a security incident.

Microsoft Secure Score category breakdown: Identity 49.32%, Data 0%, and Apps 20.71%.

![Original Microsoft Secure Score category breakdown showing Identity 49.32 percent, Data zero percent, and Apps 20.71 percent.](media/image4.png)

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| Default DLP 0/5 | 3.2.1 (E3/E5 Level 1) | PR.DS-01; PR.DS-02; PR.DS-10 | Create a policy meeting institutional needs, its covered locations, and enforcement. |

<!-- Page 8 -->
| Sensitivity labels 0/2; automatic labeling 0/1 | 3.3.1 (E3/E5 Level 1); published label policies | PR.DS-01; PR.DS-02 | Assess classification and label publication with DLP. Publication and automatic labeling are separate capabilities. |
| External calendar sharing 0/5; Outlook add-in restrictions 0/3 | 1.3.3 and 6.3.1 (E3/E5 Level 2) | PR.AA-05 | Calendar restriction remains open. Repeated add-in credit swings warrant policy validation and administrator-approved deployment. |
| Several email safeguards credited; advanced email protections uncredited | Not audited against individual CIS criteria | Not assessed | Retain credited protections and validate entitlement and policy coverage for advanced options. |
| Teams admission/presenter/anonymous-access controls uncredited; mailbox auditing 0/3 | Not audited against individual CIS criteria | PR.AA-05; DE.CM-03 | Validate meeting access and mailbox logging alongside external storage and MailTips. |

Microsoft credits several email protections, including zero-hour auto purge for spam and phishing, malware and high-confidence-phishing handling, mailbox intelligence, and other spam controls. Advanced Defender for Office 365 recommendations such as Safe Links, Safe Attachments, and impersonation protection remain uncredited and require entitlement validation. System-controlled forwarding receives credit, but blocking all forwarding does not; these are distinct settings. Existing safeguards should be retained while the continuing DLP and calendar priorities are addressed and the newly observed collaboration opportunities are consolidated.

## Cloud Workload and Attack Path Exposure

Cloud workload and attack-path exposure remain unassessed. Bethany College’s current licensing does not include the capabilities needed to evaluate workload inventory, cloud-resource security findings, or attack paths.

Microsoft 365 configuration scores do not validate cloud resource exposure or attack paths. The absence of cloud findings here does not establish that no cloud assets or risks exist.

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |

<!-- Page 9 -->
| No cloud workload inventory or attack-path evidence supplied | Not assessed | Not assessed | Resources, exposure, attack paths, or remediation cannot be assessed. |

## AI Agents and Generative AI Usage

AI agents and generative AI usage remain unassessed, so this assessment does not establish which AI services, agents, integrations, or related data-access permissions are in use. Bethany College’s current licensing does not include the capabilities needed for that evaluation.

Microsoft 365 data and consent controls do not establish AI deployment or exposure. No client AI-specific findings can be validated.

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| No AI usage, agent, or permissions evidence supplied | Not assessed | Not assessed | AI deployment and exposure cannot be assessed. |

## Detection and Operational Readiness


<!-- Page 10 -->
Detection and operational readiness have limited configuration assurance. Microsoft 365 audit-log search receives full credit at 3/3, while the separate mailbox-auditing recommendation receives 0/3. These results remain distinct because audit-search availability does not establish complete mailbox logging, retention, monitoring, or investigation coverage. There needs to be a separate mailbox-auditing policy implemented to receive credit for that recommendation. Audit-search credit does not establish detection or response effectiveness. Mailbox auditing should be validated with the collaboration settings.

No alert, incident, investigation, or response-performance evidence was available as Bethany College’s current environment is not set up to include the capabilities needed for that evaluation.

# Recommended Security Actions

The recommendations below consolidate the quarterly evidence into a short, risk-based action plan and preserve historical context from past assessments. They intentionally avoid reproducing the full Microsoft recommendation catalog but identify areas that should be prioritized for the most benefit to the environment.

|  |
| --- |
| **Security Awareness**  *As businesses rapidly scale cloud-native applications and integrate automated tools, a familiar vulnerability continues to drive some of the largest data exposures: cloud misconfigurations and “shadow” APIs. Recent analyses highlight that a vast majority of cloud security incidents stem from basic configuration oversights, such as overly permissive storage accounts and forgotten keys, not from sophisticated zero-day software exploits.*  *Because cloud ecosystems are deeply interconnected, a single overlooked API or misconfigured application can grant attackers privileged access to internal infrastructure. Mitigating this active threat requires organizations to bridge the gap between development speed and security governance, implementing continuous automated posture management to ensure visibility matches the pace of change.* |

## Active Recommendations

| **Priority** | **Identified** | **Recommendation** | **Status** |
| --- | --- | --- | --- |

<!-- Page 12 -->
| 1 | 2026 Q1; expanded Q2 | Establish a security baseline and mature identity protection. Complete administrator MFA and broaden user protection. Validate legacy-authentication blocking, consent approval, and SharePoint modern authentication. Confirm entitlements and operational exceptions before selecting the policy approach.  Document the chosen policy approach and revisit the historical student-MFA exception. | Open. MFA completion is partial. Improving recommends either implementing Microsoft Security Defaults, or a phased approach based on Bethany College's security requirements, risk tolerance, and budget. Option 1: Enable Microsoft Entra Security Defaults  Option 2: Upgrade to Microsoft 365 A3  Option 3: Upgrade to Microsoft 365 A5  See 2026 Q2 report for further details. |
| 2 | 2023 Q3 | Ensure DLP policies are enabled. Confirm current policy mode, covered locations, sensitive-information rules, and enforcement. Add a proportionate classification and label-publication plan after entitlement validation; test impacts before wider enforcement. | Open. DLP 0/5 |
| 3 | 2026 Q1 | Disable external calendar sharing. Review the organization setting and Exchange sharing policy against business needs. Restrict external calendar publication and sharing; document any required exception rather than assume the finding is closed. | Open. External-calendar-sharing restriction receives 0/5. |
| 4 | 2026 Q3 | Stabilize Outlook add-in restrictions. Review role-assignment permissions governing self-installed add-ins and provide administrator approval and centralized deployment for required add-ins. Recheck configuration alongside scoring before attributing repeated gains and losses to a cause. | New priority. Repeated three-point swings between completed and incomplete. Further review is needed. |
| 5 | 2026 Q3 | Validate collaboration and mailbox settings. Review external storage, MailTips, mailbox auditing, and Teams admission, presenter, and anonymous-access settings. Prioritize settings reported as available and verify actual policy coverage and approved business exceptions. | Open. |

<!-- Page 13 -->
| 6 | 2026 Q3 | Evaluate additional email protections proportionately. Preserve credited protections and validate licensing and policy coverage for Safe Links, Safe Attachments, impersonation protection, and forwarding restrictions before proposing additional purchases or declaring implementation gaps closed. | Open. |

## CIS Microsoft 365 Foundation Benchmark

The following actions align the supported findings to CIS Microsoft 365 Foundations Benchmark v7.0.0. Level 1 and Level 2 profiles are distinguished where applicable; the benchmark’s E3/E5 profile names do not establish Bethany College’s licenses. Microsoft scoring is not a substitute for the benchmark’s configuration audit. Related NIST CSF 2.0 outcomes are mapped in the Security Signal Review, not presented as achieved or certified outcomes.

| **CIS Ref.** | **Recommendation** | **Description** | **Status** |
| --- | --- | --- | --- |
| 5.2.2.1; 5.2.2.2; 5.2.2.3; 5.1.5.1 | MFA, legacy-authentication blocking, and application consent | MFA and legacy blocking: E3/E5 Level 1. Consent: E3/E5 Level 2. Audit the enabled policy coverage and require administrator consent rather than rely on partial score credit. | Open. MFA partial; legacy blocking and consent uncredited. |
| 3.2.1; 3.3.1 | Enabled DLP and published sensitivity label policies | E3/E5 Level 1. Verify a DLP policy meeting institutional needs is enabled for a covered location. Validate published label policies separately from automatic-labeling capabilities. | Open. DLP and labeling uncredited |
| 1.3.3; 6.3.1 | Restrict external calendar sharing and Outlook add-ins | E3/E5 Level 2. Check the calendar-sharing organization setting and default sharing policy; validate removal of the relevant self-install add-in roles from applicable role-assignment policies. | Open. External Sharing 0/5, and add-ins 0/3. |
| 7.2.1 | Require modern authentication for SharePoint applications | E3/E5 Level 1. Confirm apps that do not use modern authentication are blocked, including the LegacyAuthProtocolsEnabled setting being False. | Open. SharePoint recommendation 0/1 |

## Deferred Recommendations


<!-- Page 14 -->
No newly approved deferral is documented for Q3. The earlier student-MFA risk acceptance has not been reconfirmed and is not treated as closure. The Q2 options for more advanced identity protection remain contingent planning choices: confirm existing entitlements, operational requirements, and the desired policy flexibility before considering additional licenses. Identity Protection and privileged-access capabilities should not displace the immediate MFA and authentication-baseline work.

## Recommendation History

The history below preserves meaningful context from previous assessments without implying completion. Q2 recorded no completed or risk-accepted recommendation entries and no validated third-party, alternative, or manual closures. Current Microsoft completion credits are not dated implementation milestones, and no prior assessment recommendation is confirmed resolved by the supplied evidence.

### CIS Recommendations

| **Quarter** | **Recommendation** | **Action** | **Details** |
| --- | --- | --- | --- |
| 2026 Q1–Q2 | DLP and external calendar sharing | Retained as active | Both recommendations remain supported by current uncredited controls. Historical DLP partial implementation is not reconfirmed. No completed, risk-accepted, alternative, or manual CIS closure was documented. |

### Advisory Recommendations

| **Quarter** | **Recommendation** | **Action** | **Details** |
| --- | --- | --- | --- |
| 2026 Q1 → Q2 | Consider Enabling Security Defaults in Microsoft Entra ID | Expanded in Q2 | Q2 expanded this advice into a security baseline and mature identity approach. Q3 retains it with consent and SharePoint authentication checks, subject to entitlement validation. |
| 2026 Q1–Q2 | Student MFA exception and administrator protection | Historical context | The earlier student-MFA acceptance is not a renewed Q3 decision. Prior unprotected administrator counts were three of eight in Q1 and four of eight in Q2, Q3 reported three out of seven. |
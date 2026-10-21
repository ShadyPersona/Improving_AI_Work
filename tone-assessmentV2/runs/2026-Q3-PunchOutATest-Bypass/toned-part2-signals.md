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

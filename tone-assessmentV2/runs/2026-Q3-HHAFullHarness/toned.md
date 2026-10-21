<!-- Page 1 -->
Hialeah Housing Authority

Cloud Security Assessment – 2026: Q3

Prepared For

Luis Arellano

Prepared By

Danny George

October, 2026

# Executive Summary

Hialeah Housing Authority’s (HHA) Microsoft cloud security posture improved on a Microsoft-reported basis during Q3 2026. This assessment covers July 1 through September 30, 2026. The Q2 assessment serves as the previous-quarter baseline, and Q1 provides longer-term context. The conclusions combine the supplied Q3 score trends and control history with current-state Microsoft 365 evidence.

Secure Score provides useful evidence of Microsoft-reported control status. It does not measure overall risk or control effectiveness. The supplied evidence does not include current endpoint inventory, vulnerability exposure, incident records, Azure workload or attack-path evidence, AI usage, or operational validation of third-party controls. These areas remain unassessed. They are not presumed secure or unchanged.

The primary risk theme for Q3 is validating the coverage behind the remaining Microsoft-native email and collaboration gaps. Q2 recorded completed endpoint and email-hygiene advisories through Datto RMM, Datto EDR, and Proofpoint. Those completions remain part of HHA’s history, but present coverage and effectiveness require validation. SharePoint modern authentication became relevant during Q3 and is the only open Identity recommendation.

Overall Secure Score is 61.74% (163 of 264 points), compared with 60.00% (159 of 265) in Q2 and 58.49% (155 of 265) in Q1. Score movement is concentrated in Identity and Apps. Identity increased from 90.91% in Q1 to 96.97% in Q2 following the consent restriction, and is now 98.48%. Apps increased from 46.32% in both earlier reports to 48.15%. Data remains 77.78%. The current catalog contains 38 completed and 26 open recommendations. No recommendation regressed in Q3. This indicates that HHA kept its previously credited controls in place, but it does not confirm that those controls operate effectively.

HHA should prioritize validation of mailbox auditing, all forwarding paths, native phishing settings and their relationship to Proofpoint, and the SharePoint authentication requirement. The objective is demonstrable protection and usable monitoring rather than Secure Score points alone. Before closing these recommendations, HHA should retain evidence of control scope, tested exceptions, and accountable ownership.

# Current Microsoft Cloud Security Posture

Microsoft-reported identity controls are substantially complete, while Apps continues to contain the largest concentration of open recommendations. Data recommendations show no score movement since Q2. This assessment covers the available Microsoft 365 signals. It does not provide a comprehensive assurance opinion on all cloud and endpoint services.

## Posture Summary

Identity controls carry the strongest score credit, and Apps carries the largest open exposure. Current Secure Score credit totals 163 earned points: Identity 65/66, Apps 91/189, and Data 7/9. Administrator and user MFA, legacy authentication blocking, user-consent restriction, and external calendar-sharing restriction are marked complete. The SharePoint modern-authentication action remains open and requires attention despite the high identity score, because legacy authentication could allow older applications or connection methods to bypass stronger sign-in protections.

## Key Risk Themes

The themes below connect the material Microsoft 365 recommendations to validation and remediation discussions. Each theme distinguishes a reported configuration opportunity from a confirmed exploitable condition. Third-party product adoption is not treated as proof of effective coverage.

* **Native phishing and impersonation controls remain incomplete.** Proofpoint’s protected population, routing, policies, and exceptions should be compared with the relevant Microsoft requirements before equivalent coverage is accepted or overlapping controls are enabled.

Unified audit log search is complete, but mailbox auditing remains open as a separate control. Automatic forwarding controlled by the system is complete, while broader forwarding restriction remains open. This split shows that foundational logging is in place, but coverage is incomplete. HHA should review mailbox audit actions and all forwarding paths, document approved exceptions, and test representative events before treating these controls as operationally effective.

* **SharePoint modern authentication became relevant during Q3 and is open at 0/1.** This does not indicate that an existing control failed. Microsoft now considers the requirement applicable to the environment. Legacy authentication could allow older applications or connection methods to bypass stronger sign-in protections. HHA should identify dependent applications or workflows, confirm their compatibility with modern authentication, and then enforce the requirement through a controlled implementation plan.

## Domain Posture

The domain posture below summarizes only what the supplied evidence supports. Microsoft-reported completions are distinguished from operational assurance, and domains without current evidence are identified as unassessed. No prior indicator is carried forward as a current conclusion without validation.

|  |  |  |
| --- | --- | --- |
| Domain | Posture Indicator | Interpretation |
| Identity & Access | Strong score; targeted gap | HHA’s identity score of 98.48% is strong. The remaining gap is the open SharePoint modern authentication requirement. |
| Endpoint Security | Not assessed | Q2 records Datto adoption, but no endpoint security data was available in Defender. Current endpoint posture cannot be assessed. |
| Vulnerability Management | Not assessed | No current device exposure, CVE, or remediation records were provided. |
| Data Protection | Scope unverified | HHA has completed the DLP recommendation, but Improving does not have access to the Purview Portal, so DLP policies cannot be verified. |
| Email & Collaboration | Coverage review needed | Apps score is 91/189. Native phishing, auditing, and forwarding gaps require coverage review. |
| Detection & Operational Readiness | Partial evidence | Unified audit log search is complete. Mailbox auditing is open. Operational readiness is unverified. |
| Cloud Workload & Attack Paths | Not assessed | No Azure workload or attack-path evidence was provided. |
| AI Agents & Generative AI | Not assessed | No usage, permissions, or governance evidence was provided. |

## Control Movement and Baseline Changes

Overall Secure Score rose 1.74 percentage points since Q2. Earned points increased from 159 to 163, while available points declined from 265 to 264. Two Q3 scoring events account for the four-point increase in earned points: unified audit log search completed on August 18 (+3), and SharePoint inactive-user sign-out became relevant with full credit on August 19 (+1). These are scoring events, not confirmed implementation dates. SharePoint modern authentication became relevant on August 19 at 0/1. The identity trend’s small August step down reflects that newly relevant requirement, not a loss of earned credit. Identity is 1.51 percentage points above Q2, Apps is 1.83 points higher, and Data’s score is flat. The quarter-over-quarter movement reflects steady improvement rather than a material change in risk. The newly relevant SharePoint requirement accounts for the only notable scoring pressure in Q3. HHA should address that requirement through a planned compatibility review and continue focusing on the open controls that provide the greatest practical security benefit.

The chart below shows the Microsoft Secure Score overview and supplied trend. Peer comparisons provide context, not an overall maturity rating.

![Overall Secure Score comparison: HHA 61.74 percent; similarly sized organizations 52.21 percent.](media/image3.png)

# Security Signal Review

This review supports the domain posture with the available Microsoft 365 recommendations and score history. Framework references use CIS Microsoft 365 Foundations Benchmark v7.0.0 and NIST Cybersecurity Framework 2.0. These references identify related configuration guidance or outcomes. They do not represent certification, a full benchmark audit, or proof that controls operate effectively.

Microsoft-reported completions and open recommendations are interpreted alongside HHA’s assessment history. Where third-party services, exceptions, licensing, or operating scope cannot be verified, this assessment retains that limitation. It neither declares full mitigation nor confirms exploitation.

## Identity and Access

The identity score is strong at 98.48% (65/66), and one identity recommendation remains open. Identity Secure Score reflects 13 completed recommendations and one open recommendation. MFA for administrators (10/10) and all users (9/9), legacy authentication blocking (8/8), and user-consent restriction (4/4) are marked complete. The identity score rose from 90.91% in Q1 to 96.97% in Q2 following the consent restriction, which remains complete.

SharePoint modern authentication is the only open identity action, at 0/1, and it is the main identity gap. Both risk-policy recommendations are credited at 7/7, but they show no applicable license. That credit does not establish deployed Entra ID P2 sign-in or user-risk policies. The Q2 consent restriction remains complete, but it does not itself revoke previously granted permissions. The strong identity score shows that most core identity protections are in place. Two areas still need attention: the SharePoint requirement and the licensing limitation on risk policies. HHA should review application compatibility before requiring modern authentication. HHA should also periodically examine existing consent grants to confirm they remain appropriate for business needs.

The chart below shows the Microsoft Identity Secure Score trend and a contextual peer comparison.

![Supplied Q3 identity trend, showing high earned score credit and a small August step down as scoring requirements became relevant.](media/image4.png)

![Identity Secure Score comparison: HHA 98.48 percent; similarly sized organizations 62.34 percent.](media/image5.png)

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| Administrator and all-user MFA complete: 10/10 and 9/9 | 5.2.2.1; 5.2.2.2 (Level 1) | PR.AA-03 | The score completion reflects implemented MFA policies for users and administrators. |
| Legacy authentication block complete: 8/8 | Not independently assessed | PR.AA-03 | The score completion reflects blocking of legacy authentication. |
| User consent restriction complete: 4/4 | 5.1.5.1 (Level 2) | PR.AA-05 | The score completion reflects a restriction on user consent for applications. |
| SharePoint modern authentication open: 0/1 | 7.2.1 (Level 1) | PR.AA-03 | This is not a regression, because the requirement became newly relevant during Q3. HHA should review application compatibility and enforce it. |
| Risk policies: 7/7 each; no applicable license | Not assessed | Not assessed | The risk policies recommendation is credited as complete due to Entra Security Defaults. Deployed Entra ID P2 risk policies are not established by this credit. |

HHA should prioritize SharePoint modern authentication and verify the relevant application dependencies before enforcement. HHA should continue validating privileged access and existing application grants through administrative evidence. Current score credit alone does not establish the detailed policy configuration or operating effectiveness of these controls.

## Endpoint and Vulnerabilities

Endpoint coverage and vulnerability exposure cannot be assessed from the supplied Microsoft 365 score material. No device inventory, endpoint exposure distribution, CVE details, or affected-device records were provided, so this section cannot establish endpoint risk for any quarter. The exposure table records the evidence as unavailable rather than as zero affected devices.

EDR adoption originated in 2025 Q4 and remained open in Q1. Q2 recorded completion through Datto RMM and Datto EDR, and that advisory remains completed as history. Deployment completeness, sensor health, monitoring, and vulnerability remediation are not accessible in Microsoft Defender. As a result, the endpoint assessment cannot be completed from the available evidence. Current Datto coverage therefore remains unverified.

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
| Datto RMM / EDR: Q2 completion | Not assessed | DE.CM-09 (related outcome) | This row records historical adoption only. Current sensor and monitoring coverage remains unverified. |
| CVE records not provided | Not assessed | Not assessed | No vulnerability count, exploitability, or severity conclusion can be drawn. |
| Exposure data not provided | Not assessed | Not assessed | Unavailable values do not indicate zero exposure. |
| Remediation data not provided | Not assessed | Not assessed | No remediation trend or closure conclusion is supported by the available data. |

## Data Protection and Collaboration

Apps remains the lowest-scoring domain at 48.15% (91/189), and Data is 77.78% (7/9). DLP and Defender protection for SharePoint, OneDrive, and Teams are marked complete. Safe Links for email and Safe Attachments are also complete. These completed signals do not resolve the remaining phishing, impersonation, or forwarding settings.

HHA has established part of its data protection foundation, but current evidence does not show that protection and labeling coverage extends across the intended business scope. The most significant gaps are native phishing controls: thresholds, user and domain impersonation, associated intelligence-based actions, safety tips, and a custom anti-phishing policy. Mailbox intelligence is complete at 8/8, but its separate impersonation actions are open. Safe Links for email is 9/9, while Office applications is 0/3. Other open actions cover MailTips, Outlook add-ins, spam notifications, 30-day quarantine, bulk complaint threshold, and blocking users at the message limit. Broader forwarding restriction is 0/5, although system-controlled forwarding is 1/1. Customer Lockbox remains open even though the required license is available. Data-map labels and auto-labeling are not supported by the available licensing, so they require a scope and licensing decision, as noted in Deferred Recommendations. The phishing, impersonation, and forwarding gaps are among the priorities identified in the Executive Summary. HHA should prioritize enabling Customer Lockbox and review where sensitive information is stored and shared. HHA should determine whether broader labeling capabilities are needed based on business and regulatory requirements rather than Secure Score alone.

Data and Apps scores appear in the Secure Score overview above.

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| Unified audit 3/3; mailbox audit 0/3 | 3.1.1; 6.1.1–6.1.3 (Level 1) | PR.PS-04 | Log availability should be assessed separately from mailbox action coverage and bypass validation. |
| Forwarding: broad 0/5; automatic 1/1 | 6.2.1 (Level 1) | PR.DS-02 | Transport, outbound policy, inbox, and administrative forwarding paths and their exceptions should be validated. |
| Anti-phishing 0/3; impersonation open | 2.1.7 (E5 Level 2) | PR.PS-01 | Native gaps should be validated against documented Proofpoint coverage. Equivalence is not assumed. |
| DLP 5/5; labeling scope unverified | 3.2.1 (Level 1; DLP) | PR.DS-01; PR.DS-02; PR.DS-10 | Score credit does not demonstrate effective policy or labeling scope. |
| Calendar sharing restricted: 5/5 | 1.3.3 (Level 2) | PR.AA-05 | The current score corroborates the historical restriction. It does not constitute a full collaboration-sharing audit. |

HHA should coordinate the higher-impact email actions with Proofpoint and document tested equivalent coverage where appropriate. The remaining collaboration and data-governance controls should be addressed according to business scope and licensing.

## Cloud Workload and Attack Path Exposure

Cloud workload and attack-path exposure could not be assessed. No Azure workload inventory, Defender for Cloud findings, exposure graph, or attack-path analysis was accessible to this assessment.

Microsoft 365 score credit cannot establish the state of Azure resources, public exposure, privileged workload access, or exploitable paths. No workload count, severity, remediation status, or change from the prior assessments is asserted.

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| Workload inventory unavailable | Not assessed | Not assessed | Applicable resource population cannot be established. |
| Public exposure unavailable | Not assessed | Not assessed | This assessment makes no public exposure finding and no claim of absence. |
| Attack-path data unavailable | Not assessed | Not assessed | No exploitable path or closure conclusion can be drawn. |
| Workload configuration unavailable | Not assessed | Not assessed | No workload control-effectiveness rating is assigned. |
| Workload remediation unavailable | Not assessed | Not assessed | No trend comparison with prior assessments is supported. |

## AI Agents and Generative AI Usage

AI agent and generative AI usage could not be assessed. No usage inventory, approved-tool register, agent permissions, data-access configuration, or governance records were available.

The gap does not demonstrate unmanaged AI use, and it does not demonstrate the absence of AI use. Microsoft 365 data-protection score credit does not establish how information is shared with agents or external generative AI services.

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| AI inventory unavailable | Not assessed | Not assessed | Usage and applicable scope cannot be established. |
| Agent permissions unavailable | Not assessed | Not assessed | No overprivileged-agent finding is asserted. |
| AI sharing evidence unavailable | Not assessed | Not assessed | No client-specific data-leakage conclusion can be drawn. |
| AI governance unavailable | Not assessed | Not assessed | No claim of approved or unmanaged use is made. |
| AI monitoring unavailable | Not assessed | Not assessed | No operational effectiveness or trend rating is assigned. |

## Detection and Operational Readiness

The unified audit log search control is complete at 3/3, which is a positive score movement since Q2, but mailbox auditing remains open at 0/3. These are distinct controls, and the availability of the unified audit capability does not demonstrate complete mailbox action coverage.

No incident records, response exercises, monitoring procedures, retention validation, or investigation samples were available, so response readiness cannot be evaluated. The Q2 Datto and Proofpoint completion history does not evidence current alert handling or response readiness.

The audit improvement supports a stronger Microsoft-reported baseline. Operating effectiveness remains unverified because the Datto and Proofpoint solutions were not accessible during this assessment. HHA should review representative audit events and accountable monitoring processes before treating these settings as proven detection capability.

# Recommended Security Actions

These recommendations consolidate the material findings into a practical action plan. Priorities indicate the proposed review sequence, not measured incident severity. Identification quarters reflect the supplied assessment history or the Q3 assessment; status dates reflect this report’s review, not assumed implementation dates.

|  |
| --- |
| ***Security Awareness***  *ASM’s current evidence makes identity recovery and responsible AI usage appropriate awareness topics. Employees should use approved AI services and avoid submitting business-sensitive information unless permitted by the organization’s data-use policy. Discovery confirms access to multiple AI services, but does not establish what information employees supplied. Explain the distinction between an approved service and an approved use case, and provide a clear escalation route for uncertain requests.* |

Use practical verification and reporting scenarios in ongoing awareness discussions, particularly alongside the impersonation-control review. If training is delivered, retain participation and follow-up records. NIST CSF 2.0 PR.AT-01 is the related awareness outcome; no training completion or effectiveness evidence was supplied.

## Active Recommendations

| **Priority** | **Identified** | **Recommendation** | **Status** |
| --- | --- | --- | --- |
| 1 | 2026 Q1 | HHA should validate third-party coverage. HHA should document Datto and Proofpoint scope, mapped controls, exclusions, policy evidence, and operating tests. Secure Score treatment should be updated only where equivalent protection is supported. | This recommendation remains open because Datto and Proofpoint coverage is not sufficiently documented. |
| 2 | 2026 Q3 | HHA should require SharePoint modern authentication. HHA should test application dependencies and enforce CIS 7.2.1. | This recommendation remains open at 0/1 pending a review of SharePoint application dependencies. |
| 3 | 2026 Q3 | HHA should verify mailbox auditing. HHA should check organizational enablement, required actions, and bypass exceptions. Representative events should be tested separately from unified audit availability. | This recommendation remains open at 0/3 pending review of mailbox auditing and representative events. |
| 4 | 2026 Q3 | HHA should validate all forwarding paths. The review should cover transport, outbound policy, inbox, OOF, OWA, administrator, and automation paths. HHA should block unauthorized forwarding and document exceptions. | This recommendation remains open at 0/5 because broader forwarding paths are not fully addressed, although automatic forwarding is complete. |
| 5 | 2026 Q3 | HHA should close phishing and impersonation coverage gaps. HHA should compare native requirements with Proofpoint, then configure required protections or document tested equivalence and residual gaps. | This recommendation remains open because phishing protections are incomplete and Proofpoint coverage is not sufficiently documented. |
| 6 | 2026 Q3 | HHA should review remaining collaboration and data controls. The review should assess MailTips, add-ins, spam notifications, Office Safe Links, quarantine, bulk and sending limits, Lockbox, and labeling scope. | This recommendation remains open pending review of the remaining collaboration and data controls. |

## CIS Microsoft 365 Foundation Benchmark

The following actions relate to the supplied CIS Microsoft 365 Foundations Benchmark v7.0.0 Level 1 guidance. They are targeted recommendations, not a full Level 1 compliance assessment. Level 2 recommendations, including the custom anti-phishing policy, external calendar sharing, and user-consent restriction, appear in the Security Signal Review or the recommendation history. They are not represented here as Level 1 requirements.

| **CIS Ref.** | **Recommendation** | **Description** | **Status** |
| --- | --- | --- | --- |
| 7.2.1 | Require modern authentication for SharePoint | Compatibility should be reviewed before the requirement is enforced. Microsoft reports the action open at 0/1. | This Level 1 recommendation remains open at 0/1. |
| 6.1.1; 6.1.2 | Validate organizational and mailbox auditing | The review should confirm that AuditDisabled is false, that auditing and required actions are enabled, and that representative events are available. | This Level 1 recommendation remains open pending an auditing review. |
| 6.1.3 | Validate audit bypass associations | Bypass should not be enabled without a documented written exception. Current bypass settings were not supplied. | This Level 1 recommendation remains open pending a review of audit bypass settings. |
| 6.2.1 | Block or disable all forwarding paths | The review should validate transport and outbound policies, user, administrator, and automation paths, and documented exceptions. | This Level 1 recommendation remains open because broader forwarding paths are not fully addressed. |

## Deferred Recommendations

No current client-approved deferral was supplied. The earlier email-hygiene deferral was recorded as completed in Q2 through Proofpoint and is retained as history, not carried forward as an active deferral. The two open labeling actions without an applicable license require a scope and licensing decision. This assessment does not presume an approved deferral or recommend purchasing licenses solely to increase score.

## Recommendation History

Historical completions are retained for continuity. Current score credit corroborates the calendar-sharing restriction and the Q2 consent restriction. The Datto and Proofpoint entries describe completions recorded in Q2. They do not independently verify current service effectiveness. Q3 unified audit log progress is addressed in the Security Signal Review.

### CIS Recommendations

| **Quarter** | **Recommendation** | **Action** | **Details** |
| --- | --- | --- | --- |
| 2025 Q4 | Disable external calendar sharing | Complete | The restriction was completed on December 9, 2025 during the monthly touchpoint, as recorded in Q1 and Q2. Current Secure Score confirms the restriction at 5/5. CIS 1.3.3 is Level 2. This entry is not a broader external-sharing audit. |

<!-- Page 2 -->
| 2026 Q2 | Restrict user consent to applications | Complete | The restriction was implemented in Q2 and contributed to the Identity increase from 90.91% in Q1 to 96.97% in Q2. Current credit remains 4/4. CIS 5.1.5.1 is Level 2. The restriction does not automatically revoke earlier consent grants. |

### Advisory Recommendations

| **Quarter** | **Recommendation** | **Action** | **Details** |
| --- | --- | --- | --- |
| 2026 Q1 | Adopt endpoint detection and response | Reported complete | The adoption originated in 2025 Q4 and remained open in Q1. It was recorded complete in Q2 through Datto RMM and Datto EDR. Present coverage and effectiveness remain unvalidated. |
| 2026 Q1 | Strengthen email hygiene | Reported complete | The item was deferred in Q1 and recorded complete in Q2 using Proofpoint. Current policy scope and native-control equivalence remain unvalidated. The adoption is not reopened. |
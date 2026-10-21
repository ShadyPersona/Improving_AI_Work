Irontrax

> Cloud Security Assessment – 2026: Q3

Prepared For

Joe Santora

Prepared By

Danny George

October 8, 2026

# Executive Summary

Irontrax’s Q3 assessment continues the findings and historical context reported in Q1 and Q2, using the current Microsoft Secure Score indicators and recommended-action statuses as the observable baseline. The review covers Microsoft-reported identity, data, email, and collaboration controls. Endpoint, vulnerability, cloud workload, AI, and incident-response evidence were not available, so those domains remain unassessed rather than being presumed secure or unchanged.

Microsoft Secure Score is 39.33%, with 105 of 267 available points, compared with 38.6% and 105 of 272 points in both prior assessments. The 0.73 percentage-point increase reflects a smaller available-point denominator, not additional earned points or demonstrated remediation. Identity remains the strongest scored category at 96.72%; Data remains at 0% and Apps at 23.35%. These indicators help prioritize configuration review but do not establish overall risk maturity or framework compliance.

The primary Q3 concern is the continuing gap between Microsoft-reported identity protection and the less complete data and collaboration control baseline. The three recommendations first identified in 2024-Q2 remain open: restricting additional storage providers in Outlook on the web, preventing user installation of Outlook add-ins, and requiring modern authentication for SharePoint applications. Current action statuses support retaining these recommendations, but do not establish that no remediation work has occurred.

The current review also brings attention to common attachment filtering, data loss prevention, mail forwarding restrictions, mailbox auditing, external calendar sharing, and Teams meeting controls. These are newly emphasized in this assessment, not proven to have first arisen during Q3. No prior recommendation can be confirmed resolved, and the essentially flat Q3 score trends do not support a conclusion of major gains or regressions.

Irontrax should prioritize the continuing configuration recommendations alongside practical email and data-protection improvements. Managed IT should validate effective policy scope and business exceptions, record changes and test results, and confirm licensing before deciding whether advanced protections require additional entitlement. The aim is to demonstrate exposure reduction, not score improvement alone.

# Current Microsoft Cloud Security Posture

Irontrax has a comparatively well-scored identity baseline, while Microsoft continues to identify unaddressed opportunities in email, collaboration, and data protection. The available evidence supports a targeted configuration review; it does not provide a complete assessment of devices, workloads, incidents, or operational effectiveness.

## Posture Summary

Of 69 recommended actions, Microsoft reports 28 Completed and 41 To address. Among the open actions, 22 carry a Have license value of Yes and 19 a value of No. These flags are not independently verified entitlements: some advanced controls have inconsistent flags across completed and pending actions. Peer scores of 46.8% overall and 60.9% for identity provide comparison context only, not an assurance standard or a reliable measure of Irontrax’s risk maturity.

## Key Risk Themes

The following themes focus the remediation discussion on the material conditions represented by the current control baseline. They distinguish continuing client recommendations from additional control opportunities and areas where the evidence is too limited for a posture conclusion.

- Complete the long-standing Outlook and SharePoint hardening recommendations while preserving approved business integrations and confirming effective tenant settings.

- Close the email and collaboration gaps through attachment filtering, forwarding review, and proportionate external-sharing and meeting restrictions.

- Establish effective data-protection coverage and verify mailbox logging; score completion in a related control does not establish equivalent protection.

- Validate policy scope, licensing, and unassessed domains before drawing assurance conclusions or committing to additional products.

## Domain Posture

The domain indicators below describe the strength and limitations of the available evidence, rather than assigning unsupported maturity ratings. Q1 and Q2 did not establish comparable domain-level indicators. Current observations are therefore presented on their own merits, with historical comparisons limited to the metrics and recommendations previously reported.

| Domain | Posture Indicator | Interpretation |
| --- | --- | --- |
| Identity & Access | Strong Microsoft-reported baseline | Identity 96.72% (59/61); key MFA and legacy-authentication actions Completed. Effective coverage and the current Security Defaults setting were not independently verified. |
| Endpoint Security | Not assessed | Device inventory, onboarding, endpoint protection, and coverage evidence not provided. |
| Vulnerability Management | Not assessed | No vulnerability, affected-device, exposure, or exploitability detail available. |
| Data Protection | Requires control review | Data 0%; DLP To address at 0/5. Information-protection scope and label entitlement require validation. |
| Email & Collaboration | Mixed control baseline | Apps 23.35%; completed email protections coexist with open Outlook, SharePoint, attachment, forwarding, calendar, and Teams actions. |
| Detection & Operational Readiness | Limited assurance | Audit search Completed, mailbox auditing open. Operational monitoring and response effectiveness not assessed. |
| Cloud Workload & Attack Paths | Not assessed | Workload inventory, resource exposure, and attack-path evidence not available. |
| AI Agents & Generative AI | Not assessed | AI agent inventory, usage, permissions, and AI-specific protections not available. |

## Control Movement and Baseline Changes

Q1 and Q2 each reported 38.6% overall (105/272), 89.39% Identity, 0% Data, and 23.35% Apps. Q3 reports 39.33% overall (105/267), 96.72% Identity, 0% Data, and 23.35% Apps. Identity is 7.33 percentage points higher and currently earns 59/61 points, but no comparable prior identity point breakdown or control-by-control baseline is available to attribute that increase to specific remediation. The July–September trends are essentially flat. Neither the unchanged earned total nor a flat trend establishes that no security changes occurred.

The prior assessments reported a current-license score of 54.41%. An exact current value is not established, so that historical figure is not carried forward as the Q3 licensing ceiling. The current overview below provides context for the overall and category scores.

[image]

[image]

# Security Signal Review

This review interprets Microsoft-reported control statuses alongside the Q1 and Q2 assessment history. CIS Microsoft 365 Foundations Benchmark v7.0.0 provides configuration references where directly applicable; NIST CSF 2.0 references identify related security outcomes. Neither mapping constitutes a compliance determination or certification.

A Completed action is a useful Microsoft signal, not an independent audit of policy scope, exclusions, licensing, or operating effectiveness. Likewise, an open action is a validation and remediation opportunity, not proof of exploitation. No evidence was available to establish compensating third-party controls, so these have not been assumed when interpreting the findings.

## Identity and Access

Identity Secure Score is 96.72%, with 59 of 61 points earned. Microsoft reports completion for administrator MFA, all-user MFA, legacy authentication blocking, application-consent restriction, and Exchange modern authentication. These signals support a comparatively strong identity control baseline within the scored scope, while leaving effective coverage and exclusions subject to validation.

Q1 and Q2 described Entra Security Defaults as the identity baseline; the current evidence does not independently confirm the enabled setting or establish the mechanism behind each completed action. User- and sign-in-risk policies and all-user self-service password reset also appear Completed, despite No licensing flags. Managed IT should reconcile those statuses with actual entitlement and effective policy configuration before relying on them as assurance.

The identity score increased from 89.39% in Q1 and Q2, but the Q3 trend is essentially flat and the supplied history cannot identify a specific remediation milestone.

[image]

[image]

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| Administrator MFA 10/10; all-user MFA 9/9, Completed | 5.2.2.1; 5.2.2.2 | PR.AA-03 | Supports authentication protection; exact policy coverage and exclusions are not independently audited. |
| Legacy authentication blocking 8/8, Completed | 5.2.2.3 | PR.AA-03 | Positive identity signal; does not establish the separate SharePoint modern-authentication setting. |
| Application-consent restriction 4/4; least-privileged roles 1/1, Completed | CIS not tested | PR.AA-05 | Related to least privilege and entitlement management; consent scope and role assignments require validation. |
| User-risk and sign-in-risk policies 7/7 each; SSPR All 1/1, Completed | CIS not tested | PR.AA-03 | “Have license = No” accompanies these Completed statuses; reconcile entitlement and effective policies before relying on them. |
| Exchange modern authentication 3/3; password non-expiration 8/8, Completed | CIS not tested | PR.AA-03 | Microsoft-reported configuration signals, not a complete review of authentication methods or password security. |

Maintain the reported identity protections and validate policy coverage during routine administration. The SharePoint modern-authentication recommendation remains separate: identity-level legacy-authentication protection and completed Exchange modern authentication do not confirm the SharePoint setting.

## Endpoint and Vulnerabilities

Endpoint security and vulnerability exposure cannot be assessed from the available evidence. No device inventory, endpoint coverage information, exposure score, vulnerability details, or affected-device counts were available for Q3; the prior reports do not supply comparable endpoint metrics for this review.

The exposure table therefore records an assessment limitation for each quarter rather than zero exposure. The cloud control baseline must not be used to infer device onboarding, patch status, exploitability, or remediation progress.

| Exposure Level | 2026 Q1 | 2026 Q2 | 2026 Q3 |
| --- | --- | --- | --- |
| High | Not available | Not available | Not available |
| Medium | Not available | Not available | Not available |
| Low | Not available | Not available | Not available |

No endpoint or vulnerability visual is available within the supplied assessment scope.

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| Device inventory and onboarding — not provided | Not assessed | Not assessed | No inventory or onboarding evidence; device population and coverage not assessed. |
| Endpoint protection and configuration — not provided | Not assessed | Not assessed | No endpoint configuration evidence; protection effectiveness not assessed. |
| Vulnerability and affected-device detail — not provided | Not assessed | Not assessed | No vulnerability detail; affected systems and exploitability not assessed. |
| Exposure scores and severity distribution — not provided | Not assessed | Not assessed | No exposure metrics; no numerical comparison can be made. |
| Patch and remediation progress — not provided | Not assessed | Not assessed | No remediation records; no closure or exposure reduction is asserted. |

A future endpoint review will require inventory and coverage evidence together with vulnerability and exposure detail. Until that evidence is available, no device-specific finding, risk rating, or quarter-over-quarter improvement is asserted.

## Data Protection and Collaboration

Data remains at 0% and Apps at 23.35%, matching Q1 and Q2. Microsoft identifies DLP as To address at 0/5 points. The sensitivity-label action carries a No licensing flag, which requires entitlement validation rather than an assumption that all data protection is absent. These scores identify a Microsoft-native control gap without establishing the complete extent of Irontrax’s information protection.

The continuing OWA storage, Outlook add-in, and SharePoint modern-authentication actions remain To address at 0/5, 0/3, and 0/1 points respectively, each flagged licensed. The OWA investigation was requested in 2024-Q3; Q2 noted that earlier score fluctuations had stopped but implementation was incomplete. The add-in review should preserve approved business integrations: the earlier Salesforce Outlook integration is historical context, not a confirmed current inventory.

Common attachment filtering (0/5), blocking all forms of mail forwarding (0/5), mailbox auditing (0/3), and external calendar sharing restrictions (0/5) remain open and flagged licensed. Automatic forwarding set to system-controlled is separately Completed at 1/1, and Microsoft 365 audit log search is Completed at 3/3; neither resolves the broader forwarding or mailbox-auditing action.

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| OWA storage 0/5; Outlook add-ins 0/3, To address | 6.5.3; 6.3.1 (Level 2) | PR.PS-01; PR.PS-05 | Continuing hardening recommendations. Review approved integrations before restricting user add-in installation. |
| SharePoint modern authentication 0/1, To address | 7.2.1 (Level 1) | PR.AA-03 | Validate the SharePoint-specific legacy-authentication setting; related identity completion does not close this action. |
| DLP 0/5; common attachment filter 0/5, To address | 3.2.1; 2.1.2 (Level 1) | PR.DS-01; PR.DS-02; PR.PS-01 | Review active DLP coverage and default anti-malware filtering. Outcomes are relevant; effective protection is not proven. |
| Forwarding block 0/5; mailbox auditing 0/3, To address | Exact CIS configuration not assessed | PR.PS-01; PR.PS-04 | System-controlled forwarding and audit-search completion have different scopes; verify forwarding paths and logged mailbox activity. |
| Calendar sharing 0/5; Teams lobby 0/2, presenters 0/2, anonymous join 0/1, To address | Exact CIS configuration not assessed | PR.AA-05; PR.PS-01 | Validate access restrictions and business exceptions. Completed dial-in, external-control, and meeting-start settings remain distinct. |

Microsoft also reports completed phishing, spam, bulk-spam, and zero-hour auto-purge protections, but these do not replace attachment filtering or prove advanced anti-impersonation coverage. Teams restrictions for invited users and lobby handling (0/2), presenters (0/2), and anonymous join (0/1) remain open, while dial-in lobby protection, external control, and anonymous meeting-start restrictions each earn 1/1. Review these distinct settings against legitimate collaboration needs rather than treating the meeting baseline as wholly unprotected.

## Cloud Workload and Attack Path Exposure

Cloud workloads and attack paths are not assessed. The supplied control and score evidence does not include a workload inventory, resource exposure, permissions relationships, or attack-path analysis.

No conclusion can be drawn about the presence or absence of cloud-hosted assets, public exposure, exploitable paths, or workload remediation. Microsoft 365 identity signals do not substitute for a resource-level cloud assessment.

Workload and attack-path evidence was not provided.

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| Cloud resource inventory — not provided | Not assessed | Not assessed | Resources and business scope not established. |
| Workload protection and configuration — not provided | Not assessed | Not assessed | Workload-specific protection and posture not assessed. |
| Public exposure — not provided | Not assessed | Not assessed | No resource exposure evidence available. |
| Permissions and attack paths — not provided | Not assessed | Not assessed | No permissions relationships or attack-path analysis available. |
| Workload remediation history — not provided | Not assessed | Not assessed | No supported workload change or resolution milestone. |

No workload-specific CIS or NIST mapping is asserted without an assessed condition.

If cloud workloads are included in the next review, confirm the resource scope and obtain the relevant posture and attack-path evidence before assigning findings or remediation priorities.

## AI Agents and Generative AI Usage

AI agents and generative AI usage are not assessed. No AI application or agent inventory, permissions review, usage information, or AI-specific data-protection evidence was available.

The absence of AI evidence does not establish that Irontrax has no AI use or related exposure. Existing identity and data-protection signals cannot establish which AI services are approved, what information they access, or whether their permissions and sharing behavior are appropriate.

AI-specific evidence was not provided.

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| AI service and agent inventory — not provided | Not assessed | Not assessed | Approved or unapproved AI services and agents not established. |
| AI adoption and usage — not provided | Not assessed | Not assessed | Usage scope and business workflows not established. |
| Agent permissions and access — not provided | Not assessed | Not assessed | Delegated access and service permissions not assessed. |
| AI data access and protection — not provided | Not assessed | Not assessed | AI-specific information handling and protection not assessed. |
| AI governance and change history — not provided | Not assessed | Not assessed | No governance evidence or supported change milestone available. |

No AI-specific framework finding is assigned from the available evidence.

Any future AI review should begin with confirmed business use and service scope. The awareness guidance in this report addresses verification of impersonation attempts; it is not a finding of AI misuse or an Irontrax incident.

## Detection and Operational Readiness

Microsoft 365 audit log search is reported Completed at 3/3 points, while mailbox auditing remains To address at 0/3. This distinction matters: access to the audit-search capability does not establish that the required mailbox activities are being recorded across the intended population.

No incident records, alert-review evidence, escalation procedures, response exercises, or recovery tests were available. Operational detection and response effectiveness therefore remain unassessed. The completed email protection actions describe reported control settings, not a measured record of successful detection or response.

Validate mailbox audit configuration and demonstrate that relevant events can be retrieved. This relates to NIST CSF 2.0 PR.PS-04, which addresses log generation and availability; it does not by itself establish monitoring outcomes or response readiness.

# Recommended Security Actions

The actions below focus on the continuing client recommendations and the additional material opportunities supported by Q3. Priority reflects practical remediation sequencing, not an independently assessed severity rating. Newly emphasized actions were identified in this assessment; their underlying conditions are not proven to have begun in Q3.

| Security Awareness As businesses rapidly scale cloud-native applications and integrate automated tools, a familiar vulnerability continues to drive some of the largest data exposures: cloud misconfigurations and “shadow” APIs.  Recent analyses highlight that a vast majority of cloud security incidents stem from basic configuration oversights, such as overly permissive storage accounts and forgotten keys, not from sophisticated zero-day software exploits. Because cloud ecosystems are deeply interconnected, a single overlooked API or misconfigured application can grant attackers privileged access to internal infrastructure.  Mitigating this active threat requires organizations to bridge the gap between development speed and security governance, implementing continuous automated posture management to ensure visibility matches the pace of change. |
| --- |

## Active Recommendations

| Priority | Identified | Recommendation | Status |
| --- | --- | --- | --- |
| 1 | 2024 Q2 | Complete the three continuing Outlook and SharePoint recommendations below. Managed IT should verify effective settings and retain test results. | 2026 Q3: All three remain To address; no supported resolution. |
| 2 | 2026 Q3 | Enable and test common attachment filtering. Review external forwarding routes and document narrowly scoped business exceptions. | Open: filter 0/5 and forwarding block 0/5; flagged licensed. |
| 3 | 2026 Q3 | Implement active DLP coverage for approved information types and locations. Test enforcement and document exceptions. | Open: DLP 0/5; flagged licensed. Data score 0%. |
| 4 | 2026 Q3 | Review external calendar sharing and Teams admission, presenter, and anonymous-join restrictions. Test legitimate guest workflows before enforcement. | Open: calendar 0/5; Teams actions 0/2, 0/2, and 0/1; flagged licensed. |
| 5 | 2026 Q3 | Validate mailbox audit activities, populations, and bypass settings. Demonstrate retrieval of representative events. | Open: mailbox auditing 0/3; flagged licensed. Audit search separately Completed. |
| 6 | 2026 Q3 | Validate entitlement and scope for advanced email protection, sensitivity labels, and completed advanced identity actions before implementation or procurement. | Validation required: inconsistent license flags do not establish entitlement or a purchase requirement. |

## CIS Microsoft 365 Foundation Benchmark

The following configuration recommendations reference CIS Microsoft 365 Foundations Benchmark v7.0.0. SharePoint modern authentication, common attachment filtering, and DLP are Level 1 recommendations for the applicable E3/E5 profiles. OWA additional-storage restrictions and Outlook add-in installation restrictions are Level 2 recommendations, not Level 1. Open Microsoft actions guide validation; they do not independently establish CIS noncompliance.

| CIS Ref. | Recommendation | Description | Status |
| --- | --- | --- | --- |
| 6.5.3 | Restrict Additional Storage Providers in OWA | Level 2. Set AdditionalStorageProvidersAvailable to False in the default OWA mailbox policy; verify effective assignments to restrict unapproved external storage. | Identified 2024 Q2. Q3: To address, 0/5. Prior investigation and Q2 stabilization do not confirm implementation. |
| 6.3.1 | Ensure Installing Outlook Add-Ins Is Not Allowed | Level 2. Centrally deploy approved add-ins, then remove My Custom Apps, My Marketplace Apps, and My ReadWriteMailbox Apps from the default role assignment policy. Reconfirm any required Salesforce integration. | Identified 2024 Q2. Q3: To address, 0/3. Preserve approved integrations through administrator deployment. |
| 7.2.1 | Ensure Modern Authentication for SharePoint Applications Is Required | Level 1. Set LegacyAuthProtocolsEnabled to False, or Block access for apps without modern authentication. Test legitimate SharePoint application access independently of identity and Exchange protections. | Identified 2024 Q2. Q3: To address, 0/1. No confirmed closure. |
| 2.1.2; 3.2.1 | Enable Common Attachment Filtering and Active DLP Coverage | Level 1. Enable common attachment filtering in the default anti-malware policy, retaining required extensions and scoped exceptions. Implement active DLP with appropriate information types, locations, and tested enforcement. | Emphasized in Q3. Each action To address, 0/5; flagged licensed. Prior configuration and onset not established. |

## Deferred Recommendations

No approved deferral or accepted-risk decision is documented. Validate licensing-dependent actions before deciding on implementation or procurement. The three continuing recommendations remain active.

## Recommendation History

Q1 and Q2 recorded no completed recommendation history. Q3 does not establish resolution of any prior recommendation; Microsoft-reported completed controls are not treated as remediation milestones.

### CIS Recommendations

| Quarter | Recommendation | Action | Details |
| --- | --- | --- | --- |
| Q1–Q3 | Continuing CIS recommendations | Open | Prior reports recorded no completed history. The three 2024 Q2 recommendations remain open in Q3. |

### Advisory Recommendations

| Quarter | Recommendation | Action | Details |
| --- | --- | --- | --- |
| Q1–Q2 | Awareness continuity | Advice | Q1 emphasized impersonation verification; Q2 emphasized help-desk credential and MFA recovery. Training delivery and effectiveness were not measured. |
| Q3 | Advisory remediation history | Open | No advisory recommendation is confirmed resolved; active actions require validation. |

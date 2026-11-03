Irontrax

Cloud Security Assessment – 2026: Q3

Prepared For

Joe Santora

Prepared By

Danny George

October 8, 2026


# Executive Summary

Irontrax’s Q3 position shows no verified change from the Q1 and Q2 assessments. Identity protection remains comparatively strong in Microsoft’s reporting, while email, collaboration, and data-protection controls remain incomplete. The primary risk theme for Q3 is this continuing gap between Microsoft-reported identity protection and the less complete data and collaboration control baseline. Identity controls protect how users sign in. The open email and collaboration settings govern what information can leave Irontrax through forwarding, external storage, add-ins, and external sharing.

The Secure Score movement does not indicate security progress. Microsoft Secure Score is 39.33%, with 105 of 267 available points, compared with 38.6% and 105 of 272 points in both prior assessments. The 0.73 percentage-point increase reflects a smaller available-point denominator, not additional earned points or demonstrated remediation. Identity remains the strongest scored category at 96.72%, while Data remains at 0% and Apps at 23.35%. These indicators help prioritize configuration review, but they do not establish overall risk maturity or framework compliance.

The three recommendations first identified in 2024-Q2 remain the clearest carried-in risk: restricting additional storage providers in Outlook on the web, preventing user installation of Outlook add-ins, and requiring modern authentication for SharePoint applications. Each remains open in Q3. The current action statuses support retaining these recommendations, although they do not establish that no remediation work has occurred.

Q3 also brings six related email and collaboration controls into focus: common attachment filtering, data loss prevention, mail forwarding restrictions, mailbox auditing, external calendar sharing, and Teams meeting controls. These are newly emphasized in this assessment rather than proven to have first arisen during Q3. No prior recommendation can be confirmed resolved, and the essentially flat Q3 score trends support neither a conclusion of major gains nor one of major regressions.

This assessment covers Microsoft-reported identity, data, email, and collaboration controls. Endpoint, vulnerability, cloud workload, AI, and incident-response evidence was not available, so those domains remain unassessed rather than presumed secure or unchanged. The report continues the findings and historical context reported in Q1 and Q2, using the current Microsoft Secure Score indicators and recommended-action statuses as the observable baseline.

Irontrax should continue to use this report to guide risk-based remediation discussions rather than to pursue Secure Score improvement as an end goal. The most valuable next step is to close the continuing configuration recommendations alongside practical email and data-protection improvements. Managed IT should validate effective policy scope and business exceptions, record changes and test results, and confirm licensing before deciding whether advanced protections require additional entitlement. Progress should be measured by demonstrated exposure reduction, not score improvement alone.


# Current Microsoft Cloud Security Posture

Irontrax’s cloud security posture is uneven. Identity controls are comparatively well scored, while Microsoft continues to identify unaddressed opportunities in email, collaboration, and data protection. The available evidence supports a targeted configuration review of those areas. It does not provide a complete assessment of devices, workloads, incidents, or operational effectiveness.

## Posture Summary

Irontrax has a substantial backlog of open Microsoft recommendations, and the licensing data attached to them is not reliable enough to drive purchasing decisions. Of 69 recommended actions, Microsoft reports 28 Completed and 41 To address. Among the open actions, 22 carry a Have license value of Yes and 19 a value of No. These flags are not independently verified entitlements, and some advanced controls show inconsistent flags across completed and pending actions. Irontrax should therefore confirm entitlement before treating any open action as either ready to configure or requiring a purchase. Peer scores of 46.8% overall and 60.9% for identity provide comparison context only. They are not an assurance standard or a reliable measure of Irontrax’s risk maturity.

## Key Risk Themes

Four themes summarize the material conditions behind the Q3 control baseline. They separate the continuing client recommendations from additional control opportunities and from areas where the evidence is too limited to support a posture conclusion.

• **Long-standing Outlook and SharePoint hardening.** Complete the long-standing Outlook and SharePoint hardening recommendations while preserving approved business integrations and confirming effective tenant settings.

• **Email and collaboration exposure.** Close the email and collaboration gaps through attachment filtering, forwarding review, and proportionate external-sharing and meeting restrictions.

• **Data protection and mailbox logging.** Establish effective data-protection coverage and verify mailbox logging. Score completion in a related control does not establish equivalent protection.

• **Validation before assurance or procurement.** Validate policy scope, licensing, and unassessed domains before drawing assurance conclusions or committing to additional products.

## Domain Posture

The indicators below describe the strength and limits of the available evidence for each domain rather than assigning maturity ratings the evidence cannot support. Q1 and Q2 did not establish comparable domain-level indicators, so this table sets the Q3 baseline. Historical comparisons are limited to the metrics and recommendations previously reported.

| Domain | Posture Indicator | Interpretation |
| --- | --- | --- |
| Identity & Access | Strong Microsoft-reported baseline | Identity 96.72% (59/61); key MFA and legacy-authentication actions Completed. |
| Endpoint Security | Not assessed | Device inventory, onboarding, endpoint protection, and coverage evidence were not available. |
| Vulnerability Management | Not assessed | No vulnerability, affected-device, exposure, or exploitability detail was available. |
| Data Protection | Requires control review | Data 0%; DLP is To address at 0/5. Information-protection scope and label entitlement require review and implementation. |
| Email & Collaboration | Mixed control baseline | Apps 23.35%; completed email protections coexist with open Outlook, SharePoint, attachment, forwarding, calendar, and Teams actions. |
| Detection & Operational Readiness | Limited assurance | Audit search is Completed, but mailbox auditing remains open. Operational monitoring and response effectiveness were not assessed. |
| Cloud Workload & Attack Paths | Not assessed | Workload inventory, resource exposure, and attack-path evidence was not available. |
| AI Agents & Generative AI | Not assessed | Evidence on AI agent inventory, usage, permissions, and AI-specific protections was not available. |

## Control Movement and Baseline Changes

![Irontrax overall score of 39.33% compared with Microsoft peer average of 46.8%.](media/image2.png)![Q3 Microsoft Secure Score overview: 39.33%, 105 of 267 points; Identity 96.72%, Data 0%, and Apps 23.35%.](media/image3.png)The overall score did not move in a way that reflects security change, and the identity increase cannot yet be attributed to specific remediation. Q1 and Q2 each reported 38.6% overall (105/272), 89.39% Identity, 0% Data, and 23.35% Apps. Q3 reports 39.33% overall (105/267), 96.72% Identity, 0% Data, and 23.35% Apps. Because earned points stayed at 105, the overall increase is measurement movement from a smaller denominator. Identity is 7.33 percentage points higher and earns 59/61 points in Q3. No comparable prior identity point breakdown or control-by-control baseline is available, so that increase is unattributed rather than verified improvement. The Q3 trends are essentially flat. Neither the unchanged earned total nor a flat trend establishes that no security changes occurred.

The prior assessments also reported a current-license score of 54.41%. The Q3 license score shows 55.43%, a 1.02 point increase. Again, this can be attributed to the overall increase from a smaller denominator. The overview and trend charts show the Q3 overall and category scores.

![Overall Microsoft Secure Score trend remains essentially flat during Q3.](media/image4.png)

# Security Signal Review

This section explains the evidence behind each posture indicator. It reads Microsoft-reported control statuses alongside the Q1 and Q2 assessment history. CIS Microsoft 365 Foundations Benchmark v7.0.0 provides configuration references where directly applicable, and NIST CSF 2.0 references identify related security outcomes. Neither mapping constitutes a compliance determination or certification.

Two reading rules apply throughout. A **Completed** action is a useful Microsoft signal, not an independent audit of policy scope, exclusions, licensing, or operating effectiveness. An **open** action is a validation and remediation opportunity, not proof of exploitation. No evidence was available to establish compensating third-party controls, so none has been assumed when interpreting the findings.

## Identity and Access

Identity is Irontrax’s strongest domain, and the priority is to confirm these protections rather than rebuild them. Identity Secure Score is 96.72%, with 59 of 61 points earned. Microsoft reports completion for administrator MFA, all-user MFA, legacy authentication blocking, application-consent restriction, and Exchange modern authentication. Together, these signals indicate a comparatively strong identity control baseline within the scored scope.

One caveat limits the assurance these statuses provide. User-risk and sign-in-risk policies and all-user self-service password reset appear Completed despite No licensing flags. These policies are enabled and enforced because of Entra Security Defaults. If Irontrax were to move away from Security Defaults, these policies would need to be implemented manually.

![Irontrax identity score of 96.72% compared with Microsoft peer average of 60.9%.](media/image5.png)The identity score rose from 89.39% in Q1 and Q2 to 96.72% in Q3. The Q3 trend is essentially flat, and the supplied history cannot identify a specific remediation milestone, so the increase is recorded as unattributed movement rather than verified improvement.

![Identity Secure Score trend remains essentially flat during July through September 2026.](media/image6.png)

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| Administrator MFA 10/10; all-user MFA 9/9, Completed | 5.2.2.1; 5.2.2.2 | PR.AA-03 | User and administrator authentication protection is enabled and enforced. |
| Legacy authentication blocking 8/8, Completed | 5.2.2.3 | PR.AA-03 | This is a positive identity signal, but it does not establish the separate SharePoint modern-authentication setting. |
| Application-consent restriction 4/4; least-privileged roles 1/1, Completed | CIS not tested | PR.AA-05 | These controls relate to least privilege and entitlement management. |
| User-risk and sign-in-risk policies 7/7 each; SSPR All 1/1, Completed | CIS not tested | PR.AA-03 | “Have license = No” accompanies these Completed statuses. These policies are enabled because of Entra Security Defaults. |
| Exchange modern authentication 3/3; password non-expiration 8/8, Completed | CIS not tested | PR.AA-03 | These are Microsoft-reported configuration signals, not a complete review of authentication methods or password security. |

Irontrax should maintain the reported identity protections and validate policy coverage and exclusions during routine administration. This ensures Irontrax’s environment is as secure as Microsoft controls suggest it is. The SharePoint modern-authentication recommendation remains a separate open item. Identity-level legacy-authentication protection and completed Exchange modern authentication do not confirm the SharePoint setting, which is addressed under Data Protection and Collaboration.

## Endpoint and Vulnerabilities

Irontrax’s endpoint and vulnerability exposure is unknown for Q3, and that gap should be treated as a visibility problem rather than a clean result. No device inventory, endpoint coverage information, exposure score, vulnerability details, or affected-device counts were available for Q3, and the prior reports do not supply comparable endpoint metrics. As a result, no quarter-over-quarter comparison is possible for this domain.

The exposure table below records an assessment limitation for each quarter, not zero exposure. The cloud control baseline must not be used to infer device onboarding, patch status, exploitability, or remediation progress.

| Exposure Level | 2026 Q1 | 2026 Q2 | 2026 Q3 |
| --- | --- | --- | --- |
| High | Not available | Not available | Not available |
| Medium | Not available | Not available | Not available |
| Low | Not available | Not available | Not available |

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| Device inventory and onboarding — not provided | Not assessed | Not assessed | No inventory or onboarding evidence was provided, so device population and coverage were not assessed. |
| Endpoint protection and configuration — not provided | Not assessed | Not assessed | No endpoint configuration evidence was provided, so protection effectiveness was not assessed. |
| Vulnerability and affected-device detail — not provided | Not assessed | Not assessed | No vulnerability detail was provided, so affected systems and exploitability were not assessed. |
| Exposure scores and severity distribution — not provided | Not assessed | Not assessed | No exposure metrics were provided, so no numerical comparison can be made. |
| Patch and remediation progress — not provided | Not assessed | Not assessed | No remediation records were provided, so no closure or exposure reduction is asserted. |

## Data Protection and Collaboration

Data protection and collaboration is Irontrax’s weakest scored area, and its scores have not moved since Q1. Data remains at 0% and Apps at 23.35%, matching Q1 and Q2. Microsoft identifies DLP as To address at 0/5 points. These are carried-in conditions rather than new ones, and they identify a Microsoft-native control gap. The sensitivity-label action carries a No licensing flag, which requires Microsoft Business Premium or above Enterprise level licensing for entitlement. Irontrax has Microsoft Business Standard licensing, so the sensitivity-label action is unavailable, which limits Irontrax’s data protection capabilities.

The open controls in this domain describe one connected exposure: how information leaves Irontrax. Outlook add-ins and additional storage providers in Outlook on the web create routes to external services. Mail forwarding and external calendar sharing send information outside the organization. DLP is the control that would detect sensitive content on those routes, and Microsoft reports it as To address. Mailbox auditing determines whether such activity can be reconstructed afterward. Because no evidence of compensating third-party controls was available, Irontrax cannot yet demonstrate that sensitive information is protected on these routes.

The three continuing recommendations, first identified in 2024-Q2, remain open: OWA storage at 0/5, Outlook add-ins at 0/3, and SharePoint modern authentication at 0/1, each flagged licensed. Because Microsoft flags them as licensed, they appear to be configuration decisions rather than procurement decisions, subject to the entitlement validation noted above. The OWA investigation was requested in 2024-Q3. Q2 noted that earlier score fluctuations had stopped but implementation was incomplete. The add-in review should preserve approved business integrations. The earlier Salesforce Outlook integration is historical context, not a confirmed current inventory.

The data-egress controls show the same pattern. Common attachment filtering (0/5), blocking all forms of mail forwarding (0/5), mailbox auditing (0/3), and external calendar sharing restrictions (0/5) remain open and flagged licensed. Two related actions are Completed: automatic forwarding set to system-controlled (1/1) and Microsoft 365 audit log search (3/3). Neither resolves the broader forwarding or mailbox-auditing action, because each has a different scope.

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| OWA storage 0/5; Outlook add-ins 0/3, To address | 6.5.3; 6.3.1 (Level 2) | PR.PS-01; PR.PS-05 | These are continuing hardening recommendations. Review approved integrations before restricting user add-in installation. |
| SharePoint modern authentication 0/1, To address | 7.2.1 (Level 1) | PR.AA-03 | The SharePoint-specific legacy-authentication setting does not close this action. Modern authentication to SharePoint must be enforced to complete this control. |
| DLP 0/5; common attachment filter 0/5, To address | 3.2.1; 2.1.2 (Level 1) | PR.DS-01; PR.DS-02; PR.PS-01 | DLP coverage and default anti-malware filtering outcomes are relevant, but effective protection is not proven. |
| Forwarding block 0/5; mailbox auditing 0/3, To address | Exact CIS configuration not assessed | PR.PS-01; PR.PS-04 | System-controlled forwarding and audit-search completion have different scopes. Verify forwarding paths and logged mailbox activity. |
| Calendar sharing 0/5; Teams lobby 0/2, presenters 0/2, anonymous join 0/1, To address | Exact CIS configuration not assessed | PR.AA-05; PR.PS-01 | Validate access restrictions and business exceptions. Completed dial-in, external-control, and meeting-start settings remain distinct. |

Email filtering and Teams meetings are partially protected rather than unprotected. Microsoft reports completed phishing, spam, bulk-spam, and zero-hour auto-purge protections. These do not replace attachment filtering or prove advanced anti-impersonation coverage. In Teams, restrictions for invited users and lobby handling (0/2), presenters (0/2), and anonymous join (0/1) remain open. Dial-in lobby protection, external control, and anonymous meeting-start restrictions each earn 1/1. Irontrax should review these distinct settings against legitimate collaboration needs rather than treating the meeting baseline as wholly unprotected.

Irontrax’s next step in this domain is to close the three continuing recommendations, enable common attachment filtering, review forwarding routes, implement active DLP for approved information types and locations, and review external calendar sharing and Teams restrictions. Each change should be tested and its exceptions documented. These actions correspond to Active Recommendations 1 through 4.

## Cloud Workload and Attack Path Exposure

Irontrax’s cloud workload and attack-path exposure is not assessed in Q3. There is no workload inventory, resource exposure, permissions relationships, or attack-path analysis.

No conclusion can therefore be drawn about the presence or absence of cloud-hosted assets, public exposure, exploitable paths, or workload remediation. Microsoft 365 identity signals do not substitute for a resource-level cloud assessment.

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| Cloud resource inventory — not provided | Not assessed | Not assessed | Resources and business scope were not established. |
| Workload protection and configuration — not provided | Not assessed | Not assessed | Workload-specific protection and posture were not assessed. |
| Public exposure — not provided | Not assessed | Not assessed | No resource exposure evidence was available. |
| Permissions and attack paths — not provided | Not assessed | Not assessed | No permissions relationships or attack-path analysis was available. |
| Workload remediation history — not provided | Not assessed | Not assessed | No workload change or resolution milestone is supported by the evidence. |

No workload-specific CIS or NIST mapping is asserted without an assessed condition.

If cloud workloads are in scope for the next review, Irontrax should confirm the resource scope and provide the relevant posture and attack-path evidence before findings or remediation priorities are assigned.

## AI Agents and Generative AI Usage

AI agents and generative AI usage are not assessed in Q3. No AI application or agent inventory, permissions review, usage information, or AI-specific data-protection evidence was available.

The absence of AI evidence does not establish that Irontrax has no AI use or related exposure. Existing identity and data-protection signals cannot show which AI services are approved, what information they access, or whether their permissions and sharing behavior are appropriate.

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| --- | --- | --- | --- |
| AI service and agent inventory — not provided | Not assessed | Not assessed | Approved or unapproved AI services and agents were not established. |
| AI adoption and usage — not provided | Not assessed | Not assessed | Usage scope and business workflows were not established. |
| Agent permissions and access — not provided | Not assessed | Not assessed | Delegated access and service permissions were not assessed. |
| AI data access and protection — not provided | Not assessed | Not assessed | AI-specific information handling and protection were not assessed. |
| AI governance and change history — not provided | Not assessed | Not assessed | No governance evidence or supported change milestone was available. |

No AI-specific framework finding is assigned from the available evidence.

Irontrax should begin any future AI review by confirming business use and service scope. The awareness guidance in this report addresses verification of impersonation attempts; it is not a finding of AI misuse or an Irontrax incident.

## Detection and Operational Readiness

Irontrax can search its Microsoft 365 audit log, but it cannot yet demonstrate that mailbox activity is being recorded. Audit log search is reported Completed at 3/3 points, while mailbox auditing remains To address at 0/3. Access to the audit-search capability does not establish that the required mailbox activities are being recorded across the intended population. Without that record, Irontrax may be unable to reconstruct mailbox activity during an investigation.

Operational detection and response effectiveness remain unassessed. No incident records, alert-review evidence, escalation procedures, response exercises, or recovery tests were available. The completed email protection actions describe reported control settings, not a measured record of successful detection or response.

Irontrax should validate mailbox audit configuration and demonstrate that relevant events can be retrieved. This action relates to NIST CSF 2.0 PR.PS-04, which addresses log generation and availability. It does not by itself establish monitoring outcomes or response readiness.

# Recommended Security Actions

The actions below consolidate the Q3 evidence into a short, risk-based plan. They cover the continuing client recommendations and the additional material opportunities supported by Q3. Priority reflects practical remediation sequencing, not an independently assessed severity rating. Newly emphasized actions were identified in this assessment, but their underlying conditions are not proven to have begun in Q3.

|  |
| --- |
| ***Security Awareness***  *As businesses rapidly scale cloud-native applications and integrate automated tools, a familiar vulnerability continues to drive some of the largest data exposures: cloud misconfigurations and “shadow” APIs. Recent analyses highlight that a vast majority of cloud security incidents stem from basic configuration oversights, such as overly permissive storage accounts and forgotten keys, not from sophisticated zero-day software exploits.*    *Because cloud ecosystems are deeply interconnected, a single overlooked API or misconfigured application can grant attackers privileged access to internal infrastructure. Mitigating this active threat requires organizations to bridge the gap between development speed and security governance, implementing continuous automated posture management to ensure visibility matches the pace of change.* |

## Active Recommendations

| Priority | Identified | Recommendation | Status |
| --- | --- | --- | --- |
| 1 | 2024 Q2 | **Continuing Outlook and SharePoint hardening.** Complete the three continuing Outlook and SharePoint recommendations below. Managed IT should verify effective settings and retain test results. | 2026 Q3: All three remain To address. No resolution is supported. |
| 2 | 2026 Q3 | **Attachment filtering and forwarding control.** Enable and test common attachment filtering. Review external forwarding routes and document narrowly scoped business exceptions. | Open: filter 0/5 and forwarding block 0/5 |
| 3 | 2026 Q3 | **External calendar and Teams meeting restrictions.** Review external calendar sharing and Teams admission, presenter, and anonymous-join restrictions. Test legitimate guest workflows before enforcement. | Open: calendar 0/5; Teams actions 0/2, 0/2, and 0/1 |
| 4 | 2026 Q3 | **Mailbox audit validation.** Validate mailbox audit activities, populations, and bypass settings. Demonstrate retrieval of representative events. | Open: mailbox auditing 0/3, flagged licensed. Audit search is separately Completed. |

## CIS Microsoft 365 Foundation Benchmark

The following configuration recommendations reference CIS Microsoft 365 Foundations Benchmark v7.0.0. SharePoint modern authentication, common attachment filtering, and DLP are Level 1 recommendations for the applicable E3/E5 profiles. OWA additional-storage restrictions and Outlook add-in installation restrictions are Level 2 recommendations, not Level 1. Open Microsoft actions guide validation; they do not independently establish CIS noncompliance.

| CIS Ref. | Recommendation | Description | Status |
| --- | --- | --- | --- |
| 6.5.3 | **Restrict Additional Storage Providers in OWA** | Level 2. Set AdditionalStorageProvidersAvailable to False in the default OWA mailbox policy. Verify effective assignments to restrict unapproved external storage. | Identified 2024 Q2. Q3: To address, 0/5. Prior investigation and Q2 stabilization do not confirm implementation. |
| 6.3.1 | **Ensure Installing Outlook Add-Ins Is Not Allowed** | Level 2. Centrally deploy approved add-ins, then remove My Custom Apps, My Marketplace Apps, and My ReadWriteMailbox Apps from the default role assignment policy. Reconfirm any required Salesforce integration. | Identified 2024 Q2. Q3: To address, 0/3. Preserve approved integrations through administrator deployment. |
| 7.2.1 | **Ensure Modern Authentication for SharePoint Applications Is Required** | Level 1. Set LegacyAuthProtocolsEnabled to False, or Block access for apps without modern authentication. Test legitimate SharePoint application access independently of identity and Exchange protections. | Identified 2024 Q2. Q3: To address, 0/1. No closure is confirmed. |
| 2.1.2; 3.2.1 | **Enable Common Attachment Filtering and Active DLP Coverage** | Level 1. Enable common attachment filtering in the default anti-malware policy, retaining required extensions and scoped exceptions. Implement active DLP with appropriate information types, locations, and tested enforcement. | Emphasized in Q3. Each action remains To address at 0/5 and is flagged licensed. Prior configuration and onset were not established. |

## Deferred Recommendations

No approved deferral or accepted-risk decision is documented. Irontrax should validate licensing-dependent actions before deciding on implementation or procurement. The three continuing recommendations remain active.

## Recommendation History

Q1 and Q2 recorded no completed recommendation history. Q3 does not establish resolution of any prior recommendation. Microsoft-reported completed controls are not treated as remediation milestones.

### CIS Recommendations

| Quarter | Recommendation | Action | Details |
| --- | --- | --- | --- |
| Q1–Q3 | Continuing CIS recommendations | Open | Prior reports recorded no completed history. The three 2024 Q2 recommendations remain open in Q3. |

### Advisory Recommendations

| Quarter | Recommendation | Action | Details |
| --- | --- | --- | --- |
| Q1–Q2 | Awareness continuity | Advice | Q1 emphasized impersonation verification; Q2 emphasized help-desk credential and MFA recovery. Training delivery and effectiveness were not measured. |
| Q3 | Advisory remediation history | Open | No advisory recommendation is confirmed resolved; active actions require validation. |

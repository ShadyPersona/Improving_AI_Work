Team Daks

Cloud Security Assessment – 2026: Q3

Prepared For

Danish Dhedi

Prepared By

Danny George

October 8, 2026

# Executive Summary

Team Daks made limited, measurable progress in Q3, but the evidence does not yet show a material reduction in identity or data-protection risk. Overall Microsoft Secure Score rose to 37.49%, compared with 36.72% in Q2 and 36.61% in Q1. Identity Secure Score rose to 48.33%, compared with the reported quarter-end values of 44.42% and 43.85%, respectively. These results reflect increased Microsoft control credit. They are not a comprehensive measure of risk reduction, and they are not an independently verified September 30 configuration baseline. This assessment continues the client’s quarterly Microsoft cloud security review and draws on the supplied assessment snapshot, with the Q1 and Q2 reports as historical context.

Secure Score is a useful indicator of partially implemented controls and score movement, but it does not establish exploitability, compensating safeguards, or operational effectiveness. The available evidence supports conclusions about identity, email, collaboration, and data protection. Endpoint exposure, vulnerabilities, cloud attack paths, AI usage, and incident-response performance could not be assessed. The report treats those gaps as unknown risk throughout, not as evidence of a secure environment.

The primary risk theme for Q3 remains incomplete identity protection. All-user MFA credit improved only modestly, from 1.99/9 in both prior reports to 2.14/9, and administrative MFA remains incomplete at 9.41/10. Legacy-authentication blocking regressed slightly to 7.93/8. Incomplete sign-in protection leaves accounts more exposed to credential-based compromise and, through those accounts, exposes the email and data they can reach. The longstanding decision between Security Defaults and appropriately licensed Conditional Access therefore remains a priority and is the foundation for the identity actions in this report.

Email defenses give Team Daks a useful foundation against malicious attachments and links. Safe Links for email, Safe Attachments, mailbox intelligence, and several zero-hour auto purge controls receive full credit. That foundation does not extend to impersonation. Mailbox intelligence is not equivalent to intelligence-based impersonation protection, which is uncredited along with related user and domain protections. Data protection is the weaker area: data-protection controls are uncredited, and the Data category stands at 0%. The evidence supplied for Q3 does not substantiate resolution of a previously reported advisory finding.

Team Daks should use this assessment to guide risk-based remediation rather than pursue points as an end goal. The next-quarter action theme has three parts: validate and complete authentication coverage, strengthen impersonation defenses, and establish auditable protection for sensitive information. Before implementation, Team Daks should confirm licensing and policy scope as they stand. It should then document testing and exceptions so that subsequent assessments can distinguish configuration changes from changes in the affected user population.

# Current Microsoft Cloud Security Posture

Team Daks has a mixed Microsoft cloud control baseline. Several email and administrative safeguards receive full credit, while authentication coverage, impersonation prevention, data classification, and auditing require attention. The supplied snapshot represents the observable state for this Q3 review. It is not a point-in-time attestation of every service at quarter end.

## Posture Summary

Team Daks’ posture sits below the peer reference point, and Data is the weakest category. The overall score represents 100.48 of 268 available points. Identity is 48.33%, Apps is 35.86%, and Data is 0%. No Devices category is shown. Peer averages of 46.08% overall and 55.54% for identity provide context, not acceptable-risk thresholds. Team Daks should preserve completed controls. Low or partial control credit warrants configuration validation and focused remediation rather than assumptions about specific affected accounts.

## Key Risk Themes

Four themes capture the material patterns in the Q3 evidence. They separate control opportunities from demonstrated exposure and identify where stakeholder validation is needed. They do not reproduce the full Microsoft recommendation catalog.

Authentication coverage remains incomplete. Partial MFA coverage and a small regression in legacy-authentication blocking leave accounts exposed to credential-based compromise. Team Daks should finish user and administrator MFA coverage, validate resource assignments and exceptions, and investigate the legacy-authentication regression.

Impersonation protection needs attention beyond existing malware defenses. Malware and link controls are credited, but impersonation-specific settings are not. Team Daks should preserve completed email controls while validating anti-phishing policy coverage, protected identities and domains, quarantine actions, and safety tips.

Sensitive-data handling lacks credited policy controls. Without credited DLP or published labels, the evidence cannot show that sensitive information is classified or protected. Team Daks should establish proportionate DLP and published sensitivity labels and review forwarding, external sharing, and meeting-access settings against business needs.

Evidence coverage limits assurance. Several domains could not be assessed, so their risk is unknown rather than low. Team Daks should validate audit availability and operational ownership and obtain asset, vulnerability, cloud-workload, and AI evidence before posture ratings are assigned to those domains.

## Domain Posture

The domain indicators show two domains needing priority attention, one domain with mixed control coverage, one domain pending validation, and four domains that could not be assessed. Each indicator is a qualitative conclusion drawn from the available evidence, not a numerical maturity or risk score. Historical observations are not carried forward as configurations without validation. The Security Signal Review explains the supporting controls and the limits of each conclusion.

Domain

Posture Indicator

Interpretation

Identity & Access

Priority attention

MFA coverage remains incomplete. Identity credit improved in Q3, while legacy-authentication blocking regressed slightly.

Endpoint Security

Not assessed

No device inventory, onboarding, or endpoint health evidence was available, so endpoint risk is unknown.

Vulnerability Management

Not assessed

No CVE, affected-asset, or remediation evidence was available, so vulnerability exposure is unknown.

Data Protection

Priority attention

Data is 0%, and DLP and published sensitivity labels are uncredited. Compensating safeguards require validation.

Email & Collaboration

Mixed control coverage

Email malware and link controls receive full credit. Impersonation and collaboration-file protection remain uncredited.

Detection & Operational Readiness

Validation pending

Audit controls are uncredited. Monitoring effectiveness and response readiness were not assessed.

Cloud Workload & Attack Paths

Not assessed

No workload inventory or attack-path evidence was available, so workload exposure is unknown.

AI Agents & Generative AI

Not assessed

No AI inventory, usage, or agent-permission evidence was available, so AI exposure is unknown.

## Control Movement and Baseline Changes

Q3 score movement reflects modest gains in Microsoft control credit, not verified remediation. Overall Secure Score increased by 0.77 percentage points from Q2 and 0.88 from Q1. Identity increased by 3.91 and 4.48 percentage points, respectively. The prior reports use inconsistent identity starting baselines, so this comparison preserves their reported quarter-end values rather than reconciling them. The all-user MFA control gained 0.15 points versus Q2. The broader identity percentage gain cannot be attributed entirely to MFA, and it cannot be translated into registration coverage.

Microsoft attributes movement within Q3 to changes in the affected user population rather than to documented policy implementation. MFA credit first declined to 1.85/9, then recovered to 2.06/9 and 2.14/9. Legacy-authentication blocking lost 0.07 points in total from 8/8. Because these scores can track user counts rather than configuration, Team Daks should not read them as evidence that controls were strengthened or weakened.

# Security Signal Review

The Security Signal Review supports the domain indicators with Microsoft Secure Score recommendations and history, read alongside the prior quarterly assessments. Framework references use the CIS Microsoft 365 Foundations Benchmark v7.0.0 and NIST Cybersecurity Framework 2.0. These references identify relevant configuration requirements and security outcomes. They do not represent a completed framework audit or a declaration of compliance.

Control credit is baseline evidence, not proof of operational effectiveness. A recommendation without achieved-point metrics or a validated state is a catalog entry. It does not show that a product is deployed or that a vulnerability applies to Team Daks. Where the available evidence is insufficient, third-party safeguards, business exceptions, policy priority, and actual configuration scope require stakeholder validation.

## Identity and Access

Identity is Team Daks’ highest-priority domain because MFA coverage remains incomplete despite the Q3 score gain. Identity Secure Score increased to 48.33%. All-user MFA receives 2.14/9 and administrative MFA receives 9.41/10; both controls require attention. Q1 reported 101 of 131 users not registered for MFA, and Q2 reported 103 of 130. These are historical counts only. No account-level registration report was available for Q3, and control points cannot establish how many users are unprotected. Accounts without MFA remain exposed to password-based compromise, so confirming registration coverage is the first step.

The Conditional Access configuration described in prior quarters requires revalidation. Both prior reports described U.S.-only Conditional Access, administrator MFA, and a “Require MFA for Users” policy with no assigned resources. The recommendation first recorded in 2023 Q3 remains a decision between Security Defaults and appropriately licensed custom Conditional Access. It is not a proposal to operate both approaches together.

Team Daks’ identity score of 48.33% trails the 55.54% average for similar-size organizations. The peer value is contextual and does not determine whether Team Daks’ identity risk is acceptable.

Defender / Secure Score control evidence

CIS Microsoft 365 Benchmark

NIST CSF 2.0

Assessment interpretation

All-user MFA: 2.14/9; administrative MFA: 9.41/10. Both require attention.

5.2.2.2; 5.2.2.1 — E3/E5 Level 1

PR.AA‑03

Partial credit does not establish complete authentication coverage. Validate users, All resources assignments, exclusions, and enforcement.

Legacy-authentication blocking: 7.93/8, regressed.

5.2.2.3 — E3/E5 Level 1

PR.AA‑03; PR.PS‑01

Investigate affected accounts and legacy clients. Population-driven score movement does not demonstrate a policy change.

User app-consent restriction: 4/4, completed. Least-privileged administrative roles: 1/1, completed.

5.1.5.1 — E3/E5 Level 2 (app consent)

PR.AA‑05

Maintain approval and role governance. Existing consent grants and detailed permission reviews are not audited by these points.

Password-expiration policy: 0/8. Sign-in and user-risk policies: 0/7 each; license not held.

1.3.1 — E3/E5 Level 1 (password expiration)

PR.AA‑03; PR.PS‑01

Validate cloud-only password policy and supporting safeguards. Assess risk-policy licensing separately without assuming eligibility.

Exchange modern authentication: 3/3, completed. SharePoint modern authentication: 0/1.

6.5.1; 7.2.1 — E3/E5 Level 1

PR.AA‑03

Exchange credit does not prove equivalent SharePoint coverage. Validate dependencies before restricting legacy application access.

Several identity governance controls are credited, but they do not offset the MFA gap. User app-consent restriction, self-service password reset for all users, more than one global administrator, least-privileged roles, and Exchange modern authentication receive full credit. This reflects reported control credit in the Q3 snapshot, not proof that every CIS audit step passed or that a prior advisory was resolved. Password-expiration policy remains at 0/8, and Team Daks should review it alongside strong authentication and password protection. Sign-in and user-risk policies each receive 0/7 and are identified as unlicensed, so Team Daks should evaluate eligibility and cost separately from the core MFA decision. SharePoint modern authentication and inactive-user sign-out also remain uncredited.

## Endpoint and Vulnerabilities

Endpoint security and vulnerability management were not assessed, so Team Daks’ device risk is unknown. No device inventory, onboarding status, exposure distribution, vulnerability records, or CVE evidence was available. The absence of a Devices category does not show that endpoints are absent, protected, or free of vulnerabilities.

No quarter-over-quarter comparison is possible for endpoint exposure. The prior reports do not provide comparable endpoint exposure counts, so the table records unavailable values for Q1, Q2, and Q3 rather than zeros. Catalog recommendations without tenant metrics cannot establish an affected device population or justify a client-specific vulnerability finding.

Exposure Level

2026 Q1

2026 Q2

2026 Q3

High

Not available

Not available

Not available

Medium

Not available

Not available

Not available

Low

Not available

Not available

Not available

Defender / Secure Score control evidence

CIS Microsoft 365 Benchmark

NIST CSF 2.0

Assessment interpretation

Device inventory not available.

Not mapped

Not assessed

Asset population and endpoint scope cannot be established.

Onboarding and sensor-health evidence not available.

Not mapped

Not assessed

Defender coverage and monitoring effectiveness cannot be validated.

Exposure distribution and score not available.

Not mapped

Not assessed

High, medium, and low counts are unavailable, not zero.

Vulnerability and CVE records not available.

Not mapped

Not assessed

Affected assets, exploitability, and remediation priorities cannot be established.

Endpoint remediation evidence not available.

Not mapped

Not assessed

No endpoint improvement, regression, or resolved vulnerability is claimed.

Team Daks should obtain device inventory, Defender onboarding and health coverage, exposure distribution, and prioritized vulnerability details before endpoint risk or remediation progress is assessed. Until that evidence is available, this report assigns no exposure score, severity distribution, or resolved vulnerability.

## Data Protection and Collaboration

Data protection is a priority gap because the evidence cannot show that Team Daks’ sensitive information is classified or protected by policy. The Data category is 0%, with DLP at 0/5 and published sensitivity-label policies at 0/2. These results do not prove a data breach, and they do not establish whether compensating protections exist. They do mean that Team Daks should validate how sensitive information is classified and protected across relevant Microsoft 365 services. Auto-labeling and Purview data-map labeling each receive 0/1 and are identified as unlicensed, so those advanced capabilities are a separate eligibility decision.

Email defenses against malware and malicious links are well credited, but impersonation protection is largely uncredited. Apps credit is 35.86%. Safe Links for email (9/9), Safe Attachments block mode (8/8) and policy (5/5), common-attachment filtering (5/5), high-confidence phishing action (5/5), and zero-hour auto purge for malware (6/6), phishing (3/3), and spam (1/1) are completed. Mailbox intelligence also receives 8/8. In contrast, intelligence for impersonation protection receives 0/8. User and domain protection, related quarantine actions and safety tips, phishing threshold, and anti-phishing policy creation remain uncredited. Existing malware and link defenses should therefore not be described as comprehensive impersonation prevention.

Credited protection narrows once content moves beyond email. Safe Links for Office applications is uncredited at 0/3, and Safe Attachments for SharePoint, OneDrive, and Teams is uncredited at 0/5. Forwarding protection also needs validation. “System controlled” automatic forwarding receives 1/1, but blocking all forwarding channels receives 0/5. External calendar sharing and additional Outlook on the web storage providers each receive 0/5. These distinctions matter because a completed narrower control does not establish protection across all content or data-transfer paths.

Defender / Secure Score control evidence

CIS Microsoft 365 Benchmark

NIST CSF 2.0

Assessment interpretation

DLP: 0/5. Published sensitivity-label policies: 0/2.

3.2.1; 3.3.1 — E3/E5 Level 1

PR.DS‑01; PR.DS‑02; PR.DS‑10

Validate sensitive-data scope and pilot classification and protection policies. No incident or data-loss count is established.

Mailbox intelligence: 8/8. Intelligence for impersonation: 0/8; anti-phishing policy: 0/3. Related impersonation settings uncredited.

2.1.7 — E5 Level 2

PR.PS‑01

Existing mailbox intelligence is not full impersonation protection. Validate protected users/domains, actions, safety tips, and threshold.

Email Safe Attachments policy: 5/5; block mode: 8/8. Collaboration Safe Attachments: 0/5. Office Safe Links: 0/3.

2.1.4; 2.1.5; 2.1.1 — E5 Level 2

PR.PS‑01

Preserve credited email protections and validate coverage for collaboration files and Office links. Points do not prove every benchmark setting.

System-controlled automatic forwarding: 1/1. All forwarding blocked: 0/5.

6.2.1 — E3/E5 Level 1

PR.DS‑02; PR.PS‑01

Validate transport, outbound policy, mailbox and inbox-rule channels, and approved exceptions. The narrower setting is not equivalent to blocking all forwarding.

Teams lobby, external-control, and anonymous-start restrictions completed. Anonymous joining, invited-only auto-admission, and presenter limits uncredited.

Not mapped in this review

PR.AA‑05; PR.PS‑01

Confirm effective meeting policies and business exceptions rather than treating partial meeting controls as complete access governance.

Meeting access controls are only partly credited. Teams controls for dial-in lobby bypass, external participant control, and anonymous meeting starts each receive full credit. Anonymous joining, automatic admission of invited users only, and presenter restrictions remain uncredited. Team Daks should review meeting policy scope alongside DLP, label publication, and collaboration-file protection. Changes should be piloted with affected business teams, with licensing and exceptions validated and the resulting policies confirmed before implementation is reported as complete.

## Cloud Workload and Attack Path Exposure

Cloud workload and attack-path exposure were not assessed, so Team Daks’ cloud workload risk is unknown. No workload inventory, Defender for Cloud findings, attack-path analysis, or resource-level configuration evidence was available.

Microsoft 365 identity recommendations do not establish the presence or security of Azure workloads. Unmeasured recommendation catalog entries likewise cannot substantiate a reachable attack path or a lateral-movement finding.

Defender / Secure Score control evidence

CIS Microsoft 365 Benchmark

NIST CSF 2.0

Assessment interpretation

Cloud workload inventory not available.

Not mapped

Not assessed

Workload scope and ownership cannot be established.

Workload configuration and posture findings not available.

Not mapped

Not assessed

No client-specific cloud misconfiguration is asserted.

Attack-path analysis not available.

Not mapped

Not assessed

No reachable attack path or lateral-movement exposure is demonstrated.

Workload vulnerability evidence not available.

Not mapped

Not assessed

Cloud vulnerability exposure cannot be evaluated.

Workload monitoring and remediation evidence not available.

Not mapped

Not assessed

No workload monitoring effectiveness or remediation was assessed.

No directly applicable CIS Microsoft 365 configuration mapping is assigned to unassessed cloud workloads.

Team Daks should confirm the in-scope cloud resources and obtain workload-specific posture and attack-path evidence before exposure or remediation conclusions are drawn. No cloud risk rating is assigned in this report.

## AI Agents and Generative AI Usage

AI agents and generative AI usage were not assessed, so the report cannot say whether AI services introduce data-access risk for Team Daks. No AI application or agent inventory, permissions review, usage records, or data-access evidence was available. This report makes no quarter-over-quarter comparison for this domain.

The prior awareness discussions addressed impersonation and identity verification. They did not establish Team Daks’ deployment of AI systems. The app-consent control credited in Q3 also does not constitute an AI-governance assessment.

Defender / Secure Score control evidence

CIS Microsoft 365 Benchmark

NIST CSF 2.0

Assessment interpretation

AI service and agent inventory not available.

Not mapped

Not assessed

AI deployment and adoption cannot be established.

Agent permissions and consent evidence not available.

Not mapped

Not assessed
The general app-consent score does not validate individual AI agents or their permissions.

AI data-access and handling evidence not available.

Not mapped

Not assessed

Sensitive-data use by AI services cannot be evaluated.

AI usage and monitoring evidence not available.

Not mapped

Not assessed

No usage trend or monitoring effectiveness is asserted.

AI governance and remediation evidence not available.

Not mapped

Not assessed

No AI finding is presented as implemented, accepted, or resolved.

No AI-specific CIS Microsoft 365 mapping or unsupported alternate benchmark is assigned.

Team Daks should validate whether AI services or agents are used and obtain their owners, permissions, data access, and monitoring evidence before this domain is assessed. No AI exposure score or adoption conclusion is reported.

## Detection and Operational Readiness

Detection readiness is unverified because neither Microsoft 365 audit control is credited and monitoring and response effectiveness were not assessed. Microsoft 365 audit log search and mailbox auditing for all users each receive 0/3 and remain marked for attention. These signals warrant validation of logging availability and coverage. On their own, they do not establish that all logging is disabled or that no third-party monitoring exists. Without confirmed audit records, investigating account or mailbox misuse would be harder. This report makes no quarter-over-quarter comparison for audit controls.

CIS 3.1.1 addresses audit log search, while CIS 6.1.2 additionally requires appropriate mailbox audit actions and mailbox-type coverage. The Secure Score auditing signal does not fully test the latter. Both are E3/E5 Level 1 recommendations and support NIST PR.PS-04, which concerns generating logs and making them available for monitoring. Team Daks should validate settings and retrieve representative user and administrative events, then confirm retention, access, alert routing, and investigative ownership.

No incident history, detection results, response exercises, or operational service evidence was available. The assessment therefore cannot establish attack frequency, incident absence, or detection maturity. Monitoring of potentially adverse events under NIST DE.CM-09 remains an outcome to validate, not an outcome demonstrated by the Q3 score.

# Recommended Security Actions

The recommendations below consolidate the quarterly evidence into a risk-based action plan. Priority 0 is the foundational identity decision carried forward from the prior assessments, and subsequent priorities address supported control gaps. Status dates indicate this assessment’s review date, not a claimed implementation milestone. Actions first identified in 2026.Q3 reflect newly evaluated evidence, not proof that the underlying condition first arose in Q3.

Security Awareness

As businesses rapidly scale cloud-native applications and integrate automated tools, a familiar vulnerability continues to drive some of the largest data exposures: cloud misconfigurations and “shadow” APIs.  Published analyses highlight that a vast majority of cloud security incidents stem from basic configuration oversights, such as overly permissive storage accounts and forgotten keys, not from sophisticated zero-day software exploits.

Because cloud ecosystems are deeply interconnected, a single overlooked API or misconfigured application can grant attackers privileged access to internal infrastructure.  Mitigating this active threat requires organizations to bridge the gap between development speed and security governance, implementing continuous automated posture management to ensure visibility matches the pace of change.

Support staff should follow a documented verification procedure before changing credentials, enrolling a replacement MFA method, or restoring access. Verify the requester through an independently maintained directory or established recovery process, record the verification, and escalate exceptions rather than bypassing checks because a request sounds urgent or comes from an executive. Staff should also report unexpected MFA prompts and suspected impersonation promptly. Short scenario-based exercises for employees and support personnel would reinforce these behaviors and align with NIST PR.AT-01 and PR.AT-02; no completed training or exercise is asserted in this assessment.

## Active Recommendations

Priority

Identified

Recommendation

Status

0

2023.Q3

Confirm the identity security model. Revalidate licensing and choose Security Defaults or appropriately licensed Conditional Access. Use the latter for custom policy scope and exceptions. The supplied CIS baseline uses Conditional Access. Document the chosen approach and implementation plan.

2026 Q3 - The decision remains active. Policies and licenses in place require validation.

1

2026.Q1

Complete MFA coverage and investigate legacy-authentication gaps. Obtain up-to-date registration and sign-in reports. Validate administrative and all-user coverage, All resources targeting, and documented exclusions. Stage enforcement, provide registration support, and test access and recovery.

2026 Q3 - MFA is partially credited, and legacy blocking regressed. Implementation is not confirmed.

2

2026.Q3

Strengthen impersonation and collaboration protection. Validate anti-phishing policy scope, protected identities/domains, intelligence-based impersonation detection, quarantine actions, safety tips, and threshold. Pilot Office Safe Links and collaboration Safe Attachments while retaining completed email safeguards.

2026 Q3 - Relevant settings remain uncredited. Validation and testing are needed.

3

2026.Q3

Establish sensitive-data controls. Identify business-sensitive content and publish a practical label scheme with scoped DLP policies. Pilot notifications and protection, validate user impact and sharing requirements, and evaluate advanced labeling only after confirming licensing.

2026 Q3 - DLP and published labels are uncredited. The advanced labeling license is not held.

4

2026.Q3

Validate audit coverage and investigative readiness. Confirm audit log search, mailbox audit actions and mailbox types, retrieval of representative events, retention, and access. Assign ownership for alert review and incident escalation, then validate these arrangements through an exercise.

Q2026 3 - Audit controls are uncredited. Monitoring and response effectiveness were not assessed.

5

2026.Q3

Tighten information and meeting access. Review all forwarding channels, calendar sharing, Outlook on the web storage providers, and add-in permissions. Restrict anonymous joining, auto-admission, and presentation rights to approved business needs, documenting tested exceptions.

2026 Q3 - Forwarding, sharing, and selected meeting controls require attention.

## CIS Microsoft 365 Foundation Benchmark

These actions support alignment with CIS Microsoft 365 Foundations Benchmark v7.0.0 E3/E5 Level 1 configurations. The domain tables also reference relevant Level 2 controls and identify them as such. Team Daks should confirm profile applicability and licensing. Secure Score credit and framework mappings do not constitute a full CIS compliance assessment.

CIS Ref.

Recommendation

Description

Status

5.2.2.1; 5.2.2.2; 5.2.2.3

Validate MFA and legacy-authentication policies

E3/E5 Level 1. Verify all-user and administrator MFA targeting All resources, enabled enforcement, and reviewed exclusions. Validate legacy-client blocking and dependencies within the selected identity approach.

2026 Q3 - Partial credit is recorded, and the policy audit is pending. See active priorities 0–1.

1.3.1; 7.2.1

Review password policy and SharePoint authentication

E3/E5 Level 1. Validate non-expiring cloud-only passwords alongside MFA, banned-password safeguards, and user guidance. Require SharePoint modern authentication after checking affected applications.

2026 Q3 - Both controls are uncredited, and configuration validation is needed.

3.2.1; 3.3.1

Enable scoped DLP and publish sensitivity labels

E3/E5 Level 1. Test policies against business-sensitive content and publishing scope, including protection and external-recipient impact. Confirm licensing and applicability before enforcement.

2026 Q3 - The controls are uncredited. See active priority 3.

3.1.1; 6.1.2; 6.2.1

Validate audit and forwarding controls

E3/E5 Level 1. Confirm audit search and required mailbox actions/types. Review transport and outbound policies plus mailbox and inbox-rule forwarding, with approved exceptions.

2026 Q3 - Validation is pending. Narrower forwarding credit is not full coverage. See priorities 4–5.

## Deferred Recommendations

No client-approved deferral is documented in prior assessments, so this section lists no deferred items. The Security Defaults/Conditional Access decision remains active rather than deferred. Unlicensed risk-policy, auto-labeling, and data-map capabilities require an eligibility and business-value review. Lack of licensing is not evidence of an approved risk acceptance.

## Recommendation History

No recommendation has a confirmed closure through Q3. Q1 and Q2 reported no addressed recommendation history, and the Q3 evidence does not establish closure of a previously reported advisory or a completed CIS audit. Full credit on selected Microsoft controls is recognized in the Security Signal Review, but no historical remediation dates or resolved findings are assigned.

### CIS Recommendations

Quarter

Recommendation

Action

Details

Q1–Q3 2026

No confirmed addressed CIS recommendation

None recorded

The prior reports record no addressed history. Control credit in Q3 is not a completed CIS audit or a dated remediation record.

### Advisory Recommendations

Quarter

Recommendation

Action

Details

Q1–Q2 2026

No addressed advisory recommendation reported

None recorded

Both prior assessments state that no recommendation history was available.

Q3 2026

Security Defaults / Conditional Access decision

Continues in active plan

The recommendation originating in 2023 Q3 is retained. Q3 evidence does not substantiate implementation or resolution.

ASM International

Cloud Security Assessment – 2026: Q3

Prepared For

Steven Gasparis

Prepared By

Danny George

October 9, 2026

# Executive Summary

ASM International’s Microsoft cloud security posture is evaluated through the security signals, configuration data, endpoint inventory, vulnerability information, cloud workload inventory, and administrative insights available from Microsoft Defender, Microsoft Secure Score, Microsoft 365, and related Microsoft security portals. This assessment continues the risk-focused structure established in the previous assessments rather than presenting Microsoft Secure Score as a checklist of security controls. This report treats Secure Score as one source of evidence within a broader evaluation of cloud security risk, and it builds on the baseline rather than replacing it.

Secure Score remains useful for identifying Microsoft security recommendations, tracking control movement, and highlighting areas where Microsoft-native controls may be partially implemented or not implemented. However, Secure Score does not fully represent ASM’s actual risk posture by itself. It does not always account for compensating controls, third-party tools, operational exceptions, business requirements, exposure severity, exploitability, or whether a finding is actively exploitable in ASM’s environment. For that reason, this assessment interprets Microsoft findings through broader security domains including identity, endpoint hardening, vulnerability management, email and collaboration security, data protection, and operational readiness.

The primary Q3 risk theme is the gap between improving aggregate exposure and the identity, software, and operational conditions that still require attention. Defender’s Exposure Score is 27/100, compared with 36/100 in Q2 and 55/100 in Q1; however, 65 devices remain in the High exposure category, and active attack paths and unassigned high-severity incidents warrant focused review. The aggregate improvement therefore does not establish that the remaining higher-risk conditions have been resolved.

Overall Secure Score is 63.45%, a decline of 0.67 percentage points from Q2 and 0.69 points above Q1. This mixed trajectory indicates uneven movement: some controls improved, while new or continuing gaps offset those gains. The score movement should therefore guide validation priorities rather than be treated as a standalone measure of risk reduction.

Identity and endpoint evidence shows the same uneven pattern. Identity remains the strongest control area at 81.7%, while User MFA, Administrator MFA, and Self-Service Password Reset remain incomplete. Windows antivirus and EDR block-mode achievement are strong, but Linux real-time protection and antivirus-definition currency are incomplete. The result is inconsistent protection across account and endpoint populations, so the positive category scores do not demonstrate uniform coverage.

Application discovery identifies active generative AI and API traffic. This evidence makes approved-use governance and access control a present priority, but discovery traffic does not by itself establish license assignment, approved use, or sensitive-data disclosure.

ASM should continue to use this report to guide risk-based remediation discussions rather than to pursue Secure Score improvement as an end goal. The most valuable next step should be to prioritize incident ownership. The objective is measurable risk reduction, not score improvement alone.

# Current Microsoft Cloud Security Posture

ASM’s overall security posture is mixed. Aggregate device exposure declined across three assessments, while overall control achievement eased in Q3. High-exposure devices, broad software-update opportunities, and incomplete identity-control signals remain significant. Positive selected-control scores should be preserved, but they do not establish consistent protection across every account, device, or workload.

## Posture Summary

AMS’s overall Secure Score totals 867.3 of 1,367 available points (63.45%). This is a slight decrease from Q2’s achievement of 64.12%. Q3’s achievement split into categories are: Identity 81.7%, Data 55.67%, Device 59.35%, and Apps 79.8%.

Defender identifies 248 active security-recommendation rows and 112 active attack paths. These are recommendation and path records, not counts of unique vulnerabilities, compromised systems or incidents.

## Key Risk Themes

The key risk themes identify the primary security topics that should have focused discussions as part of this assessment. They do not intend to restate every Microsoft Secure Score recommendation or technical finding, but instead they summarize the broader patterns of risk that have emerged from the operational signals this past quarter. These themes are included to help distinguish between individual configuration opportunities and the larger areas where validation, prioritization, or security practice discussions may be needed. They reflect the supplied evidence and the continuity of ASM’s earlier recommendations, rather than an assumed maturity rating.

* MFA and SSPR achievement remain incomplete as service accounts should be reviewed and converted into a more secure form of authentication.
* Exposure reduction must reach the remaining affected systems. The lower aggregate Exposure Score coexists with 65 High-exposure devices and substantial browser, operating-system, and application weaknesses.

Detection requires operational follow-through. Unassigned high-severity incidents and custom-indicator alerts need documented validation, while attack paths to a critical administrator require review of access and connectivity.

* Data and AI governance need specific decisions. Incomplete label-publication, forwarding and mailbox-audit signals should be validated alongside sanctioned and discovered AI services, without equating traffic with confirmed disclosure.

## Domain Posture

The domain posture provides a concise view of the current Microsoft cloud security posture across the major security domains evaluated in this assessment. Rather than focusing on individual recommendations or technical findings, it summarizes the overall condition of each domain based on the available security signals, configuration data, and administrative insights. Indicators are carried forward from the previous assessment and adjusted only where the current data supports a change, so that movement between quarters remains visible. Detailed analysis and the supporting evidence behind these posture indicators are provided later in the Security Signal Review section.

|  |  |  |
| --- | --- | --- |
| Domain | Posture Indicator | Interpretation |
| Identity & Access | Coverage requires validation | 81.7% identity achievement; MFA and SSPR control signals remain incomplete and need evaluation. Service accounts should be reviewed and converted into a more secure form of authentication. |
| Endpoint Security | Mixed control achievement | Positive Windows and Linux sensor signals coexist with Linux protection gaps. |
| Vulnerability Management | Lower aggregate exposure | 27/100 Low; 65 High-exposure devices and material software weaknesses remain. |
| Data Protection | Publication requires review | DLP earns 5/5; sensitivity-label publication 0.01/2. Effective coverage requires validation. |
| Email & Collaboration | Targeted validation needed | Forwarding 0/5 and mailbox auditing 0/3 |
| Detection & Operational Readiness | Triage priority | Two High active incidents are unassigned; outcomes: It was not available. |
| Cloud Workload & Attack Paths | Path review priority | One High cloud path and two Medium on-premises paths among 112 active records. |
| AI Agents & Generative AI | Usage governance needed | Discovery confirms AI, API, and MCP traffic. Agent permissions and content: It was not available. |

## Control Movement and Baseline Changes

![Microsoft Secure Score 63.45 percent, 867.3 of 1,367 points, with Identity, Data, Device and Apps category achievement.](media/image2.png)

Q3 control movement is mixed rather than uniformly positive. Overall achievement moved from 62.76% in Q1 to 64.12% in Q2 and 63.45% in Q3. Identity moved from 82.89% in Q2 to 81.7% in Q3, a 1.19-point decrease from Q2 but a 16.90-point increase from Q1. These changes show relative stability in overall achievement alongside uneven domain movement; they do not establish that the remaining risks have been resolved.

The current Device category is 59.35%, compared with Q2’s reported 62%. Q1 reported cancellation of E5; Q2 described Business Premium, Defender for Endpoint P2 and four Entra ID P2 seats.

# Security Signal Review

The Security Signal Review provides the supporting analysis behind the posture indicators summarized earlier in this assessment. This section reviews the security signals available through Microsoft Secure Score, Microsoft Defender, Microsoft 365, endpoint inventory, vulnerability data, configuration recommendations, and administrative insights. These signals are also interpreted through a broader security program lens aligned to NIST Cybersecurity Framework outcomes and CIS Microsoft 365 Benchmark v7.0.0 where the benchmark provides directly applicable Microsoft 365 configuration recommendations.

These signals should be treated as baseline evidence rather than final maturity conclusions. Microsoft recommendations are useful for identifying available controls and configuration gaps, but they do not always account for third-party tools, managed services, business exceptions, alternate mitigations, or compensating processes. The intent of this review is therefore to distinguish between Microsoft-reported control opportunities, actual exposure reduction, operational risk, and areas requiring validation with ASM stakeholders.

## Identity and Access

Identity remains the highest-scoring category, but authentication coverage is incomplete and declined from Q2. Identity Secure Score is 81.7% in Q3, compared with 82.89% in Q2 and 64.8% in Q1. All-user MFA earns 2.33/9 points and administrator MFA earns 5.56/10; these are control-achievement signals, not counts of registered or unregistered accounts. Q2 reported 390 of 523 accounts not registered for MFA, while Q3 reports 436 out of 588 users. The continuing gap increases credential-based risk, but the account-type and enforcement context must be validated before determining the appropriate response. In the 2025-Q4 discussion, ASM stated that most tenant accounts were service accounts. These accounts should be reviewed for a more secure form of authentication that mitigates the risk posed by user-style accounts. ASM’s identity secure

The CIS Microsoft 365 Benchmark is regarding Conditional Access relating to Identity Protection. The score evidence in the table should be treated as supporting signals rather than a final maturity rating. It highlights where Microsoft sees identity protection as implemented or needing attention, and helps focus the assessment on whether continued progress is being made.

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| All-user MFA: 2.33/9 | 5.2.2.2 | PR.AA-03 | Regressed since Q2. Q3 registration counts: 436 out of 588 users. Service accounts should be reviewed and converted into a more secure form of authentication. |

| Administrator MFA: 5.56/10 | 5.2.2.1 | PR.AA-03 | Regressed since Q2. Registration counts: 4 out of 9 users. Validate privileged-account coverage and documented exclusions. |
| SSPR: 0.14/1 | 5.2.4.1; 5.2.4.2 (Level 2) | PR.AA-03 | Regressed since Q2. Registration counts: 505 of 588 users. Validate coverage between user and service accounts. Service accounts should be reviewed and converted into a more secure form of authentication. |
| User-risk policy: 6.99/7 | 5.2.2.6 | PR.AA-03 | Registration count: 1 users out of 588 users. It is recommended to exclude emergency access accounts, service principals, and service accounts from user-risk policies. Validate coverage between user and service accounts. |
| Sign-in-risk policy: 7/7 | 5.2.2.7 | PR.AA-03 | Registration count: 0 of 470 users that don't have the sign-in risky policy turned on. This is noted as it is a divergence from the above controls. When the policy triggers, the user will need MFA to access the account. If a user hasn't registered for MFA, they’re blocked from accessing their account. Validate coverage between user and service accounts. |

## Endpoint and Vulnerabilities

Aggregate endpoint exposure improved across all three assessments, but the remaining High-exposure population still requires priority remediation. Exposure declined from 55/100 in Q1 to 36/100 in Q2 and 27/100 in Q3, a nine-point improvement since Q2 and 28 points since Q1. The dashboard places 27 within the Low range of 0–29; this aggregate classification does not negate the remaining High-exposure devices.

![Defender exposure distribution showing 65 High-exposure devices; current Medium and Low counts are not displayed.](media/image3.png)High-exposure devices decreased from 73 to 68 to 65. This improvement is meaningful, but the remaining High category is not negated by the aggregate Low score.

Endpoint protection is materially stronger for Windows controls than for the reported Linux controls. Defender reports full achievement for Windows antivirus enablement (10/10), antivirus definitions (9/9), and EDR block mode (8/8), as well as Linux sensor collection and communications (10/10 each). In contrast, Linux real-time protection earns 0/10 and Linux definitions 0/9; general sensor collection, communications, and enablement each earn 8.96/10, with core components at 3/10. Real-time protection and firewall achievement are 9.79/10 and 9.9/10. Q1 reported full Linux-definition achievement, while Q2 described endpoint-control fluctuation. The Q3 evidence therefore supports restoring Linux protection and definition currency on ae2dmzlindkr01, ae2dmzctsapp01, and ae2prdctsdkr01 while preserving the positive Windows and sensor signals.

1. ae2dmzlindkr01
2. ae2dmzctsapp01
3. ae2prdctsdkr01

| Exposure Level | 2026-Q1 | 2026-Q2 | 2026-Q3 context |
| --- | --- | --- | --- |
| High | 73 | 68 | 65 |
| Medium | 32 | 45 | 552 |
| Low | 2 | 15 | 24 |

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| Exposure 27/100; High devices 65 | No direct Microsoft 365 control | ID.RA-05 | Improved since Q2. Lower aggregate exposure, but remaining High devices need prioritized remediation. |
| Linux real-time 0/10; definitions 0/9 | No direct Microsoft 365 control | PR.PS-02; DE.CM-09 | Regressed since Q2. Investigate protection and update gaps. |
| Windows AV 10/10; definitions 9/9; EDR block 8/8 | No direct Microsoft 365 control | DE.CM-09 | Improved since Q2. Positive achievement ensuring windows antivirus and EDR is in Block mode. This is not proof of complete estate coverage. |
| Linux sensor collection and communications 10/10 each | No direct Microsoft 365 control | DE.CM-09 | Positive reporting signal; distinct from antivirus protection and definition health. |

| Application / OS | Q2 catalog\* | Q2 exposed / total | Current Weaknesses | Current exposed / total |
| --- | --- | --- | --- | --- |

| Google Chrome | 1.93k | 64/72 | 3479 | 74/76 |
| Mozilla Firefox | 542 | 13/23 | 1373 | 59/62 |
| Teams Classic | Combined Teams row: 6 | Combined row: 9/70 | 5 | 9/10 |
| Teams | Not variant-specific | Not variant-specific | 1 | 1/66 |
| Teams Personal | Not variant-specific | Not variant-specific | 1 | 3/8 |
| SonicWall Netextender | 10 | 19/50 | 10 | 20/56 |
| Edge Chromium-based | 710 | 93/97 | 2734 | 66/93 |
| Oracle JDK | 233 | 8/8 | 255 | 5/5 |
| Windows Server 2016 | 2.53k | 11/11 | 3502 | 7/7 |
| Windows 10 | 2.29k | 8/8 | 3485 | 9/9 |
| Windows 11 | 1.23k | 69/69 | 2437 | 26/68 |

\**Q2 figures are reproduced as originally displayed in the prior application table; values such as 1.93k and 2.53k are rounded, not exact underlying counts. The original Q2 heading was “# of Vulnerabilities.” Current values use the export’s Weaknesses field. Teams variants are separate and are not summed.*

Changes to inventory and vulnerability catalogs make it difficult to attribute these movements solely to patching activities. Focus on the affected versions and verify any remaining exposure after remediation. While patching, do not aggregate vulnerability or device counts, as overlapping records may result in double counting.

Windows 10 remains detected on nine total devices. The prior Q1/Q2 narrative also described nine reporting devices; the Q2 table showed 8/8. The evidence does not prove Windows 10 migration progress. Validate business dependencies and deploy supported replacements. Exploit and known-threat flags aid prioritization and help establish a timeline for ASM to deploy replacement devices for these nine Windows 10 devices remaining.

## Data Protection and Collaboration

Data protection and collaboration evidence is mixed and requires policy-level validation. Data achievement is 55.67% and Apps achievement is 79.8%. DLP earns 5/5 and unified auditing 3/3, while sensitivity-label publication earns 0.01/2, external automatic forwarding 0/5, and mailbox auditing 0/3. The completed signals are positive, but they do not validate coverage of every sensitive-data scenario, workload, or mailbox action.

ASM should review publication and scope of sensitivity labels, approved forwarding exceptions and mailbox audit actions. The CIS benchmark distinguishes tenant audit-search enablement from required mailbox-level actions; one completed signal cannot substitute for the other. Policy definitions, affected mailbox inventory, retention settings, collaboration sharing controls and DLP test results: It was not available. The current evidence supports targeted configuration validation, not a conclusion that data loss has occurred or that every collaboration service is inadequately protected.

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| Sensitivity-label publication 0.01/2 | 3.3.1 | PR.DS-01 | Validate publication, user scope, and intended protection; policy detail: It was not available. |
| DLP 5/5 | 3.2.1 | PR.DS-01; PR.DS-02 | Positive enablement signal; workloads, sensitive-data scope, and tests: It was not available. |
| External automatic forwarding 0/5 | 6.2.1 | PR.DS-02 | Review forwarding channels, transport rules, outbound policy, and approved exceptions. |
| Mailbox auditing 0/3 | 6.1.2 | PR.PS-04 | ASM should review publication and scope of sensitivity labels, approved forwarding exceptions and mailbox audit actions. |
| Unified auditing 3/3 | 3.1.1 | PR.PS-04 | Positive audit-search signal; does not establish retention or mailbox-action completeness. |

Continue to preserve the positive DLP and unified-audit signals while addressing the incomplete controls. Confirm policy scope and practical enforcement with representative tests, record business exceptions and verify that audit records support investigation. Because earlier reports did not establish comparable detailed data-protection baselines, these observations should not be described as a verified deterioration since Q2.

## Cloud Workload and Attack Path Exposure

Attack-path evidence identifies three higher-priority records within 112 active paths. Defender identifies one High cloud path, two Medium on-premises paths, and 109 Low hybrid paths. The High path involves internet-exposed VM ae2tstwiniis01 and was first seen September 13. The Medium paths involve fileserver.asminternational.org and relay.asminternational.org with routes to the critical Steven Gasparis-Admin account; their first-seen date is March 29. These dates distinguish a Q3-relevant cloud exposure from paths predating the quarter, and the path records represent modeled opportunities rather than confirmed compromise.

Prioritize the internet-exposed workload and validate how the two on-premises routes could reach privileged access. The records represent modeled attack opportunities, not confirmed attacker activity or successful compromise. Detailed chain steps, current access permissions, exposure mitigations, and asset-owner decisions: It was not available. A zero recommendation count on a path is not evidence of zero risk; review the path itself and determine the appropriate network, identity, or workload response.

|  |  |  |  |
| --- | --- | --- | --- |

| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| 112 active paths: 1 High, 2 Medium, 109 Low | No direct Microsoft 365 control | ID.RA-05 | Review active attack paths to prioritize and remediate. |
| High cloud path: ae2tstwiniis01 | No direct Microsoft 365 control | ID.RA-05; ID.RA-06 | Review internet exposure and remediation options with the workload owner. |
| Medium path: fileserver.asminternational.org | No direct Microsoft 365 control | ID.RA-05 | Validate route to critical Steven Gasparis-Admin and reduce unnecessary access. |
| Medium path: relay.asminternational.org | No direct Microsoft 365 control | ID.RA-05 | Validate privileged-access relationships. |
| 109 Low hybrid path records | No direct Microsoft 365 control | ID.RA-06 | Prioritize after High/Medium paths, then prioritize based on internal decisions like user, device age, application, etc. |

CIS Microsoft 365 Foundations v7.0.0 does not provide a direct configuration mapping for these specific Azure and on-premises attack-path records. The NIST references describe applicable risk-management outcomes, not proof of compliance.

Assign owners to the High and Medium paths, validate current connectivity and privilege relationships, and document either remediation or a justified exception. Reassess the paths after changes. Their absence from earlier assessments does not establish that they did not exist, and no current evidence supports declaring the underlying conditions resolved.

## AI Agents and Generative AI Usage

AI-related application discovery confirms usage signals that require governance, but it does not establish approved use or content disclosure. Microsoft 365 Copilot Chat is marked Protected with 34 users and 34 devices, ChatGPT (Consumer & Enterprise) is Sanctioned with 39 users and 42 devices, Google Gemini is Sanctioned with 13 users and 13 devices. These per-application counts may overlap and are not additive adoption totals. Sanctioned and Protected are discovery classifications, not evidence of license assignments or approval of every use case.

GitHub Copilot is Discovered with three users and three devices, OpenAI API with two and two, Atlassian MCP with one and one. Their last-seen dates fall within Q3, supporting quarter-relevant presence, but the aggregate transaction totals are not isolated Q3 activity counts. Copilot Chat, ChatGPT and Gemini observations extend into early October and are current-state context rather than a quarter-end baseline. ChatGPT records 25,756 transactions and 6,808,373,274 upload bytes, or 6.8 Gigabytes, across the represented discovery scope. These are network measures, not proof that prompts or sensitive documents were disclosed.

|  |  |  |  |
| --- | --- | --- | --- |
| Defender / Secure Score control evidence | CIS Microsoft 365 Benchmark | NIST CSF 2.0 | Assessment interpretation |
| Copilot Chat Protected 34 users/34 devices; ChatGPT Sanctioned 39/42; Gemini Sanctioned 13/13 | 3.2.3 (Copilot DLP objective only) | ID.AM-02; PR.DS-01 | Application Discovery includes subsequent-state signals, not Copilot DLP scope. Review acceptable use and ensure data protections are in place. |
| GitHub Copilot Discovered: 3 users/3 devices | No direct Microsoft 365 control | ID.AM-02; GV.PO-01 | Confirm approved use and applicable data restrictions. |
| OpenAI API Discovered: 2 users/2 devices; Atlassian MCP: 1/1 | No direct Microsoft 365 control | ID.AM-02; GV.PO-01 | Validate service owners and permissions, as agent deployment evidence was not available. |
| ChatGPT network transactions and upload traffic | No direct Microsoft 365 control | PR.DS-02; GV.PO-01 | Network telemetry is not sensitive-content disclosure. Review acceptable use and ensure data protections are in place. |
| Langchain 13 weaknesses, 1/1 exposed; @langchain/core 1, 1/1 | No direct Microsoft 365 control | ID.RA-01; PR.PS-02 | Validate and update affected dependencies for the active exploit-available flag. Ensure proper security and hardening procedures are in place to stay up to date. |

The supplied CIS benchmark includes Copilot-specific DLP guidance (3.2.3), but no policy evidence demonstrates whether that control covers ASM’s observed usage. NIST inventory and policy outcomes are therefore used without claiming product-specific certification.

ASM must establish an approved AI-service inventory, validate data-use restrictions and access grants, and review discovered API and MCP use with the relevant owners. These records justify dependency and affected-device review; they do not establish an operating agent, exposure of sensitive content or exploitation. Prioritize the Langchain condition while confirming deployed versions and whether the libraries are in active use.

## Detection and Operational Readiness

Detection and operational readiness requires immediate ownership and documented disposition of open records. Two incidents are High severity, Active, and Unassigned, with classification and determination not set. Incident 14442, Multiple threat families detected on one endpoint, has last activity May 5; incident 14695, Unfamiliar sign-in properties involving one user, has last activity September 23. The first predates Q3 and remains relevant because of its current status, while the second is quarter-relevant. Investigation conclusions, affected-asset scope, and response outcomes were not available; neither record establishes a confirmed breach.

The alert records contain 31 informational, New and Unassigned Connection to a custom network indicator alerts, associated with CustomTI and the Command and Control category. Activity spans September 25 through early October, so the full set is not a Q3-only count. A category label and indicator match do not establish malicious command-and-control activity. Validate the indicator’s purpose, correlate endpoint and identity context, and determine whether repeated connections require containment or represent expected activity.

# Recommended Security Actions

The recommendations below consolidate the quarterly evidence into a short, risk-based action plan and preserve historical context from past assessments. They intentionally avoid reproducing the full Microsoft recommendation catalog but identify areas that should be prioritized for the most benefit to the environment.

|  |
| --- |
| ***Security Awareness***  *As businesses rapidly scale cloud-native applications and integrate automated tools, a familiar vulnerability continues to drive some of the largest data exposures: cloud misconfigurations and “shadow” APIs. Recent analyses highlight that a vast majority of cloud security incidents stem from basic configuration oversights, such as overly permissive storage accounts and forgotten keys, not from sophisticated zero-day software exploits.*  *Because cloud ecosystems are deeply interconnected, a single overlooked API or misconfigured application can grant attackers privileged access to internal infrastructure. Mitigating this active threat requires organizations to bridge the gap between development speed and security governance, implementing continuous automated posture management to ensure visibility matches the pace of change.* |

Help-desk and administrative staff should verify password-reset, MFA-change and privileged-access requests through an established secondary channel, rather than relying on urgency or apparent executive authority. Tie the exercise to ASM’s continuing MFA and SSPR review, and reinforce prompt reporting of unfamiliar sign-ins or unexpected authentication prompts. Training attendance, exercise results, and completion status: It was not available.

## Active Recommendations

|  |  |  |  |
| --- | --- | --- | --- |
| **Priority** | **Identified** | Recommendation | Status |

| 0 | 2026-Q3 | Assign and validate active incidents. Triage incidents 14442 and 14695, investigate custom-indicator connections and record disposition. NIST RS.MA-02; DE.AE-02. | Incidents are active and unassigned |
| 1 | 2026-Q3 | Reduce priority attack-path exposure. Review ae2tstwiniis01 and the two routes to Steven Gasparis-Admin. Assign owners and verify residual paths. NIST ID.RA-05; ID.RA-06. | One High and two Medium active paths. Assign responsibility and ownership. |
| 2 | 2024-Q2 | Ensure MFA coverage for human and privileged users. Obtain registration and policy inventories, review exclusions, and identify service-account alternatives. CIS 5.2.2.1/5.2.2.2; NIST PR.AA-03. | Continuing review: all-user 2.33/9; administrator 5.56/10. |
| 3 | 2023-Q3 SSPR; 2023-Q4 risk migration | Validate SSPR and risk-policy migration. Review scope, two reset methods (Level 2), authentication-method policy, and user/sign-in-risk Conditional Access before retiring legacy policies. CIS 5.2.4.1/5.2.4.2/5.2.2.6/5.2.2.7; NIST PR.AA-03. | SSPR and risk-policies need reviewed to ensure they are following Microsoft best practices. |
| 4 | 2026-Q3 | Remediate affected software and stabilize endpoint protection. Prioritize High-exposure devices, browsers, OS/JDK/Netextender/Teams versions, Linux protection gaps, and Langchain dependencies. NIST PR.PS-02; DE.CM-09. | Remediate high-exposure devices and software as 65 High devices remain, and the list of vulnerable applications remains the same quarter over quarter. |
| 5 | 2026-Q3 | Validate data and AI governance. Review label publication, forwarding exceptions and mailbox audit actions. Inventory approved AI services, API/MCP use and access grants. CIS 3.3.1/6.2.1/6.1.2; NIST PR.DS-01; PR.PS-04; GV.PO-01. | Review acceptable use and ensure data protections are in place. |

## CIS Microsoft 365 Foundation Benchmark

The following actions reference the supplied CIS Microsoft 365 Foundations Benchmark v7.0.0. The listed controls are Level 1 recommendations for the benchmark’s E3/E5 profiles; ASM’s actual license applicability must be validated before implementation. The two-method SSPR recommendation in the identity discussion is control 5.2.4.2, a Level 2 enhancement, and is not represented as Level 1 compliance. References identify configuration objectives rather than a completed CIS audit.

|  |  |  |  |
| --- | --- | --- | --- |
| **CIS Ref.** | Recommendation | Description | Status |
| 5.2.2.1; 5.2.2.2 | Validate administrator and all-user MFA | Confirm policy scope, enforcement, and exceptions against the benchmark; incomplete score signals are not a full configuration audit. | Service accounts should be reviewed and converted into a more secure form of authentication. |
| 5.2.4.1; 5.2.2.6; 5.2.2.7 | Validate SSPR and risk policies | Review All-user SSPR objective and risk-based Conditional Access. Check licensed coverage and recovery before changing scope. | Review scope, two reset methods (Level 2), authentication-method policy |
| 3.3.1; 6.2.1 | Review labels and forwarding | Publish suitable sensitivity-label policies and validate all forwarding channels, with documented business exceptions. | Incomplete label-publication, forwarding and mailbox-audit signals should be validated alongside sanctioned and discovered AI services, without equating traffic with confirmed disclosure. |

| 6.1.2; 3.1.1 | Validate mailbox audit completeness | Confirm required mailbox actions and usable audit records; preserve the positive unified-audit signal. | ASM should review publication and scope of sensitivity labels, approved forwarding exceptions and mailbox audit actions. |

## Deferred Recommendations

A client-approved deferral, risk-acceptance decision, or implementation schedule for the continuing recommendations: It was not available. Consequently, incomplete or unvalidated recommendations remain in the active review rather than being described as deferred or accepted. The historical service-account discussion does not by itself constitute an approved exemption.

## Recommendation History

The following historical outcomes were retained in the Q1 and Q2 reports. They describe actions previously reported, not independently revalidated current configurations. Current evidence does not support a new closure of the continuing MFA, SSPR or risk-policy migration recommendations.

### CIS Recommendations

|  |  |  |  |
| --- | --- | --- | --- |
| Quarter | Recommendation | Action | Details |
|  |  |  |  |

### Advisory Recommendations

|  |  |  |  |
| --- | --- | --- | --- |
| Quarter | Recommendation | **Action** | **Details** |
| 2025-Q2 | Implement Defender for Identity | Previously reported completed work | Prior reports record DC1 health-alert resolution and DC2 sensor installation. |
| 2023-Q3 | Implement Entra Identity Protection risk policies | Previously reported broad policy scope | Prior reports record User and Sign-In Risk policies scoped to All Users. This history does not close the later Conditional Access migration recommendation. |

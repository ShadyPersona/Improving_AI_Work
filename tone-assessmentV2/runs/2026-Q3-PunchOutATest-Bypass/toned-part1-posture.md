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

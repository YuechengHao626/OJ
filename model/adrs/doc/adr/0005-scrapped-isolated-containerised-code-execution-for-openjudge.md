# 5. Scrapped Isolated Containerised Code Execution for OpenJudge

Date: 2025-06-02

## Status

Accepted

## Summary

In the context of trying to achieve good performance for OpenJudge, facing the realisation that executing codes in isolated containers degrades OpenJudge's performance significantly, we decided to change OpenJudge to execute codes within the application backend, to achieve good responsiveness and scalability, accepting that we may need compensation measures to maintain security and prevent malicious codes from being executed.

## Context

- The team focuses on achieving desired levels of responsiveness, scalability and security.
- The team realised that setting up isolated containers for executing code slows down performance of OpenJudge after testing.

## Decision

The team decided to replace OpenJudge's container-isolated code execution with internal code execution. OpenJudge will now handle the execution of submitted codes within its backend, no longer requiring the configuration of external sandbox environments to run those codes. To mitigate the risk of running malicious codes within the backend, we implemented strict code format checks to stop dangerous code from being executed in the first place. This allows us to achieve good response time and scalability for OpenJudge, as it can start and finish code execution in shorter times without configuring different containers for each submitted code.

At the time of writing, we have found out from testing that internal code execution brings code execution time from minutes down to seconds from start to finish. We also found that OpenJudge was able to scale quicker when it executes codes internally rather than externally. This means we can expect the finished OpenJudge to be very responsive and provide code feedback quickly, and still meet the scalability and security requirements in the OpenJudge proposal.

## Consequences

**Advantages:**
- Reduces complexity of overall project, as we no longer need to worry about isolated container configuration.
- Reduces development time needed and guarantees timely delivery.
- Ensures high responsiveness and scalability.

**Neutral:**
- Major shift from original proposal plan, which may require detailed justification in report.

**Disadvantage:**
- Internal code execution is not as secure as container-isolated code execution, will need to ensure code format checks are robust enough to catch as many dangerous code types as possible.

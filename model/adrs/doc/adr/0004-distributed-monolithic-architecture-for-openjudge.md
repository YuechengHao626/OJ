# 4. Distributed Monolithic Architecture for OpenJudge

Date: 2025-05-26

## Status

Accepted

## Summary

In the context of completing OpenJudge on time,
facing technical difficulties in implementing microservice architecture and impending deadline,
we decided to change the architecture of OpenJudge to distributed monolithic architecture,
to achieve successful development and timely delivery of OpenJudge,
accepting that it is a significant change in direction from the original idea.

## Context

- The team has yet to implement a working microservice architecture for OpenJudge.
- The team faced technical problems causing OpenJudge to not work as expected.
- The team has less than ideal time before the deadline.

## Decision

The team decided to redesign OpenJudge's architecture to a distributed monolithic architecture. OpenJudge will be delivered as a single unified application, with code execution processed asynchronously by Celery workers fetching those tasks from an AWS SQS queue. An application load balancer is also used to scale OpenJudge appropriately based on usage. This allows us to develop and deploy OpenJudge successfully before deadline, while still meeting the important quality attributes of OpenJudge: deployability, scalability, and security.

At the time of writing, we have already achieved good progress in getting OpenJudge to work as intended with this architecture. This means we can expect to deliver a working OpenJudge before the deadline, and still meet the deployability, scalability and security requirements in the OpenJudge proposal.

## Consequences

**Advantages:**
- Reduces complexity of overall project, as a distributed monolithic architecture is simpler than a microservice architecture.
- Saves development time, as we only need to develop one unified application.
- Guarantees delivery on time.

**Neutral:**
- Major shift from original proposal plan, which may require detailed justification in report.
- Potential changes to how well OpenJudge delivers the quality attributes required, may require workarounds or compensation designs.
